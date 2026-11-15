---
title: "Counter-Strike 2 (replays)"
nav_order: 8
lang: "da"
source: game-cs2-demos.md
source_hash: "82fe00f0f2f0"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replays) {#counter-strike-2-replays}

Efter en kamp i Counter-Strike 2 laver watcheren den replay, spillet har gemt, om til filer, du kan se på et kort i 3DHeat-vieweren.

*Teknisk info: adapter `cs2-demos`, type [`replay`](sources-and-rules.md); den kører hele tiden (den venter ikke på, at et spil starter) og kigger efter nye data hvert 5. sekund.*

## Hvad der optages {#what-is-recorded}

- hver spillers position, kigge-retning, liv og penge (hver 8. tick)
- drab, dødsfald, skade, granater, plantninger og afmonteringer, der hvor de skete
- runder, stilling, økonomi; den indloggede spillers resultatlinje som statistik

## Hvor det kommer fra {#where-it-comes-from}

demoer, som CS2 gemmer: &lt;CS2>/game/csgo/replays/\*.dem (hentet fra kamphistorikken) og &lt;CS2>/game/csgo/\*.dem (optaget)

## Sådan slår du det til {#how-to-switch-it-on}

hent en kamps demo i CS2 (Watch > Your Matches), eller optag en med konsolkommandoen `record`

Indstillinger fra miljøvariabler:

- `HEAT3D_CS2`: mappen med 3DHeat CS2, når den ikke ligger ved siden af watcheren eller er installeret

## Sådan virker det {#how-it-works}

Replays og demoer: det et spil gemmer af en kamp, konverteret én gang, når kampen er slut.

En replay indeholder alt, en live-grænseflade holder tilbage i multiplayer-spil - hver spillers position, hvert drab, der hvor det skete - og den er en fil, spillet skriver til sine spillere, så læsning rører ikke ved spillet. Watcheren kigger i de mapper, spil gemmer dem i, venter, til en ny fil er holdt op med at vokse (spillet skriver ellers stadig på den), og konverterer den i en arbejdstråd, så en lang konvertering aldrig holder resten af watcheren op.

Første gang en mappe ses, bliver de replays, der allerede ligger i den, kun noteret, ikke konverteret: en spiller med års demoer ville ellers opleve, at watcheren er optaget i et døgn. `python -m heat3d_watch replays <adapter> [folder]` konverterer de eksisterende, når du beder om det.

#### Counter-Strike 2 {#counter-strike-2}

CS2 gemmer de demoer, en spiller henter fra kamphistorikken (Watch-fanen), i `<CS2>/game/csgo/replays/`, og dem, der er optaget med konsolkommandoen `record`, i `<CS2>/game/csgo/`. Hver enkelt konverteres med dette repositorys egen CS2-konverter (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: hver spillers position, kigge-retning, liv og penge hver ottende tick; drab, dødsfald, skade, granater, plantninger og afmonteringer, der hvor de skete; runder, stilling, økonomi) ind i sessionsmappen som tabellen `<map>/<match>.parquet` og resuméet `<match>.match.json`, som viewerens Heatmap- og Kamp-faner læser. Kampens resultatliste bliver sessionens statistik: for den spiller, hvis Steam-konto er logget ind på denne maskine (fra Steams `loginusers.vdf`), under de almindelige navne - drab, dødsfald, assists, ADR, KAST, headshot-procent, åbningsdrab, clutches - samt stilling og runder.

Det samme modul betjener også: [Dota 2 (replays)](game-dota-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Op-akse | `z` |
| Enheder | tommer (Source-enheder) |
| Spejlet for vieweren | `y` |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse gemmes i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det, spillet udgiver)".
- Type `replay`: den læser kun det, spillet eller platformen udleverer (replays og demoer, spillet gemmer), så den optager i online-spil lige så vel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøgler, denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

En nøgle i klammer udfyldes under kørsel (`score.{team}` er én nøgle pr. hold). Nøgler, koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne, står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Konverteren, denne adapter kører, følger 3DHeat's [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det, replayet indeholder, bliver læst eller gemt, aldrig smidt væk - læst ind i tabellen og kampdokumentet, alt andet gemt helt i sidecar-filer ved siden af dem og talt i kampdokumentets `selfCheck.completeness`. Konverterens egen dokumentation oplister, hvad den læser, gemmer rå og ikke kan læse.

## Verificeret {#verified}

konverteren er testet på rigtige turneringsdemoer; mappeovervågningen og statistikken ved tests

## Kilde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
