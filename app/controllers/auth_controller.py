from app.extensions import db
from app.models import Usuario
from sqlalchemy import select
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token


def login_controller(data):
    query = select(Usuario).where(Usuario.email == data["email"])
    usuario = db.session.execute(query).scalar_one_or_none()
    
    if usuario is None:
        return {
            "success": False,
            "message": "Usuário não encontrado."
        }, 404
    
    elif not check_password_hash(usuario.senhaHash, data["senha"]):
        return {
            "success": False,
            "message": "Credenciais inválidas."
        }, 401

    access_token = create_access_token(
        identity=str(usuario.id),
        additional_claims={"role": usuario.tipo, "nome": usuario.nome}
    )
        
    return {
        "success": True,
        "message": "Login efetuado com sucesso.",
        "access_token": access_token
    }, 200