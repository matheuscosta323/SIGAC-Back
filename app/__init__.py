from flask import Flask
from .extensions import db, migrate, jwt
from dotenv import load_dotenv
import os
from flask_cors import CORS
from datetime import timedelta
from app.models import *

# Pasta onde os certificados são salvos (mesma usada em certificado_controller.py)
PASTA_CERTIFICADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "certificados_uploaded")

def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=PASTA_CERTIFICADOS,
        static_url_path="/certificados_uploaded"
    )
    CORS(app)

    load_dotenv()
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("MYSQL_URI")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "ssl": {
            "check_hostname": False,
            "verify_mode": 0  # ssl.CERT_NONE
        }
    }
}

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    with app.app_context():
        db.create_all()

    # Blueprints de negócio
    from app.routes import bp_usuario, bp_submissao, bp_auth, bp_curso, bp_regra, bp_relatorio, bp_certificado
    app.register_blueprint(bp_usuario)
    app.register_blueprint(bp_submissao)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_curso)
    app.register_blueprint(bp_regra)
    app.register_blueprint(bp_relatorio)
    app.register_blueprint(bp_certificado)

    # Swagger UI + spec
    from app.swagger import swagger_ui_blueprint, swagger_spec_bp
    app.register_blueprint(swagger_ui_blueprint)
    app.register_blueprint(swagger_spec_bp)

    return app
