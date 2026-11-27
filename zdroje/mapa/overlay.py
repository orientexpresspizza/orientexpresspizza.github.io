# Adds the Orient Express marking to the FN HK campus map (coordinates in PDF points).
import os
F = os.environ.get("FONTS_DIR", os.path.abspath("fonts"))   # needs Cinzel[wght].ttf and Arimo[wght].ttf
RED = "rgb(67.498779%, 16.499329%, 18.399048%)"      # exact red of the map's arrows and labels (#AC2A2F)

# 1) red ring around the Občerstvení sign + the building below it
CX, CY, RX, RY = 280.8, 185.6, 23, 11   # oval around the Občerstvení sign + the building next to it

# 2) map-style arrow (same polygon as the HLAVNÍ VCHOD arrow), rotated to point left into the ring
ARROW = "M 0 0 L -9.078585 0 L -9.078585 -16.252524 L -14.265325 -16.252524 L -4.497681 -28.443514 L 5.187883 -16.252524 L 0 -16.252524 Z"
AX, AY, AS = 299.8, 174.4, 1.15      # arrow tip (at the oval's upper-right edge) and scale
ARROT = -145
TX, TY = 319.5, 169      # JSME TADY position (baseline start)                          # rotation: points down-left into the oval

# 3) gold label to the right of the arrow
x0, y0, w, h = 309, 182, 156, 38

def oe_label(here='JSME TADY'):
    """SVG group with the ring, arrow, the 'we are here' text and the gold label (here = translated text)."""
    return f'''
<g id="orient-express">
  <defs>
    <linearGradient id="oeGold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f7e2a0"/><stop offset=".55" stop-color="#d9ac52"/><stop offset="1" stop-color="#b8883a"/>
    </linearGradient>
  </defs>
  <!-- ring with white halo, like the white outline of the map's arrows -->
  <ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="none" stroke="#fff" stroke-width="4.2"/>
  <ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="none" stroke="{RED}" stroke-width="2.6"/>

  <!-- arrow: original points up with tip at (-4.5,-28.4); rotate so it points left, tip at (AX,AY) -->
  <g transform="translate({AX},{AY}) scale({AS}) rotate({ARROT}) translate(4.497681,28.443514)">
    <path d="{ARROW}" fill="{RED}" stroke="#fff" stroke-width="1" stroke-linejoin="miter" fill-rule="evenodd"/>
  </g>
  <text x="{TX}" y="{TY}" text-anchor="start" font-family="Arimo" font-weight="700" font-size="8.2"
        fill="{RED}">{here}</text>

  <!-- gold brand label -->
  <rect x="{x0+1.6}" y="{y0+2.2}" width="{w}" height="{h}" rx="4" fill="#000" opacity=".35"/>
  <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="4" fill="#0d0b08" stroke="url(#oeGold)" stroke-width="2"/>
  <rect x="{x0+3.2}" y="{y0+3.2}" width="{w-6.4}" height="{h-6.4}" rx="2.4" fill="none" stroke="#b8883a" stroke-width=".7"/>
  <text x="{x0+w/2}" y="{y0+19}" text-anchor="middle" font-family="Cinzel" font-weight="900" font-size="14.8"
        letter-spacing=".5" fill="url(#oeGold)">ORIENT EXPRESS</text>
  <text x="{x0+w/2}" y="{y0+32}" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="9.8"
        letter-spacing="3.6" fill="#f5e9cc">PIZZA</text>
</g>'''


if __name__ == '__main__':
  label = oe_label()
  svg = open("./mapa.svg", encoding="utf-8").read()
  svg = svg.replace("</svg>", label + "\n</svg>")
  open("./mapa_oe.svg", "w", encoding="utf-8").write(svg)
  html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
  @font-face {{ font-family: 'Cinzel'; src: url('file://{F}/Cinzel[wght].ttf'); font-weight: 400 900; }}
  @font-face {{ font-family: 'Arimo'; src: url('file://{F}/Arimo[wght].ttf'); font-weight: 400 700; }}
  html,body{{margin:0;background:#fff}} svg{{display:block;width:592px;height:894.457px}}</style></head>
  <body>{svg[svg.index("<svg"):]}</body></html>'''
  open("./mapa_oe.html", "w", encoding="utf-8").write(html)
