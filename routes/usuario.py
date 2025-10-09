from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from models.usuario import Usuario

bp_usuario = Blueprint("usuario", __name__)

@bp_usuario.route("/", methods=["GET"])
def pagina_inicial():
    return render_template("index.html")

# ------------------------------------
# PÁGINAS HTML (cadastro e login)
# ------------------------------------
@bp_usuario.route("/cadastro", methods=["GET"])
def pagina_cadastro():
    return render_template("cadastro.html")

@bp_usuario.route("/login", methods=["GET"])
def pagina_login():
    return render_template("login.html")


# ------------------------------------
# AÇÕES: criar usuário (via formulário)
# ------------------------------------
@bp_usuario.route("/cadastro", methods=["POST"])
def criar_usuario():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")

    if not nome or not email or not senha:
        flash("Preencha todos os campos!", "erro")
        return redirect(url_for("usuario.pagina_cadastro"))

    if Usuario.buscar_por_email(email):
        flash("E-mail já cadastrado!", "erro")
        return redirect(url_for("usuario.pagina_cadastro"))

    u = Usuario(nome=nome, email=email)
    u.set_password(senha)  # senha criptografada
    u.salvar()

    flash("Cadastro realizado com sucesso! Faça login.", "sucesso")
    return redirect(url_for("usuario.pagina_login"))


# ------------------------------------
# AÇÕES: login de usuário
# ------------------------------------
@bp_usuario.route("/login", methods=["POST"])
def login_usuario():
    email = request.form.get("email")
    senha = request.form.get("senha")

    if not email or not senha:
        flash("Preencha todos os campos!", "erro")
        return redirect(url_for("usuario.pagina_login"))

    usuario = Usuario.autenticar(email, senha)
    if not usuario:
        flash("E-mail ou senha incorretos.", "erro")
        return redirect(url_for("usuario.pagina_login"))

    # ✅ Salva informações na sessão
    session["usuario_id"] = usuario.id
    session["usuario_nome"] = usuario.nome

    flash(f"Bem-vindo, {usuario.nome}!", "sucesso")
    return redirect(url_for("usuario.home"))


# ------------------------------------
# HOME protegida (só logado acessa)
# ------------------------------------
@bp_usuario.route("/home")
def home():
    if "usuario_id" not in session:
        flash("Faça login para continuar.", "erro")
        return redirect(url_for("usuario.pagina_login"))

    nome = session.get("usuario_nome")
    return render_template("home.html", nome=nome)


# ------------------------------------
# LOGOUT
# ------------------------------------
@bp_usuario.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.", "sucesso")
    return redirect(url_for("usuario.pagina_login"))
