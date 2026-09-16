from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import ShoppingList, ShoppingListItem
from app.schemas import (
    ShoppingListCreate,
    ShoppingListItemCreate,
    ShoppingListItemOut,
    ShoppingListItemUpdate,
    ShoppingListOut,
    ShoppingListUpdate,
)

router = APIRouter(
    prefix="/shopping-lists",
    tags=["shopping-lists"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[ShoppingListOut])
def list_shopping_lists(db: Session = Depends(get_db)):
    return db.query(ShoppingList).order_by(ShoppingList.created_at.desc()).all()


@router.post("", response_model=ShoppingListOut, status_code=201)
def create_shopping_list(payload: ShoppingListCreate, db: Session = Depends(get_db)):
    shopping_list = ShoppingList(name=payload.name)
    db.add(shopping_list)
    db.commit()
    db.refresh(shopping_list)
    return shopping_list


@router.get("/{list_id}", response_model=ShoppingListOut)
def get_shopping_list(list_id: int, db: Session = Depends(get_db)):
    shopping_list = db.get(ShoppingList, list_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    return shopping_list


@router.put("/{list_id}", response_model=ShoppingListOut)
def update_shopping_list(
    list_id: int, payload: ShoppingListUpdate, db: Session = Depends(get_db)
):
    shopping_list = db.get(ShoppingList, list_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(shopping_list, field, value)
    db.commit()
    db.refresh(shopping_list)
    return shopping_list


@router.delete("/{list_id}", status_code=204)
def delete_shopping_list(list_id: int, db: Session = Depends(get_db)):
    shopping_list = db.get(ShoppingList, list_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    db.delete(shopping_list)
    db.commit()


@router.post("/{list_id}/items", response_model=ShoppingListItemOut, status_code=201)
def add_item(
    list_id: int, payload: ShoppingListItemCreate, db: Session = Depends(get_db)
):
    shopping_list = db.get(ShoppingList, list_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    if not payload.product_id and not payload.free_text_name:
        raise HTTPException(
            status_code=422,
            detail="Informe product_id ou free_text_name para o item",
        )
    item = ShoppingListItem(list_id=list_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{list_id}/items/{item_id}", response_model=ShoppingListItemOut)
def update_item(
    list_id: int,
    item_id: int,
    payload: ShoppingListItemUpdate,
    db: Session = Depends(get_db),
):
    item = db.get(ShoppingListItem, item_id)
    if not item or item.list_id != list_id:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    data = payload.model_dump(exclude_unset=True)
    checked = data.pop("checked", None)
    for field, value in data.items():
        setattr(item, field, value)
    if checked is not None:
        item.checked_at = datetime.utcnow() if checked else None

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{list_id}/items/{item_id}", status_code=204)
def delete_item(list_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.get(ShoppingListItem, item_id)
    if not item or item.list_id != list_id:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(item)
    db.commit()
