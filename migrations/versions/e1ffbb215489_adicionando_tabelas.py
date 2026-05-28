"""Adicionando tabelas

Revision ID: e1ffbb215489
Revises: 
Create Date: 2026-05-03 10:47:12.381498

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1ffbb215489'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # -------------------------------------------------------
    # Tabelas sem dependências externas
    # -------------------------------------------------------
    op.create_table('certificado',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome_arquivo', sa.String(length=100), nullable=False),
        sa.Column('url_arquivo', sa.String(length=300), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('curso',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('carga_horaria', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # CORRIGIDO: coluna renomeada de 'senha' para 'senhaHash'
    # (o model Usuario usa o atributo senhaHash)
    op.create_table('usuario',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('senhaHash', sa.String(length=300), nullable=False),
        sa.Column('tipo', sa.String(length=100), nullable=False),
        sa.Column('matricula', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # CORRIGIDO: adicionado id_curso como FK para filtrar regras por curso
    op.create_table('regra_atividade',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('area', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.String(length=300), nullable=False),
        sa.Column('limite_horas', sa.Integer(), nullable=False),
        sa.Column('requisito', sa.String(length=100), nullable=True),
        sa.Column('exige_certificado', sa.Boolean(), nullable=False),
        sa.Column('id_curso', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id_curso'], ['curso.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # -------------------------------------------------------
    # Tabelas de relacionamento (dependem de usuario e curso)
    # -------------------------------------------------------
    op.create_table('aluno_curso',
        sa.Column('id_aluno', sa.Integer(), nullable=False),
        sa.Column('id_curso', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_aluno'], ['usuario.id'], ),
        sa.ForeignKeyConstraint(['id_curso'], ['curso.id'], ),
        sa.PrimaryKeyConstraint('id_aluno', 'id_curso')
    )

    op.create_table('coordenador_curso',
        sa.Column('id_coordenador', sa.Integer(), nullable=False),
        sa.Column('id_curso', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_coordenador'], ['usuario.id'], ),
        sa.ForeignKeyConstraint(['id_curso'], ['curso.id'], ),
        sa.PrimaryKeyConstraint('id_coordenador', 'id_curso')
    )

    # -------------------------------------------------------
    # atividade_complementar (depende de regra_atividade)
    # -------------------------------------------------------
    op.create_table('atividade_complementar',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('descricao', sa.String(length=300), nullable=False),
        sa.Column('carga_horaria_solicitada', sa.Integer(), nullable=False),
        sa.Column('carga_horaria_aprovada', sa.Integer(), nullable=True),
        sa.Column('id_regra_atividade', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_regra_atividade'], ['regra_atividade.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # -------------------------------------------------------
    # submissao (depende de tudo)
    # CORRIGIDO: adicionado carga_horaria_aprovada diretamente
    # na submissao (o model Submissao tem esse campo)
    # -------------------------------------------------------
    op.create_table('submissao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_envio', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=100), nullable=False),
        sa.Column('id_aluno', sa.Integer(), nullable=False),
        sa.Column('id_curso', sa.Integer(), nullable=False),
        sa.Column('id_atividade_complementar', sa.Integer(), nullable=False),
        sa.Column('id_certificado', sa.Integer(), nullable=True),
        sa.Column('id_coordenador', sa.Integer(), nullable=True),
        sa.Column('motivo_rejeicao', sa.String(length=300), nullable=True),
        sa.Column('carga_horaria_aprovada', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id_aluno'], ['usuario.id'], ),
        sa.ForeignKeyConstraint(['id_atividade_complementar'], ['atividade_complementar.id'], ),
        sa.ForeignKeyConstraint(['id_certificado'], ['certificado.id'], ),
        sa.ForeignKeyConstraint(['id_coordenador'], ['usuario.id'], ),
        sa.ForeignKeyConstraint(['id_curso'], ['curso.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('submissao')
    op.drop_table('coordenador_curso')
    op.drop_table('atividade_complementar')
    op.drop_table('aluno_curso')
    op.drop_table('usuario')
    op.drop_table('regra_atividade')
    op.drop_table('curso')
    op.drop_table('certificado')