/**
 * Script para funcionalidades do frontend do Classificador de Emails - NOVA INTERFACE
 */

document.addEventListener('DOMContentLoaded', function () {
    // Elementos da nova interface
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('emailFile');
    const textInput = document.getElementById('emailText');
    const processBtn = document.getElementById('submitBtn');
    const progressBar = document.getElementById('progressBar');

    // Exemplos para teste
    const examples = {
        productive: "Prezados,\n\nEstou com um problema crítico no sistema de login desde ontem à tarde. Não consigo acessar minha conta para finalizar um relatório urgente que precisa ser entregue hoje.\n\nOs sintomas são: ao inserir minhas credenciais, recebo a mensagem 'Erro de autenticação' mesmo com a senha correta. Já tentei resetar a senha, mas o email de recuperação não chega.\n\nPor favor, preciso de assistência urgente pois isso está bloqueando todo o meu trabalho.\n\nAtenciosamente,\nJoão Silva\nAnalista Financeiro",
        unproductive: "Olá equipe,\n\nGostaria de desejar um feliz natal e um próspero ano novo para todos vocês!\n\nQue 2024 traga ainda mais sucesso para nossa empresa e que possamos continuar trabalhando juntos com essa energia positiva.\n\nAgradeço a todos pelo excelente trabalho realizado este ano e pela dedicação de sempre.\n\nGrande abraço,\nMaria Santos\nGerente de Departamento"
    };

    // Verificar se os elementos existem antes de adicionar event listeners
    if (!uploadArea || !fileInput || !textInput || !processBtn) {
        console.log('Página de resultados - funcionalidades reduzidas');
        setupResultsPage();
        return;
    }

    // Upload de arquivo
    uploadArea.addEventListener('click', function () {
        fileInput.click();
    });

    fileInput.addEventListener('change', function (e) {
        if (e.target.files.length > 0) {
            const fileName = e.target.files[0].name;
            uploadArea.innerHTML = `
                <i class="fas fa-file-alt"></i>
                <h3>${fileName}</h3>
                <p>Clique para selecionar outro arquivo</p>
                <input type="file" id="emailFile" name="email_file" hidden accept=".txt,.pdf">
            `;
            // Limpar textarea quando arquivo é selecionado
            textInput.value = '';
        }
    });

    // Arrastar e soltar
    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.style.background = 'rgba(255, 255, 255, 0.25)';
        this.style.borderColor = 'rgba(255, 255, 255, 0.8)';
    });

    uploadArea.addEventListener('dragleave', function () {
        this.style.background = 'rgba(255, 255, 255, 0.15)';
        this.style.borderColor = 'rgba(255, 255, 255, 0.4)';
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        this.style.background = 'rgba(255, 255, 255, 0.15)';
        this.style.borderColor = 'rgba(255, 255, 255, 0.4)';

        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            const fileName = e.dataTransfer.files[0].name;
            uploadArea.innerHTML = `
                <i class="fas fa-file-alt"></i>
                <h3>${fileName}</h3>
                <p>Clique para selecionar outro arquivo</p>
                <input type="file" id="emailFile" name="email_file" hidden accept=".txt,.pdf">
            `;
            // Limpar textarea quando arquivo é arrastado
            textInput.value = '';
        }
    });

    // Quando texto é inserido, limpar seleção de arquivo
    textInput.addEventListener('input', function () {
        if (this.value.trim() !== '') {
            fileInput.value = '';
            uploadArea.innerHTML = `
                <i class="fas fa-cloud-upload-alt"></i>
                <h3>Arraste ou clique para upload</h3>
                <p>Formatos suportados: .txt, .pdf (até 16MB)</p>
                <input type="file" id="emailFile" name="email_file" hidden accept=".txt,.pdf">
            `;
        }
    });

    // Processar email
    processBtn.addEventListener('click', function () {
        const hasFile = fileInput.files.length > 0;
        const hasText = textInput.value.trim() !== '';

        if (!hasFile && !hasText) {
            alert('Por favor, insira o texto do email ou faça upload de um arquivo.');
            return;
        }

        // Iniciar animação de processamento
        simulateProcessing();

        // Preparar dados para envio
        const formData = new FormData();

        if (hasFile) {
            formData.append('email_file', fileInput.files[0]);
        }

        if (hasText) {
            formData.append('email_text', textInput.value);
        }

        // Enviar para o backend
        fetch('/classify', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na resposta do servidor');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Redirecionar para página de resultados
                    window.location.href = `/result?classification=${encodeURIComponent(data.classification)}&response=${encodeURIComponent(data.response)}&content=${encodeURIComponent(data.original_content)}`;
                } else {
                    // Finalizar animação com erro
                    completeProcessing(false);
                    alert('Erro: ' + data.error);
                }
            })
            .catch(error => {
                // Finalizar animação com erro
                completeProcessing(false);
                alert('Erro ao processar a solicitação: ' + error.message);
            });
    });

    // Simular processamento (animação)
    function simulateProcessing() {
        processBtn.disabled = true;
        if (progressBar) progressBar.style.width = '0%';

        let width = 0;
        const interval = setInterval(function () {
            if (width >= 90) {
                clearInterval(interval);
            } else {
                width += 2;
                if (progressBar) progressBar.style.width = width + '%';
            }
        }, 30);
    }

    // Completa o processamento (sucesso ou erro)
    function completeProcessing(success) {
        if (progressBar) {
            progressBar.style.width = success ? '100%' : '0%';
        }
        processBtn.disabled = false;
    }

    // Inserir exemplos
    document.querySelectorAll('.insert-example').forEach(button => {
        button.addEventListener('click', function () {
            const exampleType = this.getAttribute('data-example');
            textInput.value = examples[exampleType];
            fileInput.value = '';

            // Limpar área de upload
            uploadArea.innerHTML = `
                <i class="fas fa-cloud-upload-alt"></i>
                <h3>Arraste ou clique para upload</h3>
                <p>Formatos suportados: .txt, .pdf (até 16MB)</p>
                <input type="file" id="emailFile" name="email_file" hidden accept=".txt,.pdf">
            `;
        });
    });

    // Configuração específica para a página de resultados
    function setupResultsPage() {
        // Copiar resposta
        const copyButton = document.querySelector('.copy-response');
        if (copyButton) {
            copyButton.addEventListener('click', function () {
                const responseText = document.querySelector('.response-text');
                if (!responseText) return;

                navigator.clipboard.writeText(responseText.textContent).then(() => {
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check me-1"></i> Copiado!';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                }).catch(err => {
                    alert('Falha ao copiar texto: ' + err);
                });
            });
        }
    }
    function cleanAIResponse(text) {
        // Remover processo de pensamento da IA se existir
        if (text.includes('Okay, the user wants me to respond') ||
            text.includes('Let me') ||
            text.includes('I need to')) {

            const lines = text.split('\n');
            let finalResponse = [];
            let inResponse = false;

            for (const line of lines) {
                const trimmedLine = line.trim();

                // Detectar início da resposta real
                if (!inResponse && (
                    trimmedLine.startsWith('Olá') ||
                    trimmedLine.startsWith('Prezado') ||
                    trimmedLine.startsWith('Caro') ||
                    trimmedLine.startsWith('Obrigado') ||
                    trimmedLine.startsWith('Agradeço')
                )) {
                    inResponse = true;
                }

                // Ignorar linhas de processo de pensamento
                if (inResponse && !trimmedLine.startsWith(('Okay', 'Let me', 'I need', 'Maybe', 'It\'s', 'I should', 'Alright'))) {
                    finalResponse.push(line);
                }
            }

            return finalResponse.length > 0 ? finalResponse.join('\n') : text;
        }

        return text;
    }
    // Inicializar a interface
    console.log('Sistema de classificação de emails inicializado com sucesso!');
});