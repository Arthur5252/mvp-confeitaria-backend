"""Popula o banco com dados fictícios de demonstração (fornecedores,
produtos, histórico de preços e uma lista de compras) — útil para gravar o
vídeo de entrega ou mostrar o painel sem precisar escanear etiquetas de
verdade antes.

Uso (a partir da raiz de backend):

    python scripts/popular_demo.py

ATENÇÃO: apaga todos os dados existentes no banco antes de popular. Não
rode isso contra um banco com dados reais que você queira manter.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.banco_dados import Base, SessaoLocal, motor  # noqa: E402
from app.modelos import (  # noqa: E402
    Fornecedor,
    ItemListaCompras,
    ListaCompras,
    OrigemPreco,
    Produto,
    RegistroPreco,
    StatusListaCompras,
    TipoFornecedor,
)

agora = datetime.now(timezone.utc).replace(tzinfo=None)


def dias_atras(quantidade):
    return agora - timedelta(days=quantidade)


def limpar_banco(sessao):
    for modelo in (ItemListaCompras, ListaCompras, RegistroPreco, Produto, Fornecedor):
        sessao.query(modelo).delete()
    sessao.commit()


def popular():
    Base.metadata.create_all(bind=motor)
    sessao = SessaoLocal()
    try:
        limpar_banco(sessao)

        fornecedores = {
            "atacadao": Fornecedor(nome="Atacadão Central", tipo=TipoFornecedor.atacado),
            "assai": Fornecedor(nome="Assaí Atacadista", tipo=TipoFornecedor.atacado),
            "extra": Fornecedor(nome="Supermercado Extra", tipo=TipoFornecedor.varejo),
            "bairro": Fornecedor(nome="Mercado do Bairro", tipo=TipoFornecedor.varejo),
        }
        sessao.add_all(fornecedores.values())
        sessao.commit()
        for fornecedor in fornecedores.values():
            sessao.refresh(fornecedor)

        produtos = {
            "farinha": Produto(nome="Farinha de trigo", unidade_padrao="kg"),
            "acucar": Produto(nome="Açúcar cristal", unidade_padrao="kg"),
            "chocolate": Produto(nome="Chocolate em pó", unidade_padrao="kg"),
            "leite_condensado": Produto(nome="Leite condensado", unidade_padrao="un"),
            "creme_leite": Produto(nome="Creme de leite", unidade_padrao="un"),
            "manteiga": Produto(nome="Manteiga", unidade_padrao="un"),
            "ovos": Produto(nome="Ovos (dúzia)", unidade_padrao="caixa"),
            "fermento": Produto(nome="Fermento em pó", unidade_padrao="un"),
        }
        sessao.add_all(produtos.values())
        sessao.commit()
        for produto in produtos.values():
            sessao.refresh(produto)

        # (produto, fornecedor, preço, quantidade mínima, dias atrás)
        dados_precos = [
            # Farinha de trigo — mostra alta gradual em dois fornecedores
            ("farinha", "extra", 5.49, 1, 45),
            ("farinha", "extra", 5.69, 1, 38),
            ("farinha", "extra", 5.79, 1, 31),
            ("farinha", "extra", 5.89, 1, 24),
            ("farinha", "extra", 5.95, 1, 17),
            ("farinha", "extra", 5.99, 1, 10),
            ("farinha", "atacadao", 3.99, 5, 45),
            ("farinha", "atacadao", 4.29, 5, 10),
            ("farinha", "bairro", 6.49, 1, 10),
            # Açúcar cristal
            ("acucar", "assai", 3.49, 5, 45),
            ("acucar", "assai", 3.79, 5, 10),
            ("acucar", "extra", 4.29, 1, 45),
            ("acucar", "extra", 4.49, 1, 24),
            ("acucar", "extra", 4.69, 1, 10),
            ("acucar", "bairro", 4.99, 1, 10),
            # Chocolate em pó
            ("chocolate", "atacadao", 18.90, 3, 10),
            ("chocolate", "extra", 22.50, 1, 10),
            # Leite condensado
            ("leite_condensado", "assai", 4.49, 12, 10),
            ("leite_condensado", "extra", 5.29, 1, 10),
            ("leite_condensado", "bairro", 5.79, 1, 3),
            # Creme de leite
            ("creme_leite", "extra", 3.19, 1, 5),
            ("creme_leite", "bairro", 3.49, 1, 3),
            # Manteiga
            ("manteiga", "atacadao", 8.49, 6, 5),
            ("manteiga", "extra", 9.99, 1, 5),
            # Ovos
            ("ovos", "extra", 12.90, 1, 0),
            ("ovos", "bairro", 13.50, 1, 0),
            # Fermento em pó
            ("fermento", "extra", 2.49, 1, 2),
        ]

        registros = {}
        for chave_produto, chave_fornecedor, preco, quantidade_minima, dias in dados_precos:
            registro = RegistroPreco(
                produto_id=produtos[chave_produto].id,
                fornecedor_id=fornecedores[chave_fornecedor].id,
                preco=preco,
                quantidade_minima=quantidade_minima,
                unidade=produtos[chave_produto].unidade_padrao,
                capturado_em=dias_atras(dias),
                origem=OrigemPreco.manual,
            )
            sessao.add(registro)
            registros[(chave_produto, chave_fornecedor, dias)] = registro
        sessao.commit()

        # Lista de compras de demonstração, com alguns itens já "escaneados"
        lista = ListaCompras(
            nome="Bolo de aniversário — encomenda",
            status=StatusListaCompras.aberta,
            criado_em=dias_atras(2),
        )
        sessao.add(lista)
        sessao.commit()
        sessao.refresh(lista)

        registro_farinha = registros[("farinha", "extra", 10)]
        registro_acucar = registros[("acucar", "extra", 10)]

        itens = [
            ItemListaCompras(
                lista_id=lista.id,
                produto_id=produtos["farinha"].id,
                quantidade_desejada=2,
                unidade="kg",
                marcado_em=dias_atras(1),
                registro_preco_vinculado_id=registro_farinha.id,
            ),
            ItemListaCompras(
                lista_id=lista.id,
                produto_id=produtos["acucar"].id,
                quantidade_desejada=1,
                unidade="kg",
                marcado_em=dias_atras(1),
                registro_preco_vinculado_id=registro_acucar.id,
            ),
            ItemListaCompras(
                lista_id=lista.id,
                produto_id=produtos["chocolate"].id,
                quantidade_desejada=1,
                unidade="kg",
            ),
            ItemListaCompras(
                lista_id=lista.id,
                produto_id=produtos["ovos"].id,
                quantidade_desejada=1,
                unidade="caixa",
            ),
        ]
        sessao.add_all(itens)
        sessao.commit()

        print("Dados de demonstração inseridos com sucesso:")
        print(f"  {len(fornecedores)} fornecedores")
        print(f"  {len(produtos)} produtos")
        print(f"  {len(dados_precos)} registros de preço")
        print("  1 lista de compras (2 itens já marcados como comprados)")
    finally:
        sessao.close()


if __name__ == "__main__":
    popular()
