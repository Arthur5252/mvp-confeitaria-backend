import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.configuracao import obter_configuracoes

configuracoes = obter_configuracoes()

# Garante que o diretório do arquivo SQLite exista (ex.: ./data/confeitaria.db)
if configuracoes.url_banco.startswith("sqlite:///"):
    caminho_banco = configuracoes.url_banco.replace("sqlite:///", "", 1)
    diretorio_banco = os.path.dirname(caminho_banco)
    if diretorio_banco:
        os.makedirs(diretorio_banco, exist_ok=True)

argumentos_conexao = (
    {"check_same_thread": False} if configuracoes.url_banco.startswith("sqlite") else {}
)

motor = create_engine(configuracoes.url_banco, connect_args=argumentos_conexao)
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

Base = declarative_base()


def obter_sessao():
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()
