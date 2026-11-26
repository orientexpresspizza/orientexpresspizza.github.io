# Orient Express Pizza – website (handoff)

Static one-page website for **Orient Express Pizza**, a new pizzeria inside the grounds of Fakultní nemocnice
Hradec Králové. Hosted free on **GitHub Pages** at **https://orientexpresspizza.eu** (domain in the `CNAME` file).
Owner communicates in English; **all website text is Czech**.

## Files
- `index.html` – the whole site (HTML + inline CSS + small JS). No build step, no framework.
- `obrazky/` – all images. The menu and posters are **images**, updated by uploading a new file with the
  **same file name** (see README.md, written in Czech for the owner).
  - `menu-1-pizza-classic.jpg`, `menu-2-pizza-premium.jpg`, `menu-3-burgery-kofte.jpg`, `menu-4-panini.jpg`
  - `akce-1-kofte-pizza.jpg`, `akce-3-coca-cola.jpg` (posters; panini was moved from Akce to Menu on request)
  - `mapa-arealu-fnhk.png` – full campus map with branding overlay + gold DETAIL frame
  - `mapa-detail.png` – crop of the DETAIL area, shown under the "Telefon a WhatsApp" card
  - `nahled-sdileni.jpg` – 1200×630 social share preview
- `zdroje/mapa/` – sources to regenerate the two map images (`overlay.py`, `render_map.py`, original PDF).
- `favicon.svg`, `CNAME` (do not delete), `README.md` (Czech instructions for the owner).

## Business facts (confirmed by owner)
- Phone / WhatsApp: **+420 724 252 217** (tel: and wa.me links appear in several places – change all)
- Address: **Sokolská 581, 500 05 Hradec Králové – Nový Hradec Králové**, inside FN HK near building 24,
  next to the Občerstvení sign. Google Maps link:
  `https://www.google.com/maps/place//data=!4m2!3m1!1s0x470c2b368ed8c40f:0xcc2b7b6991b3da63`
- Opening hours: Po–Pá 06:00–18:00, So 06:00–18:00, Ne zavřeno (also in the JSON-LD block in `<head>`).
- Orders for now **only by phone or WhatsApp**. Online ordering via Speedlo is planned – a commented-out
  "Objednat online" button is ready in the hero section.
- Amenities: venkovní terasa, stolky uvnitř, WC.
- **Opening day: Monday 7 December 2026.** The teaser (gold ribbon + "Velké otevření" card with a countdown)
  hides itself automatically from 8 Dec 2026 (script at the bottom of `index.html`, elements `.js-opening`).
- Footer: `© 2026 Orient Express Pizza · orientexpresspizza.eu`

## Design
Black + gold art-deco look matching the printed wall/window menus.
Colours: bg `#0d0b08`, gold `#ddb257` (gradient `#f7e2a0 → #d9ac52 → #b8883a`), cream text `#f5e9cc`.
Fonts (Google Fonts): Cinzel (headings/logo), Playfair Display (names), Josefin Sans (body).
Map overlay red = the map's own arrow red `#AC2A2F`; "JSME TADY" uses Arial-bold style (Arimo), no outline.
Responsive: on ≤820 px the layout stacks, landscape menu panels scroll sideways, and a fixed bottom bar
shows Zavolat / WhatsApp / Menu.

## Map overlay (approved after many iterations – change only on request)
In `zdroje/mapa/overlay.py`, PDF-point coordinates: red oval around the Občerstvení sign + adjacent building
(not the building below), map-style red arrow placed diagonally above the gold label pointing into the oval,
"JSME TADY" on the green/light-grey area, gold "ORIENT EXPRESS / PIZZA" label right next to the oval.
Detail crop `DETAIL = (150, 59, 560, 223.5)` was sized so the detail fits under the phone card on desktop and its
bottom aligns with the full map's bottom (1366 px wide viewport).

## Still open
- Domain: owner registered `orientexpresspizza.eu`; registrar not yet known. DNS needed:
  4× A `185.199.108.153` … `185.199.111.153`, 4× AAAA `2606:50c0:8000::153` … `8003::153`,
  CNAME `www` → `<github-username>.github.io`. Add the custom domain in repo Settings → Pages first,
  then DNS, then tick Enforce HTTPS. Recommend verifying the domain in GitHub account settings.
- Speedlo online-ordering link when available.
- Printed materials (wall menu, window stickers, posters) were produced in a separate design session;
  prices on the menu images: classic pizza 34 cm 230 Kč / 40 cm 250 Kč, premium 260 / 280 Kč.
