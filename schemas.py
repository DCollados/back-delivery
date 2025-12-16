from pydantic import BaseModel 
from typing import Optional, List

# serve para definir o formato dos dados que serão enviados e recebidos pela API

class Usuarioschema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool] = True
    admin: Optional[bool] = False

    class Config:
        from_atributes = True # interpretado como uma classe que vai se transformar em sql

class PedidoSchema(BaseModel):
    usuario: int

    class Config:
        from_atributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_atributes = True   

class ItemPedidoSchema(BaseModel):
    quantidade: int
    preco_unitario: float
    sabor: str
    tamanho: str

    class Config:
        from_atributes = True

class ResponsePedidoSchema(BaseModel):
    id: int
    status: str
    preco: float
    itens: List[ItemPedidoSchema] # referencia a outra classe, itens da outra classe

    class Config:
        from_atributes = True