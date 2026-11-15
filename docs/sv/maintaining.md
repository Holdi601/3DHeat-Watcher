---
title: Underhålla
nav_order: 15
lang: "sv"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Underhålla sidorna {#maintaining-these-pages}

Checklistan för varje release. Sidorna måste säga vad koden gör, läsas väl av en nybörjare, en åttaåring och en proffs, och finnas på varje språk som 3DHeat-visaren stöder.

## Releasechecklista {#release-checklist}

1. **Generera om de genererade sidorna** från koden:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Innan du committar ska samma med `--check` ge exit 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Jämför funktionerna sedan senaste release.** `VERSION` har versionen; dess tagg är `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Varje nytt kommando, alternativ, kolumn, utdata eller beteende får en rad på sidan som täcker det, och en rad i `CHANGELOG.md` under **Docs** som nämner sidan.

3. **Oberoende granskning.** Någon som inte skrev ändringen läser de ändrade sidorna - diagram och bilder inräknade - tre gånger: som nybörjare (har aldrig använt en terminal), som åttaåring (säger första stycket vad det är och varför, med enkla ord?) och som proffs (är flaggor, standardvärden och kolumner exakt det koden gör?).

4. **Åtgärda det granskningen hittade.** Bilder håller sig högst cirka 900 px breda med text på minst 12 px som visat; diagram genereras från `tools/diagrams/*.json` med `tools/flow2svg.py`. Exempel använder bara påhittade namn (`de_x`, "Demo Valley", `<map>`): aldrig en riktig karta, spelare, match-id eller figur från riktiga filer.

5. **Översättningar.** Varje översatt sida anger hashen av den engelska källan den gjordes från. Översätt om de sidor vars engelska källhash ändrats, och låt sedan varje språk granskas på samma tre sätt (enkelt, nybörjare, proffs), inklusive diagrammens etiketter.

6. **Pusha bara efter ägarens klartecken.** Committa lokalt; ägaren bestämmer när det blir offentligt.

## Översättningar: kommandona {#translations-the-commands}

Sajten är översatt till 3DHeat-visarens 40 språk: engelska i `docs/`, varje annat språk i `docs/<lang>/` med samma filnamn. `tools/docs_i18n.py` sköter bokföringen:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Översätt bara det `todo` listar: behåll Markdown, länkar, kod, fil- och kolumnnamn som de är, översätt titlar och bildbeskrivningar, och använd 3DHeat-visarens egna ord för dess knappar och paneler (dess `src/i18n/locales/<lang>/`). Genererade referenssidor och terminalbilder förblir engelska. På sajten säger en föråldrad översättning det och länkar till den engelska sidan; en saknad faller tillbaka på engelska. Språkmenyn i sidhuvudet och startsidans omdirigering efter webbläsarspråk kommer från `docs/_includes/`.
