from flask import Blueprint, request
from app.middlewares import verificar_role
from app.controllers import cadastrar_curso_controller, listar_cursos_controller


bp = Blueprint("curso", __name__, url_prefix="/api/cursos")


@bp.route("/cadastrar", methods=["POST"])
@verificar_role(["admin"])
def cadastrar_usuario():
    try:
        data = request.get_json()
        response, status = cadastrar_curso_controller(data)
        return response, status

    except Exception as e:
        print(f"Erro ao cadastrar curso: {e}")
        return {
            "success": False,
            "message": "Erro ao cadastrar curso."
        }, 500

@bp.route("/listar", methods=["GET"])
@verificar_role(["admin", "coordenador", "aluno"])
def listar_cursos():
    try:
        response, status = listar_cursos_controller()
        return response, status
    except Exception as e:
        print(f"Erro ao listar alunos: {e}")
        return {"success": False, "message": "Erro interno."}, 500