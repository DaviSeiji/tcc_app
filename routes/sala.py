from flask import Blueprint, request, jsonify
from models.sala import Sala

bp_sala = Blueprint("sala", __name__)

# ----------------------
# Listar todas as salas de um usuário
# ----------------------
@bp_sala.route("/salas/<int:usuario_id>", methods=["GET"])
def listar_salas(usuario_id):
    salas = Sala.listar_por_usuario(usuario_id)
    return jsonify([
        {
            "id": s.id,
            "nome": s.nome,
            "horario_seg": s.horario_seg,
            "horario_sab": s.horario_sab,
            "horario_dom": s.horario_dom
        } for s in salas
    ])

# ----------------------
# Buscar sala por ID
# ----------------------
@bp_sala.route("/sala/<int:id>", methods=["GET"])
def buscar_sala(id):
    s = Sala.buscar_por_id(id)
    if s:
        return jsonify({
            "id": s.id,
            "usuario_id": s.usuario_id,
            "nome": s.nome,
            "horario_seg": s.horario_seg,
            "horario_sab": s.horario_sab,
            "horario_dom": s.horario_dom
        })
    return jsonify({"error": "Sala não encontrada"}), 404

# ----------------------
# Criar nova sala
# ----------------------
@bp_sala.route("/salas", methods=["POST"])
def criar_sala():
    data = request.json
    required = ["usuario_id", "nome"]
    if not all(k in data for k in required):
        return jsonify({"error": f"Campos obrigatórios: {', '.join(required)}"}), 400

    s = Sala(
        usuario_id=data["usuario_id"],
        nome=data["nome"],
        horario_seg=data.get("horario_seg"),
        horario_sab=data.get("horario_sab"),
        horario_dom=data.get("horario_dom")
    )
    s.salvar()
    return jsonify({
        "id": s.id,
        "nome": s.nome,
        "horario_seg": s.horario_seg,
        "horario_sab": s.horario_sab,
        "horario_dom": s.horario_dom
    }), 201

# ----------------------
# Atualizar sala
# ----------------------
@bp_sala.route("/sala/<int:id>", methods=["PUT"])
def atualizar_sala(id):
    data = request.json
    s = Sala.buscar_por_id(id)
    if not s:
        return jsonify({"error": "Sala não encontrada"}), 404

    s.nome = data.get("nome", s.nome)
    s.horario_seg = data.get("horario_seg", s.horario_seg)
    s.horario_sab = data.get("horario_sab", s.horario_sab)
    s.horario_dom = data.get("horario_dom", s.horario_dom)
    s.salvar()
    return jsonify({
        "id": s.id,
        "nome": s.nome,
        "horario_seg": s.horario_seg,
        "horario_sab": s.horario_sab,
        "horario_dom": s.horario_dom
    })

# ----------------------
# Deletar sala
# ----------------------
@bp_sala.route("/sala/<int:id>", methods=["DELETE"])
def deletar_sala(id):
    s = Sala.buscar_por_id(id)
    if not s:
        return jsonify({"error": "Sala não encontrada"}), 404
    s.excluir()
    return jsonify({"message": "Sala deletada"})
