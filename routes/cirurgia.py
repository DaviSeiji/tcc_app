from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.cirurgia import Cirurgia

bp_cirurgia = Blueprint("cirurgia", __name__)

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
        duracao_prevista = request.form.get("duracao_prevista")

        if not tipo or not plano:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return redirect(url_for("cirurgia.adicionar_cirurgia"))

        c = Cirurgia(
            usuario_id=session["usuario_id"],
            tipo=tipo,
            plano=plano,
            duracao_prevista=duracao_prevista
        )
        c.salvar()
        flash("Cirurgia adicionada com sucesso!", "sucesso")
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    return render_template("adicionar_cirurgia.html")
