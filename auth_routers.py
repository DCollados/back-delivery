from fastapi import APIRouter, Depends, HTTPException
from models import Usuario, db
from sqlalchemy.orm import sessionmaker
from dependencies import pegar_sessao
from main import bcrypt_context, ALGORITHM, ACESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import Usuarioschema
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from dependencies import verificar_token
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(
    prefix="/auth", 
    tags=["auth"]
    ) # sempre usar prefixo para não ter conflito

def criar_token(id_usuario, duracao_token=None):
    if duracao_token is None:
        duracao_token = timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)

    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dict_info = {
        'user_id': str(id_usuario),
        'exp': data_expiracao
    }
    jwt_codificado = jwt.encode(dict_info, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_codificado

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario.email==email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario

@auth_router.get("/")
async def home():
    """ 
    Rota padrão de pedido, todas as rotas dos pedidos precisam de autenticação
    """
    return {"mensagem": "Você acessou a rota de autenticação"} 

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema = Usuarioschema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first() # verifica se já existe um usuario com esse email
    if usuario is not None: # se tiver, retorna é esse usuario
        return HTTPException(status_code=400, detail="Email já cadastrado")
    else: # se não tiver cria a conta do usuario
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha) # hash da senha para segurança
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": "Conta criada com sucesso {usuario_schema.email}"}
    
@auth_router.post("/login") # login - email e senha - token JWT normal
async def login(login_schema: Usuarioschema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    else:
        acess_token = criar_token(usuario.email)
        refresh_token = criar_token(usuario.email, duracao_token=timedelta(days=7)) # token de 7 dias
        return {
            "access_token": acess_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
            }

@auth_router.post("/login-form") # login pelo botão authorize do swagger
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    else:
        acess_token = criar_token(usuario.id) 
        return {
            "access_token": acess_token, # serve para apenas usuarios autenticados acessarem rotas protegidas
            "token_type": "bearer"
            }
    
@auth_router.get("/refresh_token")
async def usar_refresh_token(usuario: Usuario = Depends(verificar_token)): # quando quiser bloquear rota depends = verificar_token
    acess_token = criar_token(usuario.id)
    return {
            "access_token": acess_token,
            "token_type": "bearer"
            }