"""
Classificador de Emails com IA Zero-Shot + Heurísticas Avançadas
Mais rigoroso para classificar apenas emails de trabalho/negócio como produtivos.
Autor: Micaías Viola
Data: 2025-08-29
"""

import os
import requests
from dotenv import load_dotenv
import time
import re

# ==============================
# CONFIGURAÇÕES
# ==============================
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Defina HF_API_TOKEN no .env")

HF_MODEL = "facebook/bart-large-mnli"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Classes mais separadas para melhorar precisão
CANDIDATE_LABELS = [
    "email sobre trabalho, projetos, tarefas, reuniões ou negócios (produtivo)",
    "email solicitando informações, orçamento ou documentos profissionais (produtivo)",
    "email solicitando suporte técnico ou resolução de problemas (produtivo)",
    "email de propaganda ou marketing legítimo (improdutivo)",
    "email de golpe, phishing, fraude ou scam (improdutivo)",
    "email pessoal, cumprimentos, conversa informal, correntes ou brincadeiras (improdutivo)",
    "email de saudações, datas comemorativas ou felicitações (improdutivo)"
]

LABEL_MAP = {
    "email sobre trabalho, projetos, tarefas, reuniões ou negócios (produtivo)": "Produtivo",
    "email solicitando informações, orçamento ou documentos profissionais (produtivo)": "Produtivo",
    "email solicitando suporte técnico ou resolução de problemas (produtivo)": "Produtivo",
    "email de propaganda ou marketing legítimo (improdutivo)": "Improdutivo",
    "email de golpe, phishing, fraude ou scam (improdutivo)": "Improdutivo",
    "email pessoal, cumprimentos, conversa informal, correntes ou brincadeiras (improdutivo)": "Improdutivo",
    "email de saudações, datas comemorativas ou felicitações (improdutivo)": "Improdutivo"
}

# Ajuste para evitar falsos positivos
CONFIDENCE_THRESHOLD = 0.75
CONFIDENCE_MARGIN = 0.15

# Heurísticas — primeiro filtro rápido
KEYWORDS_PRODUTIVO = [
    "proposta", "orçamento", "reunião", "documento", "contrato", "pedido",
    "suporte", "assistência", "erro", "problema", "bloqueio", "relatório",
    "projeto", "implementação", "análise", "negócio", "parceria", "pagamento"
]

# Golpes e spam explícitos — prioridade máxima
KEYWORDS_GOLPE = [
    "parabéns", "contemplado", "benefício exclusivo", "últimos dígitos do cpf",
    "clique no link", "carro zero", "pix imediato", "ganhou", "prêmio", "sorteio",
    "transferência imediata", "oferta imperdível", "bônus garantido", "resgate seu benefício"
]

# Marketing genérico (não golpe, mas improdutivo)
KEYWORDS_MARKETING = [
    "desconto", "promoção", "ganhe", "oferta", "cupom", "publicidade",
    "cashback", "black friday", "frete grátis", "oferta relâmpago"
]


def classificar_email(email_content: str) -> str:
    """
    Classifica um email como Produtivo ou Improdutivo usando IA Zero-Shot.
    Incluí heurísticas fortes para golpes, thresholds mais altos e logs detalhados.
    """
    # Normaliza espaços e caracteres
    email_content = re.sub(r"\s+", " ", email_content).strip()

    # Se o e-mail está vazio ou muito curto → improdutivo
    if not email_content or len(email_content.split()) < 3:
        print("[LOG] Email muito curto → 'Improdutivo'")
        return "Improdutivo"

    lower_content = email_content.lower()

    # 1) Golpes têm prioridade máxima → bloqueia antes da IA
    if any(k in lower_content for k in KEYWORDS_GOLPE):
        print("[LOG] Palavra-chave de golpe detectada → 'Improdutivo'")
        return "Improdutivo"

    # 2) Marketing detectado → improdutivo
    if any(k in lower_content for k in KEYWORDS_MARKETING):
        print("[LOG] Palavra-chave de marketing detectada → 'Improdutivo'")
        return "Improdutivo"

    # 3) Palavras produtivas → sinal verde provisório, mas ainda passará pela IA
    heuristica_produtivo = any(k in lower_content for k in KEYWORDS_PRODUTIVO)

    # 4) Prepara requisição para IA
    payload = {
        "inputs": email_content,
        "parameters": {
            "candidate_labels": CANDIDATE_LABELS,
            "multi_label": False
        },
        "options": {"wait_for_model": True}
    }

    # Tenta 3 vezes em caso de falha
    for attempt in range(3):
        try:
            response = requests.post(
                HF_API_URL, headers=HEADERS, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()

            # Verifica se o resultado da API contém as chaves esperadas "labels" e "scores"
            if "labels" in result and "scores" in result:
                labels = result["labels"]
                scores = result["scores"]

                # Log detalhado
                print("\n[LOG] --- RESULTADO IA ---")
                # Percorre cada par de label e score para log
                for label, score in zip(labels, scores):
                    print(f"[LOG] {label}: {score:.4f}")
                print("[LOG] ----------------------")

                top_score = scores[0] # Maior score, API da hugging face já ordena em orden decrescente
                second_score = scores[1] if len(scores) > 1 else 0
                top_label = labels[0] # Pega o label com maior score
                final_label = LABEL_MAP.get(top_label, "Improdutivo") # Utiliza o LABEL_MAP para converter para "Produtivo" ou "Improdutivo"

                # 5) Confiança mínima — só confia se score for bem alto
                if top_score < CONFIDENCE_THRESHOLD or (top_score - second_score) < CONFIDENCE_MARGIN:
                    print(
                        f"[LOG] Confiança baixa ({top_score:.2f}) → fallback")
                    return fallback_classificacao(email_content, heuristica_produtivo)

                # 6) IA validou → retorna
                print(
                    f"[LOG] Escolhido: '{final_label}' (confiança: {top_score:.2f})")
                return final_label

            print("[LOG] Resposta inesperada da IA → fallback")
            return fallback_classificacao(email_content, heuristica_produtivo)

        except requests.exceptions.Timeout:
            print(f"[LOG] Timeout na API, tentativa {attempt+1}/3...")
            time.sleep(2)
        except Exception as e:
            print(f"[LOG] Erro na API: {e}")
            time.sleep(2)

    print("[LOG] Todas as tentativas falharam → fallback")
    return fallback_classificacao(email_content, heuristica_produtivo)


def fallback_classificacao(email_content: str, heuristica_produtivo: bool) -> str:
    """
    Classificação baseada apenas em heurísticas.
    Golpes têm prioridade > marketing > produtivo.
    """
    lower_content = email_content.lower()
    if any(k in lower_content for k in KEYWORDS_GOLPE):
        return "Improdutivo"
    if any(k in lower_content for k in KEYWORDS_MARKETING):
        return "Improdutivo"
    if heuristica_produtivo:
        return "Produtivo"
    return "Improdutivo"
