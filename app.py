# app.py
"""
Sistema de Classificação e Resposta Automática de Emails
Versão: 4.1 - Hugging Face API
Autor: Micaías Viola
"""

import os
import logging
import secrets
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, send_from_directory
)

# ----- Imports da minha aplicação -----
# Função principal que processa e classifica o email
from utils.fluxo_email import processar_email_com_resposta

# Função para extrair texto de PDFs
from utils.email_processor import extract_text_from_pdf

# ===== Ambiente / Logging =====
load_dotenv()  # Carrega variáveis do arquivo .env

# Busca API_KEY do ambiente (não usada diretamente aqui)
API_KEY = os.environ.get("API_KEY")
logging.basicConfig(level=logging.INFO)  # Configura nível de log
logger = logging.getLogger(__name__)     # Instancia logger para o app

def _gerar_secret_key() -> str:
    """
    Gera uma chave secreta para sessões Flask.
    Usa a variável de ambiente SECRET_KEY se existir, senão gera uma aleatória.
    """
    sk = os.getenv("SECRET_KEY")
    if not sk:
        sk = secrets.token_hex(24)
        logger.info("SECRET_KEY gerada automaticamente para sessões seguras.")
    return sk


# ===== Flask App =====
app = Flask(__name__)  # Cria instância do Flask
# Define chave secreta para sessões
app.config["SECRET_KEY"] = _gerar_secret_key()
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Limita uploads a 16MB

# ===== Helpers =====
def _obter_conteudo_email_da_requisicao(req) -> str:
    """
    Lê o conteúdo do email do formulário:
      - Campo de texto 'email_text', OU
      - Upload 'email_file' (txt ou pdf)
    Lança ValueError com mensagem amigável em caso de erro.
    """
    texto = req.form.get("email_text", "").strip(
    )  # Tenta pegar texto digitado
    if texto:
        logger.info("Processando texto direto de email.")
        return texto

    # Se não há texto, tenta pegar arquivo
    if "email_file" in req.files:
        arquivo = req.files["email_file"]
        if not arquivo or not arquivo.filename:
            raise ValueError("Nenhum arquivo selecionado.")
        nome = arquivo.filename.lower()

        logger.info(f"Processando arquivo: {nome}")

        if nome.endswith(".txt"):
            # Lê arquivo txt como UTF-8
            return arquivo.read().decode("utf-8", errors="ignore").strip()
        if nome.endswith(".pdf"):
            # Extrai texto de PDF
            return extract_text_from_pdf(arquivo).strip()

        raise ValueError("Formato não suportado. Envie .txt ou .pdf.")

    # Se não há texto nem arquivo
    raise ValueError("Nenhum conteúdo fornecido.")

# ===== Rotas =====
@app.route("/")
def index():
    """Página inicial com formulário."""
    return render_template("index.html")  # Renderiza página principal

@app.route("/classify", methods=["POST"])
def classify():
    """
    Recebe o email (texto ou arquivo), roda o fluxo completo:
    - classifica (Produtivo/Improdutivo)
    - gera resposta sugerida
    Armazena na sessão e devolve JSON com URL para a página de resultado.
    """
    try:
        conteudo = _obter_conteudo_email_da_requisicao(
            request)  # Pega conteúdo do email

        resultado = processar_email_com_resposta(
            conteudo)       # Classifica e gera resposta
        categoria = resultado.get(
            "categoria", "Improdutivo")    # Pega categoria
        resposta = resultado.get(
            "resposta", "Não foi possível gerar a resposta.")  # Pega resposta

        # Guarda um preview do conteúdo original (até 1000 caracteres)
        preview = conteudo if len(
            conteudo) <= 1000 else f"{conteudo[:1000]}..."

        # Salva resultado na sessão do usuário
        session["result"] = {
            "original_content": preview,
            "classification": categoria,
            "response": resposta,
        }

        logger.info(f"Email classificado como: {categoria}")
        # Retorna URL para página de resultado
        return jsonify({"success": True, "redirect": url_for("result")})

    except ValueError as e:
        # Erros esperados do usuário (ex: arquivo inválido)
        logger.warning(f"Requisição inválida: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Erros inesperados (exibe mensagem genérica)
        logger.exception("Erro ao processar email:")
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

@app.route("/result")
def result():
    """Exibe os resultados da última classificação/geração."""
    data = session.get("result")
    if not data:
        # Se não há resultado, volta para início
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        original_content=data["original_content"],
        classification=data["classification"],
        response=data["response"],
    )

@app.route("/api/classify", methods=["POST"])
def api_classify():
    """
    Endpoint JSON (programático).
    Espera: { "email_content": "..." }
    Retorna: { success, classification, response, original_content_preview }
    """
    try:
        payload = request.get_json(silent=True) or {}
        conteudo = (payload.get("email_content") or "").strip()
        if not conteudo:
            return jsonify({"error": "Conteúdo do email não fornecido."}), 400

        resultado = processar_email_com_resposta(conteudo)

        preview = conteudo if len(conteudo) <= 200 else f"{conteudo[:200]}..."

        return jsonify(
            {
                "success": True,
                "classification": resultado.get("categoria", "Improdutivo"),
                "response": resultado.get("resposta", "Não foi possível gerar a resposta."),
                "original_content_preview": preview,
            }
        )

    except Exception as e:
        logger.exception("Erro na API /api/classify:")
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

# ===== Tratadores de erro =====
@app.errorhandler(413)
def too_large(e):
    # Retorna erro se arquivo for maior que 16MB
    return jsonify({"error": "Arquivo muito grande. Máx: 16MB"}), 413

@app.errorhandler(404)
def not_found(e):
    # Retorna página 404 customizada
    return render_template("404.html"), 404


@app.route("/favicon.ico")
def favicon():
    # Serve favicon local para evitar erro no navegador
    caminho_static = os.path.join(app.root_path, "static")
    return send_from_directory(
        caminho_static, "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )

# ===== Execução =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Porta do servidor
    debug_mode = os.environ.get(
        "DEBUG", "False").lower() == "true"  # Modo debug
    if debug_mode:
        logger.warning("⚠️  MODO DEBUG ATIVADO - Não use em produção!")
    # Inicia o servidor Flask
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
