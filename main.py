from fastapi import FastAPI
from pydantic import BaseModel
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import os

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

SECRET_KEY = os.getenv("SECRET_KEY") # carrega a key do env
ALGORITHM = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACESS_TOKEN_EXPIRE_MINUTES")

app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form") # ele protege as rotas que precisam de autenticação

from auth_routers import auth_router
from order_routers import order_router

app.include_router(auth_router) # para incluir a rota no site, vai usar ele
app.include_router(order_router)

