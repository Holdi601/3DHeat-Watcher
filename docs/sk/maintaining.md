---
title: Údržba
nav_order: 15
lang: "sk"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Údržba týchto stránok {#maintaining-these-pages}

Kontrolný zoznam pre každé vydanie. Stránky musia hovoriť, čo kód robí, dobre sa čítať pre začiatočníka, osemročné dieťa aj profesionála, a existovať v každom jazyku, ktorý podporuje viewer 3DHeat.

## Kontrolný zoznam vydania {#release-checklist}

1. **Znovu vygenerujte generované stránky** z kódu:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Pred commitom musí to isté s `--check` skončiť s kódom 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Porovnajte funkcie od posledného vydania.** `VERSION` obsahuje verziu; jej značka je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Každý nový príkaz, voľba, stĺpec, výstup alebo správanie dostane riadok na stránke, ktorá ho pokrýva, a riadok v `CHANGELOG.md` pod **Docs**, ktorý uvádza túto stránku.

3. **Nezávislá kontrola.** Niekto, kto zmenu nenapísal, prečíta zmenené stránky – aj diagramy a obrázky – trikrát: ako začiatočník (nikdy nepoužil terminál), ako osemročné dieťa (hovorí prvý odsek, čo to je a prečo, prostými slovami?) a ako profesionál (sú príznaky, predvolené hodnoty a stĺpce presne také, ako ich kód robí?).

4. **Opravte, čo kontrola našla.** Obrázky zostanú najviac okolo 900 px široké s textom aspoň 12 px, ako sú zobrazené; diagramy sa generujú z `tools/diagrams/*.json` nástrojom `tools/flow2svg.py`. Príklady používajú len vymyslené názvy (`de_x`, „Demo Valley“, `<map>`): nikdy skutočnú mapu, hráča, id zápasu alebo postavu zo skutočných súborov.

5. **Preklady.** Každá preložená stránka zaznamenáva hash anglického zdroja, z ktorého vznikla. Znovu preložte stránky, ktorých hash anglického zdroja sa zmenil, a potom nech každý jazyk skontroluje tými istými tromi spôsobmi (jednoducho, pre začiatočníka, pre profesionála), vrátane popiskov diagramov.

6. **Zverejnite len so súhlasom vlastníka.** Commitnite lokálne; vlastník rozhodne, kedy sa to zverejní.

## Preklady: príkazy {#translations-the-commands}

Stránky sú preložené do 40 jazykov, ktoré podporuje viewer 3DHeat: angličtina v `docs/`, každý ďalší jazyk v `docs/<lang>/` s rovnakými názvami súborov. `tools/docs_i18n.py` vedie evidenciu:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Prekladajte len to, čo `todo` vypíše: Markdown, odkazy, kód, názvy súborov a stĺpcov ponechajte tak, ako sú; prekladajte nadpisy a popisy obrázkov a na tlačidlá a panely vieweru používajte jeho vlastné slová (jeho `src/i18n/locales/<lang>/`). Generované referenčné stránky a obrázky terminálu zostávajú v angličtine. Na webe zastaraný preklad to povie a odkáže na anglickú stránku; chýbajúca stránka sa vráti na angličtinu. Jazykové menu v hlavičke a presmerovanie domovskej stránky podľa jazyka prehliadača pochádzajú z `docs/_includes/`.
