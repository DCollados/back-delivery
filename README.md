BACKEND DELIVERY

API Rest para delivery Feita com Python e FastAPI

Fluxo FastAPI sobe pelo main e carrega todas a dependencias necessarias (rotas, banco), alembic gera a versão do banco Autenticação feita com JWT e Oauth, usuarios manda os dados a api valida com Pydantic, verifica se já existe no banco, se existir gera um jwt assina com os termos dentro do key.env banco de dados criado com SQLalchemy e alembic detecta mudança nos models, gera migrations e mantem o banco versionado

Facil de escalar e totalmente protegido

tecnologias usadas 

Python 

FastAPI 

SQLAlchemy 

Alembic 

Pydantic 

JWT para autenticação

Como rodar -> 1. Clone o repositório

git clone https://github.com/DCollados/backend-delivery.git

cd backend-delivery

pip install -r requirements.txt

Crie as migrations

alembic revision --autogenerate -m "mensagem da migration"

alembic upgrade head

Para rodar uvicorn main:app --reload
