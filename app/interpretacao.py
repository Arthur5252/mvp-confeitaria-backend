import re

from app.esquemas import ResultadoEscaneamentoOcr

# Preços em etiquetas brasileiras: "R$ 12,90", "12,90", "R$12,9"
_REGEX_PRECO = re.compile(r"(?:R\$\s*)?(\d{1,4}[.,]\d{2})")

# Palavras que indicam preço por quantidade/atacado, ex.: "LEVE 3 PAGUE 2",
# "A PARTIR DE 6 UN", "CAIXA C/ 12", "PREÇO ATACADO"
_PALAVRAS_ATACADO = re.compile(
    r"(atacad|leve\s*\d+|a partir de\s*\d+|cx\s*c/?\s*\d+|caixa\s*c/?\s*\d+|c/\s*\d+\s*un)",
    re.IGNORECASE,
)

_REGEX_QUANTIDADE_MINIMA = re.compile(
    r"(?:leve|a partir de|c/|cx c/|caixa c/)\s*(\d{1,3})", re.IGNORECASE
)

_PALAVRAS_UNIDADE = {
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


def _sugerir_unidade(texto: str) -> str:
    minusculo = texto.lower()
    # Etiquetas frequentemente colam a unidade no número (ex.: "1kg", "500g",
    # "5l"), o que não tem borda de palavra antes da unidade — checa esse
    # caso primeiro.
    unidade_colada = re.search(r"\d+[.,]?\d*\s*(kg|g|ml|l|un|pct)\b", minusculo)
    if unidade_colada:
        return _PALAVRAS_UNIDADE.get(unidade_colada.group(1), unidade_colada.group(1))

    for palavra, unidade in _PALAVRAS_UNIDADE.items():
        if re.search(rf"\b{palavra}\b", minusculo):
            return unidade
    return "un"


def _sugerir_nome(texto: str) -> str | None:
    """Usa a primeira linha "significativa" do texto como nome do produto,
    evitando linhas que sejam só números/preço."""
    for linha in texto.splitlines():
        limpa = linha.strip()
        if not limpa:
            continue
        if _REGEX_PRECO.fullmatch(limpa.replace("R$", "").strip()):
            continue
        if len(limpa) < 2:
            continue
        return limpa[:160]
    return None


def interpretar_texto_ocr(texto_bruto: str) -> ResultadoEscaneamentoOcr:
    """Heurística simples para transformar o texto bruto do OCR em um
    candidato de {nome, preço, quantidade mínima, unidade}.

    Isto é lógica própria da aplicação (não da API externa de OCR) e é
    propositalmente conservadora: quando não tem certeza, sinaliza em
    `observacao_confianca` para o usuário confirmar/editar na interface antes
    de salvar o registro de preço.
    """
    if not texto_bruto or not texto_bruto.strip():
        return ResultadoEscaneamentoOcr(
            texto_bruto=texto_bruto or "",
            observacao_confianca="Nenhum texto foi reconhecido na imagem. Tente novamente com mais luz e foco.",
        )

    correspondencia_preco = _REGEX_PRECO.search(texto_bruto)
    preco_sugerido = None
    if correspondencia_preco:
        texto_preco = correspondencia_preco.group(1).replace(",", ".")
        try:
            preco_sugerido = float(texto_preco)
        except ValueError:
            preco_sugerido = None

    eh_atacado = bool(_PALAVRAS_ATACADO.search(texto_bruto))
    quantidade_minima = 1
    if eh_atacado:
        correspondencia_quantidade = _REGEX_QUANTIDADE_MINIMA.search(texto_bruto)
        if correspondencia_quantidade:
            quantidade_minima = int(correspondencia_quantidade.group(1))

    unidade_sugerida = _sugerir_unidade(texto_bruto)
    nome_sugerido = _sugerir_nome(texto_bruto)

    observacao_confianca = None
    if preco_sugerido is None:
        observacao_confianca = "Não foi possível identificar o preço automaticamente — confira e preencha manualmente."
    elif nome_sugerido is None:
        observacao_confianca = "Não foi possível identificar o nome do produto — confira e preencha manualmente."

    return ResultadoEscaneamentoOcr(
        texto_bruto=texto_bruto,
        nome_sugerido=nome_sugerido,
        preco_sugerido=preco_sugerido,
        quantidade_minima_sugerida=quantidade_minima,
        unidade_sugerida=unidade_sugerida,
        eh_faixa_atacado=eh_atacado,
        observacao_confianca=observacao_confianca,
    )
