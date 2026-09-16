import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configurações da aplicação, lidas de variáveis de ambiente."""

    app_name: str = "Confeitaria Backend API"

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/confeitaria.db")

    # Autenticação simples (single-user) — necessária pois o sistema fica
    # exposto na internet via port forwarding.
    app_username: str = os.getenv("APP_USERNAME", "admin")
    app_password: str = os.getenv("APP_PASSWORD", "changeme")
    jwt_secret: str = os.getenv("JWT_SECRET", "insecure-dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    # Provedor de OCR (API externa). "ocr_space" é o único implementado no MVP;
    # a interface OcrProvider permite plugar outros provedores (ex.: LLM vision)
    # sem alterar o restante do sistema.
    ocr_provider: str = os.getenv("OCR_PROVIDER", "ocr_space")
    ocr_space_api_key: str = os.getenv("OCR_SPACE_API_KEY", "")
    ocr_space_endpoint: str = os.getenv(
        "OCR_SPACE_ENDPOINT", "https://api.ocr.space/parse/image"
    )

    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


@lru_cache
def get_settings() -> Settings:
    return Settings()
