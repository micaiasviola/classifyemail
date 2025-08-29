# utils/classifier.py
"""
Classificador de Emails com IA Zero-Shot + Heurísticas + Logs detalhados
Mais robusto, interpretável e com fallback inteligente.
Autor: Micaías Viola
Data: 2025-08-29
"""

import os
import requests
from dotenv import load_dotenv
from utils.email_processor import clean_email_content
import time
import re

# ==============================
# CONFIGURAÇÕES
# ==============================
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Defina HF_API_TOKEN no .env")

HF_MODEL = "facebook/bart-large-mnli"  # modelo mais robusto
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

CANDIDATE_LABELS = [  # Lista de classes naturais para a classificação, para cada label a IA retorna uma pontuação de confiança (score)
    "email pedindo ajuda, suporte técnico ou resolução de problema (produtivo)",
    "email solicitando informações, orçamento ou documentos (produtivo)",
    "email sobre reunião, projeto, tarefa ou trabalho em andamento (produtivo)",
    "email de propaganda, marketing, desconto ou spam (improdutivo)",
    "email pessoal, cumprimentos, conversa informal ou correntes (improdutivo)"
]

LABEL_MAP = {
    "email pedindo ajuda, suporte técnico ou resolução de problema (produtivo)": "Produtivo",
    "email solicitando informações, orçamento ou documentos (produtivo)": "Produtivo",
    "email sobre reunião, projeto, tarefa ou trabalho em andamento (produtivo)": "Produtivo",
    "email de propaganda, marketing, desconto ou spam (improdutivo)": "Improdutivo",
    "email pessoal, cumprimentos, conversa informal ou correntes (improdutivo)": "Improdutivo"
}

CONFIDENCE_THRESHOLD = 0.55

KEYWORDS_PRODUTIVO = [
    "proposta", "orçamento", "reunião", "documento", "contrato", "pedido",
    "suporte", "assistência", "erro", "problema", "bloqueio", "relatório"
]
KEYWORDS_IMPRODUTIVO = ["desconto", "promoção",
                        "ganhe", "oferta", "cupom", "publicidade"]


# ==============================
# FUNÇÃO PRINCIPAL
# ==============================
def classificar_email(email_content: str) -> str:
    """
    Classifica um email como Produtivo ou Improdutivo usando IA Zero-Shot.
    Inclui threshold de confiança, pré-processamento, heurísticas e logs detalhados.
    """
    # Limpa conteúdo do e-mail
    email_content = clean_email_content(email_content)
    email_content = re.sub(r"\s+", " ", email_content).strip()

    # Se o e-mail está vazio ou muito curto → improdutivo direto
    if not email_content or len(email_content.split()) < 3:
        print("[LOG] Email muito curto → classificado como 'Improdutivo'")
        return "Improdutivo"

    # Heurísticas baseadas em palavras-chave antes de chamar a IA
    lower_content = email_content.lower()
    if any(k in lower_content for k in KEYWORDS_PRODUTIVO):
        print("[LOG] Palavra-chave produtiva detectada → classificado como 'Produtivo'")
        return "Produtivo"
    if any(k in lower_content for k in KEYWORDS_IMPRODUTIVO):
        print(
            "[LOG] Palavra-chave improdutiva detectada → classificado como 'Improdutivo'")
        return "Improdutivo"

    # Prepara requisição para a API
    payload = {
        "inputs": email_content,
        "parameters": {
            "candidate_labels": CANDIDATE_LABELS,
            "multi_label": False
        },
        "options": {"wait_for_model": True}
    }

    # Tenta 3 vezes em caso de erro ou timeout
    for attempt in range(3):
        try:
            response = requests.post(
                HF_API_URL, headers=HEADERS, json=payload, timeout=60
            )
            response.raise_for_status()
            result = response.json()

            if "labels" in result and "scores" in result:
                labels = result["labels"]
                scores = result["scores"]

                # Log detalhado dos scores
                print("\n[LOG] --- RESULTADO IA ---")
                for label, score in zip(labels, scores):
                    print(f"[LOG] {label}: {score:.4f}")
                print("[LOG] ----------------------")

                # Escolhe o label com o maior score, garantindo que o resultado seja o mais provável
                top_score = max(scores)
                top_label = labels[scores.index(top_score)]

                if top_score < CONFIDENCE_THRESHOLD:
                    print(
                        f"[LOG] Confiança baixa ({top_score:.2f}) → usando fallback")
                    return fallback_classificacao(email_content)

                print(f"[LOG] Escolhido pela IA: '{LABEL_MAP.get(top_label, 'Improdutivo')}' "
                      f"(confiança: {top_score:.2f})")
                return LABEL_MAP.get(top_label, "Improdutivo")

            print("[LOG] Resposta inesperada da IA → usando fallback")
            return fallback_classificacao(email_content)

        except requests.exceptions.Timeout:
            print(f"[LOG] Timeout na API, tentativa {attempt+1}/3...")
            time.sleep(2)
        except Exception as e:
            print(f"[LOG] Erro na API Hugging Face: {e}")
            time.sleep(2)

    print("[LOG] Todas as tentativas falharam → usando fallback")
    return fallback_classificacao(email_content)


# ==============================
# FALLBACK FINAL
# ==============================
def fallback_classificacao(email_content: str) -> str:
    """
    Classificação de fallback baseada em regras simples.
    Se palavras-chave produtivas estiverem presentes, retorna 'Produtivo', senão 'Improdutivo'.
    Isso garante que sempre haja uma classificação, mesmo se a IA falhar.
    """
    lower_content = email_content.lower()
    if any(k in lower_content for k in KEYWORDS_PRODUTIVO):
        return "Produtivo"
    if any(k in lower_content for k in KEYWORDS_IMPRODUTIVO):
        return "Improdutivo"
    return "Improdutivo"
