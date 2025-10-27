from flask import Blueprint, render_template, request, redirect, url_for, session
from models.sala import Sala

bp_sala = Blueprint("sala", __name__)

# ------------------------------------
# Listar salas do usuário logado
# ------------------------------------
@bp_sala.route("/salas")
def listar_salas_usuario():
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    salas_objs = Sala.listar_por_usuario(session["usuario_id"])
    salas = [
        {
            "id": s.id,
            "nome": s.nome,
            "horario_seg_inicio": s.horario_seg_inicio,
            "horario_seg_fim": s.horario_seg_fim,
            "horario_sab_inicio": s.horario_sab_inicio,
            "horario_sab_fim": s.horario_sab_fim,
            "horario_dom_inicio": s.horario_dom_inicio,
            "horario_dom_fim": s.horario_dom_fim
        }
        for s in salas_objs
    ]
    return render_template("salas.html", salas=salas)


# ------------------------------------
# Página de adicionar nova sala
# ------------------------------------
@bp_sala.route("/salas/adicionar", methods=["GET", "POST"])
def adicionar_sala():
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    if request.method == "POST":
        nome = request.form.get("nome")

        # Pegar valores do formulário (podem estar vazios)
        horario_seg_inicio = request.form.get("horario_seg_inicio") or "07:00"
        horario_seg_fim = request.form.get("horario_seg_fim") or "19:00"
        horario_sab_inicio = request.form.get("horario_sab_inicio") or "07:00"
        horario_sab_fim = request.form.get("horario_sab_fim") or "12:00"

        # Domingo: se não informado, significa fechada
        horario_dom_inicio = request.form.get("horario_dom_inicio") or "00:00"
        horario_dom_fim = request.form.get("horario_dom_fim") or "00:00"

        # Validação mínima (nome obrigatório)
        if not nome:
            return redirect(url_for("sala.adicionar_sala"))

        # Criar e salvar sala
        s = Sala(
            usuario_id=session["usuario_id"],
            nome=nome,
            horario_seg_inicio=horario_seg_inicio,
            horario_seg_fim=horario_seg_fim,
            horario_sab_inicio=horario_sab_inicio,
            horario_sab_fim=horario_sab_fim,
            horario_dom_inicio=horario_dom_inicio,
            horario_dom_fim=horario_dom_fim
        )
        s.salvar()

        return redirect(url_for("sala.listar_salas_usuario"))

    return render_template("adicionar_sala.html")


# ------------------------------------
# Ver sala específica
# ------------------------------------
@bp_sala.route("/salas/<int:id>")
def ver_sala(id):
    sala = Sala.buscar_por_id(id)
    if not sala:
        return redirect(url_for("sala.listar_salas_usuario"))

    return render_template("ver_sala.html", sala=sala)


# ------------------------------------
# Editar sala
# ------------------------------------
@bp_sala.route("/salas/editar/<int:id>", methods=["GET", "POST"])
def editar_sala(id):
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    sala = Sala.buscar_por_id(id)
    if not sala or sala.usuario_id != session["usuario_id"]:
        return redirect(url_for("sala.listar_salas_usuario"))

    if request.method == "POST":
        sala.nome = request.form.get("nome")
        sala.horario_seg_inicio = request.form.get("horario_seg_inicio")
        sala.horario_seg_fim = request.form.get("horario_seg_fim")
        sala.horario_sab_inicio = request.form.get("horario_sab_inicio")
        sala.horario_sab_fim = request.form.get("horario_sab_fim")
        sala.horario_dom_inicio = request.form.get("horario_dom_inicio")
        sala.horario_dom_fim = request.form.get("horario_dom_fim")

        # Validação obrigatória
        if not all([sala.nome, sala.horario_seg_inicio, sala.horario_seg_fim,
                    sala.horario_sab_inicio, sala.horario_sab_fim,
                    sala.horario_dom_inicio, sala.horario_dom_fim]):
            return redirect(url_for("sala.editar_sala", id=id))

        sala.salvar()
        return redirect(url_for("sala.listar_salas_usuario"))

    return render_template("editar_sala.html", sala=sala)


# ------------------------------------
# Excluir sala
# ------------------------------------
@bp_sala.route("/excluir_salas/<int:id>")
def excluir_sala(id):
    sala = Sala.buscar_por_id(id)
    if sala:
        sala.excluir()
    return redirect(url_for("sala.listar_salas_usuario"))
