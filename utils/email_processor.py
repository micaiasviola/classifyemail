"""
Processamento e pré-processamento de emails
"""
import re
import pdfplumber


def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {e}")


def clean_email_content(text: str) -> str:
    """Remove cabeçalhos e assinaturas sem eliminar palavras importantes"""
    patterns = [
        r'From:.*?\n', r'To:.*?\n', r'Subject:.*?\n', r'Date:.*?\n',
        r'CC:.*?\n', r'BCC:.*?\n', r'Sent from.*?\n', r'________________________________',
        r'--\s*\n.*'
    ]
    for p in patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()
