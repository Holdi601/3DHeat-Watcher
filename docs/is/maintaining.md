---
title: "Viðhald"
nav_order: 15
lang: "is"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Viðhald þessara síðna {#maintaining-these-pages}

Gátlistinn fyrir hverja útgáfu. Síðurnar verða að segja það sem kóðinn gerir, lesast vel fyrir byrjanda,
8 ára barn og fagmann, og vera til á hverju tungumáli sem 3DHeat-skoðarinn styður.

## Gátlisti útgáfu {#release-checklist}

1. **Búðu til sjálfvirku síðurnar aftur** úr kóðanum:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Áður en þú vistar (commit) verður það sama með `--check` að enda með 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Berðu saman eiginleikana frá síðustu útgáfu.** `VERSION` geymir útgáfuna; merkið hennar er `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Hver ný skipun, valkostur, dálkur, úttak eða hegðun fær línu á síðunni sem fjallar um hana, og
   línu í `CHANGELOG.md` undir **Docs** sem nefnir þá síðu.

3. **Óháð yfirferð.** Einhver sem skrifaði ekki breytinguna les breyttu síðurnar - skýringarmyndir og
   myndir með - þrisvar: sem byrjandi (hefur aldrei notað terminal), sem 8 ára barn (segir
   fyrsta málsgreinin hvað þetta er og hvers vegna, með einföldum orðum?) og sem fagmaður (eru rofar, sjálfgefin gildi og
   dálkar nákvæmlega það sem kóðinn gerir?).

4. **Lagaðu það sem yfirferðin fann.** Myndir eru í mesta lagi um 900 px á breidd með texta sem er að minnsta kosti 12 px
   eins og hann birtist; skýringarmyndir eru búnar til úr `tools/diagrams/*.json` með `tools/flow2svg.py`. Dæmi nota
   aðeins tilbúin nöfn (`de_x`, "Demo Valley", `<map>`): aldrei raunverulegt kort, spilara, viðureignarauðkenni eða tölu
   úr raunverulegum skrám.

5. **Þýðingar.** Hver þýdd síða geymir hash ensku heimildarinnar sem hún var gerð út frá.
   Þýddu aftur þær síður þar sem hash ensku heimildarinnar breyttist, láttu síðan fara yfir hvert tungumál á sama
   þrjá vegu (einfalt, byrjandi, fagmaður), líka heiti á skýringarmyndum.

6. **Ýttu (push) aðeins eftir leyfi eigandans.** Vistaðu (commit) staðbundið; eigandinn ákveður hvenær það fer opinberlega.

## Þýðingar: skipanirnar {#translations-the-commands}

Vefurinn er þýddur á 40 tungumál 3DHeat-skoðarans: enska í `docs/`, hvert annað
tungumál í `docs/<lang>/` með sömu skráarheitum. `tools/docs_i18n.py` sér um bókhaldið:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Þýddu aðeins það sem `todo` telur upp: haltu Markdown, tenglum, kóða, skráar- og dálkaheitum eins og þau eru,
þýddu titla og myndlýsingar, og notaðu eigin orð 3DHeat-skoðarans fyrir hnappa hans
og spjöld (`src/i18n/locales/<lang>/`). Sjálfvirkar tilvísunarsíður og myndir af terminal haldast
á ensku. Á vefnum segir úrelt þýðing frá því og tengir á ensku síðuna; þýðing sem vantar
fellur aftur á ensku. Tungumálavalmynd haussins og tilvísun heimasíðunnar eftir tungumáli vafrans
koma úr `docs/_includes/`.
