from flask import Blueprint, render_template, request, redirect, url_for, session
from models.agenda import Agenda
from models.sala import Sala
from models.cirurgia import Cirurgia
from datetime import datetime, date, time

bp_agenda = Blueprint("agenda", __name__)

# ------------------------------------
# Listar todos os agendamentos
# ------------------------------------
@bp_agenda.route("/agendas")
def listar_agendas_usuario():
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    agendas_objs = Agenda.listar_todos()
    agendas = []
    for a in agendas_objs:
        # Busca informações adicionais da cirurgia e sala
        cirurgia = Cirurgia.buscar_por_id(a.cirurgia_id)
        sala = Sala.buscar_por_id(a.sala_id)

        agendas.append({
            "id": a.id,
            "cirurgia": cirurgia.id if cirurgia else "—",
            "sala": sala.nome if sala else "—",
            "dia": (
                datetime.strptime(a.dia, "%Y-%m-%d").strftime("%d/%m/%Y")
                if isinstance(a.dia, str) else
                a.dia.strftime("%d/%m/%Y") if a.dia else "—"
            ),
            "hora": (
                datetime.strptime(a.hora, "%H:%M:%S").strftime("%H:%M")
                if isinstance(a.hora, str) else
                a.hora.strftime("%H:%M") if a.hora else "—"
            )
        })


    return render_template("agendas.html", agendas=agendas)


# ------------------------------------
# Adicionar novo agendamento
# ------------------------------------
@bp_agenda.route("/agendas/adicionar", methods=["GET", "POST"])
def adicionar_agenda():
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    salas = Sala.listar_por_usuario(session["usuario_id"])

    cirurgias = [
        c for c in Cirurgia.listar_por_usuario(session["usuario_id"])
        if c.status == "pendente"
    ]


    if request.method == "POST":
        cirurgia_id = request.form.get("cirurgia_id")
        sala_id = request.form.get("sala_id")
        dia = request.form.get("dia")
        hora = request.form.get("hora")

        # Validação mínima
        if not all([cirurgia_id, sala_id, dia, hora]):
            return redirect(url_for("agenda.adicionar_agenda"))

        # Cria novo agendamento
        a = Agenda(
            cirurgia_id=cirurgia_id,
            sala_id=sala_id,
            dia=dia,
            hora=hora
        )
        a.salvar()

        # Atualiza o status da cirurgia para "agendada"
        cirurgia = Cirurgia.buscar_por_id(cirurgia_id)
        if cirurgia:
            cirurgia.status = "agendada"
            cirurgia.salvar()

        return redirect(url_for("agenda.listar_agendas_usuario"))

    return render_template("adicionar_agenda.html", salas=salas, cirurgias=cirurgias)


# ------------------------------------
# Ver agendamento específico
# ------------------------------------
@bp_agenda.route("/agendas/<int:id>")
def ver_agenda(id):
    agenda = Agenda.buscar_por_id(id)
    if not agenda:
        return redirect(url_for("agenda.listar_agendas_usuario"))

    cirurgia = Cirurgia.buscar_por_id(agenda.cirurgia_id)
    sala = Sala.buscar_por_id(agenda.sala_id)

    return render_template("ver_agenda.html", agenda=agenda, cirurgia=cirurgia, sala=sala)


# ------------------------------------
# Editar agendamento
# ------------------------------------
@bp_agenda.route("/agendas/editar/<int:id>", methods=["GET", "POST"])
def editar_agenda(id):
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    agenda = Agenda.buscar_por_id(id)
    if not agenda:
        return redirect(url_for("agenda.listar_agendas_usuario"))

    salas = Sala.listar_por_usuario(session["usuario_id"])
    cirurgias = Cirurgia.listar_por_usuario(session["usuario_id"])

    if request.method == "POST":
        agenda.cirurgia_id = request.form.get("cirurgia_id")
        agenda.sala_id = request.form.get("sala_id")
        agenda.dia = request.form.get("dia")
        agenda.hora = request.form.get("hora")

        if not all([agenda.cirurgia_id, agenda.sala_id, agenda.dia, agenda.hora]):
            return redirect(url_for("agenda.editar_agenda", id=id))

        agenda.salvar()

        # Garante que a cirurgia vinculada fique com status "agendada"
        cirurgia = Cirurgia.buscar_por_id(agenda.cirurgia_id)
        if cirurgia:
            cirurgia.status = "agendada"
            cirurgia.salvar()

        return redirect(url_for("agenda.listar_agendas_usuario"))

    return render_template("editar_agenda.html", agenda=agenda, salas=salas, cirurgias=cirurgias)


# ------------------------------------
# Excluir agendamento
# ------------------------------------
@bp_agenda.route("/agendas/excluir/<int:id>")
def excluir_agenda(id):
    agenda = Agenda.buscar_por_id(id)
    if agenda:
        # Antes de excluir, marca a cirurgia como "pendente" novamente
        cirurgia = Cirurgia.buscar_por_id(agenda.cirurgia_id)
        if cirurgia:
            cirurgia.status = "pendente"
            cirurgia.salvar()

        agenda.excluir()

    return redirect(url_for("agenda.listar_agendas_usuario"))
