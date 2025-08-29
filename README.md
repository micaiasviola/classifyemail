# Sistema de Classificação de Emails AutoU

Classifique automaticamente emails como **Produtivo** ou **Improdutivo** e gere respostas automáticas com IA. Suporte a texto direto ou upload de arquivos (.txt, .pdf). Interface web moderna e responsiva.

---

## 🌐 Acesse Online

Você pode acessar o sistema diretamente pelo navegador, sem instalar nada:

[https://classifyemail.onrender.com/](https://classifyemail.onrender.com/)

---

## 🚀 Como Utilizar o Site

1. **Acesse a página inicial**  
   Você verá três áreas principais:
   - **Verde:** Insira o texto do email ou faça upload de um arquivo (.txt ou .pdf).
   - **Azul:** Acompanhe o processamento do email pela IA.
   - **Vermelha:** Veja o resultado da classificação e a resposta sugerida.

2. **Inserindo Email**
   - Cole o texto do email no campo indicado **ou**
   - Clique ou arraste um arquivo .txt ou .pdf para a área de upload.

3. **Processar Email**
   - Clique em **Processar Email**.
   - Aguarde alguns segundos enquanto o sistema analisa e gera a resposta.

4. **Resultados**
   - Veja se o email foi classificado como **Produtivo** ou **Improdutivo**.
   - Confira a resposta automática sugerida.
   - Copie a resposta com um clique ou classifique outro email.

---

## 💻 Instalação Local

Siga os passos abaixo para rodar o sistema em sua máquina:

### 1. Pré-requisitos

- Python 3.13 (ou superior)
- Git
- Conta gratuita na [Hugging Face](https://huggingface.co/) para obter o token de API

### 2. Clone o Repositório

```bash
git clone https://github.com/micaiasviola/classifyemail.git
cd email-classifier
```

### 3. Crie e Ative um Ambiente Virtual (opcional, recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 4. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 5. Configure o Token da Hugging Face

Crie um arquivo `.env` na raiz do projeto e adicione seu token:

```
HF_API_TOKEN=seu_token_aqui
```

Você pode obter o token em: https://huggingface.co/settings/tokens

### 6. Execute o Sistema

```bash
python app.py
```

O site estará disponível em [http://localhost:5000](http://localhost:5000).

---

## 🛠️ Estrutura do Projeto

- `app.py` — Backend Flask principal
- `utils/` — Lógica de classificação, processamento e geração de respostas
- `templates/` — HTML das páginas
- `static/` — CSS, JS e imagens
- `requirements.txt` — Dependências Python

---

## 📝 Observações

- O sistema aceita arquivos `.txt` e `.pdf` de até 16MB.
- O processamento depende da API da Hugging Face — é necessário internet e o token válido.
- Para produção, recomenda-se configurar variáveis de ambiente seguras e usar servidores como Gunicorn.

---

## 📄 Licença

Veja o arquivo `LICENSE_EVALUATION.txt` para detalhes de uso.

---

## 🤝 Contribuição

Pull requests são bem-vindos! Para sugestões, abra uma issue.

---

## 📧 Suporte

Dúvidas? Entre em contato pelo