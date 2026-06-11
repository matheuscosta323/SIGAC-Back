from app import create_app
from flask_migrate import upgrade
from app.extensions import db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Roda as migrations
    upgrade()

    # Cria o admin se não existir
    admin_existente = db.session.execute(
        db.select(Usuario).where(Usuario.tipo == "admin")
    ).scalar_one_or_none()

    if not admin_existente:
        admin = Usuario(
            nome="Administrador",
            email="admin@senac.br",
            senhaHash=generate_password_hash("admin123"),
            tipo="admin",
            matricula=None
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run()