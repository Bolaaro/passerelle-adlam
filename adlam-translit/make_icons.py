"""Fabrique les icônes de l'application (lettre Adlam sur fond indigo) avec Chromium.

Usage :  python3 make_icons.py        (nécessite playwright, uniquement pour refaire les icônes)
"""
import base64
import pathlib

from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).parent
font = base64.b64encode(
    (root / "fonts" / "noto-sans-adlam-adlam-700-normal.woff2").read_bytes()
).decode("ascii")

# (fichier, taille, part de la hauteur occupée par la lettre)
ICONS = [
    ("icon-192.png", 192, 0.62),
    ("icon-512.png", 512, 0.62),
    ("icon-maskable-512.png", 512, 0.46),   # lettre dans la zone de sécurité des icônes « maskable »
]

PAGE = """<!doctype html><meta charset="utf-8">
<style>
@font-face {{ font-family: 'Noto Sans Adlam'; font-weight: 700;
  src: url(data:font/woff2;base64,{font}) format('woff2'); }}
html, body {{ margin: 0; }}
body {{ width: {size}px; height: {size}px; background: #131C4D; display: grid; place-items: center; overflow: hidden; }}
span {{ font: 700 {glyph}px/1 'Noto Sans Adlam'; color: #F4B63F; }}
</style>
<span>𞤀</span>"""

(root / "icons").mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    for filename, size, share in ICONS:
        page = browser.new_page(viewport={"width": size, "height": size})
        page.set_content(PAGE.format(font=font, size=size, glyph=round(size * share)))
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(200)
        page.screenshot(path=str(root / "icons" / filename))
        page.close()
    browser.close()
print("icônes créées dans icons/")
