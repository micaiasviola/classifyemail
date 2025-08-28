from utils.classifier import classify_email

emails = [
    "Prezados, estou com um problema no sistema e não consigo acessar minha conta.",
    "Olá equipe, feliz natal e um ótimo ano novo para todos!"
]

for e in emails:
    print("Email:", e)
    print("Classificação:", classify_email(e))
    print("---")

