from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.banco_dados import obter_sessao
from app.esquemas import ItemComparacaoPreco, ItemDestaque, ItemHistoricoPreco
from app.modelos import Fornecedor, RegistroPreco
from app.seguranca import obter_usuario_atual

roteador = APIRouter(
    prefix="/painel", tags=["painel"], dependencies=[Depends(obter_usuario_atual)]
)


@roteador.get("/comparacao-precos", response_model=list[ItemComparacaoPreco])
def comparacao_precos(
    produto_id: int = Query(...), sessao: Session = Depends(obter_sessao)
):
    """Para um produto, mostra o preço mais recente de cada fornecedor —
    permite comparar onde está mais barato agora."""
    registros = (
        sessao.query(RegistroPreco)
        .filter(RegistroPreco.produto_id == produto_id)
        .order_by(RegistroPreco.capturado_em.desc())
        .all()
    )

    mais_recente_por_fornecedor: dict[int, RegistroPreco] = {}
    for registro in registros:
        if registro.fornecedor_id not in mais_recente_por_fornecedor:
            mais_recente_por_fornecedor[registro.fornecedor_id] = registro

    resultado = []
    for registro in mais_recente_por_fornecedor.values():
        fornecedor = sessao.get(Fornecedor, registro.fornecedor_id)
        resultado.append(
            ItemComparacaoPreco(
                fornecedor_id=registro.fornecedor_id,
                fornecedor_nome=fornecedor.nome if fornecedor else "Desconhecido",
                preco=registro.preco,
                quantidade_minima=registro.quantidade_minima,
                unidade=registro.unidade,
                capturado_em=registro.capturado_em,
            )
        )
    return sorted(resultado, key=lambda item: item.preco)


@roteador.get("/historico-precos", response_model=list[ItemHistoricoPreco])
def historico_precos(
    produto_id: int = Query(...),
    fornecedor_id: int | None = Query(default=None),
    sessao: Session = Depends(obter_sessao),
):
    """Variação de preço de um produto ao longo do tempo (opcionalmente
    filtrado por fornecedor), para gráfico de linha no painel."""
    consulta = sessao.query(RegistroPreco).filter(RegistroPreco.produto_id == produto_id)
    if fornecedor_id is not None:
        consulta = consulta.filter(RegistroPreco.fornecedor_id == fornecedor_id)

    registros = consulta.order_by(RegistroPreco.capturado_em.asc()).all()

    resultado = []
    for registro in registros:
        fornecedor = sessao.get(Fornecedor, registro.fornecedor_id)
        resultado.append(
            ItemHistoricoPreco(
                fornecedor_id=registro.fornecedor_id,
                fornecedor_nome=fornecedor.nome if fornecedor else "Desconhecido",
                preco=registro.preco,
                capturado_em=registro.capturado_em,
            )
        )
    return resultado


@roteador.get("/destaques", response_model=list[ItemDestaque])
def destaques(sessao: Session = Depends(obter_sessao)):
    """Alguns destaques simples calculados a partir do histórico de preços:
    fornecedor mais barato em geral e maiores variações de preço recentes."""
    lista_destaques: list[ItemDestaque] = []

    registros = sessao.query(RegistroPreco).all()
    if not registros:
        return [
            ItemDestaque(
                titulo="Sem dados ainda",
                descricao="Escaneie algumas etiquetas para começar a ver comparações aqui.",
            )
        ]

    # Fornecedor com mais registros de "preço mais barato" por produto
    contagem_mais_barato: dict[int, int] = {}
    por_produto: dict[int, list[RegistroPreco]] = {}
    for registro in registros:
        por_produto.setdefault(registro.produto_id, []).append(registro)

    for registros_produto in por_produto.values():
        mais_barato = min(registros_produto, key=lambda r: r.preco)
        contagem_mais_barato[mais_barato.fornecedor_id] = (
            contagem_mais_barato.get(mais_barato.fornecedor_id, 0) + 1
        )

    if contagem_mais_barato:
        id_fornecedor_destaque = max(contagem_mais_barato, key=contagem_mais_barato.get)
        fornecedor = sessao.get(Fornecedor, id_fornecedor_destaque)
        lista_destaques.append(
            ItemDestaque(
                titulo="Fornecedor mais competitivo",
                descricao=(
                    f"{fornecedor.nome if fornecedor else 'Desconhecido'} tem o menor "
                    f"preço em {contagem_mais_barato[id_fornecedor_destaque]} produto(s) monitorado(s)."
                ),
            )
        )

    # Maior aumento de preço entre os dois últimos registros de um mesmo produto+fornecedor
    maior_aumento = None
    for registros_produto in por_produto.values():
        por_fornecedor: dict[int, list[RegistroPreco]] = {}
        for registro in registros_produto:
            por_fornecedor.setdefault(registro.fornecedor_id, []).append(registro)
        for registros_fornecedor in por_fornecedor.values():
            ordenados = sorted(registros_fornecedor, key=lambda r: r.capturado_em)
            if len(ordenados) >= 2:
                diferenca = ordenados[-1].preco - ordenados[-2].preco
                if maior_aumento is None or diferenca > maior_aumento[0]:
                    maior_aumento = (diferenca, ordenados[-1])

    if maior_aumento and maior_aumento[0] > 0:
        diferenca, registro = maior_aumento
        fornecedor = sessao.get(Fornecedor, registro.fornecedor_id)
        lista_destaques.append(
            ItemDestaque(
                titulo="Alta de preço recente",
                descricao=(
                    f"Produto subiu R$ {diferenca:.2f} no fornecedor "
                    f"{fornecedor.nome if fornecedor else 'Desconhecido'}."
                ),
            )
        )

    return lista_destaques
