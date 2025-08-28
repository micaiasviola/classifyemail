"""
Fluxo completo de processamento de emails:
1. Classificação: Produtivo / Improdutivo
2. Geração de resposta automática sugerida
Autor: Micaías
Data: 2025-08-27
"""

from utils.classifier import classificar_email
from utils.hf_response import resposta_sugerida
from utils.hf_response import gerar_resposta


def processar_email_com_resposta(texto_email: str) -> dict:
    """
    Classifica o email e gera a resposta automática sugerida.

    Args:
        texto_email (str): conteúdo do email

    Returns:
        dict: {'categoria': 'Produtivo'|'Improdutivo', 'resposta': 'texto gerado'}
    """
    # Passo 1: Classificar o email
    categoria = classificar_email(texto_email)

    # Passo 2: Gerar a resposta sugerida
    resposta = resposta_sugerida(texto_email, categoria)

    # Retornar resultados
    return {
        "categoria": categoria,
        "resposta": resposta
    }
