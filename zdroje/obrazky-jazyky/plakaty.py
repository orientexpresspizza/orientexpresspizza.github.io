#!/usr/bin/env python3
"""Localized versions of the promo posters (Akce) and the share preview.

Takes the print PDFs with live text (../Plakaty/.../editovatelne/*_text.pdf), removes the Czech text
(background photo and the red/gold banners stay), sets the translated text in the same place and style
and renders it with headless Chrome into obrazky/<lang>/ (same file names as the Czech images).

  python3 zdroje/obrazky-jazyky/plakaty.py            # ru + tr
  python3 zdroje/obrazky-jazyky/plakaty.py cs         # Czech through the same pipeline (to compare)

Needs: PyMuPDF, Pillow, Google Chrome; fonts from the poster package (fonty/) + Lobster from Google Fonts
(Kaushan Script and Anton have no Cyrillic: Russian uses Lobster and Oswald instead).
"""
import html
import os
import sys
import tempfile
from pathlib import Path

import fitz
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chrome import shot  # noqa: E402

SITE = Path(__file__).resolve().parents[2]
PKG = Path(os.environ.get('PLAKATY_DIR', SITE.parent.parent / 'Plakaty' / 'OrientExpress_plakaty_DTP' / 'final'))
FONTS = PKG / 'fonty'
BLEED = 3 / 25.4 * 72          # 3 mm in PDF points
SCALE = 1.3                    # render scale (px per PDF point), then downscaled

# translations; every line: (key, cs, ru, tr)
TEXTS = {
    'k1': ('Köfte', 'Кёфте', 'Köfte'),
    'k2': ('v chlebu', 'в хлебе', 'ekmek arası'),
    'k3': ('Köfte', 'Кёфте', 'Köfte'),
    'k4': ('Bowl', 'Боул', 'Bowl'),
    'k5': ('Pizza', 'Пицца', 'Pizza'),
    'buy': ('Kupte si', 'Купите', 'Sipariş verin'),
    'pizzy': ('2 pizzy', '2 пиццы', '2 pizza'),
    'tortilly': ('3 tortilly', '3 тортильи', '3 tortilla'),
    'burgery': ('3 burgery', '3 бургера', '3 burger'),
    'get': ('a dostanete', 'и получите', 'yanında'),
    'cola': ('1 litr Coca-Coly', '1 литр Coca-Cola', '1 litre Coca-Cola'),
    'free': ('zdarma!', 'бесплатно!', 'hediye!'),
}
LANG_IDX = {'cs': 0, 'ru': 1, 'tr': 2}

# line layout taken from the PDFs: key, style, baseline x, y, angle, font size, max width (all in PDF points)
POSTERS = {
    'akce-1-kofte-pizza.jpg': {
        'pdf': 'OrientExpress_plakat_kofte_pizza_text.pdf', 'size': (1800, 1247),
        'lines': [
            ('k1', 'script_white', 288.9, 343.8, -6, 384.0, 1000),
            ('k2', 'script_gold', 331.6, 587.6, -6, 298.7, 1150),
            ('k3', 'script_white', 1715.4, 340.7, -7, 371.8, 840),
            ('k4', 'script_dark', 1837.3, 593.7, -7, 341.4, 720),
            ('k5', 'script_white', 191.4, 1691.0, -7, 426.7, 1050),
        ]},
    'akce-3-coca-cola.jpg': {
        'pdf': 'OrientExpress_plakat_akce_cocacola_text.pdf', 'size': (1100, 1632),
        'lines': [
            ('buy', 'sans_white', 114.2, 249.4, 0, 193.9, 1000),
            ('pizzy', 'sans_banner', 149.5, 525.5, -3, 258.5, 950),
            ('get', 'sans_white', 202.4, 731.1, 0, 158.6, 1000),
            ('cola', 'cond_black', 137.7, 983.7, -2, 165, 790),
            ('free', 'red', 137.7, 1207.0, -2, 262, 760),
            ('buy', 'sans_white', 105.4, 1405.0, 0, 135.7, 590),
            ('tortilly', 'cond_banner', 130.1, 1598.2, -3, 165, 600),
            ('get', 'sans_white', 167.1, 1742.2, 0, 111.0, 680),
            ('cola', 'cond_black', 121.9, 1919.0, -2, 115, 545),
            ('free', 'red', 121.9, 2075.3, -2, 182, 530),
            ('buy', 'sans_white', 962.0, 1397.7, 0, 127.9, 550),
            ('burgery', 'cond_banner', 985.3, 1579.9, -3, 145, 540),
            ('get', 'sans_white', 1020.2, 1715.6, 0, 104.7, 640),
            ('cola', 'cond_black', 977.5, 1882.4, -2, 104, 470),
            ('free', 'red', 977.5, 2029.7, -2, 164, 460),
        ]},
}

STYLES = {
    'script_white': 'font-family:var(--script); fill:#fff; stroke:#111; stroke-width:9; paint-order:stroke; stroke-linejoin:round',
    'script_gold': 'font-family:var(--script); fill:url(#gold); stroke:#1a1208; stroke-width:7; paint-order:stroke; stroke-linejoin:round',
    'script_dark': 'font-family:var(--script); fill:#1a1208',
    'sans_white': 'font-family:Montserrat; font-weight:800; fill:#fff; stroke:#000; stroke-width:5; paint-order:stroke; '
                  'stroke-linejoin:round; filter:drop-shadow(0 5px 0 #000)',
    'sans_banner': 'font-family:Montserrat; font-weight:800; fill:#fff; stroke:#3a0508; stroke-width:3; paint-order:stroke; '
                   'filter:drop-shadow(0 4px 3px rgba(0,0,0,.45))',
    'cond_banner': 'font-family:Oswald; font-weight:700; fill:#fff; stroke:#3a0508; stroke-width:3; paint-order:stroke; '
                   'filter:drop-shadow(0 4px 3px rgba(0,0,0,.45))',
    'cond_black': 'font-family:Oswald; font-weight:600; fill:#141414',
    'red': 'font-family:var(--heavy); font-weight:var(--heavy-w); fill:#d3141c',
}

FONT_FACES = '''
@font-face { font-family: 'Kaushan Script'; src: url('{F}/KaushanScript-Regular.ttf'); }
@font-face { font-family: 'Anton'; src: url('{F}/Anton-Regular.ttf'); }
@font-face { font-family: 'Oswald'; src: url('{F}/Oswald[wght].ttf'); font-weight: 200 700; }
@font-face { font-family: 'Montserrat'; src: url('{F}/Montserrat[wght].ttf'); font-weight: 100 900; }
'''


def background(pdf, png):
    """Page without its text (photo and vector banners only), rendered at SCALE."""
    doc = fitz.open(pdf)
    page = doc[0]
    for b in page.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            for s in line['spans']:
                page.add_redact_annot(s['bbox'])
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE)).save(png)
    return page.rect.width, page.rect.height


def build(name, spec, lang, out_dir, tmp):
    bg = os.path.join(tmp, 'bg.png')
    w, h = background(PKG / 'editovatelne' / spec['pdf'], bg)
    i = LANG_IDX[lang]
    texts = []
    for key, style, x, y, ang, size, maxw in spec['lines']:
        t = html.escape(TEXTS[key][i])
        squeeze = 0.68 if style in ('cond_black', 'cond_banner', 'red') else 1
        texts.append('<text class="fit" data-maxw="%s" data-squeeze="%s" x="%s" y="%s" font-size="%s" transform="rotate(%s %s %s)" style="%s">%s</text>'
                     % (maxw, squeeze, x, y, size, ang, x, y, STYLES[style], t))
    script = "'Lobster'" if lang == 'ru' else "'Kaushan Script'"
    heavy, heavy_w = ("'Oswald'", 700) if lang == 'ru' else ("'Anton'", 400)
    page = '''<!doctype html><html lang="%s"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Lobster&display=block" rel="stylesheet">
<style>%s
html,body{margin:0;background:#000} svg{display:block}
:root{--script:%s; --heavy:%s; --heavy-w:%s}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">
<defs><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#f7e2a0"/><stop offset=".5" stop-color="#d9ac52"/><stop offset="1" stop-color="#a8782e"/></linearGradient></defs>
<image href="bg.png" width="%s" height="%s"/>
%s
</svg>
<script>
// a line wider than its banner / free space is squeezed horizontally (condensed styles, down to data-squeeze),
// and if that is not enough, made smaller
document.fonts.ready.then(function () {
  document.querySelectorAll('text.fit').forEach(function (t) {
    var max = +t.dataset.maxw, sq = +t.dataset.squeeze, w = t.getComputedTextLength();
    if (w <= max) return;
    var r = max / w;
    if (r < sq) { t.setAttribute('font-size', (+t.getAttribute('font-size')) * r / sq); }
    if (sq < 1) { t.setAttribute('textLength', max); t.setAttribute('lengthAdjust', 'spacingAndGlyphs'); }
  });
});
</script></body></html>''' % (lang, FONT_FACES.replace('{F}', 'file://' + str(FONTS)), script,
                               heavy, heavy_w, w, h, w, h, w, h, '\n'.join(texts))
    hp = os.path.join(tmp, 'page.html')
    Path(hp).write_text(page, encoding='utf-8')
    raw = os.path.join(tmp, 'shot.png')
    shot(hp, raw, w, h, SCALE)
    im = Image.open(raw).convert('RGB')
    b = round(BLEED * SCALE)
    im = im.crop((b, b, im.width - b, im.height - b))
    im = im.resize(spec['size'], Image.LANCZOS)
    out = Path(out_dir) / name
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=86, optimize=True, progressive=True)
    print('  ', out.relative_to(SITE) if SITE in out.parents else out, im.size)
    return im


def share_preview(poster, out_dir):
    """1200x630 crop of the köfte poster, same framing as obrazky/nahled-sdileni.jpg."""
    im = poster.resize((1200, round(poster.height * 1200 / poster.width)), Image.LANCZOS)
    top = 100
    im.crop((0, top, 1200, top + 630)).save(Path(out_dir) / 'nahled-sdileni.jpg', quality=86, optimize=True, progressive=True)
    print('  ', (Path(out_dir) / 'nahled-sdileni.jpg'))


def main():
    langs = sys.argv[1:] or ['ru', 'tr']
    for lang in langs:
        # Czech goes to a check folder (the real Czech images are the approved originals in obrazky/)
        out_dir = (SITE / 'obrazky' / lang) if lang != 'cs' else Path(__file__).resolve().parent / '_kontrola-cs'
        print(lang)
        for name, spec in POSTERS.items():
            with tempfile.TemporaryDirectory() as tmp:
                im = build(name, spec, lang, out_dir, tmp)
            if name.startswith('akce-1'):
                share_preview(im, out_dir)


if __name__ == '__main__':
    main()
