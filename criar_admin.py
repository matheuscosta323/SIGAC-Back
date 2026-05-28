"""
criar_admin.py — Cria o usuário admin inicial no banco do SIGAC.

Como usar:
    1. Coloque este arquivo dentro da pasta SIGAC-Back-main/
    2. Com o ambiente virtual ativado, rode:
           python criar_admin.py
"""

from app import create_app
from app.extensions import db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Verifica se já existe um admin
    admin_existente = db.session.execute(
        db.select(Usuario).where(Usuario.tipo == "admin")
    ).scalar_one_or_none()

    if admin_existente:
        print(f"Admin já existe: {admin_existente.email}")
    else:
        admin = Usuario(
            nome="Administrador",
            email="admin@senac.br",
            senhaHash=generate_password_hash("admin123"),
            tipo="admin",
            matricula=None
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin criado com sucesso!")
        print("   Email: admin@senac.br")
        print("   Senha: admin123")
        print("\n⚠️  Troque a senha após o primeiro login.")