with open("arabe.txt", encoding="utf-8") as f:
    contenu = f.read()

mots = contenu.lower().split()

propres = []

for word in mots:
    word = word.strip("?!.,:;«»%،؟؛")
    for code in range(0x064B, 0x0653):
        word = word.replace(chr(code), "")
    for alif in "أإآ":
        word = word.replace(alif, "ا")
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