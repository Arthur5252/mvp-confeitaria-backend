from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.banco_dados import Base, motor
from app.configuracao import obter_configuracoes
from app.rotas import (
    autenticacao,
    fornecedores,
    listas_compras,
    ocr,
    painel,
    produtos,
    registros_preco,
)

configuracoes = obter_configuracoes()

Base.metadata.create_all(bind=motor)

app = FastAPI(
    title=configuracoes.nome_app,
    description=(
        "API de back-end do sistema de compras para confeitaria. Consome a "
        "API externa OCR.space para leitura de etiquetas de mercado."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracoes.origens_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(autenticacao.roteador)
app.include_router(fornecedores.roteador)
app.include_router(produtos.roteador)
app.include_router(registros_preco.roteador)
app.include_router(listas_compras.roteador)
app.include_router(ocr.roteador)
app.include_router(painel.roteador)


@app.get("/saude", tags=["saúde"])
def verificar_saude():
    return {"status": "ok"}
