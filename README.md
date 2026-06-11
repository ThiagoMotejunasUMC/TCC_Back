# SGE — Backend

API REST do Sistema de Gerenciamento de Estoque para lojas varejistas de eletrônicos, construída com Python 3 e FastAPI.

## Objetivo

O SGE permite o controle granular de estoque com rastreabilidade individual por número de série, controle de espaços físicos com cálculo de ocupação, notificações automáticas de estoque mínimo e controle de acesso por cargo (operador, diretor e administrador).

---

## Tecnologias

| Tecnologia | Versão | Finalidade |
|---|---|---|
| Python | 3.14 | Linguagem principal |
| FastAPI | 0.135.3 | Framework da API REST |
| SQLAlchemy | 2.0.49 | ORM e gerenciamento de sessões |
| PostgreSQL | 15+ | Banco de dados relacional |
| psycopg2-binary | 2.9.11 | Driver de conexão PostgreSQL |
| Pydantic + pydantic-settings | 2.12.5 | Validação de dados e variáveis de ambiente |
| PyJWT | 2.13.0 | Geração e validação de tokens JWT |
| bcrypt + passlib | 4.0.1 / 1.7.4 | Hash seguro de senhas |
| python-multipart | 0.0.24 | Upload de arquivos (exportação CSV) |
| httpx | 0.28.1 | Requisições HTTP assíncronas (ViaCEP) |
| uvicorn | 0.44.0 | Servidor ASGI |
| pytest + pytest-mock + pytest-cov | 9.0.3 | Testes unitários |

---

## Pré-requisitos

- Python 3.12 ou superior
- PostgreSQL rodando localmente
- pip e venv disponíveis

---

## Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/ThiagoMotejunasUMC/TCC_Back.git
cd TCC_Back
```

### 2. Crie e ative o ambiente virtual

```bash
# Criar
python -m venv venv

# Ativar — Windows
venv\Scripts\activate

# Ativar — Mac/Linux
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Crie o banco de dados

No pgAdmin ou psql:

```sql
CREATE DATABASE sge;
```

### 5. Configure as variáveis de ambiente

Crie o arquivo `.env` dentro do diretório `app/` com o seguinte conteúdo:

```env
DATABASE_URL=postgresql://postgres:suasenha@localhost:5432/sge
SECRET_KEY=sua_chave_secreta_longa_e_aleatoria_minimo_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
EMAIL_FROM=seuemail@gmail.com
EMAIL_PASSWORD=senha_de_app_16_caracteres
FRONTEND_URL=http://localhost:5173
```

#### Variáveis obrigatórias

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | String de conexão com o PostgreSQL | — |
| `SECRET_KEY` | Chave para assinatura dos tokens JWT (mín. 32 chars) | — |
| `ALGORITHM` | Algoritmo de assinatura JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token em minutos | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token em dias | `7` |
| `FRONTEND_URL` | Origem permitida pelo CORS | `http://localhost:5173` |

#### Variáveis de e-mail (opcionais)

| Variável | Descrição |
|---|---|
| `EMAIL_FROM` | E-mail remetente dos alertas e recuperação de senha |
| `EMAIL_PASSWORD` | Senha de app do Google (16 chars) — **não use a senha normal da conta** |

> **Como gerar a senha de app do Google:** acesse myaccount.google.com → Segurança → Senhas de app. A verificação em duas etapas deve estar ativada.

---

## Inicialização

```bash
uvicorn app.main:app --reload
```

As tabelas são criadas automaticamente no banco na primeira execução.

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Criação do usuário administrador

Com o servidor rodando, gere o hash da senha e execute o SQL no banco:

```bash
# Gerar hash da senha
python -c "
import bcrypt
senha = 'Admin@123'
hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(hash)
"
```

```sql
INSERT INTO usuarios (nome, email, senha, cargo, ativo, primeiro_acesso, criado_em)
VALUES ('Administrador', 'admin@sge.com', 'COLE_O_HASH_AQUI', 'admin', true, false, NOW());
```

---

## Testes

```bash
# Todos os testes
pytest tests/ -v

# Com relatório de cobertura
pytest tests/ -v --cov=app --cov-report=term-missing
```

Resultado esperado: **206 testes, 85% de cobertura**.

---

## Estrutura de diretórios

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py         # Variáveis de ambiente (Pydantic Settings)
│   │   ├── security.py       # JWT, bcrypt e validação de senha
│   │   └── email.py          # Envio de e-mails via Gmail SMTP
│   │
│   ├── models/               # Entidades do banco (SQLAlchemy)
│   ├── schemas/              # Contratos de entrada e saída (Pydantic)
│   ├── crud/                 # Operações de acesso ao banco por entidade
│   ├── routers/              # Endpoints da API REST por módulo
│   │
│   ├── database.py           # Conexão e sessão com o PostgreSQL
│   ├── dependencies.py       # Injeção de dependências (auth, RBAC)
│   └── main.py               # Instância do FastAPI, CORS e registro de routers
│
├── tests/                    # Testes unitários (pytest)
├── conftest.py               # Configuração dos testes
├── pytest.ini                # Opções de execução do pytest
└── requirements.txt          # Dependências Python
```

---

## Endpoints principais

| Prefixo | Módulo |
|---|---|
| `/auth` | Login, refresh token, primeiro acesso, recuperação de senha |
| `/usuarios` | Gerenciamento de usuários |
| `/categorias` | Categorias de produtos |
| `/produtos` | Produtos |
| `/itens` | Itens físicos individuais |
| `/fornecedores` | Fornecedores |
| `/movimentacoes` | Entradas e saídas de estoque |
| `/espacos` | Espaços físicos de armazenamento |
| `/notificacoes` | Alertas de estoque mínimo |
| `/viacep/{cep}` | Consulta de endereço por CEP |

---

## Controle de acesso

| Cargo | Permissões |
|---|---|
| **Operador** | Criar e editar registros, registrar movimentações |
| **Diretor** | Tudo do operador + desativar registros + exportar CSV |
| **Administrador** | Acesso irrestrito + gerenciar usuários |

---

## Licença

Projeto acadêmico — Universidade de Mogi das Cruzes (UMC), 2026.
