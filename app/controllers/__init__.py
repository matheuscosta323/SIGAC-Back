from .auth_controller import login_controller
from .usuario_controller import (
    cadastrar_usuario_controller,
    vincular_usuario_curso_controller,
    listar_alunos_controller,
    listar_coordenadores_controller,
)
from .submissao_controller import (
    enviar_submissao_controller,
    listar_submissoes_controller,
    avaliar_submissao_controller,
)
from .relatorio_controller import (
    dashboard_controller,
    dashboard_aluno_controller,
    meus_cursos_controller,
)
from .curso_controller import listar_cursos_controller
from .regra_controller import (
    listar_regras_controller,
    criar_regra_controller,
    atualizar_regra_controller,
    deletar_regra_controller,
)
from .certificado_controller import (
    gerar_certificado_controller,
    listar_certificados_controller,
    deletar_certificado_controller,
)
