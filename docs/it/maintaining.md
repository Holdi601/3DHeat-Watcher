---
title: Manutenzione
nav_order: 15
lang: "it"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Manutenzione di queste pagine {#maintaining-these-pages}

La lista di controllo per ogni rilascio. Le pagine devono dire ciò che fa il codice, essere comprensibili per un principiante, un bambino di 8 anni e un esperto, ed esistere in ogni lingua supportata dal visualizzatore di 3DHeat.

## Lista di controllo del rilascio {#release-checklist}

1. **Rigenera le pagine generate** dal codice:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Prima del commit, lo stesso con `--check` deve uscire con 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Confronta le funzionalità dall'ultimo rilascio.** `VERSION` contiene la versione; il suo tag è `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Ogni nuovo comando, opzione, colonna, output o comportamento riceve una riga nella pagina che lo copre, e una riga in `CHANGELOG.md` sotto **Docs** che nomina la pagina.

3. **Revisione indipendente.** Qualcuno che non ha scritto la modifica legge le pagine cambiate - diagrammi e immagini compresi - tre volte: come principiante (non ha mai usato un terminale), come bambino di 8 anni (il primo paragrafo dice cos'è e perché, con parole semplici?) e come esperto (flag, valori predefiniti e colonne sono esattamente ciò che fa il codice?).

4. **Correggi ciò che la revisione ha trovato.** Le immagini restano larghe al massimo circa 900 px con un testo di almeno 12 px come mostrato; i diagrammi sono generati da `tools/diagrams/*.json` con `tools/flow2svg.py`. Gli esempi usano solo nomi inventati (`de_x`, "Demo Valley", `<map>`): mai una mappa reale, un giocatore, un id di partita o una figura tratta da file reali.

5. **Traduzioni.** Ogni pagina tradotta registra l'hash della fonte inglese da cui è stata fatta. Ritraduci le pagine il cui hash della fonte inglese è cambiato, poi fai rivedere ogni lingua nei tre modi (semplice, principiante, esperto), incluse le etichette dei diagrammi.

6. **Pubblica solo dopo il via libera del proprietario.** Fai il commit in locale; il proprietario decide quando rendere tutto pubblico.

## Traduzioni: i comandi {#translations-the-commands}

Il sito è tradotto nelle 40 lingue del visualizzatore di 3DHeat: l'inglese in `docs/`, ogni altra lingua in `docs/<lang>/` con gli stessi nomi di file. `tools/docs_i18n.py` tiene la contabilità:

```bash
python tools/docs_i18n.py hashes             # dopo ogni modifica all'inglese: registra l'hash di ogni pagina
python tools/docs_i18n.py svg-strings        # dopo ogni modifica alle immagini: le etichette da tradurre
python tools/docs_i18n.py status             # per lingua: aggiornate, obsolete, pagine mancanti
python tools/docs_i18n.py todo --lang de     # le pagine tedesche da (ri)tradurre
python tools/docs_i18n.py svg-build --lang de    # immagini tedesche da docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # marca le pagine tedesche con l'hash inglese
python tools/docs_i18n.py check              # esce con 1 quando hash o etichette sono obsoleti
```

Traduci solo ciò che `todo` elenca: lascia invariati Markdown, link, codice, nomi di file e di colonne, traduci i titoli e le descrizioni delle immagini, e usa le parole del visualizzatore di 3DHeat per i suoi pulsanti e pannelli (`src/i18n/locales/<lang>/`). Le pagine di riferimento generate e le immagini del terminale restano in inglese. Sul sito, una traduzione obsoleta lo dice e rimanda alla pagina inglese; una pagina mancante ricade sull'inglese. Il menu delle lingue nell'intestazione e il reindirizzamento in base alla lingua del browser nella home page vengono da `docs/_includes/`.
