from app.extensions import db
from app.models import Usuario, AlunoCurso, CoordenadorCurso, Curso, Submissao
from sqlalchemy import select, func
from werkzeug.security import generate_password_hash
from flask_jwt_extended import get_jwt, get_jwt_identity


def cadastrar_usuario_controller(data):
    role = get_jwt().get("role")
    tipo_novo_usuario = data.get("tipo")
    id_curso = data.get("id_curso")

    # Validações de permissão
    if role == "coordenador" and tipo_novo_usuario != "aluno":
        return {"success": False, "message": "Coordenador só pode cadastrar alunos."}, 403
    if role == "admin" and tipo_novo_usuario not in ("aluno", "coordenador"):
        return {"success": False, "message": "Tipo de usuário inválido."}, 400
    if tipo_novo_usuario == "aluno" and not data.get("matricula"):
        return {"success": False, "message": "Aluno precisa de matrícula."}, 400
    if not id_curso:
        return {"success": False, "message": "É necessário informar o id_curso."}, 400

    # Verificar se curso existe
    curso = db.session.execute(select(Curso).where(Curso.id == id_curso)).scalar_one_or_none()
    if not curso:
        return {"success": False, "message": "Curso não encontrado."}, 404

    # Verificar se email já existe
    email_existente = db.session.execute(
        select(Usuario).where(Usuario.email == data.get("email"))
    ).scalar_one_or_none()
    if email_existente:
        return {"success": False, "message": "E-mail já cadastrado."}, 409

    senha_hash = generate_password_hash(data["senha"])
    novo_usuario = Usuario(
        nome=data["nome"],
        email=data["email"],
        senhaHash=senha_hash,
        tipo=tipo_novo_usuario,
        matricula=data.get("matricula")
    )
    db.session.add(novo_usuario)
    db.session.flush()  # garante que o id seja gerado

    # Vincular ao curso — suporta múltiplos cursos (UniqueConstraint evita duplicata)
    if tipo_novo_usuario == "aluno":
        vinculo = AlunoCurso(id_aluno=novo_usuario.id, id_curso=id_curso)
    else:
        vinculo = CoordenadorCurso(id_coordenador=novo_usuario.id, id_curso=id_curso)
    db.session.add(vinculo)

    db.session.commit()
    return {"success": True, "message": "Cadastro efetuado com sucesso."}, 201


def vincular_usuario_curso_controller(data):
    """Vincula um usuário já existente a um curso adicional."""
    role = get_jwt().get("role")
    if role != "admin":
        return {"success": False, "message": "Apenas admin pode vincular usuários a cursos."}, 403

    id_usuario = data.get("id_usuario")
    id_curso = data.get("id_curso")

    if not id_usuario or not id_curso:
        return {"success": False, "message": "id_usuario e id_curso são obrigatórios."}, 400

    usuario = db.session.get(Usuario, id_usuario)
    if not usuario:
        return {"success": False, "message": "Usuário não encontrado."}, 404

    curso = db.session.get(Curso, id_curso)
    if not curso:
        return {"success": False, "message": "Curso não encontrado."}, 404

    if usuario.tipo == "aluno":
        existente = db.session.execute(
            select(AlunoCurso).where(
                AlunoCurso.id_aluno == id_usuario,
                AlunoCurso.id_curso == id_curso
            )
        ).scalar_one_or_none()
        if existente:
            return {"success": False, "message": "Aluno já vinculado a este curso."}, 409
        db.session.add(AlunoCurso(id_aluno=id_usuario, id_curso=id_curso))

    elif usuario.tipo == "coordenador":
        existente = db.session.execute(
            select(CoordenadorCurso).where(
                CoordenadorCurso.id_coordenador == id_usuario,
                CoordenadorCurso.id_curso == id_curso
            )
        ).scalar_one_or_none()
        if existente:
            return {"success": False, "message": "Coordenador já vinculado a este curso."}, 409
        db.session.add(CoordenadorCurso(id_coordenador=id_usuario, id_curso=id_curso))
    else:
        return {"success": False, "message": "Tipo de usuário não suporta vínculo com curso."}, 400

    db.session.commit()
    return {"success": True, "message": f"Usuário vinculado ao curso '{curso.nome}' com sucesso."}, 201


def listar_alunos_controller():
    role = get_jwt().get("role")
    if role not in ("coordenador", "admin"):
        return {"success": False, "message": "Acesso negado."}, 403

    query = (
        select(
            Usuario.id,
            Usuario.nome,
            Usuario.matricula,
            Curso.id.label("curso_id"),
            Curso.nome.label("curso_nome"),
            Curso.carga_horaria.label("total_horas"),
            func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0).label("horas_concluidas")
        )
        .join(AlunoCurso, AlunoCurso.id_aluno == Usuario.id)
        .join(Curso, Curso.id == AlunoCurso.id_curso)
        .outerjoin(
            Submissao,
            (Submissao.id_aluno == Usuario.id)
            & (Submissao.id_curso == Curso.id)
            & (Submissao.status == "aprovado")
        )
        .where(Usuario.tipo == "aluno")
        .group_by(Usuario.id, Curso.id)
    )

    alunos = db.session.execute(query).all()
    resultado = []
    for aluno in alunos:
        progresso = (aluno.horas_concluidas / aluno.total_horas * 100) if aluno.total_horas > 0 else 0
        resultado.append({
            "id": aluno.id,
            "nome": aluno.nome,
            "matricula": aluno.matricula,
            "curso_id": aluno.curso_id,
            "curso": aluno.curso_nome,
            "horas_concluidas": int(aluno.horas_concluidas),
            "total_horas": aluno.total_horas,
            "progresso": round(progresso, 1)
        })

    return {"success": True, "alunos": resultado}, 200


def listar_coordenadores_controller():
    role = get_jwt().get("role")
    if role != "admin":
        return {"success": False, "message": "Acesso negado."}, 403

    query = (
        select(
            Usuario.id,
            Usuario.nome,
            Usuario.email,
            Usuario.matricula,
            func.group_concat(Curso.nome, ", ").label("cursos")
        )
        .join(CoordenadorCurso, CoordenadorCurso.id_coordenador == Usuario.id)
        .join(Curso, Curso.id == CoordenadorCurso.id_curso)
        .where(Usuario.tipo == "coordenador")
        .group_by(Usuario.id)
    )
    coordenadores = db.session.execute(query).all()
    resultado = [
        {
            "id": c.id,
            "nome": c.nome,
            "email": c.email,
            "matricula": c.matricula,
            "cursos": c.cursos.split(", ") if c.cursos else []
        }
        for c in coordenadores
    ]
    return {"success": True, "coordenadores": resultado}, 200
