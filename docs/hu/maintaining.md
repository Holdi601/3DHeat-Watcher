---
title: "A oldalak karbantartása"
nav_order: 15
lang: "hu"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Ezen oldalak karbantartása {#maintaining-these-pages}

Minden kiadás ellenőrzőlistája. Az oldalaknak azt kell leírniuk, amit a kód csinál, és érthetőnek kell lenniük egy kezdőnek, egy 8 évesnek és egy szakembernek; minden nyelven létezniük kell, amelyet a 3DHeat megtekintő támogat.

## Kiadási ellenőrzőlista {#release-checklist}

1. **Generáld újra az oldalakat a kódból:**

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   A commit előtt ugyanez a `--check` kapcsolóval kilépési kódja 0 legyen:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Vesd össze a funkciókat az utolsó kiadás óta.** A `VERSION` tartalmazza a verziót; a címkéje `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Minden új parancs, kapcsoló, oszlop, kimenet vagy viselkedés kap egy sort arra az oldalra, amely lefedi, és egy sort a `CHANGELOG.md`-ben a **Docs** alatt, az oldal nevével.

3. **Független átnézés.** Valaki, aki nem írta a változtatást, háromszor olvassa el a változott oldalakat – az ábrákkal és képekkel együtt: kezdőként (soha nem használt terminált), 8 évesként (az első bekezdés megmondja-e egyszerű szavakkal, mi ez és miért?) és szakemberként (a kapcsolók, alapértelmezések és oszlopok pontosan azt teszik-e, amit a kód).

4. **Javítsd, amit az átnézés talált.** A képek legfeljebb körülbelül 900 px szélesek maradnak, 12 px-nél nem kisebb szöveggel, ahogy látszanak; az ábrákat a `tools/diagrams/*.json` fájlokból generáljuk a `tools/flow2svg.py` segítségével. A példák csak kitalált neveket használnak (`de_x`, "Demo Valley", `<map>`): soha nem valódi térképet, játékost, meccsazonosítót vagy valódi fájlokból származó alakzatot.

5. **Fordítások.** Minden lefordított oldal rögzíti annak az angol forrásnak a hash-ét, amelyből készült. Fordítsd újra azokat az oldalakat, amelyek angol forrásának hash-e változott, majd minden nyelvet ugyanúgy három szempontból átnézni (egyszerű, kezdő, szakember), az ábrafeliratokkal együtt.

6. **Csak a tulajdonos jóváhagyásával tolj.** Commitolj helyben; a tulajdonos dönti el, mikor lesz nyilvános.

## Fordítások: a parancsok {#translations-the-commands}

Az oldal a 3DHeat megtekintő 40 nyelvére fordított: az angol a `docs/` mappában van, minden más nyelv a `docs/<lang>/` mappában, azonos fájlnevekkel. A `tools/docs_i18n.py` végzi a nyilvántartást:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Csak azt fordítsd, amit a `todo` listáz: a Markdownt, a hivatkozásokat, a kódot, a fájl- és oszlopneveket hagyd úgy, ahogy vannak; a címeket és a képleírásokat fordítsd; és a 3DHeat megtekintő saját szavait használd a gombjaihoz és paneljeihez (a `src/i18n/locales/<lang>/` mappából). A generált referenciaoldalak és a terminálképek angolok maradnak. A webhelyen a elavult fordítás ezt jelzi, és az angol oldalra mutat; a hiányzó oldal angolra esik vissza. A fejléc nyelvi menüjét és a főoldal böngészőnyelv-átirányítását a `docs/_includes/` adja.
