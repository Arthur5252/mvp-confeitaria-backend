from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.esquemas import ResultadoEscaneamentoOcr
from app.interpretacao import interpretar_texto_ocr
from app.ocr.base import ProvedorOcr
from app.ocr.fabrica import obter_provedor_ocr
from app.seguranca import obter_usuario_atual

roteador = APIRouter(
    prefix="/ocr", tags=["ocr"], dependencies=[Depends(obter_usuario_atual)]
)

_TIPOS_CONTEUDO_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "image/heic"}


@roteador.post("/escanear", response_model=ResultadoEscaneamentoOcr)
async def escanear_etiqueta(
    arquivo: UploadFile = File(...),
    provedor: ProvedorOcr = Depends(obter_provedor_ocr),
):
    """Recebe a foto de uma etiqueta de mercado, chama a API externa de OCR
    e devolve um candidato de {nome, preço, quantidade mínima, unidade} para
    o usuário confirmar/editar antes de salvar como registro de preço.
    """
    if arquivo.content_type not in _TIPOS_CONTEUDO_PERMITIDOS:
        raise HTTPException(status_code=415, detail="Formato de imagem não suportado")

    bytes_imagem = await arquivo.read()
    if not bytes_imagem:
        raise HTTPException(status_code=422, detail="Arquivo de imagem vazio")

    texto_bruto = await provedor.extrair_texto(
        bytes_imagem, arquivo.filename or "etiqueta.jpg"
    )
    return interpretar_texto_ocr(texto_bruto)
