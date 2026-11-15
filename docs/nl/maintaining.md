---
title: Onderhoud
nav_order: 15
lang: "nl"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Deze pagina's onderhouden {#maintaining-these-pages}

De checklist voor elke release. De pagina's moeten zeggen wat de code doet, goed leesbaar zijn voor een beginner, een achtjarige en een expert, en in elke taal bestaan die de 3DHeat-viewer ondersteunt.

## Releasechecklist {#release-checklist}

1. **De gegenereerde pagina's opnieuw maken** uit de code:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Vóór het committen moet hetzelfde met `--check` met exitcode 0 eindigen:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **De functies sinds de laatste release vergelijken.** `VERSION` bevat de versie; de tag is `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Elk nieuw commando, elke nieuwe optie, kolom, uitvoer of gedrag krijgt een regel op de pagina die het beschrijft, en een
   regel in `CHANGELOG.md` onder **Docs** met de naam van die pagina.

3. **Onafhankelijke beoordeling.** Iemand die de wijziging niet geschreven heeft, leest de gewijzigde pagina's - ook de diagrammen en afbeeldingen - drie keer: als beginner (heeft nooit een terminal gebruikt), als achtjarige (zegt de eerste alinea wat het is en waarom, in gewone woorden?) en als expert (kloppen vlaggen, standaardwaarden en kolommen precies met wat de code doet?).

4. **Wat de beoordeling vond, oplossen.** Afbeeldingen blijven ongeveer 900 px breed of minder, met tekst van minstens 12 px zoals getoond; diagrammen worden gegenereerd uit `tools/diagrams/*.json` met `tools/flow2svg.py`. Voorbeelden gebruiken alleen verzonnen namen (`de_x`, "Demo Valley", `<map>`): nooit een echte kaart, speler, wedstrijd-id of figuur uit echte bestanden.

5. **Vertalingen.** Elke vertaalde pagina noteert de hash van de Engelse bron waarvan ze gemaakt is. Vertaal de pagina's opnieuw waarvan de hash van de Engelse bron veranderd is, en laat elke taal op dezelfde drie manieren nakijken (gewoon, beginner, expert), inclusief de labels in de diagrammen.

6. **Pushen alleen na de goedkeuring van de eigenaar.** Commit lokaal; de eigenaar beslist wanneer het openbaar wordt.

## Vertalingen: de commando's {#translations-the-commands}

De site is vertaald naar de 40 talen van de 3DHeat-viewer: Engels in `docs/`, elke andere taal in `docs/<lang>/` met dezelfde bestandsnamen. `tools/docs_i18n.py` doet de administratie:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Vertaal alleen wat `todo` noemt: laat Markdown, links, code, bestands- en kolomnamen zoals ze zijn, vertaal titels en beschrijvingen van afbeeldingen, en gebruik de eigen woorden van de 3DHeat-viewer voor zijn knoppen en panelen (uit `src/i18n/locales/<lang>/`). Gegenereerde referentiepagina's en terminalafbeeldingen blijven Engels. Op de site zegt een verouderde vertaling dat en linkt naar de Engelse pagina; een ontbrekende valt terug op Engels. Het taalmenu van de kop en de automatische doorverwijzing van de startpagina naar de browsertaal komen uit `docs/_includes/`.
