---
title: NVIDIA-høydepunkter
nav_order: 8
lang: "no"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA-høydepunkter {#nvidia-highlights}

Noen spill ber NVIDIA-driveren din lagre en kort video når noe skjer, for eksempel et drap. Watcheren noterer hvert av disse øyeblikkene og, når den kan, setter det på kartet der det skjedde.

Adapteren `nvidia-highlights` tar opp klippene, høydepunktene og skjermbildene NVIDIA-appen (eller GeForce Experience) lagrer, og gir hver av dem et sted på kartet når den kan. Denne siden forklarer hva NVIDIA-høydepunkter kan levere og ikke kan levere, hvilke filer watcheren leser, og hvordan et høydepunkt får en posisjon. Adapterens genererte side er [NVIDIA-høydepunkter (plattform)](game-nvidia-highlights.md).

## Hva NVIDIA-høydepunkter kan og ikke kan levere {#what-nvidia-highlights-can-and-cannot-deliver}

Et spill som støtter NVIDIA-høydepunkter snakker med NVIDIA-appen gjennom NVIDIAs GfeSDK. SDK-en bærer bare to slags meldinger:

1. **Én gang, ved start**: hvilke høydepunkttyper spillet vil bruke - en id (for eksempel `kill`), en betydning, tagger og et visningsnavn per språk. NVIDIA-appen lagrer dem per spill.
2. **I et øyeblikk av spillet**: "høydepunkt `<id>`, fra `<ms>` før nå til `<ms>` etter". Det er hele meldingen: id-en til en type spillet har registrert, og to tidsforskyvninger som forteller NVIDIA-appen hvilket stykke av dens løpende opptak den skal beholde.

SDK-en har **ingen felt for noe annet**: ingen posisjon, ingen kamp eller runde, ingen motstander, ingen våpen, ingen poengsum, ingen egne data av noe slag. Et spill kan ikke legge en posisjon i et høydepunkt, selv om det ville. Når klippet lagres, legger NVIDIA-appen til en fil, et spillnavn, en lengde og et tidspunkt.

Så alt et høydepunkt kan si er "denne typen øyeblikk, i dette spillet, på dette tidspunktet". Alt mer må komme et annet sted fra.

## Hva watcheren leser {#what-the-watcher-reads}

Alt leses fra filer NVIDIA-appen skriver for sitt eget galleri. Ingenting snakker med driveren eller appen. NVIDIA Overlay-mappen er `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Fil | Hva som hentes fra den |
|---|---|
| `UGCTracker.json` | galleriindeksen: hvert klipp og skjermbilde med sti, type (video, bilde), undertype (`InstantReplay`, ...), dato, spillets profilnavn, kjørbar fil og kortnavn, og lengde (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, opptaksmappen, og `settings.tempDirectory`, der høydepunkter venter (`<temp>\Highlights\<game>`) til de lagres |
| `Highlights\<game>\config.json` | høydepunkttypene hvert spill har registrert: id, og det engelske visningsnavnet (eller id-en der spillet ikke ga noe) |
| opptaksmappen (standard `%USERPROFILE%\Videos\NVIDIA`) og `<temp>\Highlights` | selve klipp- og skjermbildefilene (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), én mappe per spill |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | forespørslene spill som bruker GfeSDK logger - `Posted Request HL...`-linjer - slik at et høydepunkt spillet ba om blir notert selv når ingen klipp ble tatt vare på. Konfigurasjonsforespørsler (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) hoppes over. |

For hvert nytt element skriver adapteren én rad: `highlight` for en video, `screenshot` for et bilde, eller `highlight_request` for en GfeSDK-loggelinje. Feltene er:

| Felt | Hva det er |
|---|---|
| `ms` | øyeblikket: tidspunktet i filnavnet (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, lokal tid da klippet ble lagret), ellers indeksens dato, ellers filens endringstid |
| `game` | NVIDIA-profilnavnet, mappens navn eller spillet i filnavnet |
| `clip`, `media` | filens sti; `video`, `image` eller `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (fra den midlertidige høydepunktmappen) eller indeksens undertype |
| `duration_s`, `clip_start_ms` | lengden, fra indeksen eller fra videoens egen header (`moov/mvhd`, funnet uten å lese videoen); øyeblikket klippet begynner |
| `highlight_id`, `highlight_name` | høydepunkttypen, når noe navngir den (se nedenfor) |
| `exe` | spillets kjørbare fil, fra indeksen |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | den lånte posisjonen, når en ble funnet (se nedenfor) |

Øktstatistikken er `clips`, `screenshots`, `clip_seconds` og `placed` (elementer som fikk en posisjon).

**Høydepunkt-id-en** står ikke skrevet i noe dokumentert sted. Adapteren prøver to udokumenterte steder: et felt i galleriposten hvis navn inneholder "highlight", og - bare for filer i den midlertidige høydepunktmappen - en av spillets registrerte id-er (minst 4 tegn lang) som står i filnavnet. Et lagret klipp er navngitt etter spillet, som tilfeldigvis kan inneholde en id som "kill", så navnet søkes ikke. Disse to måtene er ikke sett fungere på en ekte maskin ennå: ingen klipp med en høydepunkt-id, og ingen GfeSDK-forespørselslinje, har forekommet der adapteren ble testet. Galleriindeksen, innstillingene, høydepunktdefinisjonene og klippene ble testet på ekte filer.

### Når elementer tas opp {#when-items-are-recorded}

- Et klipp skrives fortsatt en stund etter tastetrykket. Adapteren venter til en fil har samme størrelse og tid i to kontroller (hvert 10. s) og er minst 5 s gammel.
- Første gang adapteren kjører, noteres bare alt som allerede ligger i galleriet og loggene, det tas ikke opp, så år med gamle klipp ikke oversvømmer statistikken. Det den har sett, lagres i `<data>\state\nvidia-highlights.json`, så en omstart tar ikke opp noe to ganger.
- Elementer grupperes i én økt per spill. En spillets økt lukkes etter 30 minutter uten et nytt element, og slutter ved sitt siste øyeblikk i stedet for når spillet lukket seg. Øyeblikk mer enn 30 minutter fra hverandre havner i egne økter.

## Slik får et høydepunkt en posisjon {#how-a-highlight-gets-a-position}

Selve høydepunktet har ingen plass. Adapteren slår opp øyeblikket i de andre opptakene watcheren gjorde av det samme spillet på samme tid:

1. **Samme spill**: øktmappene under `<data>\sessions\` der spillnavnet samsvarer med høydepunktets. Navn sammenlignes med små bokstaver, bare bokstaver og tall. De samsvarer når de er like, eller når det korteste har minst 5 tegn og finnes i det lengste (`Counter-Strike 2` og `Counter-Strike-2`).
2. **Samme tid**: økter der start og slutt (fra `meta.json`, med ett sekunds slingringsmonn i begge ender) dekker øyeblikket. Økter som sluttet uten posisjoner, og adapterens egne økter, hoppes over.
3. **Spillerens egen rad**: i deres `events.jsonl`, den siste av spillerens egne rader med en posisjon, ved eller før øyeblikket og ikke mer enn 5 sekunder før. En rad er spillerens egen når kilden sier det: `"player": "me"`, eller `"own_car": 1` (løpsspill som tar opp hver bil etter sin fører), eller en `player` som er øktens `player` i `meta.json` (navnet kilden gir spilleren). Se [Spillerens egne rader](the-data.md#the-players-own-rows).

Når en rad finnes, får høydepunktet sin `x`, `y`, `z`, sin `session` (eller mappens navn), `position_from` (mappen den kom fra) og `position_lag_ms` (hvor lenge før øyeblikket den raden var). Høydepunktøkten tar aksene til det opptaket, så den tegnes på samme måte. Finnes ingen rad, blir høydepunktet et øyeblikk på tidslinjen uten sted.

Ting du bør vite om den lånte posisjonen:

- **Det er hvor du var da klippet ble lagret**, ikke hvor handlingen begynte. Øyeblikket er lagringstiden i filnavnet, som for en Instant Replay er slutten. `clip_start_ms` sier når klippet begynner.
- **En annen adapter må ha tatt opp det samme spillet på den tiden.** Dem som merker spillerens egne rader, og derfor kan plassere et høydepunkt: Counter-Strike 2 og Dota 2 game-state integration, Forza, Assetto Corsa-spillene, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft og minneprofiler (som `me`); F1 23/24/25, RaceRoom, Automobilista 2 og Project CARS 2 (bilens rader bærer `own_car` 1, etter spillets spillerbilindeks, dens egen plass eller den viste deltakeren); Elite Dangerous (sjåførens navn, i `meta.json` som `player`, siden journalen alltid er spillerens).
- **En reprise konverteres etter kampen**, så den kan bare plassere et klipp som slås opp etter konverteringen: klippet plasseres når det tas opp, og en reprise lagret senere ses ikke på igjen. League of Legends-repriser navngir radene dine etter Riot-ID-en i innstillingene, og med en Riot API-nøkkel gir de dem klokkeslettet som kampens tidslinje oppgir, så de finnes da. En CS2-demo kan ikke plassere et høydepunkt i det hele tatt: posisjonene er i konverterens egen tabell, ikke i `events.jsonl`, og en demo har spillets ticks men ingen klokkeslett å matche klippets øyeblikk mot.
- I Rocket League er de eneste radene med et sted ballhendelser. Et ballttreff av deg er en rad av deg, så et høydepunkt kan plasseres der du sist traff ballen.
- Spill uten noen posisjonskilde i det hele tatt (Overwatch 2, Call of Duty, Hunt: Showdown, ...) beholder høydepunktene sine som en tidslinje av øyeblikk.

## Hvorfor minnet ikke kan gi en posisjon i flerspiller {#why-memory-cannot-give-a-position-in-multiplayer}

Den andre måten å få en posisjon på ville vært å lese den ut av minnet. Ingen av minnene fungerer:

- **NVIDIAs minne har ingen posisjon i seg.** NVIDIA-appen mottar det GfeSDK bærer - en høydepunkt-id og to tidsforskyvninger - pluss videoen den tar opp. Det finnes ingen posisjon hos NVIDIA å lese. (Watcheren leser ikke NVIDIAs minne uansett; den leser filene over.)
- **Spillets minne er utenfor rekkevidde i flerspiller.** Posisjonen ligger i spillets prosess, men watcheren leser aldri minnet til et flerspillerspill: en minneadapter for et spill som er merket som spilt på nett, avvises før noe åpnes (se [Lese minne](memory-reading.md)). Flerspillerspill kjører under juks-beskyttelse (Easy Anti-Cheat, BattlEye, Vanguard, ...) som behandler at et annet program åpner spillets prosess som juks, noe som kan gi kontoen utestengelse. Et høydepunkt i et flerspillerspill får derfor bare et sted fra det spillet publiserer: dets game-state integration eller telemetri, tatt opp av en annen adapter på samme tid.
