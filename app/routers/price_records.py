from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import PriceRecord
from app.schemas import PriceRecordCreate, PriceRecordOut, PriceRecordUpdate

router = APIRouter(
    prefix="/price-records",
    tags=["price-records"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[PriceRecordOut])
def list_price_records(
    product_id: int | None = Query(default=None),
    supplier_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(PriceRecord)
    if product_id is not None:
        query = query.filter(PriceRecord.product_id == product_id)
    if supplier_id is not None:
        query = query.filter(PriceRecord.supplier_id == supplier_id)
    return query.order_by(PriceRecord.captured_at.desc()).all()


@router.post("", response_model=PriceRecordOut, status_code=201)
def create_price_record(payload: PriceRecordCreate, db: Session = Depends(get_db)):
    record = PriceRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{record_id}", response_model=PriceRecordOut)
def get_price_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(PriceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro de preço não encontrado")
    return record


@router.put("/{record_id}", response_model=PriceRecordOut)
def update_price_record(
    record_id: int, payload: PriceRecordUpdate, db: Session = Depends(get_db)
):
    record = db.get(PriceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro de preço não encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_price_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(PriceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro de preço não encontrado")
    db.delete(record)
    db.commit()
