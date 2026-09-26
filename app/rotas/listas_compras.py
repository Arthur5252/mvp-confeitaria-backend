from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.banco_dados import obter_sessao
from app.esquemas import (
    ItemListaComprasAtualizar,
    ItemListaComprasCriar,
    ItemListaComprasSaida,
    ListaComprasAtualizar,
    ListaComprasCriar,
    ListaComprasSaida,
)
from app.modelos import ItemListaCompras, ListaCompras
from app.seguranca import obter_usuario_atual

roteador = APIRouter(
    prefix="/listas-compras",
    tags=["listas de compras"],
    dependencies=[Depends(obter_usuario_atual)],
)


@roteador.get("", response_model=list[ListaComprasSaida])
def listar_listas_compras(sessao: Session = Depends(obter_sessao)):
    return sessao.query(ListaCompras).order_by(ListaCompras.criado_em.desc()).all()


@roteador.post("", response_model=ListaComprasSaida, status_code=201)
def criar_lista_compras(
    dados: ListaComprasCriar, sessao: Session = Depends(obter_sessao)
):
    lista = ListaCompras(nome=dados.nome)
    sessao.add(lista)
    sessao.commit()
    sessao.refresh(lista)
    return lista


@roteador.get("/{lista_id}", response_model=ListaComprasSaida)
def obter_lista_compras(lista_id: int, sessao: Session = Depends(obter_sessao)):
    lista = sessao.get(ListaCompras, lista_id)
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    return lista


@roteador.put("/{lista_id}", response_model=ListaComprasSaida)
def atualizar_lista_compras(
    lista_id: int,
    dados: ListaComprasAtualizar,
    sessao: Session = Depends(obter_sessao),
):
    lista = sessao.get(ListaCompras, lista_id)
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(lista, campo, valor)
    sessao.commit()
    sessao.refresh(lista)
    return lista


@roteador.delete("/{lista_id}", status_code=204)
def remover_lista_compras(lista_id: int, sessao: Session = Depends(obter_sessao)):
    lista = sessao.get(ListaCompras, lista_id)
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    sessao.delete(lista)
    sessao.commit()


@roteador.post("/{lista_id}/itens", response_model=ItemListaComprasSaida, status_code=201)
def adicionar_item(
    lista_id: int,
    dados: ItemListaComprasCriar,
    sessao: Session = Depends(obter_sessao),
):
    lista = sessao.get(ListaCompras, lista_id)
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    if not dados.produto_id and not dados.nome_livre:
        raise HTTPException(
            status_code=422,
            detail="Informe produto_id ou nome_livre para o item",
        )
    item = ItemListaCompras(lista_id=lista_id, **dados.model_dump())
    sessao.add(item)
    sessao.commit()
    sessao.refresh(item)
    return item


@roteador.patch("/{lista_id}/itens/{item_id}", response_model=ItemListaComprasSaida)
def atualizar_item(
    lista_id: int,
    item_id: int,
    dados: ItemListaComprasAtualizar,
    sessao: Session = Depends(obter_sessao),
):
    item = sessao.get(ItemListaCompras, item_id)
    if not item or item.lista_id != lista_id:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    campos = dados.model_dump(exclude_unset=True)
    marcado = campos.pop("marcado", None)
    for campo, valor in campos.items():
        setattr(item, campo, valor)
    if marcado is not None:
        item.marcado_em = datetime.utcnow() if marcado else None

    sessao.commit()
    sessao.refresh(item)
    return item


@roteador.delete("/{lista_id}/itens/{item_id}", status_code=204)
def remover_item(lista_id: int, item_id: int, sessao: Session = Depends(obter_sessao)):
    item = sessao.get(ItemListaCompras, item_id)
    if not item or item.lista_id != lista_id:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    sessao.delete(item)
    sessao.commit()
