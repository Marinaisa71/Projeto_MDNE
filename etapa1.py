import re
import spacy
from collections import Counter


# Carregando o modelo do spaCy para português

processador = spacy.load("pt_core_news_sm")


# Lista inicial de comentários

comentarios = [
    "Eu amei esse filme, foi excelente!",
    "Achei o filme horrível, muito ruim.",
    "O filme é bom, mas o final não gostei.",
    "Não é um filme ruim, porém não é excelente.",
    "Gostei bastante da atuação dos atores."
]


# Entrada de um novo comentário pelo usuário

novo_comentario = input("Digite um comentário para análise (ou pressione Enter para pular): ")

if novo_comentario.strip() != "":
    comentarios.append(novo_comentario)


# Limpeza do texto utilizando Expressões Regulares (RE)

def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"\d+", "", texto)              # remoção de números
    texto = re.sub(r"[^\w\s]", "", texto)          # remoção de pontuação e símbolos
    texto = re.sub(r"\s+", " ", texto).strip()     # remoção de espaços extras
    return texto


# Listas de palavras positivas e negativas

palavras_positivas = ["bom", "excelente", "amar", "gostar", "ótimo"]
palavras_negativas = ["ruim", "horrível", "péssimo", "odiar", "não"]

# Processamento dos comentários com spaCy

resultados = []

for comentario in comentarios:
    texto_limpo = limpar_texto(comentario)
    resultado= processador(texto_limpo)                      #tokenização
    lemas = []
    for token in resultado:
        if not token.is_stop and not token.is_punct:          #filtragem de stop words
            lemas.append(token.lemma_)                  #lematização


    # Análise de sentimento 
    score = 0
    for lema in lemas:
        if lema in palavras_positivas:
            score += 1
        elif lema in palavras_negativas:
            score -= 1

    if score > 0:
        sentimento = "Positivo"
    elif score < 0:
        sentimento = "Negativo"
    else:
        sentimento = "Neutro"

    resultados.append({
        "comentario_original": comentario,
        "texto_limpo": texto_limpo,
        "lemas": lemas,
        "sentimento": sentimento
    })


# Exibição dos resultados individuais

print("\nRESULTADOS DA ANÁLISE:\n")

for r in resultados:
    print("Comentário original:", r["comentario_original"])
    print("Texto limpo:", r["texto_limpo"])
    print("Lemas:", r["lemas"])
    print("Sentimento:", r["sentimento"])
    print("-" * 50)


# Resumo final dos sentimentos

contagem_sentimentos = Counter([r["sentimento"] for r in resultados])

print("\nRESUMO FINAL:")
for sentimento, qtd in contagem_sentimentos.items():
    print(f"{sentimento}: {qtd}")
