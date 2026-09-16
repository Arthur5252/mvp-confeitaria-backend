from fastapi import APIRouter, HTTPException, status

from app.auth import create_access_token
from app.config import get_settings
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    if payload.username != settings.app_username or payload.password != settings.app_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha inválidos"
        )
    token = create_access_token(subject=payload.username)
    return TokenResponse(access_token=token)
