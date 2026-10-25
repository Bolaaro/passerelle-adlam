# Passerelle Adlam

Translittérateur **Adlam ⇄ latin** pour le pular / fulfulde (orthographe Bamako/UNESCO).

**Utiliser l'outil : https://bolaaro.github.io/passerelle-adlam/**

Une seule page, sans serveur ni compte : tout se passe dans ton navigateur. Elle fonctionne hors ligne et s'installe comme une application (sur iPhone : Safari > Partager > Sur l'écran d'accueil).

## Fonctions
- Conversion instantanée dans les deux sens, avec lettres Adlam liées (police Noto Sans Adlam intégrée).
- Bouton ⇄ pour choisir quelle écriture est en haut.
- Clavier Adlam et clavier des lettres spéciales du latin (ɓ ɗ ŋ ñ ƴ), pour les appareils qui n'en ont pas.
- **Lettre par lettre** : le mot sous le curseur, chaque lettre Adlam reliée à son équivalent latin, avec son nom Unicode au survol.
- **Image à partager** : une carte PNG du texte, pour WhatsApp, Facebook, etc.

## Règles d'orthographe
- `ng` n'est pas `ŋ` : dans « ngaari », c'est n + g, comme `nd`. `ŋ` est une lettre à part.
- `ñ` s'écrit aussi `ny` (entrée `ɲ` acceptée, la sortie latine donne toujours `ñ`).
- `gb`, `kp`, `sh` sont des lettres uniques.
- Une consonne doublée prend la marque de gémination Adlam seulement devant une voyelle (`ullu`). Devant une consonne ou en fin de mot (`winnden`), les deux lettres restent.
- Une voyelle doublée prend la marque d'allongement (`uu`).

Une erreur dans les correspondances ? Ouvre une *issue* avec le mot, ce que l'outil donne, et ce qui est attendu.

## Pour les développeurs
- `index.src.html` : source de la page. `python3 build.py` génère `docs/` (page, manifeste, service worker, icônes).
- `config.json` : nom de l'outil, auteur, année, adresse du site.
- `adlam_translit.py` : même moteur en Python, utilisable en ligne de commande (`a2l`, `l2a`).
- Tests : `python3 -m unittest -v` (31 tests). Le moteur JavaScript et le moteur Python donnent les mêmes résultats.
- Publication : GitHub Pages, branche `main`, dossier `/docs`.

## Licence et crédits
© 2026 Ismaila H. Barry. Tous droits réservés. Pour toute utilisation ou réutilisation du code, contacte l'auteur.

Polices : Noto Sans Adlam (© The Noto Project Authors) et Andika (© SIL International), sous [SIL Open Font License 1.1](https://openfontlicense.org). Les fichiers de licence sont dans `fonts/`.
