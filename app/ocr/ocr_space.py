import httpx
from fastapi import HTTPException

from app.ocr.base import OcrProvider


class OcrSpaceProvider(OcrProvider):
    """Implementação usando a API externa gratuita OCR.space
    (https://ocr.space/ocrapi) — módulo "API externa" exigido pelo MVP.
    """

    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

    async def extract_text(self, image_bytes: bytes, filename: str) -> str:
        if not self.api_key:
            raise HTTPException(
                status_code=500,
                detail=(
                    "OCR_SPACE_API_KEY não configurada. Obtenha uma chave "
                    "gratuita em https://ocr.space/ocrapi"
                ),
            )

        files = {"file": (filename, image_bytes)}
        data = {
            "apikey": self.api_key,
            "language": "por",
            "OCREngine": 2,
            "scale": True,
            "isTable": False,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.endpoint, data=data, files=files)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Falha ao consultar a API externa de OCR ({response.status_code})",
            )

        payload = response.json()

        if payload.get("IsErroredOnProcessing"):
            error_message = payload.get("ErrorMessage") or ["Erro desconhecido no OCR"]
            raise HTTPException(
                status_code=502,
                detail=f"Erro no OCR externo: {'; '.join(error_message)}",
            )

        parsed_results = payload.get("ParsedResults") or []
        if not parsed_results:
            return ""

        return parsed_results[0].get("ParsedText", "").strip()
