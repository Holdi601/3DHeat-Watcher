---
title: Správa těchto stránek
nav_order: 15
lang: "cs"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Správa těchto stránek {#maintaining-these-pages}

Kontrolní seznam pro každé vydání. Stránky musí říkat, co kód dělá, dobře se číst pro začátečníka, osmileté dítě i pro profesionála, a musí existovat ve všech jazycích, které prohlížeč 3DHeat podporuje.

## Kontrolní seznam vydání {#release-checklist}

1. **Znovu vygenerujte generované stránky** z kódu:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Před potvrzením musí stejné příkazy s `--check` skončit s kódem 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Porovnejte funkce od posledního vydání.** `VERSION` drží verzi; její značka je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Každý nový příkaz, volba, sloupec, výstup nebo chování dostane řádek na stránce, která ho popisuje, a řádek v `CHANGELOG.md` pod **Docs** s názvem té stránky.

3. **Nezávislá kontrola.** Někdo, kdo změnu nepsal, přečte změněné stránky – včetně diagramů a obrázků – třikrát: jako začátečník (nikdy nepoužil terminál), jako osmileté dítě (říká první odstavec, co to je a proč, prostými slovy?) a jako profesionál (jsou příznaky, výchozí hodnoty a sloupce přesně takové, jaké kód dělá?).

4. **Opravte, co kontrola našla.** Obrázky zůstávají nejvýš kolem 900 px široké a text v nich má alespoň 12 px; diagramy se generují z `tools/diagrams/*.json` nástrojem `tools/flow2svg.py`. Příklady používají jen vymyšlená jména (`de_x`, „Demo Valley“, `<map>`): nikdy skutečnou mapu, hráče, id zápasu ani postavu ze skutečných souborů.

5. **Překlady.** Každá přeložená stránka si zaznamená hash anglického zdroje, ze kterého vznikla. Znovu přeložte stránky, jejichž hash anglického zdroje se změnil, a pak nechte každý jazyk zkontrolovat stejnými třemi pohledy (prostý, začátečník, profesionál), včetně popisků diagramů.

6. **Odeslat jen se souhlasem vlastníka.** Potvrďte lokálně; vlastník rozhodne, kdy se to zveřejní.

## Překlady: příkazy {#translations-the-commands}

Stránky se překládají do 40 jazyků, které prohlížeč 3DHeat podporuje: angličtina je v `docs/`, každý další jazyk v `docs/<lang>/` se stejnými názvy souborů. `tools/docs_i18n.py` vede evidenci:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Překládejte jen to, co `todo` vypíše: Markdown, odkazy, kód, názvy souborů a sloupců ponechte, přeložte nadpisy a popisy obrázků a pro tlačítka a panely prohlížeče 3DHeat používejte jeho vlastní slova (`src/i18n/locales/<lang>/`). Vygenerované referenční stránky a obrazovky terminálu zůstávají anglicky. Na webu překlad, který je zastaralý, to řekne a odkáže na anglickou stránku; chybějící stránka se zobrazí anglicky. Jazyková nabídka v záhlaví a přesměrování na jazyk prohlížeče na domovské stránce pocházejí z `docs/_includes/`.
