from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import PriceRecord, Supplier
from app.schemas import InsightItem, PriceComparisonEntry, PriceHistoryEntry

router = APIRouter(
    prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)]
)


@router.get("/price-comparison", response_model=list[PriceComparisonEntry])
def price_comparison(product_id: int = Query(...), db: Session = Depends(get_db)):
    """Para um produto, mostra o preço mais recente de cada fornecedor —
    permite comparar onde está mais barato agora."""
    records = (
        db.query(PriceRecord)
        .filter(PriceRecord.product_id == product_id)
        .order_by(PriceRecord.captured_at.desc())
        .all()
    )

    latest_by_supplier: dict[int, PriceRecord] = {}
    for record in records:
        if record.supplier_id not in latest_by_supplier:
            latest_by_supplier[record.supplier_id] = record

    result = []
    for record in latest_by_supplier.values():
        supplier = db.get(Supplier, record.supplier_id)
        result.append(
            PriceComparisonEntry(
                supplier_id=record.supplier_id,
                supplier_name=supplier.name if supplier else "Desconhecido",
                price=record.price,
                min_quantity=record.min_quantity,
                unit=record.unit,
                captured_at=record.captured_at,
            )
        )
    return sorted(result, key=lambda entry: entry.price)


@router.get("/price-history", response_model=list[PriceHistoryEntry])
def price_history(
    product_id: int = Query(...),
    supplier_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Variação de preço de um produto ao longo do tempo (opcionalmente
    filtrado por fornecedor), para gráfico de linha no dashboard."""
    query = db.query(PriceRecord).filter(PriceRecord.product_id == product_id)
    if supplier_id is not None:
        query = query.filter(PriceRecord.supplier_id == supplier_id)

    records = query.order_by(PriceRecord.captured_at.asc()).all()

    result = []
    for record in records:
        supplier = db.get(Supplier, record.supplier_id)
        result.append(
            PriceHistoryEntry(
                supplier_id=record.supplier_id,
                supplier_name=supplier.name if supplier else "Desconhecido",
                price=record.price,
                captured_at=record.captured_at,
            )
        )
    return result


@router.get("/insights", response_model=list[InsightItem])
def insights(db: Session = Depends(get_db)):
    """Alguns insights simples calculados a partir do histórico de preços:
    fornecedor mais barato em geral e maiores variações de preço recentes."""
    insights_list: list[InsightItem] = []

    records = db.query(PriceRecord).all()
    if not records:
        return [
            InsightItem(
                title="Sem dados ainda",
                description="Escaneie algumas etiquetas para começar a ver comparações aqui.",
            )
        ]

    # Fornecedor com mais registros de "preço mais barato" por produto
    cheapest_counts: dict[int, int] = {}
    by_product: dict[int, list[PriceRecord]] = {}
    for record in records:
        by_product.setdefault(record.product_id, []).append(record)

    for product_records in by_product.values():
        cheapest = min(product_records, key=lambda r: r.price)
        cheapest_counts[cheapest.supplier_id] = (
            cheapest_counts.get(cheapest.supplier_id, 0) + 1
        )

    if cheapest_counts:
        top_supplier_id = max(cheapest_counts, key=cheapest_counts.get)
        supplier = db.get(Supplier, top_supplier_id)
        insights_list.append(
            InsightItem(
                title="Fornecedor mais competitivo",
                description=(
                    f"{supplier.name if supplier else 'Desconhecido'} tem o menor "
                    f"preço em {cheapest_counts[top_supplier_id]} produto(s) monitorado(s)."
                ),
            )
        )

    # Maior aumento de preço entre os dois últimos registros de um mesmo produto+fornecedor
    biggest_increase = None
    for product_records in by_product.values():
        by_supplier: dict[int, list[PriceRecord]] = {}
        for record in product_records:
            by_supplier.setdefault(record.supplier_id, []).append(record)
        for supplier_records in by_supplier.values():
            ordered = sorted(supplier_records, key=lambda r: r.captured_at)
            if len(ordered) >= 2:
                diff = ordered[-1].price - ordered[-2].price
                if biggest_increase is None or diff > biggest_increase[0]:
                    biggest_increase = (diff, ordered[-1])

    if biggest_increase and biggest_increase[0] > 0:
        diff, record = biggest_increase
        supplier = db.get(Supplier, record.supplier_id)
        insights_list.append(
            InsightItem(
                title="Alta de preço recente",
                description=(
                    f"Produto subiu R$ {diff:.2f} no fornecedor "
                    f"{supplier.name if supplier else 'Desconhecido'}."
                ),
            )
        )

    return insights_list
