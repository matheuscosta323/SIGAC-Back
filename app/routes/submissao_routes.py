from flask import Blueprint, request
from app.controllers import criar_submissao_controller, listar_submissoes_controller, validar_submissao_controller
from app.middlewares import verificar_role

bp = Blueprint("submissao", __name__, url_prefix="/api/submissoes")

@bp.route("/criar", methods=["POST"])
@verificar_role(["aluno"])
def criar_submissao():
    try:
        data = request.get_json()  # corrigido: .get_json()
        response, status = criar_submissao_controller(data)
        return response, status
    except Exception as e:
        print(f"Erro ao criar submissão: {e}")
        return {"success": False, "message": "Erro interno."}, 500

@bp.route("/listar", methods=["GET"])
@verificar_role(["aluno", "coordenador", "admin"])
def listar_submissoes():
    try:
        status = request.args.get("status")
        response, status_code = listar_submissoes_controller(status)
        return response, status_code
    except Exception as e:
        print(f"Erro ao listar submissões: {e}")
        return {"success": False, "message": "Erro interno."}, 500

@bp.route("/validar/<int:id_submissao>", methods=["PUT"])
@verificar_role(["coordenador", "admin"])
def validar_submissao(id_submissao):
    try:
        data = request.get_json()
        response, status_code = validar_submissao_controller(id_submissao, data)
        return response, status_code
    except Exception as e:
        print(f"Erro ao validar submissão: {e}")
        return {"success": False, "message": "Erro interno."}, 500