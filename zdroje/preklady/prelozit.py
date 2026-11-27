#!/usr/bin/env python3
"""Generate the localized landing pages (/ru/, /tr/) from the Czech index.html.

index.html stays the only page that is edited by hand. This script copies it into <lang>/index.html,
replacing every Czech text with its translation from <lang>.json (a dictionary "Czech text" -> "translation").
Prices, phone numbers, images and the layout therefore always stay identical to the Czech page.

Texts that are missing in a dictionary stay in Czech and are reported as warnings
(e.g. after a menu item was changed on the Czech page). Strings listed in ponechat.json
(proper names such as "Margherita") are intentionally left as they are.

Usage:
  python3 zdroje/preklady/prelozit.py            # write ru/index.html and tr/index.html
  python3 zdroje/preklady/prelozit.py --seznam   # print all translatable texts (JSON) for translators
  python3 zdroje/preklady/prelozit.py --strict   # exit with code 1 if any text is untranslated

Standard library only (runs in GitHub Actions without pip install).
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
SRC = SITE / 'index.html'
BASE_URL = 'https://orientexpresspizza.eu/'

LANGS = {
    # code: Open Graph locale, extra Google Fonts families (fallbacks for glyphs the base fonts lack)
    'ru': {'og': 'ru_RU', 'fonts': '&family=Playfair+Display+SC:wght@700;900&family=Jost:wght@400;600'},
    'tr': {'og': 'tr_TR', 'fonts': ''},
}

TOKEN = re.compile(r'<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<[^>]+>|[^<]+', re.S)
ATTR = re.compile(r'([\w:.-]+)="([^"]*)"')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
TEXT_ATTRS = {'alt', 'title', 'aria-label'}
META_TEXT = {'description', 'og:title', 'og:description', 'og:image:alt'}
# texts without anything to translate: numbers, prices, sizes, times, phone numbers
NOTHING = re.compile(r'[\d\s.,:;·–+\-ø¼()]*(?:\s*(?:cm|Kč|g))?[\d\s.,:;·–+\-()]*')


def norm(t):
    return ' '.join(t.split())


def needs_translation(t, keep):
    return bool(t) and t not in keep and not NOTHING.fullmatch(t) and re.search(r'[^\W\d_]', t)


def wa_text(href):
    m = re.match(r'(https://wa\.me/\d+\?text=)(.*)$', href)
    return (m.group(1), unquote(m.group(2))) if m else (None, None)


def jsonld_strings(data):
    """Translatable string values of the JSON-LD block."""
    out = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == 'description' and isinstance(v, str):
                out.append(v)
            elif k == 'servesCuisine':
                out += [x for x in v if isinstance(x, str)]
            elif k == 'amenityFeature':
                out += [f['name'] for f in v if isinstance(f, dict) and 'name' in f]
            elif isinstance(v, (dict, list)):
                out += jsonld_strings(v)
    elif isinstance(data, list):
        for v in data:
            out += jsonld_strings(v)
    return out


def process(src, tr, keep, lang=None):
    """Walk the page. tr=None -> only collect texts. Returns (output html, list of texts, untranslated)."""
    found, missing, out = [], [], []
    stack = []  # open elements: (tag name, translate="no")

    def t(text):
        text = norm(text)
        if not needs_translation(text, keep):
            return None
        if text not in found:
            found.append(text)
        if tr is None:
            return None
        if tr.get(text):
            return tr[text]
        if text not in missing:
            missing.append(text)
        return None

    def no_translate():
        return any(n for _, n in stack)

    for m in TOKEN.finditer(src):
        tok = m.group(0)
        if tok.startswith('<!--') or tok.startswith('<style'):
            out.append(tok)
        elif tok.startswith('<script'):
            if 'application/ld+json' in tok[:80]:
                body = tok[tok.index('>') + 1:tok.rindex('</script>')]
                for s in jsonld_strings(json.loads(body)):
                    new = t(s)
                    if new:
                        tok = tok.replace(json.dumps(s, ensure_ascii=False), json.dumps(new, ensure_ascii=False))
                if lang:
                    tok = tok.replace('"hasMenu": "%s#menu"' % BASE_URL, '"hasMenu": "%s%s/#menu"' % (BASE_URL, lang))
                    tok = localized_image_urls(tok, lang)
            out.append(tok)
        elif tok.startswith('</'):
            name = tok[2:-1].strip().lower()
            while stack:
                if stack.pop()[0] == name:
                    break
            out.append(tok)
        elif tok.startswith('<!') or tok.startswith('<?'):
            out.append(tok)
        elif tok.startswith('<'):
            name = re.match(r'<\s*([\w-]+)', tok).group(1).lower()
            attrs = dict(ATTR.findall(tok))
            skip = no_translate() or attrs.get('translate') == 'no'

            def sub_attr(am):
                k, v = am.group(1), am.group(2)
                new = None
                if not skip and (k in TEXT_ATTRS or (k == 'content' and (attrs.get('name') in META_TEXT or attrs.get('property') in META_TEXT))):
                    new = t(html.unescape(v))
                    new = html.escape(new) if new else None
                if k == 'href' and not skip:
                    prefix, msg = wa_text(v)
                    if prefix:
                        tm = t(msg)
                        if tm:
                            trail = msg[len(msg.rstrip()):]
                            new = prefix + quote(tm + trail, safe='')
                if lang and k in ('href', 'src') and new is None:
                    new = relink(k, v, name, attrs, lang)
                return '%s="%s"' % (k, new) if new is not None else am.group(0)

            tok = ATTR.sub(sub_attr, tok)
            if lang and name == 'html':
                # the visitor picked this language: stop browsers from auto-translating it back (e.g. Chrome → Czech)
                tok = tok.replace('lang="cs"', 'lang="%s" translate="no"' % lang)
            if lang and name == 'meta' and attrs.get('charset'):
                tok += '\n<meta name="google" content="notranslate">'
            if lang and name == 'meta' and attrs.get('property') == 'og:locale':
                tok = tok.replace('cs_CZ', LANGS[lang]['og'])
            if lang and name == 'meta' and attrs.get('property') == 'og:image':
                tok = localized_image_urls(tok, lang)
            if lang and name == 'meta' and attrs.get('property') == 'og:url':
                tok = tok.replace('content="%s"' % BASE_URL, 'content="%s%s/"' % (BASE_URL, lang))
            out.append(tok)
            if name not in VOID and not tok.endswith('/>'):
                stack.append((name, attrs.get('translate') == 'no'))
        else:
            if no_translate() or (stack and stack[-1][0] in ('script', 'style')):
                out.append(tok)
                continue
            new = t(html.unescape(tok))
            if new:
                lead = tok[:len(tok) - len(tok.lstrip())]
                trail = tok[len(tok.rstrip()):]
                out.append(lead + html.escape(new, quote=False) + trail)
            else:
                out.append(tok)
    return ''.join(out), found, missing


def relink(attr, v, tag, attrs, lang):
    """Rewrite links for a page living one folder deeper (/<lang>/index.html)."""
    if tag == 'link' and attrs.get('rel') == 'alternate':
        return None  # hreflang links are the same on every page
    if tag == 'link' and attrs.get('rel') == 'canonical':
        return '%s%s/' % (BASE_URL, lang)
    if tag == 'link' and 'fonts.googleapis.com/css2' in v:
        amp = '&amp;' if '&amp;' in v else '&'
        return v.replace(amp + 'display=swap', LANGS[lang]['fonts'].replace('&', amp) + amp + 'display=swap')
    if v == '/':
        return None if tag == 'a' and attrs.get('hreflang') else '/%s/' % lang
    if re.match(r'(#|/|[a-z][a-z0-9+.-]*:)', v):
        return None
    return '../' + localized_image(v, lang)


def localized_image(path, lang):
    """obrazky/x.jpg -> obrazky/<lang>/x.jpg when a translated version of the image exists."""
    if path.startswith('obrazky/'):
        alt = 'obrazky/%s/%s' % (lang, path[len('obrazky/'):])
        if (SITE / alt).is_file():
            return alt
    return path


def localized_image_urls(text, lang):
    """Absolute image URLs (og:image, JSON-LD) -> translated version when it exists."""
    def sub(m):
        return BASE_URL + localized_image(m.group(1), lang)
    return re.sub(re.escape(BASE_URL) + r'(obrazky/[\w./-]+)', sub, text)


def finish(page, lang):
    code = lang.upper()
    page = page.replace('<span class="lang-cur" translate="no">CS</span>', '<span class="lang-cur" translate="no">%s</span>' % code)
    page = page.replace(' aria-current="page">', '>')
    page = page.replace('hreflang="%s" lang="%s">' % (lang, lang), 'hreflang="%s" lang="%s" aria-current="page">' % (lang, lang))
    note = ('<!-- VYGENEROVÁNO z /index.html skriptem zdroje/preklady/prelozit.py – neupravujte ručně, '
            'změny se přepíšou. Překlady jsou v zdroje/preklady/%s.json. -->\n' % lang)
    return page.replace('<!doctype html>\n', '<!doctype html>\n' + note, 1)


def main():
    src = SRC.read_text(encoding='utf-8')
    keep = set(json.loads((HERE / 'ponechat.json').read_text(encoding='utf-8')))
    if '--seznam' in sys.argv:
        _, found, _ = process(src, None, keep)
        print(json.dumps(found, ensure_ascii=False, indent=1))
        return 0
    total_missing = 0
    for lang in LANGS:
        tr = json.loads((HERE / ('%s.json' % lang)).read_text(encoding='utf-8'))
        page, found, missing = process(src, tr, keep, lang)
        out = SITE / lang / 'index.html'
        out.parent.mkdir(exist_ok=True)
        out.write_text(finish(page, lang), encoding='utf-8')
        unused = [k for k in tr if k not in found]
        print('%s/index.html: %d texts, %d untranslated, %d unused dictionary entries'
              % (lang, len(found), len(missing), len(unused)))
        for s in missing:
            print('::warning::%s – untranslated (stays Czech): %s' % (lang, s))
        for s in unused:
            print('  note: %s.json entry no longer on the page: %s' % (lang, s[:80]))
        total_missing += len(missing)
    return 1 if total_missing and '--strict' in sys.argv else 0


if __name__ == '__main__':
    sys.exit(main())
