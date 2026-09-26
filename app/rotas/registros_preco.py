from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.banco_dados import obter_sessao
from app.esquemas import (
    RegistroPrecoAtualizar,
    RegistroPrecoCriar,
    RegistroPrecoSaida,
)
from app.modelos import RegistroPreco
from app.seguranca import obter_usuario_atual

roteador = APIRouter(
    prefix="/registros-preco",
    tags=["registros de preço"],
    dependencies=[Depends(obter_usuario_atual)],
)


@roteador.get("", response_model=list[RegistroPrecoSaida])
def listar_registros_preco(
    produto_id: int | None = Query(default=None),
    fornecedor_id: int | None = Query(default=None),
    sessao: Session = Depends(obter_sessao),
):
    consulta = sessao.query(RegistroPreco)
    if produto_id is not None:
        consulta = consulta.filter(RegistroPreco.produto_id == produto_id)
    if fornecedor_id is not None:
        consulta = consulta.filter(RegistroPreco.fornecedor_id == fornecedor_id)
    return consulta.order_by(RegistroPreco.capturado_em.desc()).all()


@roteador.post("", response_model=RegistroPrecoSaida, status_code=201)
def criar_registro_preco(
    dados: RegistroPrecoCriar, sessao: Session = Depends(obter_sessao)
):
    registro = RegistroPreco(**dados.model_dump())
    sessao.add(registro)
    sessao.commit()
    sessao.refresh(registro)
    return registro


@roteador.get("/{registro_id}", response_model=RegistroPrecoSaida)
def obter_registro_preco(registro_id: int, sessao: Session = Depends(obter_sessao)):
    registro = sessao.get(RegistroPreco, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de preço não encontrado")
    return registro


@roteador.put("/{registro_id}", response_model=RegistroPrecoSaida)
def atualizar_registro_preco(
    registro_id: int,
    dados: RegistroPrecoAtualizar,
    sessao: Session = Depends(obter_sessao),
):
    registro = sessao.get(RegistroPreco, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de preço não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(registro, campo, valor)
    sessao.commit()
    sessao.refresh(registro)
    return registro


@roteador.delete("/{registro_id}", status_code=204)
def remover_registro_preco(registro_id: int, sessao: Session = Depends(obter_sessao)):
    registro = sessao.get(RegistroPreco, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de preço não encontrado")
    sessao.delete(registro)
    sessao.commit()
