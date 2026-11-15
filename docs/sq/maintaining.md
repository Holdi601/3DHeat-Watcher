---
title: "Mirëmbajtja"
nav_order: 15
lang: "sq"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Mirëmbajtja e këtyre faqeve {#maintaining-these-pages}

Lista e kontrollit për çdo release. Faqet duhet të thonë çfarë bën kodi, të lexohen mirë nga një fillestar,
një 8-vjeçar dhe një profesionist, dhe të ekzistojnë në çdo gjuhë që mbështet shikuesi 3DHeat.

## Lista e kontrollit të release-it {#release-checklist}

1. **Rigjenero faqet e gjeneruara** nga kodi:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Para se të bësh commit, e njëjta me `--check` duhet të dalë me 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Krahaso veçoritë që nga release-i i fundit.** `VERSION` mban versionin; etiketa e tij është `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Çdo komandë, opsion, kolonë, dalje ose sjellje e re merr një rresht në faqen që e mbulon, dhe një
   rresht në `CHANGELOG.md` nën **Docs** që e emërton atë faqe.

3. **Rishikim i pavarur.** Dikush që nuk e shkroi ndryshimin i lexon faqet e ndryshuara - diagramet dhe
   fotot përfshirë - tri herë: si fillestar (nuk ka përdorur kurrë terminal), si 8-vjeçar (a thotë
   paragrafi i parë çfarë është dhe pse, me fjalë të thjeshta?) dhe si profesionist (a janë flamujt, vlerat parazgjedhje dhe
   kolonat saktësisht çfarë bën kodi?).

4. **Rregullo çfarë gjeti rishikimi.** Fotot mbeten të gjera më së shumti rreth 900 px me tekst të paktën 12 px
   siç shfaqen; diagramet gjenerohen nga `tools/diagrams/*.json` me `tools/flow2svg.py`. Shembujt përdorin
   vetëm emra të sajuar (`de_x`, "Demo Valley", `<map>`): kurrë një hartë, lojtar, id ndeshjeje ose shifër
   të vërtetë nga skedarë të vërtetë.

5. **Përkthimet.** Çdo faqe e përkthyer regjistron hash-in e burimit anglisht nga i cili u bë.
   Ripërktheji faqet që hash-i i burimit anglisht ndryshoi, pastaj rishikoje çdo gjuhë në të njëjtat
   tri mënyra (e thjeshtë, fillestar, profesionist), përfshirë etiketat e diagrameve.

6. **Push vetëm pasi të japë miratimin pronari.** Bëj commit lokalisht; pronari vendos kur del publik.

## Përkthimet: komandat {#translations-the-commands}

Faqja është përkthyer në 40 gjuhët e shikuesit 3DHeat: anglishtja te `docs/`, çdo gjuhë tjetër
te `docs/<lang>/` me të njëjtat emra skedarësh. `tools/docs_i18n.py` mban llogaritë:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Përktheji vetëm ato që liston `todo`: lëri Markdown-in, lidhjet, kodin, emrat e skedarëve dhe kolonave siç janë,
përktheji titujt dhe përshkrimet e fotove, dhe përdor fjalët e vetë shikuesit 3DHeat për butonat
dhe panelet e tij (`src/i18n/locales/<lang>/`). Faqet e referencës së gjeneruar dhe fotot e terminalit mbeten
në anglisht. Në faqe, një përkthim i vjetruar e thotë këtë dhe lidh faqen angleze; një që mungon
kthehet te anglishtja. Menyja e gjuhës në header dhe ridrejtimi i kryefaqes sipas gjuhës së shfletuesit
vijnë nga `docs/_includes/`.
