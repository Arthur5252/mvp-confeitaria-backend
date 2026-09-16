import re

from app.schemas import OcrScanResult

# Preços em etiquetas brasileiras: "R$ 12,90", "12,90", "R$12,9"
_PRICE_RE = re.compile(r"(?:R\$\s*)?(\d{1,4}[.,]\d{2})")

# Palavras que indicam preço por quantidade/atacado, ex.: "LEVE 3 PAGUE 2",
# "A PARTIR DE 6 UN", "CAIXA C/ 12", "PREÇO ATACADO"
_WHOLESALE_KEYWORDS = re.compile(
    r"(atacad|leve\s*\d+|a partir de\s*\d+|cx\s*c/?\s*\d+|caixa\s*c/?\s*\d+|c/\s*\d+\s*un)",
    re.IGNORECASE,
)

_MIN_QTY_RE = re.compile(
    r"(?:leve|a partir de|c/|cx c/|caixa c/)\s*(\d{1,3})", re.IGNORECASE
)

_UNIT_KEYWORDS = {
    "kg": "kg",
    "quilo": "kg",
    "g": "g",
    "grama": "g",
    "l": "L",
    "litro": "L",
    "ml": "ml",
    "un": "un",
    "unid": "un",
    "unidade": "un",
    "cx": "caixa",
    "caixa": "caixa",
    "pct": "pacote",
    "pacote": "pacote",
}


def _guess_unit(text: str) -> str:
    lowered = text.lower()
    # Etiquetas frequentemente colam a unidade no número (ex.: "1kg", "500g",
    # "5l"), o que não tem borda de palavra antes da unidade — checa esse
    # caso primeiro.
    glued_match = re.search(r"\d+[.,]?\d*\s*(kg|g|ml|l|un|pct)\b", lowered)
    if glued_match:
        return _UNIT_KEYWORDS.get(glued_match.group(1), glued_match.group(1))

    for keyword, unit in _UNIT_KEYWORDS.items():
        if re.search(rf"\b{keyword}\b", lowered):
            return unit
    return "un"


def _guess_name(text: str, price_match_span: tuple[int, int] | None) -> str | None:
    """Usa a primeira linha "significativa" do texto como nome do produto,
    evitando linhas que sejam só números/preço."""
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if _PRICE_RE.fullmatch(clean.replace("R$", "").strip()):
            continue
        if len(clean) < 2:
            continue
        return clean[:160]
    return None


def parse_ocr_text(raw_text: str) -> OcrScanResult:
    """Heurística simples para transformar o texto bruto do OCR em um
    candidato de {nome, preço, quantidade mínima, unidade}.

    Isto é lógica própria da aplicação (não da API externa de OCR) e é
    propositalmente conservadora: quando não tem certeza, sinaliza em
    `confidence_note` para o usuário confirmar/editar na interface antes de
    salvar o registro de preço.
    """
    if not raw_text or not raw_text.strip():
        return OcrScanResult(
            raw_text=raw_text or "",
            confidence_note="Nenhum texto foi reconhecido na imagem. Tente novamente com mais luz e foco.",
        )

    price_match = _PRICE_RE.search(raw_text)
    guessed_price = None
    if price_match:
        price_str = price_match.group(1).replace(",", ".")
        try:
            guessed_price = float(price_str)
        except ValueError:
            guessed_price = None

    is_wholesale = bool(_WHOLESALE_KEYWORDS.search(raw_text))
    min_qty = 1
    if is_wholesale:
        qty_match = _MIN_QTY_RE.search(raw_text)
        if qty_match:
            min_qty = int(qty_match.group(1))

    guessed_unit = _guess_unit(raw_text)
    guessed_name = _guess_name(raw_text, price_match.span() if price_match else None)

    confidence_note = None
    if guessed_price is None:
        confidence_note = "Não foi possível identificar o preço automaticamente — confira e preencha manualmente."
    elif guessed_name is None:
        confidence_note = "Não foi possível identificar o nome do produto — confira e preencha manualmente."

    return OcrScanResult(
        raw_text=raw_text,
        guessed_name=guessed_name,
        guessed_price=guessed_price,
        guessed_min_quantity=min_qty,
        guessed_unit=guessed_unit,
        is_wholesale_tier=is_wholesale,
        confidence_note=confidence_note,
    )
