from app.configuracao import obter_configuracoes
from app.ocr.base import ProvedorOcr
from app.ocr.ocr_space import ProvedorOcrSpace

configuracoes = obter_configuracoes()


def obter_provedor_ocr() -> ProvedorOcr:
    """Resolve o provedor de OCR configurado via variável PROVEDOR_OCR.

    Hoje só "ocr_space" está implementado (Fase 1 / entrega da faculdade).
    Para adicionar um provedor de LLM com visão no futuro, crie uma nova
    classe que implemente ProvedorOcr e registre-a aqui.
    """
    if configuracoes.provedor_ocr == "ocr_space":
        return ProvedorOcrSpace(
            chave_api=configuracoes.chave_api_ocr_space,
            endpoint=configuracoes.endpoint_ocr_space,
        )
    raise ValueError(f"Provedor de OCR desconhecido: {configuracoes.provedor_ocr}")
