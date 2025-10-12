from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.cirurgia import Cirurgia, CirurgiaCaracteristicas
import sqlite3
from pathlib import Path

bp_cirurgia = Blueprint("cirurgia", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent
db_path = BASE_DIR / "database" / "banco_cirurgias.db"


# ------------------------------------
# Lista de cirurgias do usuário logado
# ------------------------------------
@bp_cirurgia.route("/cirurgias")
def listar_cirurgias_usuario():
    if "usuario_id" not in session:
        flash("Faça login para continuar.", "erro")
        return redirect(url_for("usuario.pagina_login"))
    
    usuario_id = session["usuario_id"]
    cirurgias = Cirurgia.listar_por_usuario(usuario_id)
    return render_template("cirurgias.html", cirurgias=cirurgias)


# ------------------------------------
# Página de adicionar nova cirurgia
# ------------------------------------
@bp_cirurgia.route("/cirurgias/adicionar", methods=["GET", "POST"])
def adicionar_cirurgia():
    if "usuario_id" not in session:
        flash("Faça login para continuar.", "erro")
        return redirect(url_for("usuario.pagina_login"))

    if request.method == "POST":
        tipo = request.form.get("tipo")
        plano = request.form.get("plano")

        if not tipo or not plano:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return redirect(url_for("cirurgia.adicionar_cirurgia"))

        # 1️⃣ Cria a cirurgia
        c = Cirurgia(
            usuario_id=session["usuario_id"],
            tipo=tipo,
            plano=plano,
            duracao_prevista=None,
            duracao_real=None,
            status="pendente"
        )
        cirurgia_id = c.salvar()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cirurgia_caracteristicas (cirurgia_id)
            VALUES (?)
        """, (cirurgia_id,))
        conn.commit()
        conn.close()

        flash("Cirurgia adicionada com sucesso!", "sucesso")
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    return render_template("adicionar_cirurgia.html")


@bp_cirurgia.route("/cirurgias/<int:id>")
def ver_cirurgia(id):
    cirurgia = Cirurgia.buscar_por_id(id)
    if not cirurgia:
        flash("Cirurgia não encontrada.", "erro")
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
        flash("Cirurgia não encontrada.", "erro")
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    cirurgia.excluir()
    flash("Cirurgia excluída com sucesso!", "sucesso")
    return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

@bp_cirurgia.route("/cirurgias/editar/<int:id>", methods=["GET", "POST"])
def editar_cirurgia(id):
    if "usuario_id" not in session:
        flash("Faça login para continuar.", "erro")
        return redirect(url_for("usuario.pagina_login"))

    # Busca cirurgia pelo ID
    cirurgia = Cirurgia.buscar_por_id(id)
    if not cirurgia:
        flash("Cirurgia não encontrada.", "erro")
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    # Busca características
    caracteristicas = CirurgiaCaracteristicas.listar_por_cirurgia(cirurgia.id)
    if caracteristicas:
        caracteristicas = caracteristicas[0]  # Pega a primeira, pois só deve ter 1 registro
    else:
        caracteristicas = None

    if request.method == "POST":
        # Atualiza dados da cirurgia
        cirurgia.tipo = request.form.get("tipo")
        cirurgia.plano = request.form.get("plano")
        cirurgia.duracao_prevista = request.form.get("duracao_prevista") or None
        cirurgia.duracao_real = request.form.get("duracao_real") or None
        cirurgia.status = request.form.get("status")
        cirurgia.salvar()

        # Atualiza ou cria características
        if not caracteristicas:
            caracteristicas = CirurgiaCaracteristicas(cirurgia_id=cirurgia.id)

        caracteristicas.sex = request.form.get("sex") or None
        caracteristicas.bmi = request.form.get("bmi") or None
        caracteristicas.asa = request.form.get("asa") or None
        caracteristicas.emop = request.form.get("emop") or None
        caracteristicas.faixa_etaria = request.form.get("faixa_etaria") or None

        caracteristicas.salvar()

        flash("Cirurgia atualizada com sucesso!", "sucesso")
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    return render_template("editar_cirurgia.html", cirurgia=cirurgia, caracteristicas=caracteristicas)