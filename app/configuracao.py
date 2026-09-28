import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Configuracoes:
    """Configurações da aplicação, lidas de variáveis de ambiente."""

    nome_app: str = "API Backend da Confeitaria"

    url_banco: str = os.getenv("URL_BANCO", "sqlite:///./data/confeitaria.db")

    # Autenticação simples (usuário único).
    usuario_app: str = os.getenv("USUARIO_APP", "admin")
    senha_app: str = os.getenv("SENHA_APP", "changeme")
    segredo_jwt: str = os.getenv("SEGREDO_JWT", "insecure-dev-secret-change-me")
    algoritmo_jwt: str = "HS256"
    expiracao_jwt_minutos: int = int(os.getenv("EXPIRACAO_JWT_MINUTOS", "60"))

    # Provedor de OCR (API externa). "ocr_space" é o único implementado no MVP;
    # a interface ProvedorOcr permite plugar outros provedores (ex.: LLM com
    # visão) sem alterar o restante do sistema.
    provedor_ocr: str = os.getenv("PROVEDOR_OCR", "ocr_space")
    chave_api_ocr_space: str = os.getenv("CHAVE_API_OCR_SPACE", "")
    endpoint_ocr_space: str = os.getenv(
        "ENDPOINT_OCR_SPACE", "https://api.ocr.space/parse/image"
    )

    origens_cors: list[str] = os.getenv("ORIGENS_CORS", "*").split(",")


@lru_cache
def obter_configuracoes() -> Configuracoes:
    return Configuracoes()
