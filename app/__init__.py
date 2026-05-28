from flask import Flask
from .extensions import db, migrate, jwt
from dotenv import load_dotenv
import os
from flask_cors import CORS
from datetime import timedelta

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    load_dotenv()
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("MYSQL_URI")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    from app.routes import bp_usuario, bp_submissao, bp_auth, bp_curso, bp_regra, bp_relatorio, bp_certificado
    app.register_blueprint(bp_usuario)
    app.register_blueprint(bp_submissao)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_curso)
    app.register_blueprint(bp_regra)
    app.register_blueprint(bp_relatorio)
    app.register_blueprint(bp_certificado)

    return app
