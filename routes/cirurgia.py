from flask import Blueprint, render_template, request, redirect, url_for, session
from models.cirurgia import Cirurgia, CirurgiaCaracteristicas
import sqlite3
from pathlib import Path
from utils.utils import prever_duracao

bp_cirurgia = Blueprint("cirurgia", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent
db_path = BASE_DIR / "database" / "banco_cirurgias.db"


# ------------------------------------
# Lista de cirurgias do usuário logado
# ------------------------------------
@bp_cirurgia.route("/cirurgias")
def listar_cirurgias_usuario():
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tipo, plano, duracao_prevista, status
        FROM cirurgias
        WHERE usuario_id = ?
    """, (session["usuario_id"],))
    cirurgias = [
        {
            "id": row[0],
            "tipo": row[1],
            "plano": row[2],
            "duracao_prevista": row[3],
            "status": row[4]
        }
        for row in cursor.fetchall()
    ]
    conn.close()

    return render_template("cirurgias.html", cirurgias=cirurgias)



# ------------------------------------
# Página de adicionar nova cirurgia
# ------------------------------------
@bp_cirurgia.route("/cirurgias/adicionar", methods=["GET", "POST"])
def adicionar_cirurgia():
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    if request.method == "POST":

        tipo = request.form.get("tipo")
        plano = request.form.get("plano")

        if not tipo or not plano:
            return redirect(url_for("cirurgia.adicionar_cirurgia"))

        # Função auxiliar
        def to_float_or_none(value):
            if value is None or value == '':
                return None
            return float(value)

        # Dicionário das características
        caracteristicas = {
            "sex": request.form.get("sex") or None,
            "bmi": to_float_or_none(request.form.get("bmi")),
            "asa": to_float_or_none(request.form.get("asa")),
            "emop": request.form.get("emop") or None,
            "department": request.form.get("department") or None,
            "optype": request.form.get("optype") or None,
            "approach": request.form.get("approach") or None,
            "position": request.form.get("position") or None,
            "ane_type": request.form.get("ane_type") or None,
            "preop_htn": request.form.get("preop_htn") or None,
            "preop_dm": request.form.get("preop_dm") or None,
            "preop_pft": request.form.get("preop_pft") or None,
            "preop_hb": to_float_or_none(request.form.get("preop_hb")),
            "preop_plt": to_float_or_none(request.form.get("preop_plt")),
            "preop_pt": to_float_or_none(request.form.get("preop_pt")),
            "preop_aptt": to_float_or_none(request.form.get("preop_aptt")),
            "preop_na": to_float_or_none(request.form.get("preop_na")),
            "preop_k": to_float_or_none(request.form.get("preop_k")),
            "preop_glucose": to_float_or_none(request.form.get("preop_glucose")),
            "preop_alb": to_float_or_none(request.form.get("preop_alb")),
            "preop_got": to_float_or_none(request.form.get("preop_got")),
            "preop_gpt": to_float_or_none(request.form.get("preop_gpt")),
            "preop_bun": to_float_or_none(request.form.get("preop_bun")),
            "preop_cr": to_float_or_none(request.form.get("preop_cr")),
            "faixa_etaria": request.form.get("faixa_etaria") or None
        }

        # Checa se alguma característica foi preenchida
        preencheu_alguma = any(v not in [None, ""] for v in caracteristicas.values())

        # Se preencheu, prevê com IA; senão, define padrão 177
        if preencheu_alguma:
            duracao_prevista = prever_duracao(caracteristicas)
        else:
            duracao_prevista = 177

        # Cria cirurgia
        c = Cirurgia(
            usuario_id=session["usuario_id"],
            tipo=tipo,
            plano=plano,
            duracao_prevista=duracao_prevista,
            duracao_real=None,
            status="Pendente"
        )
        cirurgia_id = c.salvar()

        if not cirurgia_id:
            return redirect(url_for("cirurgia.adicionar_cirurgia"))

        # Salva características se existirem
        if preencheu_alguma:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                caracteristicas["cirurgia_id"] = cirurgia_id

                colunas = ", ".join(caracteristicas.keys())
                placeholders = ", ".join(["?"] * len(caracteristicas))
                query = f"INSERT INTO cirurgia_caracteristicas ({colunas}) VALUES ({placeholders})"
                valores = tuple(caracteristicas.values())

                cursor.execute(query, valores)
                conn.commit()
            except sqlite3.Error as e:
                print(f"Erro ao inserir características: {e}")
                return redirect(url_for("cirurgia.adicionar_cirurgia"))
            finally:
                if conn:
                    conn.close()

        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    return render_template("adicionar_cirurgia.html")


# ------------------------------------
@bp_cirurgia.route("/cirurgias/<int:id>")
def ver_cirurgia(id):
    cirurgia = Cirurgia.buscar_por_id(id)
    if not cirurgia:
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cirurgia_caracteristicas WHERE cirurgia_id=?", (id,))
    row = cursor.fetchone()
    conn.close()

    caracteristicas = {}
    if row:
        colunas = [desc[0] for desc in cursor.description]
        caracteristicas = dict(zip(colunas, row))

    return render_template("ver_cirurgia.html", cirurgia=cirurgia, caracteristicas=caracteristicas)

@bp_cirurgia.route("/excluir_cirurgias/<int:id>")
def excluir_cirurgia(id):
    
    cirurgia = Cirurgia.buscar_por_id(id)
    if not cirurgia:
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    cirurgia.excluir()
    return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

@bp_cirurgia.route("/cirurgias/editar/<int:id>", methods=["GET", "POST"])
def editar_cirurgia(id):
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    # Busca a cirurgia pelo ID e garante que pertence ao usuário logado
    cirurgia = Cirurgia.buscar_por_id(id)
    if not cirurgia or cirurgia.usuario_id != session["usuario_id"]:
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    # Busca as características associadas
    # (Assumindo que sua classe de características tenha um método para buscar por cirurgia_id)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cirurgia_caracteristicas WHERE cirurgia_id = ?", (id,))
    caracteristicas_row = cursor.fetchone()
    conn.close()

    if request.method == "POST":
        # Função auxiliar para conversão de tipo
        def to_float_or_none(value):
            if value is None or value == '':
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        # 1. Atualiza os dados da tabela principal 'cirurgias'
        cirurgia.tipo = request.form.get("tipo")
        cirurgia.plano = request.form.get("plano")
        duracao_prevista = request.form.get("duracao_prevista")
        cirurgia.duracao_prevista = int(duracao_prevista) if duracao_prevista else None
        duracao_real = request.form.get("duracao_real")
        cirurgia.duracao_real = int(duracao_real) if duracao_real else None
        cirurgia.status = request.form.get("status")
        cirurgia.salvar() # Salva as alterações na tabela 'cirurgias'

        # 2. Coleta todos os dados das características do formulário
        dados_caracteristicas = {
            "sex": request.form.get("sex") or None,
            "bmi": to_float_or_none(request.form.get("bmi")),
            "asa": to_float_or_none(request.form.get("asa")),
            "emop": request.form.get("emop") or None,
            "department": request.form.get("department") or None,
            "optype": request.form.get("optype") or None,
            "approach": request.form.get("approach") or None,
            "position": request.form.get("position") or None,
            "ane_type": request.form.get("ane_type") or None,
            "preop_htn": request.form.get("preop_htn") or None,
            "preop_dm": request.form.get("preop_dm") or None,
            "preop_pft": request.form.get("preop_pft") or None,
            "preop_hb": to_float_or_none(request.form.get("preop_hb")),
            "preop_plt": to_float_or_none(request.form.get("preop_plt")),
            "preop_pt": to_float_or_none(request.form.get("preop_pt")),
            "preop_aptt": to_float_or_none(request.form.get("preop_aptt")),
            "preop_na": to_float_or_none(request.form.get("preop_na")),
            "preop_k": to_float_or_none(request.form.get("preop_k")),
            "preop_glucose": to_float_or_none(request.form.get("preop_glucose")),
            "preop_alb": to_float_or_none(request.form.get("preop_alb")),
            "preop_got": to_float_or_none(request.form.get("preop_got")),
            "preop_gpt": to_float_or_none(request.form.get("preop_gpt")),
            "preop_bun": to_float_or_none(request.form.get("preop_bun")),
            "preop_cr": to_float_or_none(request.form.get("preop_cr")),
            "faixa_etaria": request.form.get("faixa_etaria") or None
        }

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if caracteristicas_row:
            # 3A. Se já existem, atualiza (UPDATE)
            set_clause = ", ".join([f"{key} = ?" for key in dados_caracteristicas.keys()])
            query = f"UPDATE cirurgia_caracteristicas SET {set_clause} WHERE cirurgia_id = ?"
            valores = tuple(dados_caracteristicas.values()) + (id,)
            cursor.execute(query, valores)
        else:
            # 3B. Se não existem, insere (INSERT)
            dados_caracteristicas['cirurgia_id'] = id
            colunas = ", ".join(dados_caracteristicas.keys())
            placeholders = ", ".join(["?"] * len(dados_caracteristicas))
            query = f"INSERT INTO cirurgia_caracteristicas ({colunas}) VALUES ({placeholders})"
            valores = tuple(dados_caracteristicas.values())
            cursor.execute(query, valores)
        
        conn.commit()
        conn.close()
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    # Passa os dados para o template no método GET
    return render_template("editar_cirurgia.html", cirurgia=cirurgia, caracteristicas=caracteristicas_row)