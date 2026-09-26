from abc import ABC, abstractmethod


class ProvedorOcr(ABC):
    """Interface para provedores de OCR.

    Permite trocar o serviço externo (ex.: OCR.space -> um provedor de LLM
    com visão) sem alterar o resto da aplicação — apenas a implementação
    concreta usada em `app/ocr/fabrica.py`.
    """

    @abstractmethod
    async def extrair_texto(self, bytes_imagem: bytes, nome_arquivo: str) -> str:
        """Recebe os bytes de uma imagem e retorna o texto bruto reconhecido."""
        raise NotImplementedError
