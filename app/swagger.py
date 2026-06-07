"""
Configuração do Swagger/OpenAPI 3.0 para o SIGAC API.
Utiliza flask-swagger-ui + spec manual em JSON.
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
                "submissões de atividades complementares e dashboard."
            ),
            "version": "1.0.0"
        },
        "servers": [{"url": "/", "description": "Servidor local"}],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
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
                        "success": {"type": "boolean"},
                        "message": {"type": "string"},
                        "access_token": {"type": "string"}
                    }
                },
                "CadastrarUsuarioRequest": {
                    "type": "object",
                    "required": ["nome", "email", "senha", "tipo", "id_curso"],
                    "properties": {
                        "nome": {"type": "string", "example": "João Silva"},
                        "email": {"type": "string", "format": "email"},
                        "senha": {"type": "string"},
                        "tipo": {"type": "string", "enum": ["aluno", "coordenador"]},
                        "matricula": {"type": "string", "example": "20241001"},
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
                "CursoRequest": {
                    "type": "object",
                    "required": ["nome", "carga_horaria"],
                    "properties": {
                        "nome": {"type": "string", "example": "Sistemas de Informação"},
                        "carga_horaria": {"type": "integer", "example": 200}
                    }
                },
                "RegraRequest": {
                    "type": "object",
                    "required": ["area", "descricao", "limite_horas", "requisito", "exige_certificado"],
                    "properties": {
                        "area": {"type": "string", "example": "Extensão"},
                        "descricao": {"type": "string", "example": "Participação em eventos de extensão"},
                        "limite_horas": {"type": "integer", "example": 60},
                        "requisito": {"type": "string", "example": "Certificado de participação"},
                        "exige_certificado": {"type": "boolean", "example": True},
                        "id_curso": {"type": "integer", "nullable": True, "example": 1}
                    }
                },
                "ValidarSubmissaoRequest": {
                    "type": "object",
                    "required": ["status"],
                    "properties": {
                        "status": {"type": "string", "enum": ["aprovado", "recusado"]},
                        "motivo_rejeicao": {"type": "string", "example": "Certificado ilegível"},
                        "carga_horaria_aprovada": {"type": "integer", "example": 40}
                    }
                }
            }
        },
        "security": [{"BearerAuth": []}],
        "paths": {
            # ── AUTH ──────────────────────────────────────────
            "/api/auth/login": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Login de usuário",
                    "security": [],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginRequest"}}}
                    },
                    "responses": {
                        "200": {"description": "Login bem-sucedido",
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginResponse"}}}},
                        "401": {"description": "Credenciais inválidas"},
                        "404": {"description": "Usuário não encontrado"}
                    }
                }
            },
            # ── USUÁRIOS ──────────────────────────────────────
            "/api/usuarios/cadastrar": {
                "post": {
                    "tags": ["Usuários"],
                    "summary": "Cadastrar aluno ou coordenador",
                    "description": "Admin pode cadastrar alunos e coordenadores. Coordenador só pode cadastrar alunos.",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CadastrarUsuarioRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Usuário cadastrado com sucesso"},
                        "400": {"description": "Dados inválidos"},
                        "403": {"description": "Sem permissão"},
                        "404": {"description": "Curso não encontrado"},
                        "409": {"description": "E-mail já cadastrado"}
                    }
                }
            },
            "/api/usuarios/vincular-curso": {
                "post": {
                    "tags": ["Usuários"],
                    "summary": "Vincular usuário a curso adicional",
                    "description": "Permite que um aluno ou coordenador já cadastrado seja vinculado a mais de um curso. Apenas admin.",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/VincularCursoRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Vínculo criado com sucesso"},
                        "400": {"description": "Dados inválidos"},
                        "403": {"description": "Sem permissão"},
                        "404": {"description": "Usuário ou curso não encontrado"},
                        "409": {"description": "Vínculo já existente"}
                    }
                }
            },
            "/api/usuarios/listar_alunos": {
                "get": {
                    "tags": ["Usuários"],
                    "summary": "Listar alunos com progresso",
                    "description": "Retorna alunos com horas concluídas e progresso por curso. Admin e coordenador.",
                    "responses": {
                        "200": {
                            "description": "Lista de alunos",
                            "content": {"application/json": {"schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "alunos": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "nome": {"type": "string"},
                                                "matricula": {"type": "string"},
                                                "curso": {"type": "string"},
                                                "horas_concluidas": {"type": "integer"},
                                                "total_horas": {"type": "integer"},
                                                "progresso": {"type": "number"}
                                            }
                                        }
                                    }
                                }
                            }}}
                        },
                        "403": {"description": "Sem permissão"}
                    }
                }
            },
            "/api/usuarios/listar_coordenadores": {
                "get": {
                    "tags": ["Usuários"],
                    "summary": "Listar coordenadores (apenas admin)",
                    "responses": {
                        "200": {"description": "Lista de coordenadores"},
                        "403": {"description": "Sem permissão"}
                    }
                }
            },
            # ── CURSOS ────────────────────────────────────────
            "/api/cursos/cadastrar": {
                "post": {
                    "tags": ["Cursos"],
                    "summary": "Cadastrar curso (apenas admin)",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CursoRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Curso cadastrado"},
                        "403": {"description": "Sem permissão"}
                    }
                }
            },
            "/api/cursos/listar": {
                "get": {
                    "tags": ["Cursos"],
                    "summary": "Listar todos os cursos",
                    "responses": {
                        "200": {"description": "Lista de cursos"}
                    }
                }
            },
            # ── REGRAS ────────────────────────────────────────
            "/api/regras/listar": {
                "get": {
                    "tags": ["Regras"],
                    "summary": "Listar regras de atividades",
                    "parameters": [
                        {
                            "name": "curso_id",
                            "in": "query",
                            "schema": {"type": "integer"},
                            "description": "Filtrar por curso"
                        }
                    ],
                    "responses": {
                        "200": {"description": "Lista de regras"}
                    }
                }
            },
            "/api/regras/criar": {
                "post": {
                    "tags": ["Regras"],
                    "summary": "Criar regra de atividade (apenas admin)",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RegraRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Regra criada"},
                        "403": {"description": "Sem permissão"}
                    }
                }
            },
            "/api/regras/atualizar/{id_regra}": {
                "put": {
                    "tags": ["Regras"],
                    "summary": "Atualizar regra (apenas admin)",
                    "parameters": [{"name": "id_regra", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RegraRequest"}}}
                    },
                    "responses": {
                        "200": {"description": "Regra atualizada"},
                        "403": {"description": "Sem permissão"},
                        "404": {"description": "Regra não encontrada"}
                    }
                }
            },
            "/api/regras/excluir/{id_regra}": {
                "delete": {
                    "tags": ["Regras"],
                    "summary": "Excluir regra (apenas admin)",
                    "parameters": [{"name": "id_regra", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {
                        "200": {"description": "Regra excluída"},
                        "403": {"description": "Sem permissão"},
                        "404": {"description": "Regra não encontrada"}
                    }
                }
            },
            # ── SUBMISSÕES ────────────────────────────────────
            "/api/submissoes/criar": {
                "post": {
                    "tags": ["Submissões"],
                    "summary": "Criar submissão de atividade complementar (aluno)",
                    "description": "Valida regras de horas antes de criar. Use /api/certificados/upload para envio com arquivo.",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {
                            "type": "object",
                            "required": ["titulo", "id_curso", "id_regra_atividade", "carga_horaria_solicitada", "nome_arquivo", "url_arquivo"],
                            "properties": {
                                "titulo": {"type": "string"},
                                "id_curso": {"type": "integer"},
                                "id_regra_atividade": {"type": "integer"},
                                "carga_horaria_solicitada": {"type": "integer"},
                                "nome_arquivo": {"type": "string"},
                                "url_arquivo": {"type": "string"}
                            }
                        }}}
                    },
                    "responses": {
                        "201": {"description": "Submissão criada"},
                        "400": {"description": "Dados inválidos"},
                        "403": {"description": "Aluno não matriculado no curso"},
                        "422": {"description": "Limite de horas atingido"}
                    }
                }
            },
            "/api/submissoes/listar": {
                "get": {
                    "tags": ["Submissões"],
                    "summary": "Listar submissões",
                    "description": "Aluno vê as próprias, coordenador vê as do seu curso, admin vê todas.",
                    "parameters": [
                        {
                            "name": "status",
                            "in": "query",
                            "schema": {"type": "string", "enum": ["pendente", "aprovado", "recusado"]},
                            "description": "Filtrar por status"
                        }
                    ],
                    "responses": {
                        "200": {"description": "Lista de submissões"}
                    }
                }
            },
            "/api/submissoes/validar/{id_submissao}": {
                "put": {
                    "tags": ["Submissões"],
                    "summary": "Validar submissão (coordenador ou admin)",
                    "parameters": [{"name": "id_submissao", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidarSubmissaoRequest"}}}
                    },
                    "responses": {
                        "200": {"description": "Submissão validada"},
                        "400": {"description": "Status inválido ou submissão não pendente"},
                        "403": {"description": "Sem permissão"},
                        "404": {"description": "Submissão não encontrada"}
                    }
                }
            },
            # ── CERTIFICADOS ──────────────────────────────────
            "/api/certificados/upload": {
                "post": {
                    "tags": ["Certificados"],
                    "summary": "Upload de certificado com criação de submissão (aluno)",
                    "description": "Envia um arquivo (PDF/PNG/JPG) junto com os dados da atividade. Valida regras de horas.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["file", "titulo", "id_curso", "id_regra_atividade", "carga_horaria_solicitada"],
                                    "properties": {
                                        "file": {"type": "string", "format": "binary"},
                                        "titulo": {"type": "string"},
                                        "id_curso": {"type": "integer"},
                                        "id_regra_atividade": {"type": "integer"},
                                        "carga_horaria_solicitada": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Certificado enviado e submissão criada"},
                        "400": {"description": "Dados inválidos ou formato não permitido"},
                        "403": {"description": "Aluno não matriculado no curso"},
                        "422": {"description": "Limite de horas atingido"}
                    }
                }
            },
            # ── RELATÓRIOS / DASHBOARD ─────────────────────────
            "/api/relatorios/dashboard": {
                "get": {
                    "tags": ["Relatórios"],
                    "summary": "Dashboard com métricas gerais (admin e coordenador)",
                    "description": "Retorna métricas principais, evolução mensal de horas, distribuição por área e top cursos.",
                    "responses": {
                        "200": {
                            "description": "Dados do dashboard",
                            "content": {"application/json": {"schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "metricas": {
                                        "type": "object",
                                        "properties": {
                                            "total_alunos": {"type": "integer"},
                                            "total_horas_aprovadas": {"type": "integer"},
                                            "total_solicitacoes": {"type": "integer"},
                                            "total_aprovadas": {"type": "integer"},
                                            "total_pendentes": {"type": "integer"},
                                            "total_recusadas": {"type": "integer"},
                                            "taxa_aprovacao": {"type": "number"}
                                        }
                                    },
                                    "evolucao_mensal": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "mes": {"type": "string"},
                                                "horas": {"type": "integer"}
                                            }
                                        }
                                    },
                                    "distribuicao_atividades": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "area": {"type": "string"},
                                                "quantidade": {"type": "integer"}
                                            }
                                        }
                                    },
                                    "top_cursos": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "curso": {"type": "string"},
                                                "horas": {"type": "integer"}
                                            }
                                        }
                                    }
                                }
                            }}}
                        },
                        "403": {"description": "Sem permissão"}
                    }
                }
            }
        }
    }
    return jsonify(spec)
