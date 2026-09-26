from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.banco_dados import obter_sessao
from app.esquemas import FornecedorAtualizar, FornecedorCriar, FornecedorSaida
from app.modelos import Fornecedor
from app.seguranca import obter_usuario_atual

roteador = APIRouter(
    prefix="/fornecedores",
    tags=["fornecedores"],
    dependencies=[Depends(obter_usuario_atual)],
)


@roteador.get("", response_model=list[FornecedorSaida])
def listar_fornecedores(sessao: Session = Depends(obter_sessao)):
    return sessao.query(Fornecedor).order_by(func.lower(Fornecedor.nome)).all()


@roteador.post("", response_model=FornecedorSaida, status_code=201)
def criar_fornecedor(dados: FornecedorCriar, sessao: Session = Depends(obter_sessao)):
    fornecedor = Fornecedor(**dados.model_dump())
    sessao.add(fornecedor)
    sessao.commit()
    sessao.refresh(fornecedor)
    return fornecedor


@roteador.get("/{fornecedor_id}", response_model=FornecedorSaida)
def obter_fornecedor(fornecedor_id: int, sessao: Session = Depends(obter_sessao)):
    fornecedor = sessao.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return fornecedor


@roteador.put("/{fornecedor_id}", response_model=FornecedorSaida)
def atualizar_fornecedor(
    fornecedor_id: int,
    dados: FornecedorAtualizar,
    sessao: Session = Depends(obter_sessao),
):
    fornecedor = sessao.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    for campo, valor in dados.model_dump().items():
        setattr(fornecedor, campo, valor)
    sessao.commit()
    sessao.refresh(fornecedor)
    return fornecedor


@roteador.delete("/{fornecedor_id}", status_code=204)
def remover_fornecedor(fornecedor_id: int, sessao: Session = Depends(obter_sessao)):
    fornecedor = sessao.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    sessao.delete(fornecedor)
    sessao.commit()
