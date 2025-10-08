from flask import Blueprint, request, jsonify
from models.cirurgia import Cirurgia, CirurgiaCaracteristicas

bp_cirurgia = Blueprint("cirurgia", __name__)

# ----------------------
# Listar todas as cirurgias de um usuário
# ----------------------
@bp_cirurgia.route("/cirurgias/<int:usuario_id>", methods=["GET"])
def listar_cirurgias(usuario_id):
    cirurgias = Cirurgia.listar_por_usuario(usuario_id)
    return jsonify([
        {
            "id": c.id,
            "tipo": c.tipo,
            "plano": c.plano,
            "duracao_prevista": c.duracao_prevista,
            "duracao_real": c.duracao_real,
            "status": c.status
        } for c in cirurgias
    ])

# ----------------------
# Buscar cirurgia por ID
# ----------------------
@bp_cirurgia.route("/cirurgia/<int:id>", methods=["GET"])
def buscar_cirurgia(id):
    c = Cirurgia.buscar_por_id(id)
    if c:
        return jsonify({
            "id": c.id,
            "usuario_id": c.usuario_id,
            "tipo": c.tipo,
            "plano": c.plano,
            "duracao_prevista": c.duracao_prevista,
            "duracao_real": c.duracao_real,
            "status": c.status
        })
    return jsonify({"error": "Cirurgia não encontrada"}), 404

# ----------------------
# Criar nova cirurgia
# ----------------------
@bp_cirurgia.route("/cirurgias", methods=["POST"])
def criar_cirurgia():
    data = request.json
    required = ["usuario_id", "tipo", "plano"]
    if not all(k in data for k in required):
        return jsonify({"error": f"Campos obrigatórios: {', '.join(required)}"}), 400

    c = Cirurgia(
        usuario_id=data["usuario_id"],
        tipo=data["tipo"],
        plano=data["plano"],
        duracao_prevista=data.get("duracao_prevista")
    )
    c.salvar()
    return jsonify({"id": c.id, "tipo": c.tipo, "plano": c.plano}), 201

# ----------------------
# Atualizar cirurgia
# ----------------------
@bp_cirurgia.route("/cirurgia/<int:id>", methods=["PUT"])
def atualizar_cirurgia(id):
    data = request.json
    c = Cirurgia.buscar_por_id(id)
    if not c:
        return jsonify({"error": "Cirurgia não encontrada"}), 404

    c.tipo = data.get("tipo", c.tipo)
    c.plano = data.get("plano", c.plano)
    c.duracao_prevista = data.get("duracao_prevista", c.duracao_prevista)
    c.duracao_real = data.get("duracao_real", c.duracao_real)
    c.status = data.get("status", c.status)
    c.salvar()
    return jsonify({"id": c.id, "tipo": c.tipo, "plano": c.plano, "status": c.status})

# ----------------------
# Deletar cirurgia
# ----------------------
@bp_cirurgia.route("/cirurgia/<int:id>", methods=["DELETE"])
def deletar_cirurgia(id):
    c = Cirurgia.buscar_por_id(id)
    if not c:
        return jsonify({"error": "Cirurgia não encontrada"}), 404
    c.excluir()
    return jsonify({"message": "Cirurgia deletada"})

# ----------------------
# Gerenciar características de uma cirurgia
# ----------------------
@bp_cirurgia.route("/cirurgia/<int:id>/caracteristicas", methods=["GET"])
def listar_caracteristicas(id):
    caracs = CirurgiaCaracteristicas.listar_por_cirurgia(id)
    return jsonify([c.__dict__ for c in caracs])

@bp_cirurgia.route("/cirurgia/<int:id>/caracteristicas", methods=["POST"])
def criar_caracteristicas(id):
    data = request.json
    c = CirurgiaCaracteristicas(cirurgia_id=id, **data)
    c.salvar()
    return jsonify(c.__dict__), 201

@bp_cirurgia.route("/cirurgia/caracteristicas/<int:id>", methods=["PUT"])
def atualizar_caracteristicas(id):
    data = request.json
    caracs_list = CirurgiaCaracteristicas.listar_por_cirurgia(id)
    if not caracs_list:
        return jsonify({"error": "Características não encontradas"}), 404
    caracs = caracs_list[0]
    for key, value in data.items():
        if hasattr(caracs, key):
            setattr(caracs, key, value)
    caracs.salvar()
    return jsonify(caracs.__dict__)

@bp_cirurgia.route("/cirurgia/caracteristicas/<int:id>", methods=["DELETE"])
def deletar_caracteristicas(id):
    caracs_list = CirurgiaCaracteristicas.listar_por_cirurgia(id)
    if not caracs_list:
        return jsonify({"error": "Características não encontradas"}), 404
    caracs = caracs_list[0]
    caracs.deletar()
    return jsonify({"message": "Características deletadas"})
