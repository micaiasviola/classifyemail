"""
Integração com Hugging Face API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Defina HF_API_TOKEN no .env")

# Modelo de classificação em português
HF_MODEL_CLASSIFIER = "pablocosta/bert-base-portuguese-cased-finetuned"

# Modelo leve para geração de texto
HF_MODEL_GENERATOR = "gpt2"


HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


def classify_email(email_text: str) -> str:
    """
    Chama a API Hugging Face para classificar email como Produtivo/Improdutivo
    """
    payload = {"inputs": email_text, "options": {"wait_for_model": True}}

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL_CLASSIFIER}",
            headers=HEADERS,
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        # Retorno esperado: [{'label': 'positivo', 'score': 0.98}]
        label = result[0]['label'].lower()
        if "produtivo" in label or "positivo" in label:
            return "Produtivo"
        else:
            return "Improdutivo"

    except Exception as e:
        print("Erro ao classificar:", e)
        return "Improdutivo"  # fallback seguro


def generate_response(email_text: str, classification: str) -> str:
    """
    Chama a API Hugging Face para gerar resposta automática
    """
    if classification == "Improdutivo":
        prompt = f"Responda de forma cordial e curta a este email de agradecimento ou cumprimento: {email_text}"
    else:
        prompt = f"Responda de forma profissional e objetiva a este email solicitando ajuda ou ação: {email_text}"

    payload = {"inputs": prompt, "options": {"wait_for_model": True}}

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL_GENERATOR}",
            headers=HEADERS,
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        # gpt2 retorna [{'generated_text': '...'}]
        return result[0]['generated_text']

    except Exception as e:
        print("Erro ao gerar resposta:", e)
        # fallback: resposta simples
        if classification == "Produtivo":
            return "Obrigado pelo contato. Nossa equipe irá analisar sua solicitação."
        else:
            return "Obrigado pela sua mensagem. Tenha um ótimo dia!"
