from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.banco_dados import obter_sessao
from app.esquemas import ProdutoCriar, ProdutoSaida
from app.modelos import Produto
from app.seguranca import obter_usuario_atual

roteador = APIRouter(
    prefix="/produtos",
    tags=["produtos"],
    dependencies=[Depends(obter_usuario_atual)],
)


@roteador.get("", response_model=list[ProdutoSaida])
def listar_produtos(
    busca: str | None = Query(default=None), sessao: Session = Depends(obter_sessao)
):
    consulta = sessao.query(Produto)
    if busca:
        consulta = consulta.filter(Produto.nome.ilike(f"%{busca}%"))
    # Ordena ignorando maiúsculas/minúsculas — o SQLite usa collation binária
    # por padrão, o que colocaria "PRODUTO..." antes de "leite" mesmo estando
    # fora de ordem alfabética real, confundindo o seletor do painel.
    return consulta.order_by(func.lower(Produto.nome)).all()


@roteador.post("", response_model=ProdutoSaida, status_code=201)
def criar_produto(dados: ProdutoCriar, sessao: Session = Depends(obter_sessao)):
    produto = Produto(**dados.model_dump())
    sessao.add(produto)
    sessao.commit()
    sessao.refresh(produto)
    return produto


@roteador.get("/{produto_id}", response_model=ProdutoSaida)
def obter_produto(produto_id: int, sessao: Session = Depends(obter_sessao)):
    produto = sessao.get(Produto, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@roteador.delete("/{produto_id}", status_code=204)
def remover_produto(produto_id: int, sessao: Session = Depends(obter_sessao)):
    produto = sessao.get(Produto, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    sessao.delete(produto)
    sessao.commit()
