import httpx
from fastapi import HTTPException

from app.ocr.base import ProvedorOcr


class ProvedorOcrSpace(ProvedorOcr):
    """Implementação usando a API externa gratuita OCR.space
    (https://ocr.space/ocrapi) — módulo "API externa" exigido pelo MVP.
    """

    def __init__(self, chave_api: str, endpoint: str):
        self.chave_api = chave_api
        self.endpoint = endpoint

    async def extrair_texto(self, bytes_imagem: bytes, nome_arquivo: str) -> str:
        if not self.chave_api:
            raise HTTPException(
                status_code=500,
                detail=(
                    "CHAVE_API_OCR_SPACE não configurada. Obtenha uma chave "
                    "gratuita em https://ocr.space/ocrapi"
                ),
            )

        arquivos = {"file": (nome_arquivo, bytes_imagem)}
        dados = {
            "apikey": self.chave_api,
            "language": "por",
            "OCREngine": 2,
            "scale": True,
            "isTable": False,
        }

        async with httpx.AsyncClient(timeout=30.0) as cliente:
            resposta = await cliente.post(self.endpoint, data=dados, files=arquivos)

        if resposta.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Falha ao consultar a API externa de OCR ({resposta.status_code})",
            )

        corpo = resposta.json()

        if corpo.get("IsErroredOnProcessing"):
            mensagem_erro = corpo.get("ErrorMessage") or ["Erro desconhecido no OCR"]
            raise HTTPException(
                status_code=502,
                detail=f"Erro no OCR externo: {'; '.join(mensagem_erro)}",
            )

        resultados = corpo.get("ParsedResults") or []
        if not resultados:
            return ""

        return resultados[0].get("ParsedText", "").strip()
