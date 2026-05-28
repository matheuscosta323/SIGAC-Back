from flask import Blueprint, request
from app.middlewares import verificar_role
from app.controllers.regra_controller import (
    listar_regras_controller,
    criar_regra_controller,
    atualizar_regra_controller,
    excluir_regra_controller
)

bp = Blueprint("regra", __name__, url_prefix="/api/regras")

@bp.route("/listar", methods=["GET"])
@verificar_role(["admin", "coordenador", "aluno"])
def listar_regras():
    curso_id = request.args.get("curso_id", type=int)
    response, status = listar_regras_controller(curso_id)
    return response, status

@bp.route("/criar", methods=["POST"])
@verificar_role(["admin"])
def criar_regra():
    data = request.get_json()
    response, status = criar_regra_controller(data)
    return response, status

@bp.route("/atualizar/<int:id_regra>", methods=["PUT"])
@verificar_role(["admin"])
def atualizar_regra(id_regra):
    data = request.get_json()
    response, status = atualizar_regra_controller(id_regra, data)
    return response, status

@bp.route("/excluir/<int:id_regra>", methods=["DELETE"])
@verificar_role(["admin"])
def excluir_regra(id_regra):
    response, status = excluir_regra_controller(id_regra)
    return response, status