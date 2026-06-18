from app.extensions import db
from app.models import (
    Usuario, Submissao, Curso, RegraAtividade,
    AtividadeComplementar, CoordenadorCurso, AlunoCurso, DashboardAluno
)
from sqlalchemy import select, func
from flask_jwt_extended import get_jwt, get_jwt_identity
from datetime import datetime, timedelta
from flask import request as flask_request


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
# Controllers
# ─────────────────────────────────────────────

def dashboard_controller():
    claims = get_jwt()
    role = claims.get("role")
    if role not in ("admin", "coordenador"):
        return {"success": False, "message": "Acesso negado."}, 403

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


def meus_cursos_controller():
    """Retorna todos os cursos vinculados ao aluno autenticado."""
    id_aluno = int(get_jwt_identity())

    rows = db.session.execute(
        select(Curso.id, Curso.nome, Curso.carga_horaria)
        .join(AlunoCurso, AlunoCurso.id_curso == Curso.id)
        .where(AlunoCurso.id_aluno == id_aluno)
        .order_by(Curso.nome)
    ).all()

    if not rows:
        return {"success": False, "message": "Aluno sem curso vinculado."}, 404

    cursos = [
        {"id": r.id, "nome": r.nome, "carga_horaria": r.carga_horaria}
        for r in rows
    ]
    return {"success": True, "cursos": cursos}, 200


def dashboard_aluno_controller():
    """
    Retorna o dashboard do aluno filtrado por um curso específico.
    Query param obrigatório: ?id_curso=<int>
    """
    id_aluno = int(get_jwt_identity())

    # Lê o id_curso do query string
    id_curso_param = flask_request.args.get("id_curso", type=int)
    if not id_curso_param:
        return {"success": False, "message": "Parâmetro id_curso é obrigatório."}, 400

    # Valida que o aluno realmente está vinculado a este curso
    vinculo = db.session.execute(
        select(AlunoCurso)
        .where(AlunoCurso.id_aluno == id_aluno)
        .where(AlunoCurso.id_curso == id_curso_param)
    ).scalar_one_or_none()

    if not vinculo:
        return {"success": False, "message": "Aluno não vinculado a este curso."}, 403

    curso = db.session.execute(
        select(Curso).where(Curso.id == id_curso_param)
    ).scalar_one()

    # Horas por área para este curso específico
    registros = db.session.execute(
        select(DashboardAluno)
        .where(DashboardAluno.id_aluno == id_aluno)
        .where(DashboardAluno.id_curso == id_curso_param)
    ).scalars().all()

    total_aprovadas = sum(r.horas_aprovadas for r in registros)
    areas = [
        {
            "area": r.area,
            "horas_aprovadas": r.horas_aprovadas,
            "limite_horas": r.limite_horas,
            "percentual": round((r.horas_aprovadas / r.limite_horas) * 100, 1)
            if r.limite_horas > 0 else 0
        }
        for r in registros
    ]

    def contar_status(status):
        return db.session.execute(
            select(func.count()).select_from(Submissao)
            .where(Submissao.id_aluno == id_aluno)
            .where(Submissao.id_curso == id_curso_param)
            .where(Submissao.status == status)
        ).scalar()

    return {
        "success": True,
        "id_curso": curso.id,
        "curso": curso.nome,
        "progresso": {
            "horas_aprovadas": total_aprovadas,
            "carga_horaria_total": curso.carga_horaria,
            "percentual": round((total_aprovadas / curso.carga_horaria) * 100, 1)
            if curso.carga_horaria > 0 else 0
        },
        "horas_por_area": areas,
        "solicitacoes": {
            "pendentes": contar_status("pendente"),
            "aprovadas": contar_status("aprovado"),
            "recusadas": contar_status("recusado")
        }
    }, 200
