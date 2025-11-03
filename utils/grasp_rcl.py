import numpy as np
import random
from datetime import datetime, timedelta, time as dt_time

from models import Cirurgia, Sala, Agenda


# -----------------------------
# 1. Carregar dados do banco
# -----------------------------
def load_data_from_db(usuario_id):
    """Carrega cirurgias pendentes e salas do usuário, considerando agendamentos existentes."""
    cirurgias = Cirurgia.listar_por_usuario(usuario_id)
    cirurgias = [c for c in cirurgias if c.status == "Pendente" or c.status == "pendente"]

    if not cirurgias:
        print("Nenhuma cirurgia pendente encontrada.")
        return None

    salas = Sala.listar_por_usuario(usuario_id)
    if not salas:
        print("Nenhuma sala cadastrada.")
        return None

    # ----- gerar blocos (1 semana, seg a dom) -----
    blocos_id = []
    blocos_tipo = []
    blocos_duracao = []
    blocos_sala = []
    blocos_dia = []
    blocos_start_minutos = []

    hoje = datetime.now().date()
    semana = [hoje + timedelta(days=i) for i in range(7)]  # seg a dom

    # Buscar agendamentos existentes da semana
    todos_agendados = Agenda.listar_por_usuario(usuario_id)
    agendamentos_ativos = [
        a for a in todos_agendados
        if hoje <= datetime.fromisoformat(a.dia).date() < hoje + timedelta(days=7)
    ]

    for sala in salas:
        for i, dia in enumerate(semana):
            # define horários conforme o dia
            if i == 0:
                inicio, fim = sala.horario_seg_inicio, sala.horario_seg_fim
            elif i == 5:
                inicio, fim = sala.horario_sab_inicio, sala.horario_sab_fim
            elif i == 6:
                inicio, fim = sala.horario_dom_inicio, sala.horario_dom_fim
            else:
                inicio, fim = sala.horario_seg_inicio, sala.horario_seg_fim

            if not inicio or not fim or (inicio == "00:00" and fim == "00:00"):
                continue

            h_ini_h, h_ini_m = map(int, inicio.split(":")[:2])
            h_fim_h, h_fim_m = map(int, fim.split(":")[:2])
            h_ini = h_ini_h * 60 + h_ini_m
            h_fim = h_fim_h * 60 + h_fim_m
            duracao_total = h_fim - h_ini
            if duracao_total <= 0:
                continue

            # Verifica se há cirurgias já agendadas neste dia/sala
            agendados_sala_dia = [
                a for a in agendamentos_ativos
                if a.sala_id == sala.id and datetime.fromisoformat(a.dia).date() == dia
            ]

            minutos_ocupados = 0
            if agendados_sala_dia:
                for a in agendados_sala_dia:
                    hora = datetime.strptime(a.hora, "%H:%M:%S").time()
                    minutos_inicio = hora.hour * 60 + hora.minute
                    c = Cirurgia.buscar_por_id(a.cirurgia_id)
                    duracao = c.duracao_prevista or 180
                    minutos_ocupados += duracao + 30  # inclui intervalo

            minutos_ocupados = min(minutos_ocupados, duracao_total)
            duracao_livre = duracao_total - minutos_ocupados

            if duracao_livre <= 0:
                print(f"Sala {sala.nome} em {dia} já está totalmente ocupada.")
                continue

            blocos_id.append(f"{sala.id}_{dia}")
            blocos_tipo.append(sala.nome)
            blocos_duracao.append(duracao_livre)
            blocos_sala.append(sala.id)
            blocos_dia.append(dia)
            blocos_start_minutos.append(h_ini + minutos_ocupados)

    print("Blocos gerados:")
    for i in range(len(blocos_id)):
        print(f" - {blocos_id[i]}: {blocos_tipo[i]}, {blocos_duracao[i]} min livres")

    # ----- cirurgias pendentes -----
    cirurgias_tipo = []
    cirurgias_duracao = []
    cirurgias_atraso = []
    cirurgias_id = []

    for c in cirurgias:
        duracao_prev = c.duracao_prevista or 180
        atraso_prev = duracao_prev * 1.1

        cirurgias_id.append(c.id)
        cirurgias_tipo.append(c.tipo)
        cirurgias_duracao.append(duracao_prev)
        cirurgias_atraso.append(atraso_prev)

    # compatibilidade simples
    compatibilidade = np.array(
        [np.arange(len(blocos_id)) for _ in range(len(cirurgias_id))], dtype=object
    )

    return (
        cirurgias_id,
        cirurgias_tipo,
        cirurgias_duracao,
        cirurgias_atraso,
        blocos_id,
        blocos_tipo,
        blocos_duracao,
        blocos_sala,
        blocos_dia,
        blocos_start_minutos,
        compatibilidade,
    )


# -----------------------------
# 2. Funções GRASP (iguais)
# -----------------------------
def construir_ordem_grasp(cirurgias_tipo, cirurgias_duracao, cirurgias_atraso, alpha=0.3):
    indices = list(range(len(cirurgias_tipo)))
    ordem = []

    emerg_idx = [i for i, t in enumerate(cirurgias_tipo) if t == "EMERG"]
    ordem.extend(emerg_idx)

    nao_emerg_idx = [i for i, t in enumerate(cirurgias_tipo) if t != "EMERG"]

    while nao_emerg_idx:
        scores = [(i, cirurgias_atraso[i] - cirurgias_duracao[i]) for i in nao_emerg_idx]
        scores.sort(key=lambda x: x[1])
        k = max(1, int(alpha * len(scores)))
        rcl = [i for i, _ in scores[:k]]
        escolhido = random.choice(rcl)
        ordem.append(escolhido)
        nao_emerg_idx.remove(escolhido)
    return ordem


def construir_solucao(cirurgias_tipo, cirurgias_duracao, blocos_tipo, blocos_duracao, compatibilidade, ordem):
    n_blocos = len(blocos_duracao)
    cirurgias_bloco = [[] for _ in range(n_blocos)]
    cirurgias_canceladas = []
    for i in ordem:
        tipo, dur = cirurgias_tipo[i], cirurgias_duracao[i]
        alocada = False
        for b in compatibilidade[i]:
            if cirurgias_bloco[b]:
                ultimo_fim = cirurgias_bloco[b][-1][3]
                st = ultimo_fim + 30
            else:
                st = 0
            et = st + dur
            if et <= blocos_duracao[b]:
                cirurgias_bloco[b].append((i, tipo, st, et))
                alocada = True
                break
        if not alocada:
            cirurgias_canceladas.append((i, tipo, dur))
    return cirurgias_bloco, cirurgias_canceladas


def calcular_custo_total_fast(cirurgias_bloco, blocos_duracao, duracao_cirurgias, cirurgias_atraso,
                              Cot=8, Cit=3, Cswt=1, Ccs=1500):
    n_blocos = len(blocos_duracao)
    overtime = np.zeros(n_blocos)
    idle_time = np.zeros(n_blocos)
    waiting_time = np.zeros(n_blocos)
    for b_idx in range(n_blocos):
        cirs = cirurgias_bloco[b_idx]
        if len(cirs) == 0:
            idle_time[b_idx] = blocos_duracao[b_idx]
        else:
            tempos = np.array([duracao_cirurgias[i] for i in [c[0] for c in cirs]])
            tempo_total = tempos.sum() + 30 * (len(cirs) - 1)
            fim = tempo_total
            overtime[b_idx] = max(0, fim - blocos_duracao[b_idx])
            idle_time[b_idx] = max(0, blocos_duracao[b_idx] - tempo_total)
            waiting_time[b_idx] = sum([cirurgias_atraso[i] - duracao_cirurgias[i] for i in [c[0] for c in cirs]])
    custo = Cot * overtime.sum() + Cit * idle_time.sum() + Cswt * waiting_time.sum()
    total_cir = sum(len(cirs) for cirs in cirurgias_bloco)
    custo += Ccs * (len(duracao_cirurgias) - total_cir)
    return custo


def busca_local(ordem, cirurgias_tipo, cirurgias_duracao, cirurgias_atraso,
                blocos_tipo, blocos_duracao, compatibilidade, melhor_custo):
    melhor_ordem = ordem[:]
    for _ in range(30):
        nova_ordem = melhor_ordem[:]
        i, j = random.sample(range(len(ordem)), 2)
        nova_ordem[i], nova_ordem[j] = nova_ordem[j], nova_ordem[i]
        solucao, _ = construir_solucao(cirurgias_tipo, cirurgias_duracao,
                                       blocos_tipo, blocos_duracao, compatibilidade, nova_ordem)
        custo = calcular_custo_total_fast(solucao, blocos_duracao, cirurgias_duracao, cirurgias_atraso)
        if custo < melhor_custo:
            melhor_ordem = nova_ordem
            melhor_custo = custo
    return melhor_ordem, melhor_custo


def grasp(cirurgias_tipo, cirurgias_duracao, cirurgias_atraso,
          blocos_id, blocos_tipo, blocos_duracao, compatibilidade,
          max_iter=30, alpha=0.3):
    melhor_solucao = None
    melhor_custo = float('inf')
    melhor_canceladas = None
    for _ in range(max_iter):
        ordem = construir_ordem_grasp(cirurgias_tipo, cirurgias_duracao, cirurgias_atraso, alpha)
        solucao, canceladas = construir_solucao(cirurgias_tipo, cirurgias_duracao,
                                                blocos_tipo, blocos_duracao, compatibilidade, ordem)
        custo = calcular_custo_total_fast(solucao, blocos_duracao, cirurgias_duracao, cirurgias_atraso)
        nova_ordem, novo_custo = busca_local(ordem, cirurgias_tipo, cirurgias_duracao, cirurgias_atraso,
                                             blocos_tipo, blocos_duracao, compatibilidade, custo)
        if novo_custo < melhor_custo:
            melhor_custo = novo_custo
            melhor_solucao, melhor_canceladas = construir_solucao(cirurgias_tipo, cirurgias_duracao,
                                                                  blocos_tipo, blocos_duracao, compatibilidade, nova_ordem)
    return melhor_solucao, melhor_canceladas, melhor_custo


# -----------------------------
# 3. Gravar no banco Agenda
# -----------------------------
def salvar_resultado_na_agenda(melhor_solucao, blocos_sala, blocos_dia, blocos_start_minutos, cirurgias_id):
    """Salva o agendamento final no banco."""
    for b_idx, bloco in enumerate(melhor_solucao):
        sala_id = blocos_sala[b_idx]
        dia = blocos_dia[b_idx]
        start_min = blocos_start_minutos[b_idx]
        for cir in bloco:
            i, _, st, _ = cir
            minuto_absoluto = int(start_min + st)
            hora_dt = datetime.combine(dia, dt_time.min) + timedelta(minutes=minuto_absoluto)
            hora_str = hora_dt.strftime("%H:%M:%S")
            Agenda(
                cirurgia_id=cirurgias_id[i],
                sala_id=sala_id,
                dia=dia.isoformat(),
                hora=hora_str
            ).salvar()
            cirurgia_obj = Cirurgia.buscar_por_id(cirurgias_id[i])
            if cirurgia_obj:
                cirurgia_obj.status = "agendada"
                cirurgia_obj.salvar()


# -----------------------------
# 4. Função principal
# -----------------------------
def agendar_automaticamente(usuario_id):
    dados = load_data_from_db(usuario_id)
    if not dados:
        return "Sem dados suficientes para agendamento."
    (cirurgias_id, cirurgias_tipo, cirurgias_duracao, cirurgias_atraso,
     blocos_id, blocos_tipo, blocos_duracao, blocos_sala, blocos_dia,
     blocos_start_minutos, compatibilidade) = dados
    melhor_solucao, canceladas, custo = grasp(
        cirurgias_tipo, cirurgias_duracao, cirurgias_atraso,
        blocos_id, blocos_tipo, blocos_duracao, compatibilidade
    )
    salvar_resultado_na_agenda(melhor_solucao, blocos_sala, blocos_dia, blocos_start_minutos, cirurgias_id)
    print("✅ Agendamentos gerados e salvos com sucesso!")
    return custo
