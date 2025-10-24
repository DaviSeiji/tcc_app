from flask import Blueprint, render_template, request, redirect, url_for, session
from models.cirurgia import Cirurgia, CirurgiaCaracteristicas
from utils.utils import prever_duracao

bp_cirurgia = Blueprint("cirurgia", __name__)

# ------------------------------------
# Lista de cirurgias do usuário logado
# ------------------------------------
@bp_cirurgia.route("/cirurgias")
def listar_cirurgias_usuario():
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    cirurgias_objs = Cirurgia.listar_por_usuario(session["usuario_id"])
    cirurgias = [
        {
            "id": c.id,
            "tipo": c.tipo,
            "plano": c.plano,
            "duracao_prevista": c.duracao_prevista,
            "status": c.status
        }
        for c in cirurgias_objs
    ]
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

        def to_float_or_none(value):
            if value in (None, ""):
                return None
            return float(value)

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

        preencheu_alguma = any(v not in (None, "") for v in caracteristicas.values())
        duracao_prevista = prever_duracao(caracteristicas) if preencheu_alguma else 177

        # Cria cirurgia
        c = Cirurgia(
            usuario_id=session["usuario_id"],
            tipo=tipo,
            plano=plano,
            duracao_prevista=duracao_prevista,
            status="Pendente"
        )
        cirurgia_id = c.salvar()

        # Salva características se existirem
        if preencheu_alguma:
            caracteristicas["cirurgia_id"] = cirurgia_id
            cc = CirurgiaCaracteristicas(**caracteristicas)
            cc.salvar()

        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    return render_template("adicionar_cirurgia.html")


# ------------------------------------
# Ver cirurgia
# ------------------------------------
@bp_cirurgia.route("/cirurgias/<int:id>")
def ver_cirurgia(id):
    cirurgia = Cirurgia.buscar_por_id(id)
    if not cirurgia:
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    caracteristicas_list = CirurgiaCaracteristicas.listar_por_cirurgia(id)
    caracteristicas = caracteristicas_list[0].__dict__ if caracteristicas_list else {}

    return render_template("ver_cirurgia.html", cirurgia=cirurgia, caracteristicas=caracteristicas)


# ------------------------------------
# Excluir cirurgia
# ------------------------------------
@bp_cirurgia.route("/excluir_cirurgias/<int:id>")
def excluir_cirurgia(id):
    cirurgia = Cirurgia.buscar_por_id(id)
    if cirurgia:
        cirurgia.excluir()
    return redirect(url_for("cirurgia.listar_cirurgias_usuario"))


# ------------------------------------
# Editar cirurgia
# ------------------------------------
@bp_cirurgia.route("/cirurgias/editar/<int:id>", methods=["GET", "POST"])
def editar_cirurgia(id):
    if "usuario_id" not in session:
        return redirect(url_for("usuario.pagina_login"))

    cirurgia = Cirurgia.buscar_por_id(id)
    if not cirurgia or cirurgia.usuario_id != session["usuario_id"]:
        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    caracteristicas_list = CirurgiaCaracteristicas.listar_por_cirurgia(id)
    caracteristicas = caracteristicas_list[0].__dict__ if caracteristicas_list else {}

    if request.method == "POST":
        def to_float_or_none(value):
            if value in (None, ""):
                return None
            return float(value)

        cirurgia.tipo = request.form.get("tipo")
        cirurgia.plano = request.form.get("plano")
        duracao_prevista = request.form.get("duracao_prevista")
        cirurgia.duracao_prevista = int(duracao_prevista) if duracao_prevista else None
        duracao_real = request.form.get("duracao_real")
        cirurgia.duracao_real = int(duracao_real) if duracao_real else None
        cirurgia.status = request.form.get("status")
        cirurgia.salvar()

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

        if caracteristicas:
            cc = caracteristicas_list[0]
            for k, v in dados_caracteristicas.items():
                setattr(cc, k, v)
            cc.salvar()
        else:
            dados_caracteristicas["cirurgia_id"] = id
            cc = CirurgiaCaracteristicas(**dados_caracteristicas)
            cc.salvar()

        return redirect(url_for("cirurgia.listar_cirurgias_usuario"))

    return render_template("editar_cirurgia.html", cirurgia=cirurgia, caracteristicas=caracteristicas)
