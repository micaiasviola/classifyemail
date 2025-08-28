"""
Módulo para geração de respostas automáticas baseadas em regras
"""
import random


class ResponseGenerator:
    """Gerador de respostas automáticas baseado em regras"""

    def __init__(self):
        # Respostas para emails produtivos
        self.productive_responses = [
            """Olá,

Obrigado pelo seu contato. Nossa equipe de suporte já foi notificada sobre sua solicitação e entrará em contato em breve para resolver sua questão.

Caso precise de assistência imediata, você também pode consultar nossa base de conhecimento em [link] ou entrar em contato pelo telefone [número].

Atenciosamente,
Equipe de Suporte""",

            """Prezado(a),

Agradecemos seu email. Sua solicitação foi registrada em nosso sistema sob o protocolo #[número] e será atendida por nossa equipe especializada.

O prazo estimado para retorno é de até 24 horas úteis.

Atenciosamente,
Equipe Técnica""",

            """Olá,

Recebemos sua mensagem e entendemos a urgência da situação. Nossa equipe já está analisando o caso e providenciará uma solução o mais breve possível.

Agradecemos sua paciência e compreensão.

Atenciosamente,
Departamento de Suporte"""
        ]

        # Respostas para emails improdutivos
        self.unproductive_responses = [
            """Olá,

Agradecemos suas amáveis palavras e o carinho com nossa equipe!

Desejamos a você também muito sucesso e felicidade.

Atenciosamente,
Equipe""",

            """Prezado(a),

Muito obrigado pelo seu contato e pelas gentis palavras.

É um prazer tê-lo(a) em nossa comunidade!

Atenciosamente,
Equipe""",

            """Olá,

Agradecemos seu email e seus votos de felicidades!

Retribuímos os sentimentos e desejamos um excelente [evento] para você e sua família.

Atenciosamente,
Equipe"""
        ]

        # Respostas personalizadas baseadas em palavras-chave
        self.specialized_responses = {
            'natal': """Olá,

Agradecemos seus votos de Feliz Natal! 

Desejamos a você e sua família um Natal repleto de alegria, paz e momentos especiais.

Atenciosamente,
Equipe""",

            'ano novo': """Olá,

Obrigado pelos votos de Ano Novo!

Que o próximo ano traga ainda mais sucesso, saúde e felicidade para todos nós.

Atenciosamente,
Equipe""",

            'problema': """Olá,

Entendemos que você está enfrentando um problema. Nossa equipe técnica já foi acionada e está trabalhando para resolver esta questão o mais rápido possível.

Agradecemos sua paciência e compreensão.

Atenciosamente,
Equipe de Suporte Técnico""",

            'urgente': """Olá,

Identificamos a urgência de sua solicitação. Estamos priorizando seu caso e entraremos em contato em até 1 hora útil.

Para emergências imediatas, favor contactar: [telefone de emergência].

Atenciosamente,
Equipe de Suporte"""
        }

    def generate_response(self, classification: str, original_text: str) -> str:
        """
        Gera resposta automática baseada na classificação e conteúdo

        Args:
            classification: Classificação do email ('Produtivo' ou 'Improdutivo')
            original_text: Texto original do email

        Returns:
            str: Resposta automática personalizada
        """
        text_lower = original_text.lower()

        # Primeiro verificar se há palavras-chave para respostas especializadas
        for keyword, response in self.specialized_responses.items():
            if keyword in text_lower:
                return response

        # Se não houver palavra-chave especial, usar respostas genéricas
        if classification == "Produtivo":
            return random.choice(self.productive_responses)
        else:
            return random.choice(self.unproductive_responses)


# Instância global do gerador de respostas
response_generator = ResponseGenerator()


def generate_response(original_content: str, classification: str) -> str:
    """
    Função principal para geração de respostas automáticas

    Args:
        original_content: Conteúdo original do email
        classification: Classificação do email

    Returns:
        str: Resposta automática
    """
    return response_generator.generate_response(classification, original_content)
