from transformers import pipeline
import os

# Carrega token da variável de ambiente
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Defina a variável HF_API_TOKEN no seu .env")

# Inicializa pipeline zero-shot (sem use_auth_token)
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)


def classify_email(email_text: str) -> str:
    candidate_labels = ["Produtivo", "Improdutivo"]
    result = classifier(email_text, candidate_labels)
    label = result["labels"][0]  # Categoria mais provável
    return label
