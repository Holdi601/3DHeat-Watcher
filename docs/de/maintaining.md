---
title: Pflege
nav_order: 15
lang: de
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Die Seiten pflegen {#maintaining-these-pages}

Die Checkliste für jede Veröffentlichung. Die Seiten müssen sagen, was der Code tut, für einen Anfänger, einen Achtjährigen und einen Profi gut lesbar sein und in jeder Sprache existieren, die der 3DHeat-Viewer unterstützt.

## Checkliste für jede Veröffentlichung {#release-checklist}

1. **Die erzeugten Seiten aus dem Code neu erzeugen:**

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Vor dem Commit muss dasselbe mit `--check` mit 0 enden:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Die Funktionen seit der letzten Veröffentlichung vergleichen.** `VERSION` enthält die Version; ihr Tag ist `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Jeder neue Befehl, jede Option, jede Spalte, jede Ausgabe oder jedes Verhalten bekommt eine Zeile auf der Seite, die es beschreibt, und eine Zeile in `CHANGELOG.md` unter **Docs** mit dem Namen der Seite.

3. **Unabhängige Prüfung.** Jemand, der die Änderung nicht geschrieben hat, liest die geänderten Seiten - Diagramme und Bilder eingeschlossen - dreimal: als Anfänger (hat nie ein Terminal benutzt), als Achtjähriger (sagt der erste Absatz in einfachen Worten, was es ist und warum?) und als Profi (stimmen Flags, Standardwerte und Spalten genau mit dem Code überein?).

4. **Behebe, was die Prüfung gefunden hat.** Bilder bleiben höchstens etwa 900 px breit, mit Text von mindestens 12 px, wie gezeigt; Diagramme werden aus `tools/diagrams/*.json` mit `tools/flow2svg.py` erzeugt. Beispiele verwenden nur erfundene Namen (`de_x`, "Demo Valley", `<map>`): nie eine echte Karte, einen echten Spieler, eine echte Match-ID oder eine Figur aus echten Dateien.

5. **Übersetzungen.** Jede übersetzte Seite hält den Hash der englischen Quelle fest, aus der sie entstand. Übersetze die Seiten neu, deren englischer Quell-Hash sich geändert hat, und lass dann jede Sprache auf dieselben drei Arten prüfen (einfach, Anfänger, Profi), einschließlich der Beschriftungen in den Diagrammen.

6. **Erst nach dem Go des Eigentümers veröffentlichen.** Lokal committen; der Eigentümer entscheidet, wann es öffentlich wird.

## Übersetzungen: die Befehle {#translations-the-commands}

Die Seite ist in die 40 Sprachen des 3DHeat-Viewers übersetzt: Englisch in `docs/`, jede andere Sprache in `docs/<lang>/` mit denselben Dateinamen. `tools/docs_i18n.py` erledigt die Buchführung:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Übersetze nur, was `todo` auflistet: Markdown, Links, Code, Datei- und Spaltennamen bleiben, wie sie sind; Titel und Bildbeschreibungen werden übersetzt, und für die Knöpfe und Bereiche des 3DHeat-Viewers gelten seine eigenen Wörter (aus `src/i18n/locales/<lang>/`). Erzeugte Referenzseiten und Terminalbilder bleiben Englisch. Auf der Website sagt eine veraltete Übersetzung das und verlinkt die englische Seite; eine fehlende fällt auf Englisch zurück. Das Sprachmenü im Kopf und die Weiterleitung der Startseite nach der Browsersprache kommen aus `docs/_includes/`.
