import os
import traceback
from flask import Blueprint, request, jsonify
from app.middlewares import verificar_role
from app.controllers import upload_certificado_controller

bp = Blueprint("certificado", __name__, url_prefix="/api/certificados")

@bp.route("/upload", methods=["POST"])
@verificar_role(["aluno"])
def upload_certificado():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "Nenhum arquivo enviado"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "Arquivo vazio"}), 400

        # Dados do formulário
        data = {
            "titulo": request.form.get("titulo"),
            "id_curso": request.form.get("id_curso"),
            "id_regra_atividade": request.form.get("id_regra_atividade"),
            "carga_horaria_solicitada": request.form.get("carga_horaria_solicitada")
        }

        response, status = upload_certificado_controller(data, file)
        return jsonify(response), status

    except Exception as e:
        erro_detalhado = traceback.format_exc()
        print(f"Erro no upload:\n{erro_detalhado}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500