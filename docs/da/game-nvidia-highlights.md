---
title: "NVIDIA highlights (platform)"
nav_order: 34
lang: "da"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platform) {#nvidia-highlights-platform}

Watcheren gemmer det, NVIDIA highlights har gemt om dine spil, så du senere kan se din historik på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `nvidia-highlights`, type [`platform`](sources-and-rules.md); den kører hele tiden (den venter ikke på, at et spil starter) og leder efter nye data hver 10. s.*

## Hvad der registreres {#what-is-recorded}

- hvert nyt klip, highlight eller skærmbillede: spil, fil, type, længde og tidspunktet (klokkeslæt i ms)
- highlightets id og navn, når spillet har registreret det hos NVIDIA
- hvor spilleren var på det tidspunkt, når en anden adapter registrerede det samme spil dengang
- highlight-anmodninger, GfeSDK-spil logger, også når intet klip gemmes

## Hvor data kommer fra {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;spil>\config.json; klip i optagermappen (%USERPROFILE%\Videos\NVIDIA\\&lt;Spil>\\\*.mp4) og &lt;temp>\Highlights\\&lt;spil>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Sådan slår du det til {#how-to-switch-it-on}

NVIDIA-appen: Instant Replay eller Highlights slået til, klip gemt med genvejstast eller af spillet

## Sådan virker det {#how-it-works}

Hvad starteren og grafikdriveren gemmer om spil: Steams statistik,
achievements, spilletid og tidslinjer, og NVIDIAs highlights og klip.

Ingen af disse kilder kræver, at et spil medvirker eller kører, så de tre
adaptere her er altid aktive og kigger på et par filer hvert par sekund.

#### NVIDIA highlights og klip (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Det NVIDIA App / GeForce Experience gemmer, alt under
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      galleriets indeks: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, når filen blev skrevet), profileName, drsName
                     (exe'en), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (hvor klip gemmes),
                     settings.tempDirectory (highlights venter i
                     <temp>\Highlights\<spil>, til de gemmes)
Highlights\<spil>\config.json  de highlight-typer, et spil har registreret:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: tekst}}}, profileName, drsName, shortName}
```
og selve klipfilerne, `<optagermappe>\<Spil>\<Spil> åååå.mm.dd -
tt.mm.ss.ff.DVR.mp4` (skærmbilleder: `<Spil> Screenshot åååå.mm.dd - ...png`), hvor tiden i filnavnet er den lokale tid, klippet blev gemt. GfeSDK-spil logger
også deres highlight-kald i `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Hvad dette kan og ikke kan levere: et spil, der understøtter NVIDIA Highlights
(GfeSDK), registrerer highlight-typer én gang - et id som "kill", en
betydning, tags, et visningsnavn - og siger senere kun "highlight <id>,
fra <ms> før nu til <ms> efter". Der er ingen positioner, ingen kamp eller runde,
ingen modstander, ingen egne data: SDK'en har intet felt til noget af det. Et gemt
klip tilføjer en fil, et spilnavn, en længde og et tidspunkt. Så det, der
registreres, er "denne slags øjeblik, i dette spil, på dette tidspunkt" - og et sted
kun ved at slå tidspunktet op i en anden adapters optagelse af det samme spil
(`position_at`), hvilket denne adapter gør for hvert klip, den registrerer.
<https://developer.nvidia.com/highlights>

Hver adapter gemmer det, den allerede har set, i `<data>\state\<id>.json`, så en genstart
ikke registrerer noget to gange.

Hver kørsel gemmer også det, dens rækker kommer fra, helt (3DHeats konverterregel,
docs/converters.md i viewerens repository), i `heat.raw.parquet`: statistikfilens
og dens skemas bytes og spillets localconfig-blok (steam-stats; en statistikfil, dekoderen ikke kan læse,
får en kørsel, der kun holder dens bytes), tidslinjefilens header og hver post som JSON
(steam-timeline), hvert klips indeksindgang i galleriet, spillets highlight-definitioner og
hver GfeSDK-logllinje, også dem der ikke er highlight-anmodninger (nvidia-highlights).

Det samme modul bruges også af: [Steam-statistik (platform)](game-steam-stats.md), [Steam Timeline (platform)](game-steam-timeline.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | kun lånte: stedet, en anden optagelse af samme spil har for det tidspunkt |
| Op-akse | `y` |
| Enheder | meter |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **nej**. `games --markdown` viser det som "kun enkeltspiller".
- Type `platform`: den læser kun det spillet eller platformen udleverer (det Steam eller grafikdriveren gemmer), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- hvert nyt klip og skærmbillede: spil, fil, type, medie, længde (indeks, ellers MP4-headeren), tidspunktet ud fra filnavnet, highlightets id og navn, hvor spillet har registreret dem, og spillerens sted dengang fra en anden adapters optagelse
- GfeSDK-highlight-anmodninger (hver `Posted Request HL...` undtagen konfigurationskald) med deres tidspunkt

**Gemt råt**

- `UGC`: klippets hele indgang i galleriets indeks UGCTracker.json, hvert felt NVIDIA skriver
- `clip_file`: for et klip indekset ikke lister, filens sti, størrelse, tid og mappe
- `highlights_config`: spillets `Highlights\<spil>\config.json` som skrevet (betydning, tags, navne på alle sprog), én gang pr. kørsel
- `gfesdk_log`: hver linje i GfeSDK-loggene, læst efter første kørsel; `used` sand for highlight-anmodningerne og falsk for resten (konfiguration, videoindstillinger, SDK'ens egne beskeder)

**Ikke tilgængeligt**

- selve klippene og skærmbillederne: video og billeder bliver, hvor NVIDIA gemte dem; rækkerne nævner filen
- det, der var der før adapterens første kørsel: det regnes som allerede set, så års klip ikke bliver til kørsler på én gang (`baseline`; falsk optager dem)
- UGCTracker.json's `apps` og `info` og GallerySettings.json: appens indstillinger, ikke øjeblikke fra spillet; optagermappen de nævner, bruges
- positioner, runder, modstandere: GfeSDK har intet felt til dem

**Størrelse**: cirka 1 KB pr. klip og et par KB definitioner og logllinjer pr. spilstart: langt under 1 MB i timen

## Verificeret {#verified}

testet på et rigtigt galleriindeks, indstillinger, highlight-definitioner og klip fra en lokal installation; GfeSDK-highlight-anmodningslinjer og highlight-id'er i klip er ikke testet

## Kilde {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
