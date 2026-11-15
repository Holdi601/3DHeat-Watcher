---
title: "Întreținerea acestor pagini"
nav_order: 15
lang: "ro"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Întreținerea acestor pagini {#maintaining-these-pages}

Lista de verificare pentru fiecare lansare. Paginile trebuie să spună ce face codul, să se citească bine pentru un începător, un copil de 8 ani și un profesionist, și să existe în fiecare limbă pe care o suportă vizualizatorul 3DHeat.

## Lista de verificare pentru lansare {#release-checklist}

1. **Regenerează paginile generate** din cod:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Înainte de commit, la fel cu `--check` trebuie să iasă cu codul 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Compară funcțiile de la ultima lansare.** `VERSION` ține versiunea; eticheta ei este `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Fiecare comandă, opțiune, coloană, ieșire sau comportament nou primește o linie în pagina care îl acoperă, și o linie în `CHANGELOG.md` sub **Docs** care numește pagina.

3. **Revizuire independentă.** Cineva care nu a scris schimbarea citește de trei ori paginile modificate - inclusiv diagramele și imaginile: ca începător (n-a folosit niciodată un terminal), ca un copil de 8 ani (primul paragraf spune ce este și de ce, în cuvinte simple?) și ca profesionist (steagurile, valorile implicite și coloanele sunt exact ce face codul?).

4. **Repară ce a găsit revizuirea.** Imaginile rămân cel mult circa 900 px lățime, cu text de cel puțin 12 px, așa cum apar; diagramele se generează din `tools/diagrams/*.json` cu `tools/flow2svg.py`. Exemplele folosesc doar nume inventate (`de_x`, "Demo Valley", `<map>`): niciodată o hartă reală, un jucător, un id de meci sau o cifră din fișiere reale.

5. **Traduceri.** Fiecare pagină tradusă notează hash-ul sursei engleze din care a fost făcută. Retraduce paginile al căror hash al sursei engleze s-a schimbat, apoi fiecare limbă este revizuită în aceleași trei moduri (simplu, începător, profesionist), inclusiv etichetele diagramelor.

6. **Publică doar cu acordul proprietarului.** Fă commit local; proprietarul decide când devine public.

## Traduceri: comenzile {#translations-the-commands}

Site-ul este tradus în cele 40 de limbi ale vizualizatorului 3DHeat: engleza în `docs/`, fiecare altă limbă în `docs/<lang>/`, cu aceleași nume de fișiere. `tools/docs_i18n.py` face evidența:

```bash
python tools/docs_i18n.py hashes             # după orice schimbare în engleză: notează hash-ul fiecărei pagini
python tools/docs_i18n.py svg-strings        # după orice schimbare a imaginilor: etichetele de tradus
python tools/docs_i18n.py status             # pe limbă: pagini actuale, învechite, lipsă
python tools/docs_i18n.py todo --lang de     # paginile în germană de tradus (sau retradus)
python tools/docs_i18n.py svg-build --lang de    # imaginile în germană din docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # marchează paginile în germană cu hash-ul lor englez
python tools/docs_i18n.py check              # iese cu 1 când hash-urile sau etichetele sunt vechi
```

Traduce doar ce listează `todo`: păstrează Markdown-ul, linkurile, codul, numele fișierelor și coloanelor așa cum sunt, tradu titlurile și descrierile imaginilor, și folosește cuvintele proprii ale vizualizatorului 3DHeat pentru butoane și panouri (din `src/i18n/locales/<lang>/`). Paginile de referință generate și imaginile cu terminalul rămân în engleză. Pe site, o traducere învechită o spune și face link la pagina engleză; una lipsă cade înapoi pe engleză. Meniul de limbă din antet și redirecționarea de pe pagina principală, după limba browserului, vin din `docs/_includes/`.
