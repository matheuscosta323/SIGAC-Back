from flask import Blueprint
from app.middlewares import verificar_role
from app.controllers import dashboard_controller, dashboard_aluno_controller

bp = Blueprint("relatorio", __name__, url_prefix="/api/relatorios")

@bp.route("/dashboard", methods=["GET"])
@verificar_role(["admin", "coordenador"])
def dashboard():
    response, status = dashboard_controller()
    return response, status


@bp.route("/dashboard-aluno", methods=["GET"])
@verificar_role(["aluno"])
def dashboard_aluno():
    response, status = dashboard_aluno_controller()
    return response, status