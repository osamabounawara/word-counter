# Word Counter — from French to Arabic to Tunisian Darija

A word-frequency counter in Python, built from scratch. It worked on French in one evening, then I fed it Arabic and watched it break. This README is the story of each break: what I saw, how I reasoned about it, and how I fixed it. The last one, Tunisian darija, I couldn't fix with a few lines, and that's where my next projects come from.

**Handles:** French · Modern Standard Arabic (punctuation, tashkeel removal, alif normalization) · tested on Tunisian darija and Arabizi

## How to run

```bash
python3 counter.py
```

The program reads the file named in `counter.py` (`text.txt`, `arabe.txt` or `darija.txt`) and prints the 20 most frequent words.

## How it works

```
read the file → lowercase → split into words → clean each word → count → sort → top 20
```

Cleaning is where all the interesting problems live:

```python
for word in mots:
    word = word.strip("?!.,:;«»%،؟؛")          # punctuation at the edges, French and Arabic
    for code in range(0x064B, 0x0653):          # the 8 Arabic diacritics (tashkeel)
        word = word.replace(chr(code), "")
    for alif in "أإآ":                           # alif normalization
        word = word.replace(alif, "ا")
    if word != "":
        propres.append(word)
```

Counting uses a plain dictionary: if the word is already a key, add 1; otherwise create it with 1. Sorting uses `sorted(compteur, key=compteur.get, reverse=True)[:20]`. I wrote both by hand before learning that `collections.Counter(...).most_common(20)` does the same thing, so I know exactly what it does inside.

---

## Stage 1 — French: my first surprises

I started with a French news paragraph. Three problems showed up immediately.

**`La` and `la` counted as two words.** Fixed with `lower()`. But my first attempt, `contenu.lower()` on its own line, changed nothing. That's how I learned that **Python strings are immutable**: `lower()`, `strip()` and `replace()` never modify a string, they return a new one, which you have to store (`contenu = contenu.lower()`). This rule came back at every stage after that.

**Punctuation glued to words** (`vital,` ≠ `vital`). Fixed with `strip()`, which removes characters only at the start and end of a word. That turned out to be exactly right for French, because the hyphens *inside* `va-t-elle` and `Evry-Courcouronnes` survive.

**French quotes `« »` became words of their own**, because they're separated by spaces. After stripping they turn into empty strings, so I only keep a word if it isn't empty.

**Design choices:**
- Hyphenated words stay one word (`va-t-elle`, `quatre-vingts`).
- The typographic apostrophe `’` (not the same character as `'`) is not handled yet, so `d’un` currently counts as one token. It's on the next-steps list.

## Stage 2 — Arabic: a sentence designed to break it

I tested with a sentence written specifically to trigger every trap at once:

```
ذَهَبَ أحمد إلى المكتبة، وفي المَكْتَبَةِ وجد احمد كتاباً جديداً. هل قرأ أحمد الكتاب؟ نعم، قرأ الكتابَ كله؛ ثم أعاد الكتاب إلى المكتبة.
```

`المكتبة`, `الكتاب` and `أحمد` each appear **3 times**. The first run said this:

```
أحمد : 2
المكتبة، : 1
المَكْتَبَةِ : 1
احمد : 1
الكتاب؟ : 1
الكتابَ : 1
الكتاب : 1
المكتبة : 1
```

No word reached 3. Three different problems were hiding in there.

### Problem 1 — Arabic punctuation is not French punctuation

`المكتبة،` kept its comma because the Arabic comma `،` is a different character from `,`. The same goes for `؟` and `؛`. The fix was to add them to `strip()`, which doesn't care about language: it removes whatever characters you give it.

### Problem 2 — Tashkeel: one letter on screen is not one character in memory

`المكتبة` and `المَكْتَبَةِ` look like the same word to a reader. To understand why Python disagreed, I looked inside:

```python
list("المَكْتَبَةِ")      # every fatha and kasra shows up as its own element
len("المكتبة")           # 7
len("المَكْتَبَةِ")        # 12
```

Each diacritic is a **separate Unicode character**, placed right after its letter. My first idea was `strip()`, but `strip()` only touches the edges of a word, and the vowels sit in the middle. So I used `replace()` instead, looping over the 8 diacritics between U+064B and U+0652 (tanwin, fatha, damma, kasra, shadda, sukun). `range(0x064B, 0x0653)` generates them, since the end of a range is excluded.

### Problem 3 — Hamza: normalization is a choice, not a fix

`أحمد` and `احمد` are the same name written two ways. I normalized `أ`, `إ` and `آ` to a plain `ا`.

This one taught me that **normalization loses information**. `إلى` becomes `الى`, and `قرأ` becomes `قرا`. For counting words, that's the right trade-off, and it's what most Arabic NLP tools do. For a spell-checker, it would be a bug. There's no universally correct answer; it depends on what the tool is for.

**After the three fixes:** `احمد : 3`, `المكتبة : 3`, `الكتاب : 3`. Correct.

## Stage 3 — Tunisian darija: where `replace()` stops working

Then I wrote a paragraph the way Tunisians actually write online, switching between Arabic script and Arabizi mid-sentence:

```
مرحبا بيك عزيزي القارئ، زارتنا البركة . اليوم خصصت برشا وقت باش نصنع برنامج يحسب الكلمات بالدارجة
barcha ness yektbou belderja
شنوا رايك fel programme mte3i
```

As a reader, I see repeated words. The program counted **every word exactly once**. This time it isn't a missing character in a list. These are problems of a different kind:

| What I see | Why the program can't | What it would take |
|---|---|---|
| `برشا` = `barcha` | Two scripts, not one character in common | Arabizi → Arabic conversion |
| `بالدارجة` = `belderja` = "darija" | Small words glued on: `ب` + `ال` + `دارجة`, `b` + `el` + `derja` (same for `fel`) | Clitic segmentation |
| `programme` = `برنامج` | Same meaning, two languages | A design decision: a word counter probably *shouldn't* merge them |
| `شنوا` vs `شنوة` | Darija has no official spelling | Spelling-variant normalization |

Arabizi writes Arabic sounds with Latin letters and digits that *look like* the Arabic letter: `3` = ع, `7` = ح, `9` = ق, `5` = خ, `2` = ء. Billions of messages are written this way, and very few tools can read them. That's the problem I want to work on next.

---

## What I learned

- **Relative paths:** `open("texte.txt")` looks in the folder the terminal is in, and Linux filenames are exact. My first `FileNotFoundError` was a filename that didn't match.
- **Strings are immutable:** every string method returns a new string.
- **`strip()` vs `replace()`:** edges only vs everywhere.
- **Unicode:** what looks like one letter can be several characters.
- **Normalization is a design decision**, with a cost you should write down.
- **Some problems aren't bugs.** When `replace()` stopped being enough, the problem had become a project.

## Next steps

- [ ] Choose the input file at launch: `python3 counter.py darija.txt` (`sys.argv`)
- [ ] Handle the typographic apostrophe `’` (split `d’un` into `d` + `un`)
- [ ] Normalize `ة`/`ه` and `ى`/`ي`
- [ ] **Arabizi ↔ Arabic converter**, so `barcha` and `برشا` can finally be counted together
- [ ] **Arabic root and clitic analysis**, so `بالدارجة` can be recognized as `دارجة`
