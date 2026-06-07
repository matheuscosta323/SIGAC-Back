from flask import Blueprint, request
from app.controllers import (
    cadastrar_usuario_controller,
    listar_alunos_controller,
    listar_coordenadores_controller,
)
from app.controllers.usuario_controller import vincular_usuario_curso_controller
from app.middlewares import verificar_role

bp = Blueprint("usuario", __name__, url_prefix="/api/usuarios")


@bp.route("/cadastrar", methods=["POST"])
@verificar_role(["admin", "coordenador"])
def cadastrar_usuario():
    try:
        data = request.get_json()
        if not data:
            return {"success": False, "message": "Corpo da requisição inválido."}, 400
        response, status = cadastrar_usuario_controller(data)
        return response, status
    except Exception as e:
        print(f"Erro ao cadastrar usuário: {e}")
        return {"success": False, "message": "Erro interno."}, 500


@bp.route("/vincular-curso", methods=["POST"])
@verificar_role(["admin"])
def vincular_usuario_curso():
    try:
        data = request.get_json()
        if not data:
            return {"success": False, "message": "Corpo da requisição inválido."}, 400
        response, status = vincular_usuario_curso_controller(data)
        return response, status
    except Exception as e:
        print(f"Erro ao vincular usuário ao curso: {e}")
        return {"success": False, "message": "Erro interno."}, 500


@bp.route("/listar_alunos", methods=["GET"])
@verificar_role(["admin", "coordenador"])
def listar_alunos():
    try:
        response, status = listar_alunos_controller()
        return response, status
    except Exception as e:
        print(f"Erro ao listar alunos: {e}")
        return {"success": False, "message": "Erro interno."}, 500


@bp.route("/listar_coordenadores", methods=["GET"])
@verificar_role(["admin"])
def listar_coordenadores():
    try:
        response, status = listar_coordenadores_controller()
        return response, status
    except Exception as e:
        print(f"Erro ao listar coordenadores: {e}")
        return {"success": False, "message": "Erro interno."}, 500
