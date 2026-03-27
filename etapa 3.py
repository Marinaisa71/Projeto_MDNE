import re
import spacy
from collections import Counter
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
# Carregando o modelo do spaCy para portuguГЄs
processador = spacy.load("pt_core_news_sm")
def coletar_comentarios_adorocinema():
"""Coleta comentГЎrios do AdoroCinema"""
print("\n" + "="*60)
print("COLETA DE DADOS COM WEB SCRAPING")
print("="*60)
url = "https://www.adorocinema.com/filmes/filme-265940/criticas/espectadores/"
comentarios_coletados = []
try:
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'html.parser')
criticas = soup.find_all('div', class_='content-txt')
for critica in criticas[:15]:
texto = critica.get_text().strip()
if texto and len(texto) > 30:
comentarios_coletados.append(texto)
print(f"вњ“ Coletados {len(comentarios_coletados)} comentГЎrios")
except Exception as e:
print(f"вњ— Erro na coleta: {e}")
comentarios_coletados = [
"Um dos melhores filmes do ano! Fernanda Torres estГЎ magnГ-fica e deverГЎ ser indicada ao Oscar",
"Filme excelente, muito emocionante! Amei cada momento. AtuaГ§Гµes brilhantes.",
"NГЈo gostei do filme, achei muito longo e cansativo. A histГіria nГЈo prende.",
"O filme Г© bom, mas poderia ser melhor. A direГ§ГЈo Г© competente.",
"Ainda Estou Aqui Г© uma obra-prima! Perfeito em todos os aspectos.",
"Que filme incrГ-vel! AtuaГ§ГЈo impecГЎvel, merece todos os prГЄmios.",
"NГЈo entendi o hype. Filme lento e nГЈo desenvolve os personagens.",
"Simplesmente maravilhoso! Uma aula de histГіria, recomendo fortemente!",
"Achei o filme regular. Tem momentos bons, mas outros muito arrastados.",
"FantГЎstico! Melhor filme do ano, sem dГєvidas!",
"PГ©ssimo! Perda de tempo, nГЈo recomendo pra ninguГ©m."
]
return comentarios_coletados
def analise_spacy_completa(texto):
doc = processador(texto)
#TOKENIZAГ‡ГѓO:
tokens = [token.text for token in doc if not token.is_punct]
print(f" {tokens[:15]}...")
#LEMATIZAГ‡ГѓO
lemas = [f"{token.text} в†’ {token.lemma_}" for token in doc if not token.is_punct][:15]
for lema in lemas:
print(f" {lema}")
#POS TAGGING:
pos = [f"{token.text} ({token.pos_})" for token in doc if not token.is_punct][:15]
for p in pos:
print(f" {p}")
#NOUN CHUNKS (Frases Nominais)
chunks = [chunk.text for chunk in doc.noun_chunks][:8]
for chunk in chunks:
print(f" {chunk}")
#ENTIDADES NOMEADAS
if doc.ents:
for ent in doc.ents[:8]:
print(f" {ent.text} в†’ {ent.label_} ({spacy.explain(ent.label_)})")
else:
print(" Nenhuma entidade encontrada")
#SEGMENTAГ‡ГѓO DE SENTENГ‡AS
sentencas = list(doc.sents)
print(f" Total: {len(sentencas)} sentenГ§as")
for i, sent in enumerate(sentencas[:5], 1):
print(f" {i}. {sent.text[:100]}...")
def analisar_sentimento_melhorado(texto):
#AnГЎlise de sentimento com dicionГЎrios completos
palavras_positivas = {
# Muito positivas (+3)
"magnГ-fica": 3, "magnГ-fico": 3, "espetacular": 3, "extraordinГЎrio": 3,
# Muito positivas (+2.5)
"obra-prima": 2.5, "obra prima": 2.5, "masterpiece": 2.5,
# Muito positivas (+2)
"excelente": 2, "maravilhoso": 2, "perfeito": 2, "impecГЎvel": 2,
"fantГЎstico": 2, "sensacional": 2, "brilhante": 2, "genial": 2,
# Positivas (+1.5)
"incrГ-vel": 1.5, "emocionante": 1.5, "lindo": 1.5, "amei": 1.5,
"fabuloso": 1.5, "magnГ-fico": 1.5,
# Positivas (+1)
"bom": 1, "Гіtimo": 1, "gostei": 1, "recomendo": 1, "legal": 1,
"bacana": 1, "interessante": 1, "competente": 1, "boa": 1,
# Verbos positivos
"aclamar": 1.5, "indicar": 1, "merecer": 1.5, "valer": 1
}
palavras_negativas = {
# Muito negativas (-3)
"pГ©ssimo": -3, "horrГ-vel": -3, "terrГ-vel": -3, "lixo": -3,
# Muito negativas (-2.5)
"decepcionante": -2.5, "odiei": -2.5,
# Negativas (-2)
"cansativo": -2, "chato": -2, "arrastado": -2, "frustrante": -2,
"entediante": -2,
# Negativas (-1.5)
"ruim": -1.5, "fraco": -1.5, "lento": -1.5,
# Levemente negativas (-1)
"regular": -1, "confuso": -1, "previsГ-vel": -1, "medГ-ocre": -1
}
# Intensificadores
intensificadores = {
"muito": 1.5, "extremamente": 2.0, "bastante": 1.3,
"demais": 1.5, "tГЈo": 1.3, "super": 1.4, "realmente": 1.3,
"absolutamente": 1.5
}
# Palavras de negaГ§ГЈo
negacoes = {"nГЈo", "nem", "nunca", "jamais", "nunca"}
# Frases positivas compostas
frases_positivas = [
"um dos melhores", "melhor filme", "deverГЎ ser indicada",
"merece o oscar", "obra prima", "imperdГ-vel"
]
# Frases negativas compostas
frases_negativas = [
"nГЈo gostei", "nГЈo recomendo", "nГЈo vale", "deixa a desejar",
"perda de tempo"
]
texto_lower = texto.lower()
score = 0
palavras_detectadas = []
# 1. Verificar frases compostas positivas
for frase in frases_positivas:
if frase in texto_lower:
if "melhor" in frase:
score += 2
palavras_detectadas.append(f" '{frase}' (+2)")
else:
score += 1.5
palavras_detectadas.append(f" '{frase}' (+1.5)")
# 2. Verificar frases compostas negativas
for frase in frases_negativas:
if frase in texto_lower:
score -= 2
palavras_detectadas.append(f" '{frase}' (-2)")
# 3. Processar com spaCy para contexto
doc = processador(texto_lower)
negar_proximo = False
intensidade = 1.0
for i, token in enumerate(doc):
palavra = token.text
lemma = token.lemma_
# Verificar negaГ§ГЈo
if palavra in negacoes:
negar_proximo = True
continue
# Verificar intensificador
if palavra in intensificadores:
intensidade = intensificadores[palavra]
palavras_detectadas.append(f" intensificador: {palavra} (x{intensidade})")
continue
# Verificar palavra positiva
if lemma in palavras_positivas or palavra in palavras_positivas:
peso = palavras_positivas.get(lemma, palavras_positivas.get(palavra, 1))
peso_final = peso * intensidade
if negar_proximo:
peso_final = -peso_final
palavras_detectadas.append(f" {palavra} (negado: {peso_final})")
negar_proximo = False
else:
palavras_detectadas.append(f" {palavra} (+{peso_final})")
score += peso_final
intensidade = 1.0
# Verificar palavra negativa
elif lemma in palavras_negativas or palavra in palavras_negativas:
peso = palavras_negativas.get(lemma, palavras_negativas.get(palavra, -1))
peso_final = peso * intensidade
if negar_proximo:
peso_final = -peso_final
palavras_detectadas.append(f" {palavra} (negado, virou positivo: {peso_final})")
negar_proximo = False
else:
palavras_detectadas.append(f" {palavra} ({peso_final})")
score += peso_final
intensidade = 1.0
# Resetar negaГ§ГЈo se encontrar pontuaГ§ГЈo
if token.is_punct:
negar_proximo = False
# Mostrar palavras detectadas
if palavras_detectadas:
print(" Palavras/frases analisadas:")
for p in palavras_detectadas[:10]:
print(f" {p}")
# ClassificaГ§ГЈo
if score >= 2.5:
sentimento = "MUITO POSITIVO"
elif score >= 1.5:
sentimento = "POSITIVO"
elif score >= 0.5:
sentimento = "LEVEMENTE POSITIVO"
elif score <= -2.5:
sentimento = "MUITO NEGATIVO"
elif score <= -1.5:
sentimento = "NEGATIVO"
elif score <= -0.5:
sentimento = "LEVEMENTE NEGATIVO"
else:
sentimento = "NEUTRO/MISTO"
return score, sentimento, palavras_detectadas
def analise_com_embeddings(comentarios):
print("\n" + "="*60)
print("ANГЃLISE COM EMBEDDINGS")
print("="*60)
# DicionГЎrio expandido
palavras = {
# Muito positivas (+3)
"magnГ-fica": 3, "magnГ-fico": 3, "espetacular": 3,
# Muito positivas (+2.5)
"obra-prima": 2.5, "obra prima": 2.5,
# Muito positivas (+2)
"excelente": 2, "maravilhoso": 2, "perfeito": 2, "impecГЎvel": 2,
"fantГЎstico": 2, "brilhante": 2, "genial": 2,
# Positivas (+1.5)
"incrГ-vel": 1.5, "emocionante": 1.5, "amei": 1.5, "lindo": 1.5,
# Positivas (+1)
"bom": 1, "Гіtimo": 1, "gostei": 1, "recomendo": 1,
"merece": 1, "indicada": 1,
# Negativas
"ruim": -1.5, "fraco": -1.5, "lento": -1.5,
"chato": -2, "cansativo": -2, "arrastado": -2,
"pГ©ssimo": -3, "horrГ-vel": -3
}
# Frases especiais
frases_especiais = {
"um dos melhores": 2.5,
"melhor filme": 2.5,
"deverГЎ ser indicada": 2,
"merece o oscar": 2.5,
"obra prima": 2.5,
"nГЈo gostei": -2,
"nГЈo recomendo": -2,
"perda de tempo": -2.5
}
scores = []
for comentario in comentarios:
score = 0
comentario_lower = comentario.lower()
palavras_encontradas = []
# Verificar frases especiais primeiro
for frase, peso in frases_especiais.items():
if frase in comentario_lower:
score += peso
palavras_encontradas.append(f"{frase}({peso:+})")
# Verificar palavras individuais
for palavra, peso in palavras.items():
if palavra in comentario_lower:
# Evitar contar duas vezes
if palavra not in [f.split('(')[0] for f in palavras_encontradas]:
score += peso
palavras_encontradas.append(f"{palavra}({peso:+})")
scores.append(score)
print(f"\n ComentГЎrio: {comentario[:100]}...")
print(f" Palavras/frases: {', '.join(palavras_encontradas[:8])}")
print(f" Score: {score:.2f}")
if score >= 2:
print(f" в†’ MUITO POSITIVO")
elif score >= 1:
print(f" в†’ POSITIVO")
elif score >= 0.5:
print(f" в†’ LEVEMENTE POSITIVO")
elif score <= -2:
print(f" в†’ MUITO NEGATIVO")
elif score <= -1:
print(f" в†’ NEGATIVO")
elif score <= -0.5:
print(f" в†’ LEVEMENTE NEGATIVO")
else:
print(f" в†’ NEUTRO/MISTO")
return scores
def graficos_final(comentarios, scores_regras, scores_embeddings=None):
#GrГЎficos finais
plt.style.use('seaborn-v0_8-darkgrid')
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
# 1. DistribuiГ§ГЈo dos scores
axes[0, 0].hist(scores_regras, bins=12, edgecolor='black', color='steelblue', alpha=0.7)
axes[0, 0].axvline(x=0, color='red', linestyle='--', alpha=0.5, label='Neutro')
axes[0, 0].axvline(x=np.mean(scores_regras), color='green', linestyle='--', alpha=0.7, label=f'MГ©dia: {np.mean(scores_regras):.2f}')
axes[0, 0].set_title('DistribuiГ§ГЈo dos Scores de Sentimento', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Score')
axes[0, 0].set_ylabel('FrequГЄncia')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)
# 2. Categorias de sentimento
sentimentos = []
for score in scores_regras:
if score >= 2.5:
sentimentos.append('Muito Positivo')
elif score >= 1.5:
sentimentos.append('Positivo')
elif score >= 0.5:
sentimentos.append('Leve Positivo')
elif score <= -2.5:
sentimentos.append('Muito Negativo')
elif score <= -1.5:
sentimentos.append('Negativo')
elif score <= -0.5:
sentimentos.append('Leve Negativo')
else:
sentimentos.append('Neutro')
contagem = Counter(sentimentos)
cores = ['darkgreen', 'green', 'lightgreen', 'gray', 'lightsalmon', 'red', 'darkred']
barras = axes[0, 1].bar(contagem.keys(), contagem.values(), color=cores[:len(contagem)])
axes[0, 1].set_title('DistribuiГ§ГЈo por Categoria', fontsize=12, fontweight='bold')
axes[0, 1].tick_params(axis='x', rotation=45)
for barra in barras:
altura = barra.get_height()
axes[0, 1].text(barra.get_x() + barra.get_width()/2., altura,
 f'{int(altura)}', ha='center', va='bottom')
# 3. GrГЎfico de pizza
axes[1, 0].pie(contagem.values(), labels=contagem.keys(), autopct='%1.1f%%',
 colors=cores[:len(contagem)], startangle=90)
axes[1, 0].set_title('ProporГ§ГЈo de Sentimentos', fontsize=12, fontweight='bold')
# 4. ComparaГ§ГЈo
if scores_embeddings:
axes[1, 1].scatter(scores_regras, scores_embeddings, s=80, alpha=0.6, c='steelblue')
min_val = min(min(scores_regras), min(scores_embeddings))
max_val = max(max(scores_regras), max(scores_embeddings))
axes[1, 1].plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='CorrelaГ§ГЈo ideal')
correlacao = np.corrcoef(scores_regras, scores_embeddings)[0, 1]
axes[1, 1].set_title(f'ComparaГ§ГЈo: Regras vs Embeddings\nCorrelaГ§ГЈo: {correlacao:.2f}', fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel('Score Regras')
axes[1, 1].set_ylabel('Score Embeddings')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)
plt.suptitle('AnГЎlise de Sentimentos - "Ainda Estou Aqui"', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('analise_sentimentos_final.png', dpi=300, bbox_inches='tight')
print("\nвњ… GrГЎfico salvo como 'analise_sentimentos_final.png'")
plt.show()
def main():
print("="*60)
print("ANALISADOR DE SENTIMENTOS - TERCEIRA ETAPA")
print("Ainda Estou Aqui")
print("="*60)
# Menu
print("\nESCOLHA A ORIGEM:")
print("1. Coletar do AdoroCinema")
print("2. Usar comentГЎrios de exemplo")
opcao = input("\nOpГ§ГЈo (1 ou 2): ").strip()
if opcao == "1":
comentarios = coletar_comentarios_adorocinema()
else:
comentarios = [
"Um dos melhores filmes do ano! Fernanda Torres estГЎ magnГ-fica e deverГЎ ser indicada ao Oscar",
"Filme excelente, muito emocionante! Amei cada momento. AtuaГ§Гµes brilhantes.",
"NГЈo gostei do filme, achei muito longo e cansativo. A histГіria nГЈo prende.",
"O filme Г© bom, mas poderia ser melhor. A direГ§ГЈo Г© competente.",
"Ainda Estou Aqui Г© uma obra-prima! Perfeito em todos os aspectos.",
"Que filme incrГ-vel! AtuaГ§ГЈo impecГЎvel, merece todos os prГЄmios.",
"NГЈo entendi o hype. Filme lento e nГЈo desenvolve os personagens.",
"Simplesmente maravilhoso! Uma aula de histГіria, recomendo fortemente!",
"Achei o filme regular. Tem momentos bons, mas outros muito arrastados.",
"FantГЎstico! Melhor filme do ano, sem dГєvidas!",
"PГ©ssimo! Perda de tempo, nГЈo recomendo pra ninguГ©m."
]
print(f"\nвњ“ {len(comentarios)} comentГЎrios carregados")
# 1. DEMONSTRAГ‡ГѓO SPACY
print("\n" + "="*60)
print("ETAPA 1: ANГЃLISE COMPLETA COM SPACY")
print("="*60)
analise_spacy_completa(comentarios[0])
# 2. ANГЃLISE DE SENTIMENTOS MELHORADA
print("\n" + "="*60)
print("ETAPA 2: ANГЃLISE DE SENTIMENTOS")
print("="*60)
scores_regras = []
for i, comentario in enumerate(comentarios, 1):
print(f"\n--- Analisando comentГЎrio {i} ---")
print(f" Texto: {comentario}")
score, sentimento, palavras = analisar_sentimento_melhorado(comentario)
scores_regras.append(score)
print(f"\n RESULTADO FINAL:")
print(f" Score: {score:.2f}")
print(f" Sentimento: {sentimento}")
print("-" * 50)
# 3. EMBEDDINGS
scores_embeddings = analise_com_embeddings(comentarios)
# 4. GRГЃFICOS
graficos_final(comentarios, scores_regras, scores_embeddings)
# 5. RESUMO FINAL
print("\n" + "="*60)
print("RESUMO FINAL")
print("="*60)
print(f"\n ESTATГЌSTICAS:")
print(f" Score mГ©dio: {np.mean(scores_regras):.2f}")
print(f" Score mГ-nimo: {np.min(scores_regras):.2f}")
print(f" Score mГЎximo: {np.max(scores_regras):.2f}")
# DistribuiГ§ГЈo final
sentimentos_finais = []
for score in scores_regras:
if score >= 2.5:
sentimentos_finais.append('Muito Positivo')
elif score >= 1.5:
sentimentos_finais.append('Positivo')
elif score >= 0.5:
sentimentos_finais.append('Leve Positivo')
elif score <= -2.5:
sentimentos_finais.append('Muito Negativo')
elif score <= -1.5:
sentimentos_finais.append('Negativo')
elif score <= -0.5:
sentimentos_finais.append('Leve Negativo')
else:
sentimentos_finais.append('Neutro')
sent_count = Counter(sentimentos_finais)
print(f"\n DistribuiГ§ГЈo final:")
for sent, qtd in sent_count.items():
print(f" {sent}: {qtd} ({qtd/len(comentarios)*100:.1f}%)")
print("\n" + "="*60)
print(" ANГЃLISE CONCLUГЌDA!")
print("="*60)
if __name__ == "__main__":
main()
