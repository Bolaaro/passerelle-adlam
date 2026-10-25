# Passerelle Adlam

Convertisseur Adlam ⇄ latin pour le pular (orthographe Bamako/UNESCO). Page unique, sans serveur, qui fonctionne hors ligne et s'installe comme une application.

## Contenu
- `docs/` : le site prêt à publier (généré, ne pas modifier à la main)
- `index.src.html`, `build.py`, `config.json`, `fonts/`, `icons/` : sources
- `adlam_translit.py` + `test_adlam_translit.py` : version Python et ses tests

## Mettre ton nom et ton droit d'auteur
1. Ouvre `config.json` : renseigne `"author"` avec ton nom (et `"name"` si tu changes le nom de l'outil).
2. `python3 build.py` : régénère `docs/`.
La mention « © 2026 Ton Nom » apparaît alors en pied de page et sur les images partagées.

## Publier sur GitHub Pages
Dépôt GitHub > Settings > Pages > Source : branche `main`, dossier `/docs`.

## Tests
`python3 -m unittest -v` (26 tests).

## Licence
À choisir (MIT, GPL, etc.) et à ajouter dans un fichier `LICENSE`.
Les polices (Noto Sans Adlam, Andika) restent sous SIL OFL 1.1 : garde les fichiers dans `fonts/`.
