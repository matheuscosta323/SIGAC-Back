from app.extensions import db
from app.models import (
    Usuario, Submissao, Curso, RegraAtividade,
    AtividadeComplementar, CoordenadorCurso, AlunoCurso
)
from sqlalchemy import select, func
from flask_jwt_extended import get_jwt, get_jwt_identity
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _ids_cursos_coordenador(id_coordenador):
    rows = db.session.execute(
        select(CoordenadorCurso.id_curso)
        .where(CoordenadorCurso.id_coordenador == id_coordenador)
    ).scalars().all()
    return list(rows)


def _metricas_curso(id_curso):
    """Retorna dict de métricas filtradas por um único curso."""
    total_alunos = db.session.execute(
        select(func.count(func.distinct(AlunoCurso.id_aluno)))
        .where(AlunoCurso.id_curso == id_curso)
    ).scalar() or 0

    total_horas = db.session.execute(
        select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
        .where(Submissao.id_curso == id_curso)
        .where(Submissao.status == "aprovado")
    ).scalar() or 0

    total_sol = db.session.execute(
        select(func.count()).select_from(Submissao)
        .where(Submissao.id_curso == id_curso)
    ).scalar() or 0

    total_aprov = db.session.execute(
        select(func.count()).select_from(Submissao)
        .where(Submissao.id_curso == id_curso)
        .where(Submissao.status == "aprovado")
    ).scalar() or 0

    total_pend = db.session.execute(
        select(func.count()).select_from(Submissao)
        .where(Submissao.id_curso == id_curso)
        .where(Submissao.status == "pendente")
    ).scalar() or 0

    total_rec = db.session.execute(
        select(func.count()).select_from(Submissao)
        .where(Submissao.id_curso == id_curso)
        .where(Submissao.status == "recusado")
    ).scalar() or 0

    taxa = round((total_aprov / total_sol * 100), 1) if total_sol > 0 else 0

    return {
        "total_alunos": total_alunos,
        "total_horas_aprovadas": int(total_horas),
        "total_solicitacoes": total_sol,
        "total_aprovadas": total_aprov,
        "total_pendentes": total_pend,
        "total_recusadas": total_rec,
        "taxa_aprovacao": taxa
    }


def _evolucao_mensal_curso(id_curso):
    resultado = []
    for i in range(5, -1, -1):
        mes = datetime.now().replace(day=1) - timedelta(days=30 * i)
        inicio = mes.replace(day=1)
        fim = (inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        total = db.session.execute(
            select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
            .where(Submissao.id_curso == id_curso)
            .where(Submissao.status == "aprovado")
            .where(Submissao.data_envio >= inicio)
            .where(Submissao.data_envio <= fim)
        ).scalar() or 0
        resultado.append({"mes": mes.strftime("%b/%y"), "horas": int(total)})
    return resultado


def _distribuicao_curso(id_curso):
    rows = db.session.execute(
        select(RegraAtividade.area, func.count(Submissao.id).label("quantidade"))
        .join(AtividadeComplementar, AtividadeComplementar.id == Submissao.id_atividade_complementar)
        .join(RegraAtividade, RegraAtividade.id == AtividadeComplementar.id_regra_atividade)
        .where(Submissao.id_curso == id_curso)
        .group_by(RegraAtividade.area)
    ).all()
    return [{"area": r.area, "quantidade": r.quantidade} for r in rows]


def _submissoes_curso(id_curso):
    """Retorna lista detalhada de submissões com nome do aluno e área."""
    rows = db.session.execute(
        select(
            Submissao.id,
            Submissao.status,
            Submissao.carga_horaria_aprovada,
            AtividadeComplementar.descricao.label("titulo"),
            AtividadeComplementar.carga_horaria_solicitada,
            RegraAtividade.area,
            Usuario.nome.label("aluno_nome")
        )
        .join(AtividadeComplementar, AtividadeComplementar.id == Submissao.id_atividade_complementar)
        .join(RegraAtividade, RegraAtividade.id == AtividadeComplementar.id_regra_atividade)
        .join(Usuario, Usuario.id == Submissao.id_aluno)
        .where(Submissao.id_curso == id_curso)
        .order_by(Submissao.id.desc())
    ).all()

    return [{
        "id": r.id,
        "aluno_nome": r.aluno_nome,
        "titulo": r.titulo,
        "area": r.area,
        "carga_horaria_solicitada": r.carga_horaria_solicitada,
        "carga_horaria_aprovada": r.carga_horaria_aprovada,
        "status": r.status
    } for r in rows]


# ─────────────────────────────────────────────
# Controller principal
# ─────────────────────────────────────────────

def dashboard_controller():
    claims = get_jwt()
    role = claims.get("role")
    if role not in ("admin", "coordenador"):
        return {"success": False, "message": "Acesso negado."}, 403

    # ── ADMIN: dados globais ──────────────────
    if role == "admin":
        total_alunos = db.session.execute(
            select(func.count()).select_from(Usuario).where(Usuario.tipo == "aluno")
        ).scalar()

        total_horas = db.session.execute(
            select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
            .where(Submissao.status == "aprovado")
        ).scalar()

        total_sol = db.session.execute(select(func.count()).select_from(Submissao)).scalar()
        total_aprov = db.session.execute(
            select(func.count()).select_from(Submissao).where(Submissao.status == "aprovado")
        ).scalar()
        total_pend = db.session.execute(
            select(func.count()).select_from(Submissao).where(Submissao.status == "pendente")
        ).scalar()
        total_rec = db.session.execute(
            select(func.count()).select_from(Submissao).where(Submissao.status == "recusado")
        ).scalar()
        taxa = round((total_aprov / total_sol * 100), 1) if total_sol > 0 else 0

        evolucao = []
        for i in range(5, -1, -1):
            mes = datetime.now().replace(day=1) - timedelta(days=30 * i)
            inicio = mes.replace(day=1)
            fim = (inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            total_mes = db.session.execute(
                select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
                .where(Submissao.status == "aprovado")
                .where(Submissao.data_envio >= inicio)
                .where(Submissao.data_envio <= fim)
            ).scalar() or 0
            evolucao.append({"mes": mes.strftime("%b/%y"), "horas": int(total_mes)})

        dist_rows = db.session.execute(
            select(RegraAtividade.area, func.count(Submissao.id).label("quantidade"))
            .join(AtividadeComplementar, AtividadeComplementar.id == Submissao.id_atividade_complementar)
            .join(RegraAtividade, RegraAtividade.id == AtividadeComplementar.id_regra_atividade)
            .group_by(RegraAtividade.area)
        ).all()

        top_rows = db.session.execute(
            select(Curso.nome.label("curso"),
                   func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0).label("horas"))
            .join(Submissao, Submissao.id_curso == Curso.id)
            .where(Submissao.status == "aprovado")
            .group_by(Curso.id)
            .order_by(func.sum(Submissao.carga_horaria_aprovada).desc())
            .limit(5)
        ).all()

        return {
            "success": True,
            "metricas": {
                "total_alunos": total_alunos,
                "total_horas_aprovadas": int(total_horas or 0),
                "total_solicitacoes": total_sol,
                "total_aprovadas": total_aprov,
                "total_pendentes": total_pend,
                "total_recusadas": total_rec,
                "taxa_aprovacao": taxa
            },
            "evolucao_mensal": evolucao,
            "distribuicao_atividades": [{"area": r.area, "quantidade": r.quantidade} for r in dist_rows],
            "top_cursos": [{"curso": r.curso, "horas": int(r.horas)} for r in top_rows]
        }, 200

    # ── COORDENADOR: um bloco por curso ──────
    id_coordenador = int(get_jwt_identity())
    cursos_ids = _ids_cursos_coordenador(id_coordenador)

    if not cursos_ids:
        return {"success": True, "cursos": []}, 200

    cursos_rows = db.session.execute(
        select(Curso.id, Curso.nome).where(Curso.id.in_(cursos_ids))
    ).all()

    cursos = []
    for curso_row in cursos_rows:
        cursos.append({
            "id": curso_row.id,
            "nome": curso_row.nome,
            "metricas": _metricas_curso(curso_row.id),
            "evolucao_mensal": _evolucao_mensal_curso(curso_row.id),
            "distribuicao_atividades": _distribuicao_curso(curso_row.id),
            "submissoes": _submissoes_curso(curso_row.id)
        })

    return {"success": True, "cursos": cursos}, 200
