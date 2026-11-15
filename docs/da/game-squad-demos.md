---
title: "Squad (replays)"
nav_order: 40
lang: "da"
source: game-squad-demos.md
source_hash: "a908f7e6d9c3"
nav_exclude: true
search_exclude: true
---
# Squad (replays) {#squad-replays}

Efter en kamp i Squad laver watcheren den replay, spillet har gemt, om til filer, du kan se på et kort i 3DHeat-vieweren.

*Teknisk info: adapter `squad-demos`, type [`replay`](sources-and-rules.md); den kører hele tiden (den venter ikke på, at et spil starter) og kigger efter nye data hvert 5. sekund.*

## Hvad der optages {#what-is-recorded}

- hver spillers position, kropsdrejning og fart, hver gang serveren replikerer den (op til 8 gange i sekundet), til fods og i jordkøretøjer
- hver spillers navn, hold, fraktion og trup, og følger holdskift
- ikke: helikopteres bevægelse, drab og udsættelige genstande - se læserens README

## Hvor det kommer fra {#where-it-comes-from}

serverdemoer, Squad optager med admin-kommandoen AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, læst af den eksterne læser `heat3d-squad-demo` (exporters/ext/squad-demo)

## Sådan slår du det til {#how-to-switch-it-on}

optag på serveren: giv admin'en `demos`-tilladelsen i Admins.cfg, og brug derefter AdminDemoRec &lt;name> og AdminDemoStop i spillets konsol; kopiér demoen hertil og installér læseren: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Indstillinger fra miljøvariabler:

- `HEAT3D_SQUAD_DEMO`: konverterens mappe (en klon eller udpakket udgivelse), når den ikke er installeret eller ligger ved siden af watcheren

## Sådan virker det {#how-it-works}

Replays og demoer: det et spil gemmer af en kamp, konverteret én gang, når kampen er slut.

En replay indeholder alt, en live-grænseflade holder tilbage i multiplayer-spil - hver spillers position, hvert drab, der hvor det skete - og den er en fil, spillet skriver til sine spillere, så læsning rører ikke ved spillet. Watcheren kigger i de mapper, spil gemmer dem i, venter, til en ny fil er holdt op med at vokse (spillet skriver ellers stadig på den), og konverterer den i en arbejdstråd, så en lang konvertering aldrig holder resten af watcheren op.

Første gang en mappe ses, bliver de replays, der allerede ligger i den, kun noteret, ikke konverteret: en spiller med års demoer ville ellers opleve, at watcheren er optaget i et døgn. `python -m heat3d_watch replays <adapter> [folder]` konverterer de eksisterende, når du beder om det.

#### Squad {#squad}

Squads dedikerede servere optager en demo af en kamp, når en admin med `demos`-tilladelsen kører AdminDemoRec &lt;name> (og AdminDemoStop), i `<server>/SquadGame/Saved/Demos/<name>.replay` - en Unreal Engine-netværksreplay, der indeholder det, serveren replikerede, inklusive hver spillers bevægelse. Watcheren læser dem ikke selv: det gør en ekstern læser (3DHeat Squad demo-læser, `exporters/ext/squad-demo`, kommandoen `heat3d-squad-demo`), holdt adskilt, så et problem med den ikke rører ved noget andet. Den køres på hver ny demo i de mapper, en lokal server skriver til, eller i en mappe, indstillingerne tilføjer til demoer kopieret fra en lejet server, og lægges i sessionsmappen som `<map>/<match>.parquet` og `<match>.match.json`. Laget, kortet, antallet af spillere og kampens længde bliver sessionens statistik.

Det samme modul betjener også: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Op-akse | `z` |
| Enheder | Unreal-enheder (centimeter) |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse gemmes i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det, spillet udgiver)".
- Type `replay`: den læser kun det, spillet eller platformen udleverer (replays og demoer, spillet gemmer), så den optager i online-spil lige så vel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøgler, denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

En nøgle i klammer udfyldes under kørsel (`score.{team}` er én nøgle pr. hold). Nøgler, koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne, står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Konverteren, denne adapter kører, følger 3DHeat's [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det, replayet indeholder, bliver læst eller gemt, aldrig smidt væk - læst ind i tabellen og kampdokumentet, alt andet gemt helt i sidecar-filer ved siden af dem og talt i kampdokumentets `selfCheck.completeness`. Konverterens egen dokumentation oplister, hvad den læser, gemmer rå og ikke kan læse.

## Verificeret {#verified}

læseren er kontrolleret på offentlige serverdemoer (bevægelsen stemmer med den hastighed, den bærer; hver rækkes hold stemmer med dens soldats fraktion) og ved tests på byggede demoer; denne hook ved tests med en erstatningskommando

## Kilde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
