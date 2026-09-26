from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modelos import OrigemPreco, StatusListaCompras, TipoFornecedor


# ---------- Autenticação ----------


class RequisicaoLogin(BaseModel):
    usuario: str
    senha: str


class RespostaToken(BaseModel):
    token_acesso: str
    tipo_token: str = "bearer"


# ---------- Fornecedor ----------


class FornecedorBase(BaseModel):
    nome: str
    tipo: TipoFornecedor = TipoFornecedor.varejo
    observacoes: str | None = None


class FornecedorCriar(FornecedorBase):
    pass


class FornecedorAtualizar(FornecedorBase):
    pass


class FornecedorSaida(FornecedorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    criado_em: datetime


# ---------- Produto ----------


class ProdutoBase(BaseModel):
    nome: str
    unidade_padrao: str = "un"
    categoria: str | None = None


class ProdutoCriar(ProdutoBase):
    pass


class ProdutoSaida(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    criado_em: datetime


# ---------- Registro de preço ----------


class RegistroPrecoBase(BaseModel):
    produto_id: int
    fornecedor_id: int
    preco: float
    quantidade_minima: int = 1
    unidade: str = "un"
    origem: OrigemPreco = OrigemPreco.manual
    texto_ocr_bruto: str | None = None


class RegistroPrecoCriar(RegistroPrecoBase):
    pass


class RegistroPrecoAtualizar(BaseModel):
    preco: float | None = None
    quantidade_minima: int | None = None
    unidade: str | None = None


class RegistroPrecoSaida(RegistroPrecoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    capturado_em: datetime


# ---------- Lista de compras ----------


class ListaComprasCriar(BaseModel):
    nome: str


class ListaComprasAtualizar(BaseModel):
    nome: str | None = None
    status: StatusListaCompras | None = None


class ItemListaComprasCriar(BaseModel):
    produto_id: int | None = None
    nome_livre: str | None = None
    quantidade_desejada: float = 1
    unidade: str = "un"


class ItemListaComprasAtualizar(BaseModel):
    quantidade_desejada: float | None = None
    unidade: str | None = None
    marcado: bool | None = None
    registro_preco_vinculado_id: int | None = None


class ItemListaComprasSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lista_id: int
    produto_id: int | None
    nome_livre: str | None
    quantidade_desejada: float
    unidade: str
    marcado_em: datetime | None
    registro_preco_vinculado_id: int | None


class ListaComprasSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    criado_em: datetime
    status: StatusListaCompras
    itens: list[ItemListaComprasSaida] = []


# ---------- OCR ----------


class ResultadoEscaneamentoOcr(BaseModel):
    texto_bruto: str
    nome_sugerido: str | None = None
    preco_sugerido: float | None = None
    quantidade_minima_sugerida: int = 1
    unidade_sugerida: str = "un"
    eh_faixa_atacado: bool = False
    observacao_confianca: str | None = None


# ---------- Painel ----------


class ItemComparacaoPreco(BaseModel):
    fornecedor_id: int
    fornecedor_nome: str
    preco: float
    quantidade_minima: int
    unidade: str
    capturado_em: datetime


class ItemHistoricoPreco(BaseModel):
    fornecedor_id: int
    fornecedor_nome: str
    preco: float
    capturado_em: datetime


class ItemDestaque(BaseModel):
    titulo: str
    descricao: str
