from sqlalchemy.orm import sessionmaker, Session
from models import db, Usuario
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from main import SECRET_KEY, ALGORITHM, oauth2_schema

def pegar_sessao(): # instancia a session para a rota so for ativa quando tiver essa def
    try: # garantir que a sessão vai ser fechada
        Session = sessionmaker(bind=db) # serve para quando for realizar essa função no banco
        session = Session()
        yield session # retorna o valor mas não encerra a sessão
    finally:
        session.close() # fecha a sessão após o uso

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:    
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM) # parametros para decodificar o token
        id_usuario = int(dic_info("user_id"))  # se existe o id do usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso negado, verifique a validade do token") # caso o usuario forneca o token errado
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario: # esta tentando acessar com um usuario que não existe, apenas validação 
        raise HTTPException(status_code=401, detail="Acesso negado")
    return usuario