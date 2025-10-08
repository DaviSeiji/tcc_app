from flask import Blueprint, request, jsonify
from models.usuario import Usuario

bp_usuario = Blueprint("usuario", __name__)

# ----------------------
# Listar todos os usuários
# ----------------------
@bp_usuario.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = Usuario.listar_todos()
    return jsonify([{"id": u.id, "nome": u.nome, "email": u.email} for u in usuarios])

# ----------------------
# Buscar usuário por email
# ----------------------
@bp_usuario.route("/usuarios/<email>", methods=["GET"])
def buscar_usuario(email):
    u = Usuario.buscar_por_email(email)
    if u:
        return jsonify({"id": u.id, "nome": u.nome, "email": u.email})
    return jsonify({"error": "Usuário não encontrado"}), 404

# ----------------------
# Criar novo usuário
# ----------------------
@bp_usuario.route("/usuarios", methods=["POST"])
def criar_usuario():
    data = request.json
    if not all(k in data for k in ("nome", "email", "senha")):
        return jsonify({"error": "Campos obrigatórios: nome, email, senha"}), 400
    
    # Verifica se o email já existe
    if Usuario.buscar_por_email(data["email"]):
        return jsonify({"error": "Email já cadastrado"}), 400

    u = Usuario(nome=data["nome"], email=data["email"], senha=data["senha"])
    u.salvar()
    return jsonify({"id": u.id, "nome": u.nome, "email": u.email}), 201

# ----------------------
# Atualizar usuário
# ----------------------
@bp_usuario.route("/usuarios/<int:id>", methods=["PUT"])
def atualizar_usuario(id):
    data = request.json
    u = Usuario(id=id, nome=data.get("nome"), email=data.get("email"), senha=data.get("senha"))
    u.atualizar()
    return jsonify({"id": u.id, "nome": u.nome, "email": u.email})

# ----------------------
# Deletar usuário
# ----------------------
@bp_usuario.route("/usuarios/<int:id>", methods=["DELETE"])
def deletar_usuario(id):
    u = Usuario(id=id)
    u.deletar()
    return jsonify({"message": "Usuário deletado"})
