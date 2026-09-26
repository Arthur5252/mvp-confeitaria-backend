import enum
from datetime import datetime

from sqlalchemy import (
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

from app.banco_dados import Base


class TipoFornecedor(str, enum.Enum):
    varejo = "varejo"
    atacado = "atacado"


class StatusListaCompras(str, enum.Enum):
    aberta = "aberta"
    concluida = "concluida"


class OrigemPreco(str, enum.Enum):
    manual = "manual"
    ocr = "ocr"


class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False, unique=True)
    tipo = Column(Enum(TipoFornecedor), nullable=False, default=TipoFornecedor.varejo)
    observacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    registros_preco = relationship(
        "RegistroPreco", back_populates="fornecedor", cascade="all, delete-orphan"
    )


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(160), nullable=False)
    unidade_padrao = Column(String(20), nullable=False, default="un")
    categoria = Column(String(80), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    apelidos = relationship(
        "ApelidoProduto", back_populates="produto", cascade="all, delete-orphan"
    )
    registros_preco = relationship(
        "RegistroPreco", back_populates="produto", cascade="all, delete-orphan"
    )
    itens_lista = relationship("ItemListaCompras", back_populates="produto")


class ApelidoProduto(Base):
    __tablename__ = "apelidos_produto"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    texto_bruto = Column(String(200), nullable=False)

    produto = relationship("Produto", back_populates="apelidos")


class RegistroPreco(Base):
    __tablename__ = "registros_preco"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    preco = Column(Float, nullable=False)
    quantidade_minima = Column(Integer, nullable=False, default=1)
    unidade = Column(String(20), nullable=False, default="un")
    capturado_em = Column(DateTime, default=datetime.utcnow)
    origem = Column(Enum(OrigemPreco), nullable=False, default=OrigemPreco.manual)
    texto_ocr_bruto = Column(Text, nullable=True)

    produto = relationship("Produto", back_populates="registros_preco")
    fornecedor = relationship("Fornecedor", back_populates="registros_preco")


class ListaCompras(Base):
    __tablename__ = "listas_compras"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(160), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    status = Column(
        Enum(StatusListaCompras), nullable=False, default=StatusListaCompras.aberta
    )

    itens = relationship(
        "ItemListaCompras", back_populates="lista", cascade="all, delete-orphan"
    )


class ItemListaCompras(Base):
    __tablename__ = "itens_lista_compras"

    id = Column(Integer, primary_key=True, index=True)
    lista_id = Column(Integer, ForeignKey("listas_compras.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=True)
    nome_livre = Column(String(160), nullable=True)
    quantidade_desejada = Column(Float, nullable=False, default=1)
    unidade = Column(String(20), nullable=False, default="un")
    marcado_em = Column(DateTime, nullable=True)
    registro_preco_vinculado_id = Column(
        Integer, ForeignKey("registros_preco.id"), nullable=True
    )

    lista = relationship("ListaCompras", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_lista")
    registro_preco_vinculado = relationship("RegistroPreco")
