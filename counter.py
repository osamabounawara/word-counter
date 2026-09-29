with open("text.txt", encoding="utf-8") as f:
    contenu = f.read()
contenu=contenu.lower()
mots = contenu.split()

propres = []

for word in mots:
    word = word.strip("?!.,:;«»")
    if word != "":
        propres.append(word)

compteur = {}

for mot in propres:
    if mot in compteur:
        compteur[mot] = compteur[mot] + 1
    else:
        compteur[mot] = 1

top = sorted(compteur, key=compteur.get, reverse=True)[:20]

for mot in top:
    print(mot, ":", compteur[mot])
