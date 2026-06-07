# SIGAC — Backend

API RESTful do **Sistema de Gerenciamento de Atividades Complementares**, desenvolvida com Flask + SQLAlchemy + MySQL.

---

## Tecnologias

| Tecnologia | Versão |
|---|---|
| Python | 3.11+ |
| Flask | 3.0.3 |
| Flask-JWT-Extended | 4.6.0 |
| Flask-SQLAlchemy | 3.1.1 |
| Flask-Migrate | 4.0.7 |
| flask-swagger-ui | 4.11.1 |
| PyMySQL | 1.1.1 |

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/SIGAC-Back.git
cd SIGAC-Back

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

### Variáveis de ambiente (`.env`)

```env
MYSQL_URI=mysql+pymysql://usuario:senha@localhost:3306/sigac
JWT_SECRET=sua_chave_secreta_aqui
```

---

## Executando

```bash
# Aplicar migrações
flask db upgrade

# Criar admin inicial
python criar_admin.py

# Rodar em desenvolvimento
python server.py

# Rodar em produção
gunicorn "app:create_app()" --bind 0.0.0.0:5000
```

---

## Documentação — Swagger UI

Com o servidor rodando, acesse:

```
http://localhost:5000/api/docs
```

A spec OpenAPI 3.0 está disponível em `/api/swagger.json`.

---

## Estrutura do Projeto

```
SIGAC-Back/
├── app/
│   ├── __init__.py          # Factory da aplicação Flask
│   ├── swagger.py           # Configuração do Swagger/OpenAPI
│   ├── controllers/         # Lógica de negócio
│   │   ├── auth_controller.py
│   │   ├── usuario_controller.py
│   │   ├── curso_controller.py
│   │   ├── regra_controller.py
│   │   ├── submissao_controller.py
│   │   ├── certificado_controller.py
│   │   └── relatorio_controller.py
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── usuario.py
│   │   ├── curso.py
│   │   ├── aluno_curso.py
│   │   ├── coordenador_curso.py
│   │   ├── regra_atividade.py
│   │   ├── atividade_complementar.py
│   │   ├── submissao.py
│   │   └── certificado.py
│   ├── routes/              # Definição de endpoints
│   ├── middlewares/         # Autenticação JWT / verificação de role
│   └── extensions/          # SQLAlchemy, Migrate, JWT
├── migrations/              # Migrações Alembic
├── certificados_uploaded/   # Arquivos enviados pelos alunos
├── requirements.txt
├── server.py
└── criar_admin.py
```

---

## Endpoints Principais

### Auth
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/login` | Login (retorna JWT) |

### Usuários
| Método | Rota | Roles | Descrição |
|---|---|---|---|
| POST | `/api/usuarios/cadastrar` | admin, coordenador | Cadastra aluno ou coordenador |
| POST | `/api/usuarios/vincular-curso` | admin | Vincula usuário a curso adicional |
| GET | `/api/usuarios/listar_alunos` | admin, coordenador | Lista alunos com progresso |
| GET | `/api/usuarios/listar_coordenadores` | admin | Lista coordenadores |

### Cursos
| Método | Rota | Roles | Descrição |
|---|---|---|---|
| POST | `/api/cursos/cadastrar` | admin | Cria curso |
| GET | `/api/cursos/listar` | todos | Lista cursos |

### Regras de Atividade
| Método | Rota | Roles | Descrição |
|---|---|---|---|
| GET | `/api/regras/listar?curso_id=` | todos | Lista regras (filtro por curso) |
| POST | `/api/regras/criar` | admin | Cria regra |
| PUT | `/api/regras/atualizar/<id>` | admin | Atualiza regra |
| DELETE | `/api/regras/excluir/<id>` | admin | Exclui regra |

### Submissões
| Método | Rota | Roles | Descrição |
|---|---|---|---|
| POST | `/api/submissoes/criar` | aluno | Cria submissão (JSON) |
| GET | `/api/submissoes/listar?status=` | todos | Lista submissões filtradas |
| PUT | `/api/submissoes/validar/<id>` | coordenador, admin | Aprova ou recusa |

### Certificados
| Método | Rota | Roles | Descrição |
|---|---|---|---|
| POST | `/api/certificados/upload` | aluno | Upload de arquivo + criação de submissão |

### Relatórios
| Método | Rota | Roles | Descrição |
|---|---|---|---|
| GET | `/api/relatorios/dashboard` | admin, coordenador | Métricas, evolução mensal, distribuição |

---

## Regras de Negócio

- **Múltiplos cursos**: alunos e coordenadores podem ser vinculados a mais de um curso via `/api/usuarios/vincular-curso`.
- **Limite de horas por regra**: ao criar ou aprovar uma submissão, o sistema verifica o total já aprovado para aquela regra/curso/aluno e rejeita se ultrapassar o `limite_horas` da regra.
- **Validação de arquivo**: apenas PDF, PNG e JPG são aceitos no upload de certificados.
- **Motivo obrigatório**: ao recusar uma submissão, `motivo_rejeicao` é obrigatório.
- **Coordenador validando**: coordenador só pode validar submissões de cursos que coordena.

---

## Autenticação

Todas as rotas (exceto `/api/auth/login`) exigem o header:

```
Authorization: Bearer <access_token>
```

O token JWT contém as claims `role` (aluno | coordenador | admin) e `nome`.

---

## Papéis (Roles)

| Role | Pode fazer |
|---|---|
| `admin` | Tudo |
| `coordenador` | Cadastrar alunos, listar alunos, validar submissões dos seus cursos, ver dashboard |
| `aluno` | Submeter atividades, fazer upload de certificados, ver suas próprias submissões |
