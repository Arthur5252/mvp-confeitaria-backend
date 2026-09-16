from app.config import get_settings
from app.ocr.base import OcrProvider
from app.ocr.ocr_space import OcrSpaceProvider

settings = get_settings()


def get_ocr_provider() -> OcrProvider:
    """Resolve o provedor de OCR configurado via env var OCR_PROVIDER.

    Hoje só "ocr_space" está implementado (Fase 1 / entrega da faculdade).
    Para adicionar um provedor de LLM vision no futuro, crie uma nova classe
    que implemente OcrProvider e registre-a aqui.
    """
    if settings.ocr_provider == "ocr_space":
        return OcrSpaceProvider(
            api_key=settings.ocr_space_api_key, endpoint=settings.ocr_space_endpoint
        )
    raise ValueError(f"Provedor de OCR desconhecido: {settings.ocr_provider}")
