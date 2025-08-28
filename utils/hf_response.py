# utils/hf_response.py
"""
Gerador de Respostas Automáticas usando Hugging Face Chat-Completion
Modelo: HuggingFaceTB/SmolLM3-3B
Autor: Micaías Viola
Data: 2025-08-27
"""
import re
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Carregar token do .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN")
if not HF_TOKEN:
    raise ValueError("Defina HF_TOKEN ou HF_API_TOKEN no .env")

# Inicializar cliente Hugging Face
client = InferenceClient(api_key=HF_TOKEN)


def extrair_resposta_final(texto: str) -> str:
    """
    Extrai apenas a resposta formal final de uma saída do modelo,
    removendo qualquer raciocínio interno.
    """
    # Tenta capturar a resposta a partir de um cumprimento formal
    padrao = r"(?:Prezado|Prezada|Prezados|Olá|Caro|Cara|Bom dia|Boa tarde|Boa noite)[\s\S]+"
    match = re.search(padrao, texto, flags=re.IGNORECASE)
    if match:
        return match.group(0).strip()

    # Se não encontrar cumprimento formal, pega a última seção após duas quebras de linha
    partes = texto.strip().split("\n\n")
    if len(partes) > 1:
        return partes[-1].strip()

    # Caso nada seja detectado, retorna todo o texto como fallback
    return texto.strip()


def gerar_resposta_chat(texto_email: str, categoria: str) -> str:
    """
    Gera resposta automática baseada na categoria do email
    usando chat-completion da Hugging Face.
    """
    if categoria == "Produtivo":
        prompt = (
            "Você é um assistente profissional. "
            "IMPORTANTE: A sua tarefa é gerar APENAS a mensagem final pronta para ser enviada. "
            "NUNCA explique o seu raciocínio, NUNCA descreva seus pensamentos internos, "
            "NÃO diga o que vai fazer, NÃO mostre anotações, NEM comentários internos. "
            "Responda diretamente como se estivesse enviando o email ao usuário.\n\n"
            f"Email recebido:\n{texto_email}\n\n"
            "Responda com uma mensagem educada, clara e profissional."
        )
    else:  # Improdutivo
        prompt = (
            "Você é um assistente cordial. "
            "IMPORTANTE: A sua tarefa é gerar APENAS a mensagem final pronta para ser enviada. "
            "NUNCA explique o seu raciocínio, NUNCA descreva seus pensamentos internos, "
            "NÃO diga o que vai fazer, NEM mostre comentários internos. "
            "Responda diretamente como se estivesse enviando o email ao usuário.\n\n"
            f"Email recebido:\n{texto_email}\n\n"
            "Responda com uma mensagem curta, amigável e educada."
        )

    try:
        completion = client.chat.completions.create(
            model="HuggingFaceTB/SmolLM3-3B",
            messages=[{"role": "user", "content": prompt}],
        )
        resposta = completion.choices[0].message["content"].strip()

        # Extrair somente a resposta formal final
        resposta_final = extrair_resposta_final(resposta)

        print(f"[LOG] Resposta final:\n{resposta_final}\n")
        return resposta_final

    except Exception as e:
        print(f"[LOG] Erro ao gerar resposta via Hugging Face: {e}")
        return texto_fallback(categoria)


def texto_fallback(categoria: str) -> str:
    """Texto seguro caso a API falhe"""
    if categoria == "Produtivo":
        return "Obrigado pelo contato. Nossa equipe analisará sua solicitação em breve."
    else:
        return "Obrigado pelo seu email. Desejamos um ótimo dia!"


def resposta_sugerida(texto_email: str, categoria: str) -> str:
    """Sugere uma resposta para o email baseado na categoria"""
    return gerar_resposta_chat(texto_email, categoria)


gerar_resposta = gerar_resposta_chat
