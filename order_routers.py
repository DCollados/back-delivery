from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from models import Pedido, Usuario, ItemPedido
from auth_routers import criar_token
from typing import List

# a rota que está e dominio.com/pedidos/lista ai retorna o que deve ser retornado

order_router = APIRouter(
    prefix="/pedidos", 
    tags=["pedidos"],
    dependencies=[Depends(verificar_token)] # todas as rotas precisam que seja passada um usuario autenticado
    ) # sempre usar prefixo para não ter conflito

@order_router.get("/") # endpoint vazio para o prefixo pedidos, retorna quando entra no /pedidos
async def pedidos():
    return {"mensagem": "Você acessou a rota de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema = PedidoSchema, session: Session = Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": "Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}

@order_router.get("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    pedido.status = "CANCELADO"
    session.commit()
    return {
        "mensagem": "Pedido numero: {pedido.id} cancelado com sucesso", # evita o lazyloaded
        "pedido": pedido
        }

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        return HTTPException(status_code=401, detail="Você nao tem permissão para acessar essa rota")
    else:
        pedidos = session.query(Pedido).all()
        return {
            "pedidos": pedidos
            }
    
@order_router.post("/pedido/adicionar_item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, item_pedido_schema: ItemPedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    item_pedido = ItemPedido(
        quantidade=item_pedido_schema.quantidade,
        preco_unitario=item_pedido_schema.preco_unitario,
        sabor=item_pedido_schema.sabor,
        tamanho=item_pedido_schema.tamanho,
        pedido_id=pedido.id
    )
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item adicionado com sucesso ao pedido {pedido.id}",
        "pedido": pedido,
        "preco_atualizado": pedido.preco
        }

@order_router.post("/pedido/remover_item/{id_item_pedido}")
async def adicionar_item_pedido(id_item_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item removido com sucesso ao pedido {pedido.id}",
        "pedido": item_pedido.pedido
        }

@order_router.get("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    pedido.status = "FINALIZADO"
    session.commit()
    return {
        "mensagem": "Pedido numero: {pedido.id} finalizado com sucesso", # evita o lazyloaded
        "pedido": pedido
        }

@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    return {
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido

    }

@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema]) # retorna a lista de um schema
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    return pedidos