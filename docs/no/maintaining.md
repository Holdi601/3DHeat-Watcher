---
title: Vedlikehold
nav_order: 15
lang: "no"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Vedlikehold av disse sidene {#maintaining-these-pages}

Sjekklisten for hver utgivelse. Sidene må si hva koden gjør, lese godt for en nybegynner, en 8-åring og en profesjonell, og finnes på alle språk 3DHeat-vieweren støtter.

## Sjekkliste for utgivelse {#release-checklist}

1. **Generer de genererte sidene på nytt** fra koden:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Før du committer, må det samme med `--check` avslutte med 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Sammenlign funksjonene siden forrige utgivelse.** `VERSION` holder versjonen; taggen er `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Hver ny kommando, valg, kolonne, utdata eller oppførsel får en linje på siden som dekker den, og en linje i `CHANGELOG.md` under **Docs** som nevner siden.

3. **Uavhengig gjennomgang.** Noen som ikke skrev endringen, leser de endrede sidene - diagrammer og bilder inkludert - tre ganger: som en nybegynner (har aldri brukt en terminal), som en 8-åring (sier det første avsnittet hva det er og hvorfor, med enkle ord?) og som en profesjonell (er flagg, standarder og kolonner nøyaktig det koden gjør?).

4. **Rett det gjennomgangen fant.** Bilder holder seg på omtrent 900 px i bredden, med tekst på minst 12 px som vist; diagrammer genereres fra `tools/diagrams/*.json` med `tools/flow2svg.py`. Eksempler bruker bare påståtte navn (`de_x`, "Demo Valley", `<map>`): aldri et ekte kart, en ekte spiller, en ekte kamp-id eller en figur fra ekte filer.

5. **Oversettelser.** Hver oversatt side registrerer hashen til den engelske kilden den ble laget fra. Oversett på nytt de sidene der den engelske kildehashen endret seg, og la hvert språk gjennomgås på de samme tre måtene (enkelt, nybegynner, profesjonell), inkludert diagramtekstene.

6. **Send bare etter eierens OK.** Commit lokalt; eieren bestemmer når det går offentlig.

## Oversettelser: kommandoene {#translations-the-commands}

Siden er oversatt til de 40 språkene 3DHeat-vieweren støtter: engelsk i `docs/`, hvert annet språk i `docs/<lang>/` med de samme filnavnene. `tools/docs_i18n.py` gjør bokføringen:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Oversett bare det `todo` lister: behold Markdown, lenker, kode, fil- og kolonnenavn som de er, oversett titler og bildebeskrivelser, og bruk 3DHeat-vieweren sine egne ord for knapper og paneler (dens `src/i18n/locales/<lang>/`). Genererte referansesider og terminalbilder forblir engelske. På nettstedet sier en utdatert oversettelse fra og lenker til den engelske siden; en manglende faller tilbake til engelsk. Språkmenyen i headeren og nettleserspråk-omdirigeringen på forsiden kommer fra `docs/_includes/`.
