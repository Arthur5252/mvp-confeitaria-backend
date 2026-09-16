from abc import ABC, abstractmethod


class OcrProvider(ABC):
    """Interface para provedores de OCR.

    Permite trocar o serviço externo (ex.: OCR.space -> um provedor de LLM
    vision) sem alterar o resto da aplicação — apenas a implementação
    concreta usada em `app/ocr/factory.py`.
    """

    @abstractmethod
    async def extract_text(self, image_bytes: bytes, filename: str) -> str:
        """Recebe os bytes de uma imagem e retorna o texto bruto reconhecido."""
        raise NotImplementedError
