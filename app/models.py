import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class SupplierType(str, enum.Enum):
    varejo = "varejo"
    atacado = "atacado"


class ShoppingListStatus(str, enum.Enum):
    aberta = "aberta"
    concluida = "concluida"


class PriceSource(str, enum.Enum):
    manual = "manual"
    ocr = "ocr"


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True)
    type = Column(Enum(SupplierType), nullable=False, default=SupplierType.varejo)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    price_records = relationship(
        "PriceRecord", back_populates="supplier", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    canonical_unit = Column(String(20), nullable=False, default="un")
    category = Column(String(80), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    aliases = relationship(
        "ProductAlias", back_populates="product", cascade="all, delete-orphan"
    )
    price_records = relationship(
        "PriceRecord", back_populates="product", cascade="all, delete-orphan"
    )
    list_items = relationship("ShoppingListItem", back_populates="product")


class ProductAlias(Base):
    __tablename__ = "product_aliases"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    raw_text = Column(String(200), nullable=False)

    product = relationship("Product", back_populates="aliases")


class PriceRecord(Base):
    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    price = Column(Float, nullable=False)
    min_quantity = Column(Integer, nullable=False, default=1)
    unit = Column(String(20), nullable=False, default="un")
    captured_at = Column(DateTime, default=datetime.utcnow)
    source = Column(Enum(PriceSource), nullable=False, default=PriceSource.manual)
    raw_ocr_text = Column(Text, nullable=True)

    product = relationship("Product", back_populates="price_records")
    supplier = relationship("Supplier", back_populates="price_records")


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(
        Enum(ShoppingListStatus), nullable=False, default=ShoppingListStatus.aberta
    )

    items = relationship(
        "ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan"
    )


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("shopping_lists.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    free_text_name = Column(String(160), nullable=True)
    desired_qty = Column(Float, nullable=False, default=1)
    unit = Column(String(20), nullable=False, default="un")
    checked_at = Column(DateTime, nullable=True)
    matched_price_record_id = Column(
        Integer, ForeignKey("price_records.id"), nullable=True
    )

    shopping_list = relationship("ShoppingList", back_populates="items")
    product = relationship("Product", back_populates="list_items")
    matched_price_record = relationship("PriceRecord")
