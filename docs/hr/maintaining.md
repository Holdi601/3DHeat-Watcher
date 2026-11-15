---
title: "Održavanje ovih stranica"
nav_order: 15
lang: "hr"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Održavanje ovih stranica {#maintaining-these-pages}

Popis za svako izdanje. Stranice moraju reći što kod radi, biti lako čitljive za početnika, osmogodišnjaka i profesionalca, i postojati na svakom jeziku koji 3DHeat preglednik podržava.

## Popis za izdanje {#release-checklist}

1. **Ponovno generirajte stranice** iz koda:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Prije commita, isto s `--check` mora završiti s 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Usporedite značajke od zadnjeg izdanja.** `VERSION` sadrži verziju; njezina oznaka je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Svaka nova naredba, opcija, stupac, izlaz ili ponašanje dobiva redak na stranici koja ga pokriva, i redak u `CHANGELOG.md` pod **Docs** koji navodi tu stranicu.

3. **Neovisni pregled.** Netko tko nije napisao promjenu čita izmijenjene stranice - uključujući dijagrame i slike - tri puta: kao početnik (nikad nije koristio terminal), kao osmogodišnjak (kaže li prvi odlomak jasno što je i zašto, običnim riječima?) i kao profesionalac (jesu li zastavice, zadane vrijednosti i stupci točno ono što kod radi?).

4. **Ispravite što je pregled pronašao.** Slike ostaju široke najviše oko 900 px, s tekstom od najmanje 12 px kako se prikazuje; dijagrami se generiraju iz `tools/diagrams/*.json` pomoću `tools/flow2svg.py`. Primjeri koriste samo izmišljena imena (`de_x`, "Demo Valley", `<map>`): nikad pravu kartu, pravog igrača, pravi ID utakmice ili lik iz pravih datoteka.

5. **Prijevodi.** Svaka prevedena stranica bilježi hash engleskog izvora iz kojeg je nastala. Ponovno prevedite stranice čiji se hash engleskog izvora promijenio, pa neka svaki jezik pregledaju na isti tri načina (jednostavno, za početnike, za profesionalce), uključujući oznake na dijagramima.

6. **Objavljujte tek nakon vlasnikova odobrenja.** Commitajte lokalno; vlasnik odlučuje kad ide javno.

## Prijevodi: naredbe {#translations-the-commands}

Stranica se prevodi na 40 jezika 3DHeat preglednika: engleski je u `docs/`, svaki ostali jezik u `docs/<lang>/` s istim imenima datoteka. `tools/docs_i18n.py` vodi evidenciju:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Prevodite samo ono što `todo` navodi: zadržite Markdown, poveznice, kod, imena datoteka i stupaca, a prevedite naslove i opise slika, i koristite vlastite riječi preglednika 3DHeat za njegove gumbe i panele (njegov `src/i18n/locales/<lang>/`). Generirane referentne stranice i terminalne slike ostaju na engleskom. Na stranici, zastarjeli prijevod to kaže i upućuje na englesku stranicu; nedostajuća stranica se prikazuje na engleskom. Izbornik jezika u zaglavlju i preusmjeravanje početne stranice prema jeziku preglednika dolaze iz `docs/_includes/`.
