from fastapi import APIRouter, HTTPException, status

from app.configuracao import obter_configuracoes
from app.esquemas import RequisicaoLogin, RespostaToken
from app.seguranca import criar_token_acesso

roteador = APIRouter(prefix="/autenticacao", tags=["autenticação"])
configuracoes = obter_configuracoes()


@roteador.post("/entrar", response_model=RespostaToken)
def entrar(dados: RequisicaoLogin):
    if (
        dados.usuario != configuracoes.usuario_app
        or dados.senha != configuracoes.senha_app
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha inválidos"
        )
    token = criar_token_acesso(assunto=dados.usuario)
    return RespostaToken(token_acesso=token)
