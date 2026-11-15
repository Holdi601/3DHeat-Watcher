---
title: "World of Tanks (replays)"
nav_order: 47
lang: "da"
source: game-wot-replays.md
source_hash: "c3fbbeebfee0"
nav_exclude: true
search_exclude: true
---
# World of Tanks (replays) {#world-of-tanks-replays}

Efter en kamp i World of Tanks laver watcheren den replay, spillet har gemt, om til filer, du kan se på et kort i 3DHeat-vieweren.

*Teknisk info: adapter `wot-replays`, type [`replay`](sources-and-rules.md); den kører hele tiden (den venter ikke på, at et spil starter) og kigger efter nye data hvert 5. sekund.*

## Hvad der optages {#what-is-recorded}

- hvert køretøjs position og retning ca. 10 gange i sekundet, mens optagerklienten kendte det: sit eget hold hele tiden, en fjende mens den er spottet
- spiller, hold og køretøj (nation:tank) for hver; dødsfald, hvor offeret faldt, og drab, hvor dræberen stod, med ca. et sekunds præcision, fra resultaterne
- kortet; optagerens drab, skade, overlevelse og resultat som statistik

## Hvor det kommer fra {#where-it-comes-from}

replays, World of Tanks gemmer: &lt;World of Tanks>/replays/\*.wotreplay (med slagoptagelse slået til), konverteret af den eksterne konverter `heat3d-wot-replay` (exporters/ext/wot-replay)

## Sådan slår du det til {#how-to-switch-it-on}

slå slagoptagelse til i World of Tanks' indstillinger (General > Record battles), og installér konverteren: pip install -e &lt;3DHeat>/exporters/ext/wot-replay

Indstillinger fra miljøvariabler:

- `HEAT3D_WOT_REPLAY`: konverterens mappe (en klon eller udpakket udgivelse), når den ikke er installeret eller ligger ved siden af watcheren

## Sådan virker det {#how-it-works}

Replays og demoer: det et spil gemmer af en kamp, konverteret én gang, når kampen er slut.

En replay indeholder alt, en live-grænseflade holder tilbage i multiplayer-spil - hver spillers position, hvert drab, der hvor det skete - og den er en fil, spillet skriver til sine spillere, så læsning rører ikke ved spillet. Watcheren kigger i de mapper, spil gemmer dem i, venter, til en ny fil er holdt op med at vokse (spillet skriver ellers stadig på den), og konverterer den i en arbejdstråd, så en lang konvertering aldrig holder resten af watcheren op.

Første gang en mappe ses, bliver de replays, der allerede ligger i den, kun noteret, ikke konverteret: en spiller med års demoer ville ellers opleve, at watcheren er optaget i et døgn. `python -m heat3d_watch replays <adapter> [folder]` konverterer de eksisterende, når du beder om det.

#### World of Tanks og World of Warships {#world-of-tanks-and-world-of-warships}

Begge gemmer en replay af hvert slag i `<game>/replays/`, når optagelse er slået til (`*.wotreplay`, `*.wowsreplay`); installationerne findes gennem Wargaming Game Centers liste, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, og Steam. Ligesom med War Thunder læser watcheren ikke filerne selv: en ekstern konverter af hver gør det (`exporters/ext/wot-replay`, kommandoen `heat3d-wot-replay`; `exporters/ext/wows-replay`, kommandoen `heat3d-wows-replay`), holdt adskilt, så et problem med Wargamings vilkår kun rammer den konverter. Fundet på PATH, installeret eller ved siden af watcheren laver den hver ny replay om til `<map>/<match>.parquet` og `<match>.match.json` i sessionsmappen; mangler den, siger watcheren én gang, hvordan den installeres. Optagerens linje - køretøj eller skib, drab, skade (World of Tanks), om de overlevede, og resultatet (World of Tanks) - bliver sessionens statistik. Hvad hver konverter læser, og hvad den ikke gør, står i dens README.

Det samme modul betjener også: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Op-akse | `y` |
| Enheder | meter (x øst, y op, z nord) |
| Spejlet for vieweren | `z` |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse gemmes i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det, spillet udgiver)".
- Type `replay`: den læser kun det, spillet eller platformen udleverer (replays og demoer, spillet gemmer), så den optager i online-spil lige så vel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøgler, denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

En nøgle i klammer udfyldes under kørsel (`score.{team}` er én nøgle pr. hold). Nøgler, koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne, står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Konverteren, denne adapter kører, følger 3DHeat's [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det, replayet indeholder, bliver læst eller gemt, aldrig smidt væk - læst ind i tabellen og kampdokumentet, alt andet gemt helt i sidecar-filer ved siden af dem og talt i kampdokumentets `selfCheck.completeness`. Konverterens egen dokumentation oplister, hvad den læser, gemmer rå og ikke kan læse.

## Verificeret {#verified}

konverteren er kontrolleret på offentlige replays fra flere spilversioner og ved tests på byggede replays; denne hook ved tests med en erstatningskommando

## Kilde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
