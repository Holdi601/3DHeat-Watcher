---
title: "Vzdrževanje"
nav_order: 15
lang: "sl"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Vzdrževanje teh strani {#maintaining-these-pages}

Seznam opravil za vsako izdajo. Strani morajo povedati, kaj koda dela, biti razumljive začetniku, osemletniku in strokovnjaku ter obstajati v vseh jezikih, ki jih podpira pregledovalnik 3DHeat.

## Seznam za izdajo {#release-checklist}

1. **Ponovno ustvarite generirane strani** iz kode:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Pred potrditvijo mora enako z `--check` vrniti 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Primerjajte funkcije od zadnje izdaje.** `VERSION` hrani različico; njena oznaka je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Vsak nov ukaz, možnost, stolpec, izpis ali vedenje dobi vrstico na strani, ki ga opisuje, in vrstico v `CHANGELOG.md` pod **Docs**, ki navaja to stran.

3. **Neodvisen pregled.** Nekdo, ki ni napisal spremembe, prebere spremenjene strani - tudi diagrame in slike - trikrat: kot začetnik (še nikoli ni uporabil terminala), kot osemletnik (ali prvi odstavek pove, kaj to je in zakaj, z jasnimi besedami?) in kot strokovnjak (so zastavice, privzete vrednosti in stolpci točno to, kar koda dela?).

4. **Popravite, kar je pregled našel.** Slike ostanejo široke največ okoli 900 px, z besedilom vsaj 12 px, kakor so prikazane; diagrami so ustvarjeni iz `tools/diagrams/*.json` s `tools/flow2svg.py`. Primeri uporabljajo samo izmišljena imena (`de_x`, "Demo Valley", `<map>`): nikoli pravega zemljevida, igralca, ID-ja tekme ali lika iz pravih datotek.

5. **Prevodi.** Vsaka prevedena stran beleži zgoščeno vrednost (hash) angleškega vira, iz katerega je nastala. Ponovno prevedite strani, katerih zgoščena vrednost angleškega vira se je spremenila, nato jih za vsak jezik pregledajo na enake tri načine (preprosto, začetnik, strokovnjak), tudi oznake na diagramih.

6. **Objavite šele po dovoljenju lastnika.** Potrdite lokalno; lastnik odloči, kdaj gre javno.

## Prevodi: ukazi {#translations-the-commands}

Stran je prevedena v 40 jezikov pregledovalnika 3DHeat: angleščina je v `docs/`, vsak drug jezik pa v `docs/<lang>/` z enakimi imeni datotek. `tools/docs_i18n.py` vodi evidenco:

```bash
python tools/docs_i18n.py hashes             # po vsaki angleški spremembi: zapišite zgoščeno vrednost vsake strani
python tools/docs_i18n.py svg-strings        # po vsaki spremembi slike: oznake za prevod
python tools/docs_i18n.py status             # po jezikih: aktualne, zastarele in manjkajoče strani
python tools/docs_i18n.py todo --lang de     # nemške strani za (ponovni) prevod
python tools/docs_i18n.py svg-build --lang de    # nemške slike iz docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # nemške strani označi z zgoščeno vrednostjo angleškega vira
python tools/docs_i18n.py check              # izhod 1, ko so zgoščene vrednosti ali oznake zastarele
```

Prevedite samo tisto, kar navede `todo`: ohranite Markdown, povezave, kodo, imena datotek in stolpcev, prevedite naslove in opise slik ter uporabljajte besede pregledovalnika 3DHeat za njegove gumbe in plošče (njegov `src/i18n/locales/<lang>/`). Generirane referenčne strani in slike terminala ostanejo v angleščini. Na spletnem mestu zastarel prevod to pove in povezuje na angleško stran; manjkajoča stran se vrne na angleščino. Jezikovni meni v glavi in preusmeritev na domači strani glede na jezik brskalnika prihajata iz `docs/_includes/`.
