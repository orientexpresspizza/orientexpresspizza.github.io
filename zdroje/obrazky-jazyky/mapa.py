#!/usr/bin/env python3
"""Localized campus map (obrazky/<lang>/mapa-arealu-fnhk.png and -1200.png).

From the original FN HK PDF (zdroje/mapa/mapa-fnhk-original.pdf) it removes the Czech title, legend texts,
gate labels and the numbered list of buildings, and sets them again in Russian / Turkish. Building numbers,
street names and public-transport stop names stay as they are (they match the signs and announcements).
The Orient Express marking (ring, arrow, "we are here", gold label) is the approved one from
zdroje/mapa/overlay.py, only its text is translated.

  python3 zdroje/obrazky-jazyky/mapa.py          # ru + tr
  python3 zdroje/obrazky-jazyky/mapa.py cs       # Czech through the same pipeline into _kontrola-cs/ (to compare)

Needs: PyMuPDF, Pillow, Google Chrome (fonts Arimo, Source Sans 3, Cinzel from Google Fonts).
"""
import html
import sys
import tempfile
from pathlib import Path

import fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
SITE = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SITE / 'zdroje' / 'mapa'))
from chrome import shot  # noqa: E402
from overlay import oe_label  # noqa: E402

PDF = SITE / 'zdroje' / 'mapa' / 'mapa-fnhk-original.pdf'
W, H = 592, 894.457
K = 2400 / 592                       # px per PDF point (same as zdroje/mapa/render_map.py)
L = {'cs': 0, 'ru': 1, 'tr': 2}
RED = '#ac2a2f'

TITLE = ('Orientační plán Fakultní nemocnice Hradec Králové',
         'План Университетской больницы Градец-Кралове',
         'Hradec Králové Üniversite Hastanesi Yerleşke Planı')
HERE_TXT = ('JSME TADY', 'МЫ ЗДЕСЬ', 'BURADAYIZ')

# red gate labels: centre x, baseline of line 1, (line 1, line 2) per language
GATES = [
    (208.8, 66.5, (('HLAVNÍ VCHOD', '(pěší brána)'), ('ГЛАВНЫЙ ВХОД', '(для пешеходов)'), ('ANA GİRİŞ', '(yaya kapısı)'))),
    (471.7, 307.6, (('HLAVNÍ VRÁTNICE', '(vjezd os. automobilů)'), ('ГЛАВНАЯ ПРОХОДНАЯ', '(въезд легковых авто)'),
                    ('ANA KAPI', '(otomobil girişi)'))),
    (474.5, 529.9, (('NÁKLADNÍ VRÁTNICE', '(technický vjezd)'), ('ГРУЗОВАЯ ПРОХОДНАЯ', '(технический въезд)'),
                    ('YÜK KAPISI', '(servis girişi)'))),
]

LEGEND = [  # top to bottom, next to the icons
    ('Pohotovostní služba', 'Неотложная помощь', 'Acil servis'),
    ('Lékárna', 'Аптека', 'Eczane'),
    ('Informace', 'Информация', 'Danışma'),
    ('Parkoviště', 'Парковка', 'Otopark'),
    ('Mincovní pokladna', 'Платёжный автомат', 'Ödeme otomatı'),
    ('Telefon', 'Телефон', 'Telefon'),
    ('Poštovní schránka', 'Почтовый ящик', 'Posta kutusu'),
    ('Občerstvení', 'Буфет', 'Büfe'),
    ('Bankomat ČSOB', 'Банкомат ČSOB', 'ATM ČSOB'),
    ('Bankomat Čs. spořitelny', 'Банкомат Česká spořitelna', 'ATM Česká spořitelna'),
    ('Dětské hřiště', 'Детская площадка', 'Çocuk oyun alanı'),
    ('Zastávka MHD', 'Остановка транспорта (MHD)', 'Toplu taşıma durağı (MHD)'),
]

# building list: (number, (cs, ru, tr), emergency-icon, sub-items [((cs, ru, tr), icon)])
I_KARDIO = ('I. interní kardioangiologická klinika', 'I терапевтическая кардиоангиологическая клиника',
            'I. İç Hastalıkları – Kardiyoanjiyoloji Kliniği')
I_GERONTO = ('III. interní gerontometabolická klinika', 'III терапевтическая геронтометаболическая клиника',
             'III. İç Hastalıkları – Gerontometabolik Klinik')
COLUMNS = [
    [
        ('1', ('Ortopedická klinika', 'Ортопедическая клиника', 'Ortopedi Kliniği'), 0, []),
        ('2', ('Radiologická klinika – centrální rentgen', 'Радиологическая клиника – центральный рентген',
               'Radyoloji Kliniği – merkezi röntgen'), 0, []),
        ('3', ('Oční klinika', 'Глазная клиника', 'Göz Kliniği'), 1, []),
        ('4', ('Klinika otorinolaryngologie a chirurgie hlavy a krku', 'Клиника оториноларингологии и хирургии головы и шеи',
               'Kulak Burun Boğaz ve Baş-Boyun Cerrahisi Kliniği'), 1, []),
        ('5', ('Fingerlandův ústav patologie', 'Институт патологии им. Фингерланда', 'Fingerland Patoloji Enstitüsü'), 0, []),
        ('5/1', ('Ústav soudního lékařství', 'Институт судебной медицины', 'Adli Tıp Enstitüsü'), 0, []),
        ('6', ('Klinika Infekčních nemocí', 'Клиника инфекционных болезней', 'Enfeksiyon Hastalıkları Kliniği'), 1, []),
        ('7', ('Psychiatrická klinika', 'Психиатрическая клиника', 'Psikiyatri Kliniği'), 1, []),
        ('8', ('Neurologická klinika', 'Неврологическая клиника', 'Nöroloji Kliniği'), 0, []),
        ('9', ('Porodnická a gynekologická klinika', 'Акушерско-гинекологическая клиника',
               'Kadın Hastalıkları ve Doğum Kliniği'), 1, []),
        ('9/1', ('Tkáňová ústředna – tkáňové zařízení', 'Тканевый центр – банк тканей', 'Doku Merkezi – doku bankası'), 0, []),
        ('10', ('Pavilon interních oborů', 'Корпус терапевтических отделений', 'Dahili Bilimler Binası'), 0, [
            (I_KARDIO, 0),
            (('II. interní gastroenterologická klinika', 'II терапевтическая гастроэнтерологическая клиника',
              'II. İç Hastalıkları – Gastroenteroloji Kliniği'), 0),
            (I_GERONTO, 0),
            (('Oddělení ambulantních provozů', 'Отделение амбулаторной помощи', 'Ayakta Tedavi Bölümü'), 0),
            (('Lékárna U Modrého robota', 'Аптека «U Modrého robota»', 'U Modrého robota Eczanesi'), 1),
        ]),
        ('11', ('Stomatologická klinika', 'Стоматологическая клиника', 'Diş Hekimliği Kliniği'), 1, []),
        ('12', ('Ředitelství FN HK', 'Дирекция FN HK', 'FN HK Yönetimi'), 0, []),
        ('13', ('Transfúzní oddělení', 'Отделение переливания крови', 'Kan Transfüzyon Bölümü'), 0, []),
    ], [
        ('14', ('Plicní pavilon', 'Пульмонологический корпус', 'Göğüs Hastalıkları Binası'), 0, [
            (('Plicní klinika', 'Пульмонологическая клиника', 'Göğüs Hastalıkları Kliniği'), 0),
            (I_KARDIO, 0),
            (I_GERONTO, 0),
            (('Rehabilitační klinika', 'Реабилитационная клиника', 'Rehabilitasyon Kliniği'), 0),
        ]),
        ('15', ('Radiologická klinika – Diagnost. centrum', 'Радиологическая клиника – диагностический центр',
                'Radyoloji Kliniği – Tanı Merkezi'), 0, []),
        ('16', ('Neurochirurgická klinika', 'Нейрохирургическая клиника', 'Beyin Cerrahisi Kliniği'), 0, []),
        ('17', ('Ústav klinické imunologie a alergologie, Ústav klinické mikrobiologie',
                'Институт клинической иммунологии и аллергологии, Институт клинической микробиологии',
                'Klinik İmmünoloji ve Alerji Enstitüsü, Klinik Mikrobiyoloji Enstitüsü'), 0, []),
        ('18', ('Dětská klinika', 'Детская клиника', 'Çocuk Kliniği'), 1, []),
        ('20', ('Nemocniční lékárna', 'Больничная аптека', 'Hastane Eczanesi'), 0, []),
        ('21', ('Pavilon Akademika Bedrny', 'Корпус академика Бедрны', 'Akademisyen Bedrna Binası'), 0, [
            (('Chirurgická klinika', 'Хирургическая клиника', 'Genel Cerrahi Kliniği'), 0),
            (('Kardiochirurgická klinika', 'Кардиохирургическая клиника', 'Kalp Cerrahisi Kliniği'), 0),
            (('Urologická klinika', 'Урологическая клиника', 'Üroloji Kliniği'), 0),
            (('Odd. centrálních sálů a sterilizace', 'Отд. центральных операционных и стерилизации',
              'Merkezi Ameliyathane ve Sterilizasyon Böl.'), 0),
            (('KARIM', 'KARIM (анестезиология и реанимация)', 'KARIM (Anestezi ve Yoğun Bakım)'), 0),
        ]),
        ('22', ('Ústav klinické biochemie a diagnostiky, Klinika nemocí kožních a pohlavních',
                'Институт клинической биохимии и диагностики, Клиника кожных и венерических болезней',
                'Klinik Biyokimya ve Tanı Enstitüsü, Dermatoloji ve Zührevi Hastalıklar Kliniği'), 0, []),
    ], [
        ('23', ('Pavilon profesora Bašteckého', 'Корпус профессора Баштецкого', 'Profesör Baštecký Binası'), 0, [
            (('Kl. onkologie a radioterapie', 'Клиника онкологии и радиотерапии', 'Onkoloji ve Radyoterapi Kliniği'), 0),
            (('Odd. nukleární medicíny', 'Отделение ядерной медицины', 'Nükleer Tıp Bölümü'), 0),
            (('IV. interní hematologická klinika', 'IV терапевтическая гематологическая клиника',
              'IV. İç Hastalıkları – Hematoloji Kliniği'), 0),
        ]),
        ('24', ('Odbor výpočetních systémů (OVS)', 'Отдел вычислительных систем (OVS)', 'Bilgi İşlem Dairesi (OVS)'), 0, []),
        ('27', ('Hemodialyzační středisko', 'Центр гемодиализа', 'Hemodiyaliz Merkezi'), 0, []),
        ('28', ('Hlavní vrátnice (vjezdová)', 'Главная проходная (въезд)', 'Ana kapı (araç girişi)'), 0, []),
        ('29', ('Reprocentrum, OÚ, CTBT, ONH, Oddělení péče o zaměstnance, Odborová organizace, Oddělení vzdělávání',
                'Репроцентр, OÚ, CTBT, ONH, отдел по работе с персоналом, профсоюз, отдел обучения',
                'Üreme Merkezi, OÚ, CTBT, ONH, Personel Hizmetleri, Sendika, Eğitim Bölümü'), 0, []),
        ('30', ('Stravovací provoz', 'Пищеблок', 'Yemek hizmetleri'), 0, []),
        ('31', ('Prádelna, MTZ – sklad prádla', 'Прачечная, MTZ – склад белья', 'Çamaşırhane, MTZ – çamaşır deposu'), 0, []),
        ('34', ('MTZ', 'MTZ (снабжение)', 'MTZ (malzeme tedarik)'), 0, []),
        ('40', ('Výukové centrum LF UK', 'Учебный центр мед. факультета UK', 'LF UK Eğitim Merkezi'), 0, []),
        ('43, 44', ('Sklad SZM', 'Склад медицинских материалов', 'Tıbbi malzeme deposu'), 0, []),
        ('45', ('Centrální spisovna', 'Центральный архив', 'Merkez arşiv'), 0, []),
        ('46', ('Odbor MTZ', 'Отдел MTZ', 'MTZ Dairesi'), 0, []),
        ('47', ('Provozní odbor, Depozita', 'Хозяйственный отдел, камера хранения', 'İşletme Dairesi, emanet'), 0, []),
        ('48', ('Vstupní budova, Odbor investic, OZT, Odd. kriz. managementu, Odd. soc. péče, Informace, Tel. ústředna, '
                'LOK, ČLK, Tkáňová ústředna – orgánová banka',
                'Входной корпус, отдел инвестиций, OZT, отд. кризисного управления, отд. соц. помощи, информация, '
                'телефонная станция, LOK, ČLK, тканевый центр – банк органов',
                'Giriş binası, Yatırım Dairesi, OZT, Kriz Yönetimi Böl., Sosyal Hizmetler Böl., Danışma, Santral, '
                'LOK, ČLK, Doku Merkezi – organ bankası'), 0, []),
        ('50', ('Pohotovost – Emergency', 'Неотложная помощь – Emergency', 'Acil servis – Emergency'), 1, []),
    ],
]
COL_X = [(70.0, 232), (238.1, 407), (412.9, 586)]   # left edge, right limit (PDF points)
LIST_TOP, LIST_BOTTOM = 635.5, 889

CROSS = ('<svg class="x" viewBox="0 0 11 11"><rect width="11" height="11" rx="1.6" fill="#c2121a"/>'
         '<path d="M4.1 1.6h2.8v2.5h2.5v2.8H6.9v2.5H4.1V6.9H1.6V4.1h2.5z" fill="#fff"/></svg>')


def base_png(out_png):
    """Original map without the texts that get translated, rendered at K."""
    doc = fitz.open(PDF)
    page = doc[0]
    # 1) vector-outlined texts (gate labels, legend) + the list with its icons: remove line art fully inside
    for r in [(182, 58.5, 236, 77.5), (433.5, 299, 510, 319), (92, 430, 186.5, 622), (60, 630, 588, 892)]:
        page.add_redact_annot(fitz.Rect(*r), fill=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED)
    # 2) live Czech text that gets translated (title, cargo gate); numbers, streets and stop names stay
    for b in page.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            t = ''.join(s['text'] for s in line['spans'])
            if t.startswith(('Orientační plán', 'NÁKLADNÍ', '(technický')):
                page.add_redact_annot(line['bbox'], fill=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    page.get_pixmap(matrix=fitz.Matrix(K, K)).save(out_png)


def esc(s):
    return html.escape(s, quote=False)


def with_icon(text, icon):
    """Text, optionally followed by the emergency icon glued to the last word (never alone on a line)."""
    if not icon:
        return esc(text)
    head, _, last = text.rpartition(' ')
    return (esc(head) + ' ' if head else '') + '<span class="nw">%s%s</span>' % (esc(last), CROSS)


def page_html(lang):
    i = L[lang]
    parts = []
    for cx, y, texts in GATES:
        a, b = texts[i]
        parts.append('<text class="gate" x="%s" y="%s">%s</text><text class="gate" x="%s" y="%s">%s</text>'
                     % (cx, y, esc(a), cx, y + 8.4, esc(b)))
    for n, t in enumerate(LEGEND):
        parts.append('<text class="leg fit" data-maxw="88" x="96.4" y="%.2f">%s</text>' % (441.95 + 15.83 * n, esc(t[i])))
    parts.append('<text class="title fit" data-maxw="571" transform="translate(39 646.1) rotate(-90)">%s</text>' % esc(TITLE[i]))
    svg_texts = '\n'.join(parts)

    cols = []
    for (x, right), col in zip(COL_X, COLUMNS):
        items = []
        for num, name, icon, subs in col:
            items.append('<div class="it"><span class="n">%s</span><span class="t">%s</span></div>'
                         % (esc(num), with_icon(name[i], icon)))
            for sub, sicon in subs:
                items.append('<div class="sub">– %s</div>' % with_icon(sub[i], sicon))
        cols.append('<div class="col" style="left:%spx;width:%spx">%s</div>' % (x, right - x, ''.join(items)))

    overlay = oe_label(HERE_TXT[i])
    return '''<!doctype html><html lang="%(lang)s"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Arimo:wght@400;700&family=Cinzel:wght@700;900&family=Source+Sans+3:ital,wght@0,400;1,600&display=block" rel="stylesheet">
<style>
html,body{margin:0;background:#fff}
.page{position:relative;width:%(W)spx;height:%(H)spx;overflow:hidden}
.page img,.page svg.top{position:absolute;left:0;top:0;width:%(W)spx;height:%(H)spx}
.gate{font:700 7px Arimo,sans-serif;fill:%(RED)s;text-anchor:middle}
.leg{font:400 7px Arimo,sans-serif;fill:#1f1e21}
.title{font:italic 600 26.6px 'Source Sans 3',sans-serif;fill:#000}
.col{position:absolute;top:%(TOP)spx;font:400 8.6px/10.3px 'Source Sans 3',sans-serif;color:#000}
.it{display:grid;grid-template-columns:minmax(17px,max-content) 1fr}
.n{white-space:nowrap;padding-right:3px}
.nw{white-space:nowrap}
.sub{padding-left:23px;text-indent:-6px}
.x{display:inline-block;width:1.3em;height:1.3em;vertical-align:-.28em;margin-left:.35em}
</style></head><body>
<div class="page">
<img src="base.png" alt="">
<svg class="top" viewBox="0 0 %(W)s %(H)s" xmlns="http://www.w3.org/2000/svg">
%(texts)s
%(overlay)s
</svg>
%(cols)s
</div>
<script>
document.fonts.ready.then(function () {
  // texts that must stay inside their box get smaller
  document.querySelectorAll('text.fit').forEach(function (t) {
    var max = +t.dataset.maxw, w = t.getComputedTextLength();
    if (w > max) t.style.fontSize = (parseFloat(getComputedStyle(t).fontSize) * max / w) + 'px';
  });
  // the building list must end above the bottom edge: shrink all three columns together
  var cols = document.querySelectorAll('.col'), size = 8.6;
  function bottom() { var b = 0; cols.forEach(function (c) { b = Math.max(b, c.getBoundingClientRect().bottom); }); return b; }
  while (bottom() > %(BOTTOM)s && size > 6) {
    size -= 0.1;
    cols.forEach(function (c) { c.style.fontSize = size + 'px'; c.style.lineHeight = (size * 1.2) + 'px'; });
  }
});
</script></body></html>''' % {'lang': lang, 'W': W, 'H': H, 'RED': RED, 'TOP': LIST_TOP, 'BOTTOM': LIST_BOTTOM,
                             'texts': svg_texts, 'overlay': overlay, 'cols': '\n'.join(cols)}


def quantize(im):
    return im.quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)


def build(lang):
    out_dir = SITE / 'obrazky' / lang if lang != 'cs' else HERE / '_kontrola-cs'
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        base_png(tmp / 'base.png')
        (tmp / 'page.html').write_text(page_html(lang), encoding='utf-8')
        shot(tmp / 'page.html', tmp / 'shot.png', W, H + 1, K)
        full = Image.open(tmp / 'shot.png').convert('RGB')
    full = full.crop((0, 0, 2400, 3628))            # same pixel size as the Czech images
    quantize(full).save(out_dir / 'mapa-arealu-fnhk.png', optimize=True)
    small = full.resize((1200, 1814), Image.LANCZOS)
    quantize(small).save(out_dir / 'mapa-arealu-fnhk-1200.png', optimize=True)
    print('  %s: mapa-arealu-fnhk.png %s, -1200.png %s' % (out_dir, full.size, small.size))


if __name__ == '__main__':
    for lang in sys.argv[1:] or ['ru', 'tr']:
        build(lang)
