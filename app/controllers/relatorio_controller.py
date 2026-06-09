from app.extensions import db
from app.models import Usuario, Submissao, Curso, RegraAtividade, AtividadeComplementar, CoordenadorCurso
from sqlalchemy import select, func
from flask_jwt_extended import get_jwt, get_jwt_identity
from datetime import datetime, timedelta


def _ids_cursos_coordenador(id_coordenador):
    """Retorna lista de IDs de cursos vinculados ao coordenador."""
    rows = db.session.execute(
        select(CoordenadorCurso.id_curso).where(CoordenadorCurso.id_coordenador == id_coordenador)
    ).scalars().all()
    return list(rows)


def dashboard_controller():
    claims = get_jwt()
    role = claims.get("role")
    if role not in ("admin", "coordenador"):
        return {"success": False, "message": "Acesso negado."}, 403

    # Coordenador vê apenas os cursos que gerencia; admin vê tudo
    filtrar_por_cursos = None
    cursos_gerenciados = []
    if role == "coordenador":
        id_coordenador = int(get_jwt_identity())
        cursos_ids = _ids_cursos_coordenador(id_coordenador)
        if not cursos_ids:
            # Coordenador sem cursos vinculados — retorna zerado com aviso
            return {
                "success": True,
                "aviso": "Nenhum curso vinculado a este coordenador.",
                "cursos_gerenciados": [],
                "metricas": {
                    "total_alunos": 0, "total_horas_aprovadas": 0,
                    "total_solicitacoes": 0, "total_aprovadas": 0,
                    "total_pendentes": 0, "total_recusadas": 0, "taxa_aprovacao": 0
                },
                "evolucao_mensal": [],
                "distribuicao_atividades": [],
                "top_cursos": []
            }, 200
        filtrar_por_cursos = cursos_ids
        # Nomes dos cursos gerenciados para exibição no front
        nomes = db.session.execute(
            select(Curso.id, Curso.nome).where(Curso.id.in_(filtrar_por_cursos))
        ).all()
        cursos_gerenciados = [{"id": r.id, "nome": r.nome} for r in nomes]

    # Helper para aplicar filtro de cursos nas queries de Submissao
    def filtro_submissao(query):
        if filtrar_por_cursos is not None:
            return query.where(Submissao.id_curso.in_(filtrar_por_cursos))
        return query

    # 1. Métricas principais
    if filtrar_por_cursos is not None:
        # Total de alunos matriculados nos cursos do coordenador
        from app.models import AlunoCurso
        total_alunos = db.session.execute(
            select(func.count(func.distinct(AlunoCurso.id_aluno)))
            .where(AlunoCurso.id_curso.in_(filtrar_por_cursos))
        ).scalar()
    else:
        total_alunos = db.session.execute(
            select(func.count()).select_from(Usuario).where(Usuario.tipo == "aluno")
        ).scalar()

    total_horas_aprovadas = db.session.execute(
        filtro_submissao(
            select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
            .where(Submissao.status == "aprovado")
        )
    ).scalar()

    total_solicitacoes = db.session.execute(
        filtro_submissao(select(func.count()).select_from(Submissao))
    ).scalar()

    total_aprovadas = db.session.execute(
        filtro_submissao(
            select(func.count()).select_from(Submissao).where(Submissao.status == "aprovado")
        )
    ).scalar()

    total_pendentes = db.session.execute(
        filtro_submissao(
            select(func.count()).select_from(Submissao).where(Submissao.status == "pendente")
        )
    ).scalar()

    total_recusadas = db.session.execute(
        filtro_submissao(
            select(func.count()).select_from(Submissao).where(Submissao.status == "recusado")
        )
    ).scalar()

    taxa_aprovacao = round((total_aprovadas / total_solicitacoes * 100), 1) if total_solicitacoes > 0 else 0

    metricas = {
        "total_alunos": total_alunos,
        "total_horas_aprovadas": int(total_horas_aprovadas or 0),
        "total_solicitacoes": total_solicitacoes,
        "total_aprovadas": total_aprovadas,
        "total_pendentes": total_pendentes,
        "total_recusadas": total_recusadas,
        "taxa_aprovacao": taxa_aprovacao
    }

    # 2. Evolução mensal (últimos 6 meses)
    ultimos_6_meses = []
    for i in range(5, -1, -1):
        mes = datetime.now().replace(day=1) - timedelta(days=30 * i)
        nome_mes = mes.strftime("%b/%y")
        inicio_mes = mes.replace(day=1)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        base_q = (
            select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
            .where(Submissao.status == "aprovado")
            .where(Submissao.data_envio >= inicio_mes)
            .where(Submissao.data_envio <= fim_mes)
        )
        total_mes = db.session.execute(filtro_submissao(base_q)).scalar()
        ultimos_6_meses.append({"mes": nome_mes, "horas": int(total_mes or 0)})

    # 3. Distribuição por área de atividade
    dist_q = (
        select(
            RegraAtividade.area,
            func.count(Submissao.id).label("quantidade")
        )
        .join(AtividadeComplementar, AtividadeComplementar.id == Submissao.id_atividade_complementar)
        .join(RegraAtividade, RegraAtividade.id == AtividadeComplementar.id_regra_atividade)
        .group_by(RegraAtividade.area)
    )
    if filtrar_por_cursos is not None:
        dist_q = dist_q.where(Submissao.id_curso.in_(filtrar_por_cursos))
    distribuicao_rows = db.session.execute(dist_q).all()

    distribuicao_atividades = [
        {"area": row.area, "quantidade": row.quantidade}
        for row in distribuicao_rows
    ]

    # 4. Top cursos por horas aprovadas
    top_q = (
        select(
            Curso.nome.label("curso"),
            func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0).label("horas")
        )
        .join(Submissao, Submissao.id_curso == Curso.id)
        .where(Submissao.status == "aprovado")
        .group_by(Curso.id)
        .order_by(func.sum(Submissao.carga_horaria_aprovada).desc())
        .limit(5)
    )
    if filtrar_por_cursos is not None:
        top_q = top_q.where(Curso.id.in_(filtrar_por_cursos))
    top_cursos_rows = db.session.execute(top_q).all()

    top_cursos = [{"curso": row.curso, "horas": int(row.horas)} for row in top_cursos_rows]

    return {
        "success": True,
        "cursos_gerenciados": cursos_gerenciados,  # lista vazia para admin
        "metricas": metricas,
        "evolucao_mensal": ultimos_6_meses,
        "distribuicao_atividades": distribuicao_atividades,
        "top_cursos": top_cursos
    }, 200
