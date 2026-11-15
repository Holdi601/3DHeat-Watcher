---
title: "Održavanje"
nav_order: 15
lang: "bs"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Održavanje ovih stranica {#maintaining-these-pages}

Kontrolna lista za svako izdanje. Stranice moraju reći šta kod radi, čitati se dobro početniku,
osmogodišnjaku i profesionalcu, i postojati na svakom jeziku koji preglednik 3DHeat podržava.

## Kontrolna lista izdanja {#release-checklist}

1. **Ponovo generirajte generirane stranice** iz koda:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Prije commita isto s `--check` mora završiti s 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Usporedite funkcije od zadnjeg izdanja.** `VERSION` drži verziju; njena oznaka je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Svaka nova komanda, opcija, kolona, izlaz ili ponašanje dobiva liniju na stranici koja ih pokriva, i
   liniju u `CHANGELOG.md` pod **Docs** koja imenuje tu stranicu.

3. **Neovisan pregled.** Neko ko nije pisao promjenu čita promijenjene stranice - uključujući dijagrame i
   slike - tri puta: kao početnik (nikad nije koristio terminal), kao osmogodišnjak (kaže li
   prvi odlomak šta je to i zašto, jednostavnim riječima?) i kao profesionalac (jesu li zastavice, zadane vrijednosti i
   kolone tačno ono što kod radi?).

4. **Popravite ono što je pregled našao.** Slike ostaju široke najviše oko 900 px s tekstom od najmanje 12 px
   kako je prikazano; dijagrami se generiraju iz `tools/diagrams/*.json` pomoću `tools/flow2svg.py`. Primjeri koriste
   samo izmišljena imena (`de_x`, "Demo Valley", `<map>`): nikad pravu mapu, igrača, id meča ili broj
   iz pravih datoteka.

5. **Prijevodi.** Svaka prevedena stranica bilježi hash engleskog izvora iz kojeg je napravljena.
   Ponovo prevedite stranice kojima se hash engleskog izvora promijenio, pa svaki jezik pregledajte na isti
   tri načina (jednostavno, početnik, profesionalac), uključujući oznake na dijagramima.

6. **Objavite tek nakon odobrenja vlasnika.** Commitajte lokalno; vlasnik odlučuje kad ide javno.

## Prijevodi: komande {#translations-the-commands}

Stranica je prevedena na 40 jezika preglednika 3DHeat: engleski u `docs/`, svaki drugi
jezik u `docs/<lang>/` s istim imenima datoteka. `tools/docs_i18n.py` vodi evidenciju:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Prevodite samo ono što `todo` navodi: Markdown, linkove, kod, imena datoteka i kolona ostavite kakvi jesu,
prevedite naslove i opise slika, i koristite vlastite riječi preglednika 3DHeat za njegove tastere
i panele (njegov `src/i18n/locales/<lang>/`). Generirane referentne stranice i slike terminala ostaju
engleske. Na stranici zastarjeli prijevod to kaže i povezuje englesku stranicu; nedostajući
vraća se na engleski. Izbornik jezika u zaglavlju i preusmjeravanje početne stranice prema jeziku preglednika
dolaze iz `docs/_includes/`.
