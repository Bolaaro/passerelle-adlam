"""
adlam_translit.py
Translittération bidirectionnelle Adlam <-> Latin (orthographe Bamako/UNESCO du Pular/Fula)

Source des correspondances : charte Unicode 17.0, bloc Adlam (U+1E900-U+1E95F)
https://unicode.org/charts/PDF/U1E900.pdf

Auteur : voir config.json (nom de l'auteur à renseigner), 2026.
"""

from __future__ import annotations
import unicodedata

# ---------------------------------------------------------------------------
# 1. Table des lettres de base (capitale Adlam -> latin minuscule)
#    L'ordre suit celui du bloc Unicode Adlam (proche de l'abjad arabe :
#    alif, dal, lam, mim, ba, sin...).
# ---------------------------------------------------------------------------

# (codepoint capitale, codepoint minuscule, latin)
BASE_LETTERS = [
    (0x1E900, 0x1E922, "a"),
    (0x1E901, 0x1E923, "d"),
    (0x1E902, 0x1E924, "l"),
    (0x1E903, 0x1E925, "m"),
    (0x1E904, 0x1E926, "b"),
    (0x1E905, 0x1E927, "s"),
    (0x1E906, 0x1E928, "p"),
    (0x1E907, 0x1E929, "ɓ"),
    (0x1E908, 0x1E92A, "r"),
    (0x1E909, 0x1E92B, "e"),
    (0x1E90A, 0x1E92C, "f"),
    (0x1E90B, 0x1E92D, "i"),
    (0x1E90C, 0x1E92E, "o"),
    (0x1E90D, 0x1E92F, "ɗ"),
    (0x1E90E, 0x1E930, "ƴ"),
    (0x1E90F, 0x1E931, "w"),
    (0x1E910, 0x1E932, "n"),
    (0x1E911, 0x1E933, "k"),
    (0x1E912, 0x1E934, "y"),
    (0x1E913, 0x1E935, "u"),
    (0x1E914, 0x1E936, "j"),
    (0x1E915, 0x1E937, "c"),   # CHI -> /tʃ/, "c" en orthographe Bamako
    (0x1E916, 0x1E938, "h"),
    (0x1E917, 0x1E939, "q"),   # emprunts (arabe, etc.)
    (0x1E918, 0x1E93A, "g"),
    (0x1E919, 0x1E93B, "ñ"),   # NYA -> ñ (anciennement noté ɲ ou ny)
    (0x1E91A, 0x1E93C, "t"),
    (0x1E91B, 0x1E93D, "ŋ"),   # lettre à part entière, distincte de "ng" (ex. ngaari = n + g)
    # Lettres supplémentaires (emprunts / dialectes)
    (0x1E91C, 0x1E93E, "v"),
    (0x1E91D, 0x1E93F, "x"),   # KHA -> emprunts arabes (kh)
    (0x1E91E, 0x1E940, "gb"),
    (0x1E91F, 0x1E941, "z"),
    (0x1E920, 0x1E942, "kp"),
    (0x1E921, 0x1E943, "sh"),  # emprunts (ʃ)
]

# Digrammes latins qui doivent être reconnus AVANT les lettres simples
# lors du passage latin -> Adlam (les plus longs d'abord).
LATIN_DIGRAPHS_PRIORITY = ["gb", "kp", "sh", "ny"]

# Variantes latines alternatives -> forme canonique utilisée ci-dessus
LATIN_ALIASES = {
    "ny": "ñ",  # ny et ñ sont la même lettre (le latin affiche toujours ñ)
    "ɲ": "ñ",   # ancienne graphie (API), toujours acceptée à la saisie
    # "ng" n'est PAS un alias de ŋ : ngaari s'écrit n + g, comme nd s'écrit n + d.
    "bh": "ɓ",
    "dh": "ɗ",
    "yh": "ƴ",
    "kh": "x",
}

# ---------------------------------------------------------------------------
# 2. Chiffres
# ---------------------------------------------------------------------------
DIGITS = [(0x1E950 + i, str(i)) for i in range(10)]

# ---------------------------------------------------------------------------
# 3. Ponctuation propre à l'Adlam
# ---------------------------------------------------------------------------
PUNCTUATION = [
    (0x1E95E, "!"),   # ADLAM INITIAL EXCLAMATION MARK
    (0x1E95F, "?"),   # ADLAM INITIAL QUESTION MARK
]

# ---------------------------------------------------------------------------
# 4. Diacritiques (marques combinantes)
#    On les traite séparément car ils modifient la lettre précédente plutôt
#    que d'être des lettres à part entière.
# ---------------------------------------------------------------------------
ALIF_LENGTHENER = 0x1E944       # allonge le "a"
VOWEL_LENGTHENER = 0x1E945      # double la voyelle précédente
GEMINATION_MARK = 0x1E946       # double la consonne précédente
HAMZA = 0x1E947
CONSONANT_MODIFIER = 0x1E948    # pré-nasalisation / mutation consonantique
GEMINATE_CONSONANT_MODIFIER = 0x1E949
NUKTA = 0x1E94A
NASALIZATION_MARK = 0x1E94B     # marque de pré-nasalisation

VOWELS_LATIN = set("aeiou")

# ---------------------------------------------------------------------------
# Construction des dictionnaires de correspondance
# ---------------------------------------------------------------------------

def _build_maps():
    adlam_to_lat = {}   # codepoint (str) -> latin
    lat_to_adlam_cap = {}
    lat_to_adlam_small = {}

    for cap, small, lat in BASE_LETTERS:
        adlam_to_lat[chr(cap)] = lat
        adlam_to_lat[chr(small)] = lat
        # Pour la génération latin -> Adlam, la clé est en minuscule latine
        lat_to_adlam_cap[lat] = chr(cap)
        lat_to_adlam_small[lat] = chr(small)

    for cp, d in DIGITS:
        adlam_to_lat[chr(cp)] = d

    for cp, p in PUNCTUATION:
        adlam_to_lat[chr(cp)] = p

    return adlam_to_lat, lat_to_adlam_cap, lat_to_adlam_small


ADLAM_TO_LATIN, LATIN_TO_ADLAM_CAP, LATIN_TO_ADLAM_SMALL = _build_maps()

DIGIT_TO_ADLAM = {d: chr(cp) for cp, d in DIGITS}
PUNCT_TO_ADLAM = {p: chr(cp) for cp, p in PUNCTUATION}


# ---------------------------------------------------------------------------
# 5. Adlam -> Latin
# ---------------------------------------------------------------------------

def adlam_to_latin(text: str) -> str:
    """Convertit un texte en écriture Adlam vers l'orthographe latine
    Bamako/UNESCO du Pular. Gère la gémination, l'allongement vocalique
    et la pré-nasalisation via les marques combinantes.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        cp = ord(ch)

        # Marques combinantes : elles modifient le caractère latin déjà émis
        # (la lettre doublée est toujours en minuscule : "Ll" et non "LL")
        if cp == GEMINATION_MARK or cp == GEMINATE_CONSONANT_MODIFIER:
            if out and out[-1][:1].isalpha():
                out.append(out[-1].lower())  # double la dernière lettre (gémination)
            i += 1
            continue
        if cp == VOWEL_LENGTHENER or cp == ALIF_LENGTHENER:
            if out and out[-1].lower() in VOWELS_LATIN:
                out.append(out[-1].lower())  # voyelle longue -> doublée en latin
            i += 1
            continue
        if cp == NASALIZATION_MARK:
            out.append("n")  # pré-nasalisation -> "n" devant la consonne suivante
            i += 1
            continue
        if cp in (HAMZA, NUKTA, CONSONANT_MODIFIER):
            # Pas d'équivalent direct simple : on ignore proprement plutôt
            # que de produire un caractère erroné.
            i += 1
            continue

        latin = ADLAM_TO_LATIN.get(ch)
        if latin is not None:
            # Restituer une majuscule si la lettre Adlam était une capitale
            if unicodedata.category(ch) == "Lu" and latin:
                out.append(latin[0].upper() + latin[1:])
            else:
                out.append(latin)
        else:
            out.append(ch)  # espaces, ponctuation latine déjà mélangée, etc.
        i += 1

    return "".join(out)


# ---------------------------------------------------------------------------
# 6. Latin -> Adlam
# ---------------------------------------------------------------------------

def _match_longest(text: str, i: int):
    """Essaie de faire correspondre le plus long digramme/lettre latine
    possible à partir de la position i (insensible à la casse)."""
    for length in (2, 1):
        if i + length <= len(text):
            chunk = text[i:i + length].lower()
            chunk = LATIN_ALIASES.get(chunk, chunk)
            if chunk in LATIN_TO_ADLAM_CAP:
                return chunk, length
    return None, 0


# Mots où une consonne doublée devant une voyelle garde ses deux lettres
# (pas de marque de gémination). Écrits en minuscules ; ajouter ici d'autres cas.
GEMINATION_EXCEPTIONS = {"allah", "allahou"}


def _word_at(text: str, i: int) -> str:
    """Le mot (suite de lettres) qui contient la position i, en minuscules."""
    start = i
    while start > 0 and text[start - 1].isalpha():
        start -= 1
    end = i
    while end < len(text) and text[end].isalpha():
        end += 1
    return text[start:end].lower()


def latin_to_adlam(text: str) -> str:
    """Convertit un texte en orthographe latine Bamako/UNESCO du Pular
    vers l'écriture Adlam. Les lettres simples doublées (voyelle ou
    consonne) sont rendues avec les marques d'allongement/gémination
    Adlam plutôt que par répétition du glyphe.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]

        if ch.isdigit():
            out.append(DIGIT_TO_ADLAM.get(ch, ch))
            i += 1
            continue
        if ch in PUNCT_TO_ADLAM:
            out.append(PUNCT_TO_ADLAM[ch])
            i += 1
            continue
        if ch.isspace():
            out.append(ch)
            i += 1
            continue

        chunk, length = _match_longest(text, i)
        if chunk is None:
            out.append(ch)  # caractère non reconnu : laissé tel quel
            i += 1
            continue

        is_upper = text[i].isupper()
        base = LATIN_TO_ADLAM_CAP[chunk] if is_upper else LATIN_TO_ADLAM_SMALL[chunk]

        # Détection de gémination / voyelle longue par répétition de
        # la même lettre latine juste après (ex: "ii", "kk")
        next_chunk, next_len = _match_longest(text, i + length)
        if next_chunk == chunk and chunk in VOWELS_LATIN:
            out.append(base)
            out.append(chr(VOWEL_LENGTHENER))
            i += length + next_len
            continue
        if next_chunk == chunk and chunk not in VOWELS_LATIN:
            # Consonne doublée : la marque de gémination n'est utilisée que
            # si une voyelle suit (« ullu »). Devant une consonne ou en fin
            # de mot (« winnden »), on garde les deux lettres.
            after, _ = _match_longest(text, i + length + next_len)
            if after in VOWELS_LATIN and _word_at(text, i) not in GEMINATION_EXCEPTIONS:
                out.append(base)
                out.append(chr(GEMINATION_MARK))
            else:
                second = text[i + length]
                out.append(base)
                out.append(LATIN_TO_ADLAM_CAP[chunk] if second.isupper() else LATIN_TO_ADLAM_SMALL[chunk])
            i += length + next_len
            continue

        out.append(base)
        i += length

    return "".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Translittère entre l'écriture Adlam et l'orthographe "
                     "latine Bamako/UNESCO du Pular/Fula."
    )
    parser.add_argument(
        "direction",
        choices=["a2l", "l2a"],
        help="a2l = Adlam -> Latin ; l2a = Latin -> Adlam",
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="Texte à convertir. Si omis, lit depuis l'entrée standard.",
    )
    args = parser.parse_args()

    if args.text:
        input_text = " ".join(args.text)
    else:
        input_text = sys.stdin.read().rstrip("\n")

    if args.direction == "a2l":
        print(adlam_to_latin(input_text))
    else:
        print(latin_to_adlam(input_text))


if __name__ == "__main__":
    _main()
