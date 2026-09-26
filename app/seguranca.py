from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.configuracao import obter_configuracoes

configuracoes = obter_configuracoes()
esquema_bearer = HTTPBearer()


def criar_token_acesso(assunto: str) -> str:
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=configuracoes.expiracao_jwt_minutos
    )
    carga = {"sub": assunto, "exp": expiracao}
    return jwt.encode(
        carga, configuracoes.segredo_jwt, algorithm=configuracoes.algoritmo_jwt
    )


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer),
) -> str:
    token = credenciais.credentials
    try:
        carga = jwt.decode(
            token,
            configuracoes.segredo_jwt,
            algorithms=[configuracoes.algoritmo_jwt],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
    usuario = carga.get("sub")
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )
    return usuario
