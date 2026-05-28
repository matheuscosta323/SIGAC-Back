from app.extensions import db
from app.models import RegraAtividade
from sqlalchemy import select
from flask_jwt_extended import get_jwt

def listar_regras_controller(curso_id=None):
    role = get_jwt().get("role")
    if role not in ("admin", "coordenador", "aluno"):
        return {"success": False, "message": "Acesso negado."}, 403

    query = select(RegraAtividade)
    if curso_id:
        query = query.where(RegraAtividade.id_curso == curso_id)
    regras = db.session.execute(query).scalars().all()
    resultado = [
        {
            "id": r.id,
            "area": r.area,
            "descricao": r.descricao,
            "limite_horas": r.limite_horas,
            "requisito": r.requisito,
            "exige_certificado": r.exige_certificado,
            "id_curso": r.id_curso
        }
        for r in regras
    ]
    return {"success": True, "regras": resultado}, 200

def criar_regra_controller(data):
    role = get_jwt().get("role")
    if role != "admin":
        return {"success": False, "message": "Apenas admin pode criar regras."}, 403

    nova = RegraAtividade(
        area=data["area"],
        descricao=data["descricao"],
        limite_horas=data["limite_horas"],
        requisito=data["requisito"],
        exige_certificado=data["exige_certificado"],
        id_curso=data.get("id_curso")
    )
    db.session.add(nova)
    db.session.commit()
    return {"success": True, "message": "Regra criada com sucesso."}, 201

def atualizar_regra_controller(id_regra, data):
    role = get_jwt().get("role")
    if role != "admin":
        return {"success": False, "message": "Apenas super_admin pode editar regras."}, 403

    regra = db.session.get(RegraAtividade, id_regra)
    if not regra:
        return {"success": False, "message": "Regra não encontrada."}, 404

    regra.area = data.get("area", regra.area)
    regra.descricao = data.get("descricao", regra.descricao)
    regra.limite_horas = data.get("limite_horas", regra.limite_horas)
    regra.requisito = data.get("requisito", regra.requisito)
    regra.exige_certificado = data.get("exige_certificado", regra.exige_certificado)
    regra.id_curso = data.get("id_curso", regra.id_curso)
    db.session.commit()
    return {"success": True, "message": "Regra atualizada."}, 200

def excluir_regra_controller(id_regra):
    role = get_jwt().get("role")
    if role != "admin":
        return {"success": False, "message": "Apenas admin pode excluir regras."}, 403

    regra = db.session.get(RegraAtividade, id_regra)
    if not regra:
        return {"success": False, "message": "Regra não encontrada."}, 404
    db.session.delete(regra)
    db.session.commit()
    return {"success": True, "message": "Regra excluída."}, 200