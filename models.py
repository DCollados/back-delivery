from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import declarative_base, relationship

db = create_engine("sqlite:///banco.db") # conexão com o banco de dados

Base = declarative_base() # classe base para os modelos do banco de dados

class Usuario(Base): # classes/tabelas do banco
    __tablename__ = "usuarios" # nome da tabela no banco de dados

    id = Column('id', Integer, primary_key=True, autoincrement=True) # autoincrement e para criar o proximo usuario sem ter que informar
    nome = Column('nome', String, index=True)
    email = Column('email', String, unique=True, index=True)
    senha = Column('senha', String)
    ativo = Column('ativo', Boolean, default=True)
    admin = Column('admin', Boolean, default=False) # se eu não disser se ele é admin ou não, por padrão ele não é que usa o default

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column('status', String) 
    usuario = Column('usuario', ForeignKey('usuarios.id')) # chave estrangeira que referencia o id da tabela usuarios
    preco = Column('preco', Float)
    itens = relationship("ItemPedido", cascade="all, delete") # está conectando as 2 tabelas, quando deletar um pedido cascadea todos itens relacionado ao pedido

    def __init__(self, usuario, status='PENDENTE', preco=0.0):
        self.status = status
        self.usuario = usuario
        self.preco = preco

    def calcular_preco(self):
       self.preco = sum(item.preco_unitario * item.quantidade for item in self.itens)

class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido = Column('pedido', ForeignKey('pedidos.id'))
    sabor = Column('sabor', String)
    tamanho = Column('tamanho', String)
    quantidade = Column('quantidade', Integer)
    preco_unitario = Column('preco_unitario', Float)

    def __init__(self, pedido, sabor, tamanho, quantidade, preco_unitario):
        self.pedido = pedido
        self.sabor = sabor
        self.tamanho = tamanho
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario


# criar migration: alembic revision --autogenerate -m "Add itens no pedido"
# executar migration: alembic upgrade head