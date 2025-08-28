# utils/classifier.py
"""
Classificador de Emails usando Hugging Face Zero-Shot Classification API
Com logs detalhados e labels otimizados para melhor precisão
Autor: Micaías Viola
Data: 2025-08-28
"""

import os
import requests
from dotenv import load_dotenv
from utils.email_processor import clean_email_content
import time

load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Defina HF_API_TOKEN no .env")

# Modelo principal
HF_MODEL = "typeform/distilbert-base-uncased-mnli"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Labels mais curtos e claros
CANDIDATE_LABELS = [
    "request",  # Produtivo
    "greeting"  # Improdutivo
]

LABEL_MAP = {
    "request": "Produtivo",
    "greeting": "Improdutivo"
}


def classificar_email(email_content: str) -> str:
    """
    Classifica um email como Produtivo ou Improdutivo usando Zero-Shot Classification.
    Tenta 3 vezes em caso de timeout ou erro da API.
    """
    if not email_content.strip():
        return "Improdutivo"

    payload = {
        "inputs": email_content,
        "parameters": {
            "candidate_labels": CANDIDATE_LABELS,
            "multi_label": True  # pega o label com maior score
        },
        "options": {"wait_for_model": True}
    }

    for attempt in range(3):
        try:
            response = requests.post(
                HF_API_URL, headers=HEADERS, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()

            # Escolhe o label com maior score
            if "labels" in result and "scores" in result:
                labels = result["labels"]
                scores = result["scores"]
                top_label = labels[scores.index(max(scores))]
                return LABEL_MAP.get(top_label, "Improdutivo")

            return "Improdutivo"

        except requests.exceptions.Timeout:
            print(f"[Aviso] Timeout na API, tentativa {attempt+1}/3...")
            time.sleep(2)
        except Exception as e:
            print(f"[Erro] Hugging Face API: {e}")
            time.sleep(2)

    # Se todas as tentativas falharem
    return "Improdutivo"
