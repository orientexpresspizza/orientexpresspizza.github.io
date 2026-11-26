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
| mapa-arealu-fnhk.png | Plán areálu FN HK s vyznačeným Orient Express Pizza |
| nahled-sdileni.jpg | Náhled při sdílení odkazu (1200×630) |

## Telefon, adresa, otevírací doba
Jsou v souboru `index.html` – vyhledejte `724 252 217` (telefon je na několika místech), `Sokolská` a `Otevírací doba`
(tužka ✏️ = upravit, pak **Commit changes**).

## Soubor CNAME
Obsahuje doménu `orientexpresspizza.eu`. Nemažte ho.

## Upoutávka „Otevíráme 7. prosince“
Po 7. 12. 2026 se sama skryje. Natrvalo ji odstraníte smazáním prvků s třídou `js-opening` v `index.html`.
