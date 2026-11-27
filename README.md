# Orient Express Pizza – web

Statická stránka na GitHub Pages: https://orientexpresspizza.eu

## Jak upravit menu (ceny, názvy, složení)
Menu je **text** v souboru `index.html` (část `<section id="menu">`), takže se na mobilu samo přizpůsobí šířce displeje.
1. Otevřete `index.html` a klikněte na tužku ✏️.
2. Vyhledejte (Ctrl+F) název jídla nebo cenu a přepište ji. Ceny pizzy (34 cm / 40 cm) jsou v hlavičce
   sekce Pizza Classic a Pizza Premium, ostatní ceny jsou u jednotlivých položek (např. `190 Kč`).
3. Dole klikněte **Commit changes**. Za 1–2 minuty je změna na webu
   (v prohlížeči případně obnovte stránku Ctrl+F5).

Novou položku přidáte zkopírováním celého řádku `<li>…</li>` sousední položky a přepsáním textu.
Pozor: tištěné menu na oknech je samostatné – při změně ceny ho upravte zvlášť.

## Jak aktualizovat plakáty (Akce) a obrázky
1. Otevřete složku `obrazky`.
2. Klikněte **Add file → Upload files** a nahrajte nový obrázek se **stejným názvem souboru**
   (např. `akce-3-coca-cola.jpg`). Starý se tím nahradí.
3. Dole klikněte **Commit changes**. Za 1–2 minuty je změna na webu.

Doporučení: JPG, šířka 1500–2600 px, velikost do ~500 kB.

| Soubor | Co obsahuje |
|---|---|
| akce-1-kofte-pizza.jpg | Köfte v chlebu / Bowl / Pizza |
| akce-3-coca-cola.jpg | Akce Coca-Cola zdarma |
| mapa-arealu-fnhk.png | Plán areálu FN HK s vyznačeným Orient Express Pizza (plná velikost, otevře se po klepnutí) |
| mapa-arealu-fnhk-1200.png | Totéž zmenšené na šířku 1200 px – zobrazuje se na stránce (při výměně plánu nahraďte oba) |
| nahled-sdileni.jpg | Náhled při sdílení odkazu (1200×630) |

## Telefon, adresa, otevírací doba
Jsou v souboru `index.html` – vyhledejte `724 252 217` (telefon je na několika místech), `Nemocnice 590` a `Otevírací doba`
(tužka ✏️ = upravit, pak **Commit changes**).
Stejné údaje jsou ještě v bloku `application/ld+json` v horní části `index.html` (pro Google) – telefon je tam
zapsán jako `+420724252217`, otevírací doba jako `06:00`/`18:00`. Při změně upravte i tam.

## Jazykové verze (ruština, turečtina)
Web má kromě češtiny ruskou (https://orientexpresspizza.eu/ru/) a tureckou (https://orientexpresspizza.eu/tr/) verzi,
přepínač jazyka je vpravo nahoře.
- **Upravujte jen `index.html`** (česky). Po uložení (Commit changes) se ruská a turecká verze vytvoří znovu samy
  (GitHub Actions, zabere to asi 1–2 minuty navíc). Ceny, telefon, otevírací doba i obrázky se převezmou automaticky.
- Soubory `ru/index.html` a `tr/index.html` **neupravujte ručně** – při další změně se přepíšou.
- Když změníte nebo přidáte český text (např. složení pizzy), zůstane v ruské a turecké verzi česky, dokud se nedoplní
  překlad. Překlady jsou v `zdroje/preklady/ru.json` a `zdroje/preklady/tr.json` (vlevo český text přesně jako
  v `index.html`, vpravo překlad).
- Plakáty (Akce), plán areálu a náhled pro sdílení mají ruskou a tureckou verzi ve složkách `obrazky/ru/` a `obrazky/tr/`
  (stejné názvy souborů). **Když nahrajete nový český plakát**, přeložená verze se sama nezmění – smažte ve složkách
  `obrazky/ru` a `obrazky/tr` soubor se stejným názvem (pak se tam ukáže český plakát), nebo požádejte o nový překlad.

## Soubor CNAME
Obsahuje doménu `orientexpresspizza.eu`. Nemažte ho.

## Ověření pro Google, Seznam a Bing – nemazat
- soubor `googlefeee2772b0309337.html` – ověření webu v Google Search Console,
- řádek `<meta name="seznam-wmt" …>` v hlavičce `index.html` – ověření v Seznam Webmaster.
- řádek `<meta name="msvalidate.01" …>` v hlavičce `index.html` – ověření v Bing Webmaster Tools.

Když je smažete, přestanou fungovat statistiky vyhledávání. Po větší změně obsahu webu upravte datum
v `sitemap.xml` (`<lastmod>`).

## Upoutávka „Otevíráme 7. prosince“
Po 7. 12. 2026 se sama skryje. Natrvalo ji odstraníte smazáním prvků s třídou `js-opening` v `index.html`.
Texty odpočtu ve všech jazycích jsou ve skriptu na konci `index.html`.
