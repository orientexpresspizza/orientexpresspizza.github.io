# Regenerates obrazky/mapa-arealu-fnhk.png (with DETAIL frame) and obrazky/mapa-detail.png.
# Run from this folder:  pdftocairo -svg mapa-fnhk-original.pdf mapa.svg  (once)
#                        python3 render_map.py
# Needs: playwright (chromium), Pillow, fonts Cinzel[wght].ttf + Arimo[wght].ttf in ./fonts (or FONTS_DIR).
import os, asyncio, subprocess, sys
from playwright.async_api import async_playwright
from PIL import Image

K = 2400 / 592                       # px per PDF point
DETAIL = (150, 59, 560, 223.5)        # detail crop in PDF points – keep in sync with DZ in overlay.py
OUT = os.path.abspath("../../obrazky")

async def shot(path):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 592, "height": 895}, device_scale_factor=K)
        await pg.goto("file://" + os.path.abspath("mapa_oe.html"))
        await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(800)
        await pg.screenshot(path=path)
        await b.close()

def q(im):
    return im.quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)

if not os.path.exists("mapa.svg"):
    subprocess.run(["pdftocairo", "-svg", "mapa-fnhk-original.pdf", "mapa.svg"], check=True)
for frame in ("0", "1"):
    subprocess.run([sys.executable, "overlay.py"], check=True, env={**os.environ, "FRAME": frame})
    asyncio.run(shot(f"mapa_oe_{frame}.png"))
plain = Image.open("mapa_oe_0.png").convert("RGB")
framed = Image.open("mapa_oe_1.png").convert("RGB")
q(framed).save(f"{OUT}/mapa-arealu-fnhk.png", optimize=True)
x0, y0, x1, y1 = DETAIL
q(plain.crop((round(x0*K), round(y0*K), round(x1*K), round(y1*K)))).save(f"{OUT}/mapa-detail.png", optimize=True)
print("hotovo:", OUT)
