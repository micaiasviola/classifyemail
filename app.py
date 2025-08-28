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

# ----- Imports da sua aplicação -----
from utils.fluxo_email import processar_email_com_resposta
from utils.email_processor import extract_text_from_pdf

# ===== Ambiente / Logging =====
load_dotenv()

API_KEY = os.environ.get("API_KEY")  # busca a variável do ambiente
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _gerar_secret_key() -> str:
    sk = os.getenv("SECRET_KEY")
    if not sk:
        sk = secrets.token_hex(24)
        logger.info("SECRET_KEY gerada automaticamente para sessões seguras.")
    return sk


# ===== Flask App =====
app = Flask(__name__)
app.config["SECRET_KEY"] = _gerar_secret_key()
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# (Opcional) servir favicon local para evitar erros 404 de /favicon.ico


@app.route("/favicon.ico")
def favicon():
    caminho_static = os.path.join(app.root_path, "static")
    return send_from_directory(
        caminho_static, "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


# ===== Helpers =====
def _obter_conteudo_email_da_requisicao(req) -> str:
    """
    Lê o conteúdo do email do formulário:
      - Campo de texto 'email_text', OU
      - Upload 'email_file' (txt ou pdf)
    Lança ValueError com mensagem amigável em caso de erro.
    """
    # Texto digitado
    texto = req.form.get("email_text", "").strip()
    if texto:
        logger.info("Processando texto direto de email.")
        return texto

    # Arquivo enviado
    if "email_file" in req.files:
        arquivo = req.files["email_file"]
        if not arquivo or not arquivo.filename:
            raise ValueError("Nenhum arquivo selecionado.")
        nome = arquivo.filename.lower()

        logger.info(f"Processando arquivo: {nome}")

        if nome.endswith(".txt"):
            # Tenta decodificar como UTF-8; ignora erros de encoding
            return arquivo.read().decode("utf-8", errors="ignore").strip()
        if nome.endswith(".pdf"):
            return extract_text_from_pdf(arquivo).strip()

        raise ValueError("Formato não suportado. Envie .txt ou .pdf.")

    # Nada encontrado
    raise ValueError("Nenhum conteúdo fornecido.")


# ===== Rotas =====
@app.route("/")
def index():
    """Página inicial com formulário."""
    return render_template("index.html")


@app.route("/classify", methods=["POST"])
def classify():
    """
    Recebe o email (texto ou arquivo), roda o fluxo completo:
    - classifica (Produtivo/Improdutivo)
    - gera resposta sugerida
    Armazena na sessão e devolve JSON com URL para a página de resultado.
    """
    try:
        conteudo = _obter_conteudo_email_da_requisicao(request)

        # Fluxo único (evita divergência entre rotas/implementações)
        resultado = processar_email_com_resposta(conteudo)
        categoria = resultado.get("categoria", "Improdutivo")
        resposta = resultado.get(
            "resposta", "Não foi possível gerar a resposta.")

        # Guarda um preview do conteúdo original
        preview = conteudo if len(
            conteudo) <= 1000 else f"{conteudo[:1000]}..."

        session["result"] = {
            "original_content": preview,
            "classification": categoria,
            "response": resposta,
        }

        logger.info(f"Email classificado como: {categoria}")
        return jsonify({"success": True, "redirect": url_for("result")})

    except ValueError as e:
        # Erros esperados do usuário (sem stacktrace)
        logger.warning(f"Requisição inválida: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Erros inesperados (mostra mensagem genérica ao cliente)
        logger.exception("Erro ao processar email:")
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500


@app.route("/result")
def result():
    """Exibe os resultados da última classificação/geração."""
    data = session.get("result")
    if not data:
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
    return jsonify({"error": "Arquivo muito grande. Máx: 16MB"}), 413


@app.errorhandler(404)
def not_found(e):
    # Se não houver 404.html, você pode trocar por um retorno JSON:
    # return jsonify({"error": "Rota não encontrada."}), 404
    return render_template("404.html"), 404


# ===== Execução =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"
    if debug_mode:
        logger.warning("⚠️  MODO DEBUG ATIVADO - Não use em produção!")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
