from .submissao_controller import criar_submissao_controller, listar_submissoes_controller, validar_submissao_controller
from .usuario_controller import (
    cadastrar_usuario_controller,
    vincular_usuario_curso_controller,
    listar_alunos_controller,
    listar_coordenadores_controller
)
from .auth_controller import login_controller
from .curso_controller import cadastrar_curso_controller, listar_cursos_controller
from .certificado_controller import upload_certificado_controller
from .regra_controller import listar_regras_controller, criar_regra_controller, atualizar_regra_controller, excluir_regra_controller
from .relatorio_controller import dashboard_controller
