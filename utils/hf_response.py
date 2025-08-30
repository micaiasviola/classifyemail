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


def limpar_raciocinio_interno(texto: str) -> str:
    
    # Remove qualquer frase que pareça raciocínio interno ou conteúdo não solicitado.
   
    # Remove textos comuns de pensamento do modelo (em inglês e português)
    padroes = [
        r"(?i)(let me|i should|they want|maybe|so i|alright|let's|okay,|então vou|preciso|vou pensar|deixa eu).*",
        r"(?i)(analisando|pensando|raciocínio|planejando).*"
    ]
    for padrao in padroes:
        texto = re.sub(padrao, "", texto).strip() # Remove os textos que combinam com o padrão e retorna o texto limpo
    return texto

def extrair_resposta_final(texto: str) -> str:
    """
    Extrai apenas a resposta formal final de uma saída do modelo,
    removendo qualquer raciocínio interno.
    """

    # 1) Limpa raciocínio interno
    texto = limpar_raciocinio_interno(texto)

    # 2) Tenta encontrar mensagens que começam com cumprimentos
    padrao = r"(?:Prezado|Prezada|Prezados|Olá|Caro|Cara|Bom dia|Boa tarde|Boa noite)[\s\S]+"
    match = re.search(padrao, texto, flags=re.IGNORECASE)
    if match:
        return match.group(0).strip()

    # 3) Se não encontrar, divide o texto em partes após duas quebras de linha (geralmente é a resposta)
    partes = texto.strip().split("\n\n")
    if len(partes) > 1:
        return limpar_raciocinio_interno(partes[-1].strip())

    # Caso nada seja detectado, retorna todo o texto limpo
    return texto.strip()

def gerar_resposta_chat(texto_email: str, categoria: str) -> str:
    """
    Gera resposta automática baseada na categoria do email
    usando chat-completion da Hugging Face.
    """
    if categoria == "Produtivo": # Prompt especifico para o modelo Produtivo
        prompt = (
            "Você é um assistente profissional. "
            "IMPORTANTE: Sua tarefa é responder APENAS com a mensagem final pronta para envio. "
            "PROIBIDO explicar raciocínio, planejar a resposta ou dar justificativas. "
            "NÃO escreva nada sobre o que você vai fazer, NEM descreva seus pensamentos. "
            "Responda SOMENTE em português, com uma mensagem clara, educada e profissional.\n\n"
            f"Email recebido:\n{texto_email}\n\n"
            "Mensagem final:"
        )
    else:  # Prompt especifico para o modelo Improdutivo
        prompt = (
            "Você é um assistente cordial. "
            "IMPORTANTE: Sua tarefa é responder APENAS com a mensagem final pronta para envio. "
            "PROIBIDO explicar raciocínio, planejar a resposta ou dar justificativas. "
            "NÃO escreva nada sobre o que você vai fazer, NEM descreva seus pensamentos. "
            "Responda SOMENTE em português, com uma mensagem curta, amigável e educada.\n\n"
            f"Email recebido:\n{texto_email}\n\n"
            "Mensagem final:"
        )

    try:
        # 1) Envia o prompt para o modelo de chat da Hugging Face
        completion = client.chat.completions.create(
            model="HuggingFaceTB/SmolLM3-3B",
            messages=[{"role": "user", "content": prompt}],
        )

        # 2) Extrai a resposta do modelo, pega a primeira resposta gerada
        resposta = completion.choices[0].message["content"].strip() 

        # 3) Usa a função para extrair a resposta final para garantir que a resposta venha sem o raciocínio interno
        resposta_final = extrair_resposta_final(resposta)

        print(f"[LOG] Resposta final:\n{resposta_final}\n")
        return resposta_final

    except Exception as e:
        print(f"[LOG] Erro ao gerar resposta via Hugging Face: {e}")
        return texto_fallback(categoria)

# 4) Textos de fallback seguros para casos de falha
def texto_fallback(categoria: str) -> str:
    """Texto seguro caso a API falhe"""
    if categoria == "Produtivo":
        return "Obrigado pelo contato. Nossa equipe analisará sua solicitação em breve."
    else:
        return "Obrigado pelo seu email. Desejamos um ótimo dia!"

# Alias da geração de resposta para facilitar a importação em outros modulos
def resposta_sugerida(texto_email: str, categoria: str) -> str:
    """Sugere uma resposta para o email baseado na categoria"""
    return gerar_resposta_chat(texto_email, categoria)

gerar_resposta = gerar_resposta_chat
