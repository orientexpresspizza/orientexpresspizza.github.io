# Regenerates obrazky/mapa-arealu-fnhk.png (full size) and obrazky/mapa-arealu-fnhk-1200.png (page copy).
# Run from this folder:  pdftocairo -svg mapa-fnhk-original.pdf mapa.svg  (once)
#                        python3 render_map.py
# Needs: playwright (chromium), Pillow, fonts Cinzel[wght].ttf + Arimo[wght].ttf in ./fonts (or FONTS_DIR).
import os, asyncio, subprocess, sys
from playwright.async_api import async_playwright
from PIL import Image

K = 2400 / 592                       # px per PDF point
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
subprocess.run([sys.executable, "overlay.py"], check=True)
asyncio.run(shot("mapa_oe.png"))
full = Image.open("mapa_oe.png").convert("RGB")
q(full).save(f"{OUT}/mapa-arealu-fnhk.png", optimize=True)                     # opened on tap (zoom)
small = full.resize((1200, round(full.height * 1200 / full.width)), Image.LANCZOS)
q(small).save(f"{OUT}/mapa-arealu-fnhk-1200.png", optimize=True)              # shown on the page (less memory on phones)
print("hotovo:", OUT)
