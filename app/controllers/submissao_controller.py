from app.extensions import db
from app.models import (
    Submissao, AtividadeComplementar, Certificado,
    Usuario, Curso, CoordenadorCurso, RegraAtividade, AlunoCurso
)
from sqlalchemy import select, func
from flask_jwt_extended import get_jwt, get_jwt_identity


def criar_submissao_controller(data):
    id_aluno = int(get_jwt_identity())

    id_curso = data.get("id_curso")
    id_regra_atividade = data.get("id_regra_atividade")
    carga_horaria_solicitada = data.get("carga_horaria_solicitada")
    titulo = data.get("titulo")

    if not all([id_curso, id_regra_atividade, carga_horaria_solicitada, titulo]):
        return {"success": False, "message": "Dados incompletos."}, 400

    # Verificar se aluno está matriculado no curso
    vinculo = db.session.execute(
        select(AlunoCurso).where(
            AlunoCurso.id_aluno == id_aluno,
            AlunoCurso.id_curso == id_curso
        )
    ).scalar_one_or_none()
    if not vinculo:
        return {"success": False, "message": "Aluno não matriculado neste curso."}, 403

    # Verificar regra e limite de horas
    regra = db.session.get(RegraAtividade, id_regra_atividade)
    if not regra:
        return {"success": False, "message": "Regra de atividade não encontrada."}, 404
    if regra.id_curso and regra.id_curso != id_curso:
        return {"success": False, "message": "Regra não pertence a este curso."}, 400

    # Verificar horas já aprovadas nesta regra para o aluno/curso
    horas_ja_aprovadas = db.session.execute(
        select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
        .join(AtividadeComplementar, AtividadeComplementar.id == Submissao.id_atividade_complementar)
        .where(Submissao.id_aluno == id_aluno)
        .where(Submissao.id_curso == id_curso)
        .where(Submissao.status == "aprovado")
        .where(AtividadeComplementar.id_regra_atividade == id_regra_atividade)
    ).scalar() or 0

    horas_solicitadas = int(carga_horaria_solicitada)
    if (horas_ja_aprovadas + horas_solicitadas) > regra.limite_horas:
        horas_disponiveis = regra.limite_horas - horas_ja_aprovadas
        return {
            "success": False,
            "message": (
                f"Limite de horas para esta atividade atingido. "
                f"Você já tem {int(horas_ja_aprovadas)}h aprovadas e o limite é {regra.limite_horas}h. "
                f"Disponível: {max(0, horas_disponiveis)}h."
            )
        }, 422

    certificado = Certificado(
        nome_arquivo=data["nome_arquivo"],
        url_arquivo=data["url_arquivo"]
    )
    db.session.add(certificado)
    db.session.flush()

    atividade = AtividadeComplementar(
        descricao=titulo,
        carga_horaria_solicitada=horas_solicitadas,
        carga_horaria_aprovada=None,
        id_regra_atividade=id_regra_atividade
    )
    db.session.add(atividade)
    db.session.flush()

    nova_submissao = Submissao(
        id_aluno=id_aluno,
        status="pendente",
        id_curso=id_curso,
        id_atividade_complementar=atividade.id,
        id_certificado=certificado.id,
        id_coordenador=None,
        motivo_rejeicao=None,
        carga_horaria_aprovada=None
    )
    db.session.add(nova_submissao)
    db.session.commit()

    return {"success": True, "message": "Submissão criada com sucesso."}, 201


def listar_submissoes_controller(status=None):
    role = get_jwt().get("role")
    id_usuario = int(get_jwt_identity())

    query = select(
        Submissao.id,
        Submissao.status,
        Submissao.data_envio,
        Submissao.motivo_rejeicao,
        Submissao.carga_horaria_aprovada,
        Usuario.nome.label("aluno_nome"),
        Usuario.email.label("aluno_email"),
        Curso.nome.label("curso_nome"),
        AtividadeComplementar.descricao.label("atividade_descricao"),
        AtividadeComplementar.carga_horaria_solicitada,
        RegraAtividade.area.label("regra_area"),
        RegraAtividade.limite_horas.label("regra_limite_horas"),
        Certificado.url_arquivo.label("certificado_url")
    ).join(Usuario, Usuario.id == Submissao.id_aluno
    ).join(Curso, Curso.id == Submissao.id_curso
    ).join(AtividadeComplementar, AtividadeComplementar.id == Submissao.id_atividade_complementar
    ).join(RegraAtividade, RegraAtividade.id == AtividadeComplementar.id_regra_atividade
    ).outerjoin(Certificado, Certificado.id == Submissao.id_certificado)

    if role == "aluno":
        query = query.where(Submissao.id_aluno == id_usuario)
    elif role == "coordenador":
        subquery = select(CoordenadorCurso.id_curso).where(
            CoordenadorCurso.id_coordenador == id_usuario
        )
        query = query.where(Submissao.id_curso.in_(subquery))
    # admin vê tudo

    if status:
        query = query.where(Submissao.status == status)

    submissoes = db.session.execute(query).all()
    resultado = [
        {
            "id": s.id,
            "status": s.status,
            "data_envio": s.data_envio.isoformat(),
            "aluno_nome": s.aluno_nome,
            "aluno_email": s.aluno_email,
            "curso_nome": s.curso_nome,
            "atividade_descricao": s.atividade_descricao,
            "regra_area": s.regra_area,
            "regra_limite_horas": s.regra_limite_horas,
            "carga_horaria_solicitada": s.carga_horaria_solicitada,
            "certificado_url": s.certificado_url,
            "motivo_rejeicao": s.motivo_rejeicao,
            "carga_horaria_aprovada": s.carga_horaria_aprovada
        }
        for s in submissoes
    ]

    return {"success": True, "submissoes": resultado}, 200


def validar_submissao_controller(id_submissao, data):
    role = get_jwt().get("role")
    id_coordenador = int(get_jwt_identity())

    submissao = db.session.get(Submissao, id_submissao)
    if not submissao:
        return {"success": False, "message": "Submissão não encontrada."}, 404

    if submissao.status != "pendente":
        return {"success": False, "message": "Apenas submissões pendentes podem ser validadas."}, 400

    # Coordenador só pode validar submissões do seu curso
    if role == "coordenador":
        vinculo = db.session.execute(
            select(CoordenadorCurso).where(
                CoordenadorCurso.id_coordenador == id_coordenador,
                CoordenadorCurso.id_curso == submissao.id_curso
            )
        ).scalar_one_or_none()
        if not vinculo:
            return {"success": False, "message": "Você não coordena este curso."}, 403

    novo_status = data.get("status")
    if novo_status not in ("aprovado", "recusado"):
        return {"success": False, "message": "Status inválido. Use 'aprovado' ou 'recusado'."}, 400

    submissao.status = novo_status
    submissao.id_coordenador = id_coordenador

    if novo_status == "recusado":
        motivo = data.get("motivo_rejeicao")
        if not motivo:
            return {"success": False, "message": "Motivo de rejeição é obrigatório."}, 400
        submissao.motivo_rejeicao = motivo
    elif novo_status == "aprovado":
        atividade = db.session.get(AtividadeComplementar, submissao.id_atividade_complementar)
        carga_aprovada = data.get("carga_horaria_aprovada") or atividade.carga_horaria_solicitada

        # Verificar limite da regra
        regra = db.session.get(RegraAtividade, atividade.id_regra_atividade)
        if regra:
            horas_anteriores = db.session.execute(
                select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
                .join(AtividadeComplementar, AtividadeComplementar.id == Submissao.id_atividade_complementar)
                .where(Submissao.id_aluno == submissao.id_aluno)
                .where(Submissao.id_curso == submissao.id_curso)
                .where(Submissao.status == "aprovado")
                .where(AtividadeComplementar.id_regra_atividade == atividade.id_regra_atividade)
                .where(Submissao.id != id_submissao)
            ).scalar() or 0

            horas_disponiveis = regra.limite_horas - horas_anteriores
            carga_aprovada = min(int(carga_aprovada), max(0, horas_disponiveis))

        submissao.carga_horaria_aprovada = carga_aprovada
        atividade.carga_horaria_aprovada = carga_aprovada

    db.session.commit()
    return {"success": True, "message": f"Submissão {novo_status} com sucesso."}, 200
