"""Assemble le site dans docs/ : page (polices intégrées), manifeste, service worker, icônes.

Usage :  python3 build.py

Le nom de l'outil et la signature se règlent dans config.json.
Le dossier docs/ est prêt à publier tel quel (GitHub Pages : Settings > Pages > dossier /docs).
"""
import base64
import hashlib
import html
import json
import pathlib
import shutil
import unicodedata

root = pathlib.Path(__file__).parent
cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
NAME = cfg["name"].strip()
SHORT_NAME = cfg["short_name"].strip()
AUTHOR = cfg["author"].strip()
YEAR = int(cfg["year"])
SITE_URL = cfg.get("site_url", "").strip().rstrip("/") + "/" if cfg.get("site_url", "").strip() else ""

out = root / "docs"
out.mkdir(exist_ok=True)


def js_string(value: str) -> str:
    """Chaîne JavaScript sûre à l'intérieur d'un <script>."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


# --- Polices intégrées en base64 -------------------------------------------------
LATIN_RANGE = (
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
    "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
)
PULAR_RANGE = "U+014A-014B,U+0181,U+018A,U+019D,U+01B3-01B4,U+0253,U+0257,U+0272"

FACES = [
    # (famille, graisse, fichier, unicode-range)
    ("Noto Sans Adlam", 400, "noto-sans-adlam-adlam-400-normal.woff2", None),
    ("Noto Sans Adlam", 700, "noto-sans-adlam-adlam-700-normal.woff2", None),
    ("Andika", 400, "andika-latin-400-normal.woff2", LATIN_RANGE),
    ("Andika", 700, "andika-latin-700-normal.woff2", LATIN_RANGE),
    ("Andika", 400, "andika-pular-400.woff2", PULAR_RANGE),
    ("Andika", 700, "andika-pular-700.woff2", PULAR_RANGE),
]

font_css = []
for family, weight, filename, urange in FACES:
    data = base64.b64encode((root / "fonts" / filename).read_bytes()).decode("ascii")
    rule = (
        f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};"
        f"font-display:swap;src:url(data:font/woff2;base64,{data}) format('woff2');"
    )
    if urange:
        rule += f"unicode-range:{urange};"
    font_css.append(rule + "}")

# --- Noms Unicode des lettres (infobulles de la bande « lettre par lettre ») -----
names = {}
for cp in [*range(0x1E900, 0x1E94C), *range(0x1E950, 0x1E95A), 0x1E95E, 0x1E95F]:
    name = unicodedata.name(chr(cp), "")
    if name:
        names[cp] = name.capitalize()

# --- Page ------------------------------------------------------------------------
page = (root / "index.src.html").read_text(encoding="utf-8")
copyright_line = f"© {YEAR} {html.escape(AUTHOR)}." if AUTHOR else ""

DESCRIPTION = "Convertit le pular entre l'écriture Adlam et l'orthographe latine, lettre par lettre."
og = [
    ('property="og:type"', "website"),
    ('property="og:title"', NAME + ": translittérateur Adlam et latin pour le pular/fulfulde"),
    ('property="og:description"', DESCRIPTION),
    ('property="og:locale"', "fr_FR"),
    ('name="twitter:card"', "summary_large_image"),
]
if SITE_URL:   # Facebook et WhatsApp exigent une adresse complète pour l'image
    og += [
        ('property="og:url"', SITE_URL),
        ('property="og:image"', SITE_URL + "og-image.png"),
        ('property="og:image:width"', "1200"),
        ('property="og:image:height"', "630"),
        ('property="og:image:alt"', NAME + " : Adlam et latin"),
        ('name="twitter:image"', SITE_URL + "og-image.png"),
    ]
og_tags = "\n".join(f'<meta {attr} content="{html.escape(value, quote=True)}">' for attr, value in og)

replacements = [
    ("__OG__", og_tags),
    ("/*__FONTS__*/", "\n".join(font_css)),
    ("/*__NAMES__*/{}", json.dumps(names)),
    ("__NAME_JS__", js_string(NAME)),
    ("__AUTHOR_JS__", js_string(AUTHOR)),
    ("__YEAR__", str(YEAR)),
    ("__COPYRIGHT__", copyright_line),
    ("__NAME__", html.escape(NAME)),
]
for placeholder, value in replacements:
    assert placeholder in page, f"repère introuvable : {placeholder}"
    page = page.replace(placeholder, value)
(out / "index.html").write_text(page, encoding="utf-8")

# --- Manifeste, service worker, icônes ------------------------------------------
manifest = {
    "name": NAME,
    "short_name": SHORT_NAME,
    "description": "Convertit le pular entre l'écriture Adlam et l'orthographe latine.",
    "lang": "fr",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#131C4D",
    "theme_color": "#131C4D",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
(out / "manifest.webmanifest").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

version = hashlib.sha256(page.encode("utf-8")).hexdigest()[:8]
service_worker = f"""// Généré par build.py : le nom du cache change à chaque nouvelle version de la page.
const CACHE = 'adlam-{version}';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png'];

self.addEventListener('install', event => {{
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  );
}});

self.addEventListener('activate', event => {{
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
}});

// En ligne : la dernière version du site. Hors ligne : la copie gardée en mémoire.
self.addEventListener('fetch', event => {{
  const request = event.request;
  if (request.method !== 'GET' || new URL(request.url).origin !== location.origin) return;
  event.respondWith(
    fetch(request)
      .then(response => {{
        const copy = response.clone();
        caches.open(CACHE).then(cache => cache.put(request, copy));
        return response;
      }})
      .catch(() => caches.match(request).then(hit => hit || caches.match('./index.html')))
  );
}});
"""
(out / "sw.js").write_text(service_worker, encoding="utf-8")

for icon in ("icon-192.png", "icon-512.png", "icon-maskable-512.png", "og-image.png"):
    shutil.copy(root / "icons" / icon, out / icon)

if not SITE_URL:
    print("ATTENTION : renseigne \"site_url\" dans config.json pour que l'image d'aperçu s'affiche sur Facebook/WhatsApp.")
print(f"docs/ prêt : « {NAME} », signature « {AUTHOR or '(non définie)'} », "
      f"index.html {(out / 'index.html').stat().st_size / 1024:.0f} Ko, cache adlam-{version}")
