import re
import spacy
from collections import Counter
import requests
from bs4 import BeautifulSoup

# Carregando o modelo do spaCy para português
processador = spacy.load("pt_core_news_sm")

def coletar_comentarios_adorocinema():
    """
    ETAPA 2: WEB SCRAPING
    Coleta comentários sobre filmes do AdoroCinema
    """
    print("\n" + "="*60)
    #TAPA 2: COLETA DE DADOS COM WEB SCRAPING
    print("="*60)
    
    # URL correta para o filme "Ainda Estou Aqui" (brasileiro)
    url = "https://www.adorocinema.com/filmes/filme-265940/criticas/espectadores/"
    
    comentarios_coletados = []
    
    try:
        print(f"Acessando: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print("✓ Página acessada com sucesso!")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        criticas = soup.find_all('div', class_='content-txt')
        
        print(f"✓ Encontradas {len(criticas)} críticas na página")
        
        for i, critica in enumerate(criticas[:15], 1): 
            texto = critica.get_text().strip()
            if texto and len(texto) > 30: 
                comentarios_coletados.append(texto)
                print(f"  Comentário {i}: {texto[:100]}...")
        
        print(f"\n✓ Total coletado: {len(comentarios_coletados)} comentários")
        
    except Exception as e:
        print(f"✗ Erro na coleta: {e}")
        print("Usando comentários de exemplo...")
        comentarios_coletados = [
            "Filme excelente, muito emocionante! Amei cada momento. Atuações brilhantes de Fernanda Torres e Selton Melo.",
            "Não gostei do filme, achei muito longo e cansativo. A história não prende a atenção.",
            "O filme é bom, mas poderia ser melhor. A direção é competente, porém o roteiro é fraco.",
            "Ainda Estou Aqui é uma obra-prima! A maneira como retrata a ditadura é perfeita e emocionante.",
            "Que filme incrível! A atuação da Fernanda Torres está impecável, merece todos os prêmios.",
            "Não entendi o hype. O filme é lento demais e não desenvolve bem os personagens secundários.",
            "Simplesmente maravilhoso! Uma aula de história e um show de atuação. Recomendo fortemente!",
            "Achei o filme regular. Tem seus momentos bons, mas também tem partes muito arrastadas.",
            "Fantástico! A reconstituição de época é impecável e a trilha sonora é emocionante.",
            "Desnecessariamente longo. Poderia contar a mesma história em 1h30, mas se estende por 2h30."
        ]
    
    return comentarios_coletados

def limpar_texto(texto):
    """Limpeza básica com RE"""
    texto = texto.lower()
    texto = re.sub(r"\d+", "", texto)
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def analisar_sentimento_avancado(texto):
    """
    Análise de sentimento avançada considerando:
    - Intensidade das palavras
    - Negação (ex: "não gostei" vira negativo)
    - Contexto
    - Advérbios de intensidade (muito, pouco, extremamente)
    """
    
    # Dicionários com pesos (intensidade)
    palavras_positivas = {
        # Pesos fortes (+2)
        "excelente": 2, "brilhante": 2, "perfeito": 2, "obra prima":2, "obra-prima":2,
        "impecável": 2, "maravilhoso": 2, "fantástico": 2, "sensacional": 2,
        "magistral": 2, "genial": 2, "extraordinário": 2, "incrível": 2,
        
        # Pesos médios (+1.5)
        "incrível": 1.5, "emocionante": 1.5, "ótimo": 1.5, "lindo": 1.5,"amar":1.5,
        "emocionar": 1.5, "emocionado": 1.5, "emocionada": 1.5,
        
        # Pesos normais (+1)
        "bom": 1, "gostar": 1, "recomendar": 1, "belo": 1,
        "competente": 1, "acertar": 1, "acerto": 1, "qualidade": 1,
        
        # Verbos positivos
        "acertar": 1, "merecer": 1, "valer": 1,
    }
    
    palavras_negativas = {
        # Pesos fortes (-2)
        "horrível": -2, "péssimo": -2, "terrível": -2, "desastre": -2,
        "lixo": -2, "odiar": -2,
        
        # Pesos médios (-1.5)
        "decepcionante": -1.5, "frustrante": -1.5, "cansativo": -1.5,"longo":-1.5,
        
        # Pesos normais (-1)
        "ruim": -1, "fraco": -1, "chato": -1, "lento": -1, "arrastado": -1,
        "confuso": -1, "previsível": -1, "medíocre": -1, "regular": -1,
        "estranho": -1,
    }
    
    # Advérbios de intensidade (modificam o peso das palavras seguintes)
    intensificadores = {
        "muito": 1.5,
        "extremamente": 2.0,
        "bastante": 1.3,
        "demais": 1.5,
        "pouco": 0.5,  # reduz a intensidade
        "levemente": 0.3,
    }
    
    # Palavras de negação (invertem o sentimento)
    negacoes = {"não", "nem", "nunca", "jamais"}
    
    # Processa o texto com spaCy
    doc = processador(texto.lower())
    
    score = 0
    palavras_analisadas = []
    negar_proxima = False
    intensidade_atual = 1.0
    
    for token in doc:
        palavra = token.text
        lema = token.lemma_
        
        # Verifica se é palavra de negação
        if palavra in negacoes:
            negar_proxima = True
            palavras_analisadas.append(f"[NEGAÇÃO: {palavra}]")
            continue
        
        # Verifica se é intensificador
        if palavra in intensificadores:
            intensidade_atual = intensificadores[palavra]
            palavras_analisadas.append(f"[INTENSIFICADOR: {palavra} x{intensidade_atual}]")
            continue
        
        # Verifica se é palavra positiva
        if lema in palavras_positivas or palavra in palavras_positivas:
            peso_base = palavras_positivas.get(lema, palavras_positivas.get(palavra, 1))
            peso_final = peso_base * intensidade_atual
            
            if negar_proxima:
                peso_final = -peso_final  # inverte o sinal
                palavras_analisadas.append(f"{palavra} (NEGADO: {peso_final})")
                negar_proxima = False
            else:
                palavras_analisadas.append(f"+{palavra} ({peso_final})")
            
            score += peso_final
            intensidade_atual = 1.0  # reseta intensificador
        
        # Verifica se é palavra negativa
        elif lema in palavras_negativas or palavra in palavras_negativas:
            peso_base = palavras_negativas.get(lema, palavras_negativas.get(palavra, -1))
            peso_final = peso_base * intensidade_atual
            
            if negar_proxima:
                peso_final = -peso_final  # inverte o sinal (dupla negação vira positivo)
                palavras_analisadas.append(f"{palavra} (NEGADO: {peso_final})")
                negar_proxima = False
            else:
                palavras_analisadas.append(f"{palavra} ({peso_final})")
            
            score += peso_final
            intensidade_atual = 1.0  # reseta intensificador
        
        # Se não encontrou palavra relevante, mantém estado das negações
        else:
            # Se for pontuação, reseta a negação (fim da frase)
            if token.is_punct:
                negar_proxima = False
    
    return score, palavras_analisadas

def analisar_comentarios(comentarios):
    """Análise completa dos comentários"""
    
    resultados = []
    
    print("\n" + "="*60)
    #TAPA 1: ANÁLISE DE SENTIMENTO AVANÇADA
    print("="*60)
    
    for i, comentario in enumerate(comentarios, 1):
        print(f"\n--- Analisando comentário {i} ---")
        print(f"Texto: {comentario[:150]}...")
        
        # Análise avançada
        score, palavras_detectadas = analisar_sentimento_avancado(comentario)
        
        # Classificação com thresholds mais precisos
        if score >= 1.5:
            sentimento = "MUITO POSITIVO 🌟🌟🌟"
        elif score >= 0.5:
            sentimento = "POSITIVO 👍"
        elif score <= -1.5:
            sentimento = "MUITO NEGATIVO 💔💔"
        elif score <= -0.5:
            sentimento = "NEGATIVO 👎"
        else:
            sentimento = "NEUTRO/ MISTO ✨"
        
        # Mostra detalhes da análise
        print(f"Palavras analisadas: {palavras_detectadas}")
        print(f"Score: {score:.2f}")
        print(f"Sentimento: {sentimento}")
        
        resultados.append({
            "comentario": comentario,
            "score": score,
            "sentimento": sentimento,
            "detalhes": palavras_detectadas
        })
    
    return resultados

def main():
    """Função principal"""
    
    print("="*60)
    print("ANALISADOR DE SENTIMENTOS - AINDA ESTOU AQUI")
    print("="*60)
    
    # MENU
    print("\nEscolha a origem:")
    print("1. Coletar do AdoroCinema (Web Scraping)")
    print("2. Usar comentários de exemplo")
    print("3. Digitar manualmente")
    
    opcao = input("\nOpção (1, 2 ou 3): ").strip()
    
    # COLETA
    if opcao == "1":
        comentarios = coletar_comentarios_adorocinema()
    elif opcao == "2":
        comentarios = [
            "Filme excelente, muito emocionante! Amei cada momento. Atuações brilhantes de Fernanda Torres e Selton Melo.",
            "Não gostei do filme, achei muito longo e cansativo. A história não prende a atenção.",
            "O filme é bom, mas poderia ser melhor. A direção é competente, porém o roteiro é fraco.",
            "Ainda Estou Aqui é uma obra-prima! A maneira como retrata a ditadura é perfeita e emocionante.",
            "Que filme incrível! A atuação da Fernanda Torres está impecável, merece todos os prêmios."
        ]
        print(f"\nUsando {len(comentarios)} comentários de exemplo.")
    else:
        comentarios = []
        print("\nDigite seus comentários (Enter vazio para encerrar):")
        while True:
            coment = input("Comentário: ").strip()
            if not coment:
                break
            comentarios.append(coment)
    
    if not comentarios:
        print("Nenhum comentário para analisar.")
        return
    
    # ANÁLISE
    resultados = analisar_comentarios(comentarios)
    
    # RESUMO ESTATÍSTICO
    print("\n" + "="*60)
    print("RESUMO ESTATÍSTICO")
    print("="*60)
    
    scores = [r["score"] for r in resultados]
    sentimentos = [r["sentimento"] for r in resultados]
    
    # Estatísticas gerais
    print(f"\nTotal de comentários: {len(resultados)}")
    print(f"Score médio: {sum(scores)/len(scores):.2f}")
    print(f"Score mínimo: {min(scores):.2f}")
    print(f"Score máximo: {max(scores):.2f}")
    
    # Distribuição de sentimentos
    print("\nDistribuição:")
    contagem = Counter(sentimentos)
    for sent, qtd in contagem.items():
        porcentagem = (qtd/len(resultados))*100
        print(f"  {sent}: {qtd} ({porcentagem:.1f}%)")
    
    # Comentários mais relevantes
    print("\n" + "="*60)
    print("COMENTÁRIOS DESTAQUE")
    print("="*60)
    
    # Ordena por score (mais positivo e mais negativo)
    resultados_ordenados = sorted(resultados, key=lambda x: x["score"], reverse=True)
    
    print("\n🔝 MAIS POSITIVOS:")
    for r in resultados_ordenados[:2]:
        print(f"  Score: {r['score']:.2f} - {r['comentario'][:100]}...")
    
    print("\n📉 MAIS NEGATIVOS:")
    for r in resultados_ordenados[-2:]:
        print(f"  Score: {r['score']:.2f} - {r['comentario'][:100]}...")

if __name__ == "__main__":
    main()