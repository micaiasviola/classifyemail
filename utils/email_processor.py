"""
Processamento e pré-processamento de emails
Autor: Micaías Viola
Data: 2025-08-27
"""
import re
from typing import Union

from PyPDF2 import PdfReader


def clean_email_content(text: str) -> str:
    """
    Remove assinaturas, espaços extras e normaliza o texto do email.
    """
    # Remove assinaturas comuns
    text = re.sub(r'Atenciosamente.*', '', text,
                  flags=re.IGNORECASE | re.DOTALL)
    # Remove múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    # Remove cabeçalhos de email (exemplo)
    text = re.sub(r'From:.*\n', '', text)
    return text.strip()


def extract_text_from_pdf(file: Union[str, bytes]) -> str:
    """
    Extrai texto de um arquivo PDF enviado pelo usuário.
    """
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
