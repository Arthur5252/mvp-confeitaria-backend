"""Popula o banco com dados fictícios de demonstração (fornecedores,
produtos, histórico de preços e uma lista de compras) — útil para gravar o
vídeo de entrega ou mostrar o dashboard sem precisar escanear etiquetas de
verdade antes.

Uso (a partir da raiz de confeitaria-backend):

    python scripts/seed_demo.py

ATENÇÃO: apaga todos os dados existentes no banco antes de popular. Não
rode isso contra um banco com dados reais que você queira manter.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import (  # noqa: E402
    PriceRecord,
    PriceSource,
    Product,
    ShoppingList,
    ShoppingListItem,
    ShoppingListStatus,
    Supplier,
    SupplierType,
)

now = datetime.now(timezone.utc).replace(tzinfo=None)


def days_ago(n):
    return now - timedelta(days=n)


def reset_database(db):
    for model in (ShoppingListItem, ShoppingList, PriceRecord, Product, Supplier):
        db.query(model).delete()
    db.commit()


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        reset_database(db)

        suppliers = {
            "atacadao": Supplier(name="Atacadão Central", type=SupplierType.atacado),
            "assai": Supplier(name="Assaí Atacadista", type=SupplierType.atacado),
            "extra": Supplier(name="Supermercado Extra", type=SupplierType.varejo),
            "bairro": Supplier(name="Mercado do Bairro", type=SupplierType.varejo),
        }
        db.add_all(suppliers.values())
        db.commit()
        for s in suppliers.values():
            db.refresh(s)

        products = {
            "farinha": Product(name="Farinha de trigo", canonical_unit="kg"),
            "acucar": Product(name="Açúcar cristal", canonical_unit="kg"),
            "chocolate": Product(name="Chocolate em pó", canonical_unit="kg"),
            "leite_cond": Product(name="Leite condensado", canonical_unit="un"),
            "creme_leite": Product(name="Creme de leite", canonical_unit="un"),
            "manteiga": Product(name="Manteiga", canonical_unit="un"),
            "ovos": Product(name="Ovos (dúzia)", canonical_unit="caixa"),
            "fermento": Product(name="Fermento em pó", canonical_unit="un"),
        }
        db.add_all(products.values())
        db.commit()
        for p in products.values():
            db.refresh(p)

        # (produto, fornecedor, preço, qtd mínima, dias atrás)
        price_data = [
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
            ("leite_cond", "assai", 4.49, 12, 10),
            ("leite_cond", "extra", 5.29, 1, 10),
            ("leite_cond", "bairro", 5.79, 1, 3),
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

        records = {}
        for product_key, supplier_key, price, min_qty, days in price_data:
            record = PriceRecord(
                product_id=products[product_key].id,
                supplier_id=suppliers[supplier_key].id,
                price=price,
                min_quantity=min_qty,
                unit=products[product_key].canonical_unit,
                captured_at=days_ago(days),
                source=PriceSource.manual,
            )
            db.add(record)
            records[(product_key, supplier_key, days)] = record
        db.commit()

        # Lista de compras de demonstração, com alguns itens já "escaneados"
        shopping_list = ShoppingList(
            name="Bolo de aniversário — encomenda",
            status=ShoppingListStatus.aberta,
            created_at=days_ago(2),
        )
        db.add(shopping_list)
        db.commit()
        db.refresh(shopping_list)

        farinha_record = records[("farinha", "extra", 10)]
        acucar_record = records[("acucar", "extra", 10)]

        items = [
            ShoppingListItem(
                list_id=shopping_list.id,
                product_id=products["farinha"].id,
                desired_qty=2,
                unit="kg",
                checked_at=days_ago(1),
                matched_price_record_id=farinha_record.id,
            ),
            ShoppingListItem(
                list_id=shopping_list.id,
                product_id=products["acucar"].id,
                desired_qty=1,
                unit="kg",
                checked_at=days_ago(1),
                matched_price_record_id=acucar_record.id,
            ),
            ShoppingListItem(
                list_id=shopping_list.id,
                product_id=products["chocolate"].id,
                desired_qty=1,
                unit="kg",
            ),
            ShoppingListItem(
                list_id=shopping_list.id,
                product_id=products["ovos"].id,
                desired_qty=1,
                unit="caixa",
            ),
        ]
        db.add_all(items)
        db.commit()

        print("Dados de demonstração inseridos com sucesso:")
        print(f"  {len(suppliers)} fornecedores")
        print(f"  {len(products)} produtos")
        print(f"  {len(price_data)} registros de preço")
        print("  1 lista de compras (2 itens já marcados como comprados)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
