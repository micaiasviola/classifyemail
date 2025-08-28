# utils/classifier.py
"""
Classificador de Emails usando Hugging Face Zero-Shot Classification API
Com logs detalhados para debug
Autor: Micaías Viola
Data: 2025-08-27
"""

import os
import requests
from dotenv import load_dotenv
from utils.email_processor import clean_email_content

load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Defina HF_API_TOKEN no .env")

HF_MODEL = "facebook/bart-large-mnli"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

CANDIDATE_LABELS = [
    "email reporting a problem or requesting action",  # Produtivo
    "friendly greeting or thank you email"           # Improdutivo
]
LABEL_MAP = {
    "email reporting a problem or requesting action": "Produtivo",
    "friendly greeting or thank you email": "Improdutivo"
}


def classificar_email(email_content: str) -> str:
    if not email_content.strip():
        return "Improdutivo"

    payload = {
        "inputs": email_content,  # apenas o email
        "parameters": {
            "candidate_labels": CANDIDATE_LABELS,
            "multi_label": False
        },
        "options": {"wait_for_model": True}
    }

    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        top_label = result.get("labels", [])[0]
        return LABEL_MAP.get(top_label, "Improdutivo")
    except Exception as e:
        print("Erro ao chamar Hugging Face API:", e)
        return "Improdutivo"
