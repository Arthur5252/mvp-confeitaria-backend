from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import PriceSource, ShoppingListStatus, SupplierType


# ---------- Auth ----------


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Supplier ----------


class SupplierBase(BaseModel):
    name: str
    type: SupplierType = SupplierType.varejo
    notes: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(SupplierBase):
    pass


class SupplierOut(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Product ----------


class ProductBase(BaseModel):
    name: str
    canonical_unit: str = "un"
    category: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Price record ----------


class PriceRecordBase(BaseModel):
    product_id: int
    supplier_id: int
    price: float
    min_quantity: int = 1
    unit: str = "un"
    source: PriceSource = PriceSource.manual
    raw_ocr_text: str | None = None


class PriceRecordCreate(PriceRecordBase):
    pass


class PriceRecordUpdate(BaseModel):
    price: float | None = None
    min_quantity: int | None = None
    unit: str | None = None


class PriceRecordOut(PriceRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    captured_at: datetime


# ---------- Shopping list ----------


class ShoppingListCreate(BaseModel):
    name: str


class ShoppingListUpdate(BaseModel):
    name: str | None = None
    status: ShoppingListStatus | None = None


class ShoppingListItemCreate(BaseModel):
    product_id: int | None = None
    free_text_name: str | None = None
    desired_qty: float = 1
    unit: str = "un"


class ShoppingListItemUpdate(BaseModel):
    desired_qty: float | None = None
    unit: str | None = None
    checked: bool | None = None
    matched_price_record_id: int | None = None


class ShoppingListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    list_id: int
    product_id: int | None
    free_text_name: str | None
    desired_qty: float
    unit: str
    checked_at: datetime | None
    matched_price_record_id: int | None


class ShoppingListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    created_at: datetime
    status: ShoppingListStatus
    items: list[ShoppingListItemOut] = []


# ---------- OCR ----------


class OcrScanResult(BaseModel):
    raw_text: str
    guessed_name: str | None = None
    guessed_price: float | None = None
    guessed_min_quantity: int = 1
    guessed_unit: str = "un"
    is_wholesale_tier: bool = False
    confidence_note: str | None = None


# ---------- Dashboard ----------


class PriceComparisonEntry(BaseModel):
    supplier_id: int
    supplier_name: str
    price: float
    min_quantity: int
    unit: str
    captured_at: datetime


class PriceHistoryEntry(BaseModel):
    supplier_id: int
    supplier_name: str
    price: float
    captured_at: datetime


class InsightItem(BaseModel):
    title: str
    description: str
