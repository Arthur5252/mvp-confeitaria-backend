from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth import get_current_user
from app.ocr.base import OcrProvider
from app.ocr.factory import get_ocr_provider
from app.parsing import parse_ocr_text
from app.schemas import OcrScanResult

router = APIRouter(prefix="/ocr", tags=["ocr"], dependencies=[Depends(get_current_user)])

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}


@router.post("/scan", response_model=OcrScanResult)
async def scan_label(
    file: UploadFile = File(...),
    provider: OcrProvider = Depends(get_ocr_provider),
):
    """Recebe a foto de uma etiqueta de mercado, chama a API externa de OCR
    e devolve um candidato de {nome, preço, quantidade mínima, unidade} para
    o usuário confirmar/editar antes de salvar como price-record.
    """
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415, detail="Formato de imagem não suportado"
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=422, detail="Arquivo de imagem vazio")

    raw_text = await provider.extract_text(image_bytes, file.filename or "etiqueta.jpg")
    return parse_ocr_text(raw_text)
