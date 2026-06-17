"""
Configuração do Swagger/OpenAPI 3.0 para o SIGAC API.
Utiliza flask-swagger-ui + spec manual em JSON.

Documentação gerada/atualizada a partir da análise de:
- app/routes/*.py
- app/controllers/*.py
- app/models/*.py
- app/middlewares/auth_middleware.py
"""

from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/api/docs"
API_URL = "/api/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "SIGAC API"}
)

swagger_spec_bp = Blueprint("swagger_spec", __name__)


@swagger_spec_bp.route("/api/swagger.json")
def swagger_spec():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "SIGAC API",
            "description": (
                "API do Sistema de Gerenciamento de Atividades Complementares (SIGAC). "
                "Gerencia usuários (alunos, coordenadores, admin), cursos, regras, "
                "submissões de atividades complementares, certificados e dashboards "
                "(gerencial para admin/coordenador e individual para o aluno)."
            ),
            "version": "1.1.0"
        },
        "servers": [{"url": "/", "description": "Servidor local"}],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": (
                        "Token JWT obtido em /api/auth/login. "
                        "Contém claims adicionais: role (admin|coordenador|aluno) e nome."
                    )
                }
            },
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": False},
                        "message": {"type": "string"}
                    }
                },
                "Success": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "message": {"type": "string"}
                    }
                },

                # ── AUTH ────────────────────────────────────
                "LoginRequest": {
                    "type": "object",
                    "required": ["email", "senha"],
                    "properties": {
                        "email": {"type": "string", "format": "email", "example": "admin@sigac.com"},
                        "senha": {"type": "string", "example": "senha123"}
                    }
                },
                "LoginResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "message": {"type": "string", "example": "Login efetuado com sucesso."},
                        "access_token": {"type": "string"}
                    }
                },

                # ── USUÁRIOS ────────────────────────────────
                "CadastrarUsuarioRequest": {
                    "type": "object",
                    "required": ["nome", "email", "senha", "tipo", "id_curso"],
                    "properties": {
                        "nome": {"type": "string", "example": "João Silva"},
                        "email": {"type": "string", "format": "email"},
                        "senha": {"type": "string"},
                        "tipo": {"type": "string", "enum": ["aluno", "coordenador"]},
                        "matricula": {
                            "type": "string",
                            "example": "20241001",
                            "description": "Obrigatório quando tipo = aluno."
                        },
                        "id_curso": {"type": "integer", "example": 1}
                    }
                },
                "VincularCursoRequest": {
                    "type": "object",
                    "required": ["id_usuario", "id_curso"],
                    "properties": {
                        "id_usuario": {"type": "integer", "example": 5},
                        "id_curso": {"type": "integer", "example": 2}
                    }
                },
                "AlunoComProgresso": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 5},
                        "nome": {"type": "string", "example": "Maria Souza"},
                        "matricula": {"type": "string", "example": "20241002"},
                        "curso_id": {"type": "integer", "example": 1},
                        "curso": {"type": "string", "example": "Sistemas de Informação"},
                        "horas_concluidas": {"type": "integer", "example": 40},
                        "total_horas": {"type": "integer", "example": 200},
                        "progresso": {"type": "number", "format": "float", "example": 20.0}
                    }
                },
                "Coordenador": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 3},
                        "nome": {"type": "string", "example": "Carlos Lima"},
                        "email": {"type": "string", "format": "email"},
                        "matricula": {"type": "string", "nullable": True},
                        "cursos": {
                            "type": "array",
                            "items": {"type": "string"},
                            "example": ["Sistemas de Informação", "Engenharia de Software"]
                        }
                    }
                },

                # ── CURSOS ──────────────────────────────────
                "CursoRequest": {
                    "type": "object",
                    "required": ["nome", "carga_horaria"],
                    "properties": {
                        "nome": {"type": "string", "example": "Sistemas de Informação"},
                        "carga_horaria": {"type": "integer", "example": 200}
                    }
                },
                "Curso": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "nome": {"type": "string", "example": "Sistemas de Informação"},
                        "carga_horaria": {"type": "integer", "example": 200}
                    }
                },

                # ── REGRAS ──────────────────────────────────
                "RegraRequest": {
                    "type": "object",
                    "required": ["area", "descricao", "limite_horas", "requisito", "exige_certificado"],
                    "properties": {
                        "area": {"type": "string", "example": "Extensão"},
                        "descricao": {"type": "string", "example": "Participação em eventos de extensão"},
                        "limite_horas": {"type": "integer", "example": 60},
                        "requisito": {"type": "string", "example": "Certificado de participação"},
                        "exige_certificado": {"type": "boolean", "example": True},
                        "id_curso": {
                            "type": "integer",
                            "nullable": True,
                            "example": 1,
                            "description": "Se omitido/nulo, a regra é considerada global (todos os cursos)."
                        }
                    }
                },
                "Regra": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "area": {"type": "string", "example": "Extensão"},
                        "descricao": {"type": "string", "example": "Participação em eventos de extensão"},
                        "limite_horas": {"type": "integer", "example": 60},
                        "requisito": {"type": "string", "example": "Certificado de participação"},
                        "exige_certificado": {"type": "boolean", "example": True},
                        "id_curso": {"type": "integer", "nullable": True, "example": 1}
                    }
                },

                # ── SUBMISSÕES ──────────────────────────────
                "CriarSubmissaoRequest": {
                    "type": "object",
                    "required": [
                        "titulo", "id_curso", "id_regra_atividade",
                        "carga_horaria_solicitada", "nome_arquivo", "url_arquivo"
                    ],
                    "properties": {
                        "titulo": {"type": "string", "example": "Participação na Semana Acadêmica"},
                        "id_curso": {"type": "integer", "example": 1},
                        "id_regra_atividade": {"type": "integer", "example": 2},
                        "carga_horaria_solicitada": {"type": "integer", "example": 20},
                        "nome_arquivo": {
                            "type": "string",
                            "example": "certificado.pdf",
                            "description": "Usado quando o arquivo já foi enviado/hospedado fora deste endpoint."
                        },
                        "url_arquivo": {
                            "type": "string",
                            "example": "https://storage.exemplo.com/certificado.pdf"
                        }
                    }
                },
                "Submissao": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 10},
                        "status": {"type": "string", "enum": ["pendente", "aprovado", "recusado"]},
                        "data_envio": {"type": "string", "format": "date-time"},
                        "aluno_nome": {"type": "string", "example": "Maria Souza"},
                        "aluno_email": {"type": "string", "format": "email"},
                        "curso_nome": {"type": "string", "example": "Sistemas de Informação"},
                        "atividade_descricao": {"type": "string", "example": "Participação na Semana Acadêmica"},
                        "regra_area": {"type": "string", "example": "Extensão"},
                        "regra_limite_horas": {"type": "integer", "example": 60},
                        "carga_horaria_solicitada": {"type": "integer", "example": 20},
                        "certificado_url": {"type": "string", "nullable": True},
                        "motivo_rejeicao": {"type": "string", "nullable": True},
                        "carga_horaria_aprovada": {"type": "integer", "nullable": True}
                    }
                },
                "ValidarSubmissaoRequest": {
                    "type": "object",
                    "required": ["status"],
                    "properties": {
                        "status": {"type": "string", "enum": ["aprovado", "recusado"]},
                        "motivo_rejeicao": {
                            "type": "string",
                            "example": "Certificado ilegível",
                            "description": "Obrigatório quando status = recusado."
                        },
                        "carga_horaria_aprovada": {
                            "type": "integer",
                            "example": 40,
                            "description": (
                                "Opcional quando status = aprovado. Se omitido, usa a carga "
                                "solicitada (limitada ao saldo disponível na regra)."
                            )
                        }
                    }
                },

                # ── DASHBOARD ADMIN/COORDENADOR ─────────────
                "MetricasDashboard": {
                    "type": "object",
                    "properties": {
                        "total_alunos": {"type": "integer", "example": 120},
                        "total_horas_aprovadas": {"type": "integer", "example": 3400},
                        "total_solicitacoes": {"type": "integer", "example": 210},
                        "total_aprovadas": {"type": "integer", "example": 150},
                        "total_pendentes": {"type": "integer", "example": 40},
                        "total_recusadas": {"type": "integer", "example": 20},
                        "taxa_aprovacao": {"type": "number", "format": "float", "example": 71.4}
                    }
                },
                "EvolucaoMensalItem": {
                    "type": "object",
                    "properties": {
                        "mes": {"type": "string", "example": "jan/26"},
                        "horas": {"type": "integer", "example": 320}
                    }
                },
                "DistribuicaoAtividadeItem": {
                    "type": "object",
                    "properties": {
                        "area": {"type": "string", "example": "Extensão"},
                        "quantidade": {"type": "integer", "example": 18}
                    }
                },
                "TopCursoItem": {
                    "type": "object",
                    "properties": {
                        "curso": {"type": "string", "example": "Sistemas de Informação"},
                        "horas": {"type": "integer", "example": 980}
                    }
                },
                "DashboardAdminResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "metricas": {"$ref": "#/components/schemas/MetricasDashboard"},
                        "evolucao_mensal": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/EvolucaoMensalItem"}
                        },
                        "distribuicao_atividades": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/DistribuicaoAtividadeItem"}
                        },
                        "top_cursos": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/TopCursoItem"}
                        }
                    }
                },
                "DashboardCoordenadorCurso": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "nome": {"type": "string", "example": "Sistemas de Informação"},
                        "metricas": {"$ref": "#/components/schemas/MetricasDashboard"},
                        "evolucao_mensal": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/EvolucaoMensalItem"}
                        },
                        "distribuicao_atividades": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/DistribuicaoAtividadeItem"}
                        },
                        "submissoes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer", "example": 10},
                                    "aluno_nome": {"type": "string", "example": "Maria Souza"},
                                    "titulo": {"type": "string", "example": "Participação na Semana Acadêmica"},
                                    "area": {"type": "string", "example": "Extensão"},
                                    "carga_horaria_solicitada": {"type": "integer", "example": 20},
                                    "carga_horaria_aprovada": {"type": "integer", "nullable": True},
                                    "status": {"type": "string", "enum": ["pendente", "aprovado", "recusado"]}
                                }
                            }
                        }
                    }
                },
                "DashboardCoordenadorResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "cursos": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/DashboardCoordenadorCurso"},
                            "description": "Um bloco de métricas por curso coordenado. Lista vazia se o coordenador não possui cursos vinculados."
                        }
                    }
                },

                # ── DASHBOARD ALUNO (NOVO) ──────────────────
                "HorasPorAreaItem": {
                    "type": "object",
                    "properties": {
                        "area": {"type": "string", "example": "Extensão"},
                        "horas_aprovadas": {"type": "integer", "example": 30},
                        "limite_horas": {"type": "integer", "example": 60},
                        "percentual": {"type": "number", "format": "float", "example": 50.0}
                    }
                },
                "DashboardAlunoResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "curso": {"type": "string", "example": "Sistemas de Informação"},
                        "progresso": {
                            "type": "object",
                            "properties": {
                                "horas_aprovadas": {"type": "integer", "example": 90},
                                "carga_horaria_total": {"type": "integer", "example": 200},
                                "percentual": {"type": "number", "format": "float", "example": 45.0}
                            }
                        },
                        "horas_por_area": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/HorasPorAreaItem"}
                        },
                        "solicitacoes": {
                            "type": "object",
                            "properties": {
                                "pendentes": {"type": "integer", "example": 3},
                                "aprovadas": {"type": "integer", "example": 5},
                                "recusadas": {"type": "integer", "example": 1}
                            }
                        }
                    }
                }
            }
        },
        "security": [{"BearerAuth": []}],
        "tags": [
            {"name": "Auth", "description": "Autenticação e emissão de token JWT"},
            {"name": "Usuários", "description": "Cadastro e listagem de alunos e coordenadores"},
            {"name": "Cursos", "description": "Cadastro e listagem de cursos"},
            {"name": "Regras", "description": "Regras de atividades complementares por área/curso"},
            {"name": "Submissões", "description": "Envio e validação de submissões de atividades complementares"},
            {"name": "Certificados", "description": "Upload de certificados (com criação automática de submissão)"},
            {"name": "Relatórios", "description": "Dashboards gerenciais (admin/coordenador) e individual (aluno)"}
        ],
        "paths": {
            # ── AUTH ──────────────────────────────────────────
            "/api/auth/login": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Login de usuário",
                    "description": "Autentica por e-mail e senha. Retorna um JWT com claims 'role' e 'nome'.",
                    "security": [],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginRequest"}}}
                    },
                    "responses": {
                        "200": {
                            "description": "Login bem-sucedido",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginResponse"}}}
                        },
                        "401": {
                            "description": "Credenciais inválidas",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
                        },
                        "404": {
                            "description": "Usuário não encontrado",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
                        },
                        "500": {
                            "description": "Erro interno ao efetuar login",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
                        }
                    }
                }
            },

            # ── USUÁRIOS ──────────────────────────────────────
            "/api/usuarios/cadastrar": {
                "post": {
                    "tags": ["Usuários"],
                    "summary": "Cadastrar aluno ou coordenador",
                    "description": (
                        "Admin pode cadastrar alunos e coordenadores. Coordenador só pode "
                        "cadastrar alunos. Aluno exige matrícula. Vincula automaticamente "
                        "o usuário criado ao id_curso informado."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CadastrarUsuarioRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Usuário cadastrado com sucesso",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                        "400": {"description": "Dados inválidos / corpo da requisição ausente",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "403": {"description": "Sem permissão (role não autorizada para o tipo solicitado)",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Curso não encontrado",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "409": {"description": "E-mail já cadastrado",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/usuarios/vincular-curso": {
                "post": {
                    "tags": ["Usuários"],
                    "summary": "Vincular usuário a curso adicional",
                    "description": "Permite vincular um aluno ou coordenador já cadastrado a mais de um curso. Apenas admin.",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/VincularCursoRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Vínculo criado com sucesso",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                        "400": {"description": "Dados inválidos (id_usuario/id_curso ausentes ou tipo não suportado)",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "403": {"description": "Sem permissão (apenas admin)",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Usuário ou curso não encontrado",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "409": {"description": "Vínculo já existente",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/usuarios/listar_alunos": {
                "get": {
                    "tags": ["Usuários"],
                    "summary": "Listar alunos com progresso",
                    "description": (
                        "Retorna todos os alunos com curso vinculado, horas concluídas "
                        "(submissões aprovadas) e percentual de progresso. Admin e coordenador."
                    ),
                    "responses": {
                        "200": {
                            "description": "Lista de alunos",
                            "content": {"application/json": {"schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean", "example": True},
                                    "alunos": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/AlunoComProgresso"}
                                    }
                                }
                            }}}
                        },
                        "403": {"description": "Sem permissão",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/usuarios/listar_coordenadores": {
                "get": {
                    "tags": ["Usuários"],
                    "summary": "Listar coordenadores",
                    "description": "Retorna coordenadores com os cursos que cada um coordena. Apenas admin.",
                    "responses": {
                        "200": {
                            "description": "Lista de coordenadores",
                            "content": {"application/json": {"schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean", "example": True},
                                    "coordenadores": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Coordenador"}
                                    }
                                }
                            }}}
                        },
                        "403": {"description": "Sem permissão (apenas admin)",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },

            # ── CURSOS ────────────────────────────────────────
            "/api/cursos/cadastrar": {
                "post": {
                    "tags": ["Cursos"],
                    "summary": "Cadastrar curso",
                    "description": "Apenas admin.",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CursoRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Curso cadastrado",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                        "400": {"description": "Corpo da requisição inválido",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "403": {"description": "Sem permissão",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/cursos/listar": {
                "get": {
                    "tags": ["Cursos"],
                    "summary": "Listar todos os cursos",
                    "description": "Disponível para admin, coordenador e aluno.",
                    "responses": {
                        "200": {
                            "description": "Lista de cursos",
                            "content": {"application/json": {"schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean", "example": True},
                                    "cursos": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Curso"}
                                    }
                                }
                            }}}
                        },
                        "403": {"description": "Sem permissão",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },

            # ── REGRAS ────────────────────────────────────────
            "/api/regras/listar": {
                "get": {
                    "tags": ["Regras"],
                    "summary": "Listar regras de atividades",
                    "description": "Disponível para admin, coordenador e aluno. Pode ser filtrada por curso.",
                    "parameters": [
                        {
                            "name": "curso_id",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Filtrar regras por curso"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de regras",
                            "content": {"application/json": {"schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean", "example": True},
                                    "regras": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Regra"}
                                    }
                                }
                            }}}
                        },
                        "403": {"description": "Sem permissão",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/regras/criar": {
                "post": {
                    "tags": ["Regras"],
                    "summary": "Criar regra de atividade",
                    "description": "Apenas admin. Se id_curso não for informado, a regra é global.",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RegraRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Regra criada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                        "403": {"description": "Sem permissão (apenas admin)",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/regras/atualizar/{id_regra}": {
                "put": {
                    "tags": ["Regras"],
                    "summary": "Atualizar regra",
                    "description": "Apenas admin. Campos omitidos mantêm o valor atual.",
                    "parameters": [{"name": "id_regra", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RegraRequest"}}}
                    },
                    "responses": {
                        "200": {"description": "Regra atualizada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                        "403": {"description": "Sem permissão (apenas admin)",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Regra não encontrada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/regras/excluir/{id_regra}": {
                "delete": {
                    "tags": ["Regras"],
                    "summary": "Excluir regra",
                    "description": "Apenas admin.",
                    "parameters": [{"name": "id_regra", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {
                        "200": {"description": "Regra excluída",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                        "403": {"description": "Sem permissão (apenas admin)",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Regra não encontrada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },

            # ── SUBMISSÕES ────────────────────────────────────
            "/api/submissoes/criar": {
                "post": {
                    "tags": ["Submissões"],
                    "summary": "Criar submissão de atividade complementar (aluno)",
                    "description": (
                        "Valida vínculo do aluno ao curso e limite de horas da regra antes de "
                        "criar. Usa um arquivo já hospedado externamente (nome_arquivo/url_arquivo). "
                        "Para enviar o arquivo diretamente, use /api/certificados/upload."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CriarSubmissaoRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Submissão criada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                        "400": {"description": "Dados incompletos",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "403": {"description": "Aluno não matriculado neste curso",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Regra de atividade não encontrada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "422": {"description": "Limite de horas da regra atingido",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/submissoes/listar": {
                "get": {
                    "tags": ["Submissões"],
                    "summary": "Listar submissões",
                    "description": "Aluno vê apenas as próprias, coordenador vê as do(s) seu(s) curso(s), admin vê todas.",
                    "parameters": [
                        {
                            "name": "status",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "enum": ["pendente", "aprovado", "recusado"]},
                            "description": "Filtrar por status"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de submissões",
                            "content": {"application/json": {"schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean", "example": True},
                                    "submissoes": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Submissao"}
                                    }
                                }
                            }}}
                        },
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/submissoes/validar/{id_submissao}": {
                "put": {
                    "tags": ["Submissões"],
                    "summary": "Validar submissão (coordenador ou admin)",
                    "description": (
                        "Aprova ou recusa uma submissão pendente. Coordenador só pode validar "
                        "submissões do(s) curso(s) que coordena. Ao aprovar, a carga horária "
                        "aprovada é limitada ao saldo disponível na regra."
                    ),
                    "parameters": [{"name": "id_submissao", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidarSubmissaoRequest"}}}
                    },
                    "responses": {
                        "200": {"description": "Submissão validada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                        "400": {"description": "Status inválido, motivo de rejeição ausente ou submissão não pendente",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "403": {"description": "Coordenador não responsável por este curso",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Submissão não encontrada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },

            # ── CERTIFICADOS ──────────────────────────────────
            "/api/certificados/upload": {
                "post": {
                    "tags": ["Certificados"],
                    "summary": "Upload de certificado com criação de submissão (aluno)",
                    "description": (
                        "Envia um arquivo (PDF/PNG/JPG/JPEG) junto com os dados da atividade. "
                        "Valida vínculo ao curso e limite de horas da regra, salva o arquivo no "
                        "servidor e cria a submissão (status inicial: pendente)."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["file", "titulo", "id_curso", "id_regra_atividade", "carga_horaria_solicitada"],
                                    "properties": {
                                        "file": {"type": "string", "format": "binary"},
                                        "titulo": {"type": "string", "example": "Participação na Semana Acadêmica"},
                                        "id_curso": {"type": "integer", "example": 1},
                                        "id_regra_atividade": {"type": "integer", "example": 2},
                                        "carga_horaria_solicitada": {"type": "integer", "example": 20}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Certificado enviado e submissão criada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                        "400": {"description": "Dados incompletos, arquivo ausente/vazio ou formato não permitido",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "403": {"description": "Aluno não matriculado neste curso",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Regra de atividade não encontrada",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "422": {"description": "Limite de horas da regra atingido",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Erro interno",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },

            # ── RELATÓRIOS / DASHBOARD ─────────────────────────
            "/api/relatorios/dashboard": {
                "get": {
                    "tags": ["Relatórios"],
                    "summary": "Dashboard gerencial (admin e coordenador)",
                    "description": (
                        "Para admin: retorna métricas globais, evolução mensal (últimos 6 meses), "
                        "distribuição de atividades por área e top 5 cursos por horas aprovadas. "
                        "Para coordenador: retorna o mesmo conjunto de métricas, porém um bloco "
                        "por curso coordenado (incluindo lista detalhada de submissões), via campo "
                        "'cursos'. O formato da resposta varia conforme a role do usuário autenticado."
                    ),
                    "responses": {
                        "200": {
                            "description": "Dados do dashboard (formato depende da role: admin ou coordenador)",
                            "content": {"application/json": {"schema": {
                                "oneOf": [
                                    {"$ref": "#/components/schemas/DashboardAdminResponse"},
                                    {"$ref": "#/components/schemas/DashboardCoordenadorResponse"}
                                ]
                            }}}
                        },
                        "403": {"description": "Sem permissão",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/relatorios/dashboard-aluno": {
                "get": {
                    "tags": ["Relatórios"],
                    "summary": "Dashboard individual do aluno",
                    "description": (
                        "Retorna o progresso do aluno autenticado no curso em que está matriculado: "
                        "horas aprovadas e percentual de conclusão geral, horas aprovadas por área "
                        "(com limite e percentual de cada regra) e contagem de solicitações por status. "
                        "Requer que o aluno esteja vinculado a um curso."
                    ),
                    "responses": {
                        "200": {
                            "description": "Dados do dashboard do aluno",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/DashboardAlunoResponse"}}}
                        },
                        "403": {"description": "Sem permissão (apenas aluno)",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Aluno sem curso vinculado",
                                 "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            }
        }
    }
    return jsonify(spec)
