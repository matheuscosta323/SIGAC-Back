from datetime import datetime
import os
from app.extensions import db
from app.models import Certificado, AtividadeComplementar, Submissao, RegraAtividade, AlunoCurso
from sqlalchemy import select, func
from flask_jwt_extended import get_jwt_identity

PASTA_UPLOAD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "certificados_uploaded")
EXTENSOES_PERMITIDAS = {"pdf", "png", "jpg", "jpeg"}


def _extensao_permitida(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS


def upload_certificado_controller(data, arquivo):
    id_aluno = int(get_jwt_identity())
    titulo = data.get("titulo")
    id_curso = data.get("id_curso")
    id_regra_atividade = data.get("id_regra_atividade")
    carga_horaria_solicitada = data.get("carga_horaria_solicitada")

    if not all([titulo, id_curso, id_regra_atividade, carga_horaria_solicitada, arquivo]):
        return {"success": False, "message": "Dados incompletos."}, 400

    if not _extensao_permitida(arquivo.filename):
        return {"success": False, "message": "Formato de arquivo não permitido. Use PDF, PNG ou JPG."}, 400

    id_curso = int(id_curso)
    id_regra_atividade = int(id_regra_atividade)
    horas_solicitadas = int(carga_horaria_solicitada)

    # Verificar vínculo aluno-curso
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
    if regra.exige_certificado and (not arquivo or arquivo.filename == ""):
        return {"success": False, "message": "Esta atividade exige certificado."}, 400

    horas_ja_aprovadas = db.session.execute(
        select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
        .join(AtividadeComplementar, AtividadeComplementar.id == Submissao.id_atividade_complementar)
        .where(Submissao.id_aluno == id_aluno)
        .where(Submissao.id_curso == id_curso)
        .where(Submissao.status == "aprovado")
        .where(AtividadeComplementar.id_regra_atividade == id_regra_atividade)
    ).scalar() or 0

    if (horas_ja_aprovadas + horas_solicitadas) > regra.limite_horas:
        horas_disponiveis = regra.limite_horas - horas_ja_aprovadas
        return {
            "success": False,
            "message": (
                f"Limite de horas para esta atividade atingido. "
                f"Aprovadas: {int(horas_ja_aprovadas)}h / Limite: {regra.limite_horas}h. "
                f"Disponível: {max(0, horas_disponiveis)}h."
            )
        }, 422

    # Salvar arquivo
    os.makedirs(PASTA_UPLOAD, exist_ok=True)
    nome_arquivo = f"{id_aluno}_{int(datetime.now().timestamp())}_{arquivo.filename}"
    filepath = os.path.join(PASTA_UPLOAD, nome_arquivo)
    arquivo.save(filepath)

    # Criar certificado
    certificado = Certificado(nome_arquivo=nome_arquivo, url_arquivo=filepath)
    db.session.add(certificado)
    db.session.flush()

    # Criar atividade complementar
    atividade = AtividadeComplementar(
        descricao=titulo,
        carga_horaria_solicitada=horas_solicitadas,
        carga_horaria_aprovada=None,
        id_regra_atividade=id_regra_atividade
    )
    db.session.add(atividade)
    db.session.flush()

    # Criar submissão
    submissao = Submissao(
        id_aluno=id_aluno,
        status="pendente",
        id_curso=id_curso,
        id_atividade_complementar=atividade.id,
        id_certificado=certificado.id,
        id_coordenador=None,
        motivo_rejeicao=None,
        carga_horaria_aprovada=None
    )
    db.session.add(submissao)
    db.session.commit()

    return {"success": True, "message": "Certificado enviado e submissão criada com sucesso."}, 201
