---
title: "NVIDIA-høydepunkter (plattform)"
nav_order: 34
lang: "no"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA-høydepunkter (plattform) {#nvidia-highlights-platform}

Watcher lagrer det NVIDIA-høydepunkter har tatt vare på om spillene dine, så du kan se på historikken din senere på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `nvidia-highlights`, type [`platform`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill skal starte) og ser etter nye data hvert 10. sekund.*

## Hva som tas opp {#what-is-recorded}

- hvert nye klipp, høydepunkt eller skjermbilde: spill, fil, type, lengde og tidspunktet (klokkeslett i ms)
- høydepunktets id og navn når spillet registrerte det hos NVIDIA
- hvor spilleren var på det tidspunktet, når en annen adapter tok opp det samme spillet da
- høydepunktforespørsler som GfeSDK-spill logger, selv når ingen klipp lagres

## Hvor dataene kommer fra {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;spill>\config.json; klipp i opptaksmappen (%USERPROFILE%\Videos\NVIDIA\\&lt;Spill>\\\*.mp4) og &lt;temp>\Highlights\\&lt;spill>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Slik slår du det på {#how-to-switch-it-on}

NVIDIA-appen: Instant Replay eller Highlights slått på, klipp lagret med hurtigtast eller av spillet

## Slik fungerer det {#how-it-works}

Det launcheren og grafikkdriveren tar vare på om spilling: Steams statistikk,
achievements, spilletid og tidslinjer, samt NVIDIAs høydepunkter og klipp.

Ingen av disse kildene krever at et spill samarbeider eller kjører, så de tre
adapterne her er alltid på og ser på noen få filer hvert par sekund.

#### NVIDIA-høydepunkter og klipp (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Det NVIDIA App / GeForce Experience tar vare på, alt under
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      galleriindeksen: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, når filen ble skrevet), profileName, drsName
                     (exe-filen), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (hvor klipp lagres),
                     settings.tempDirectory (høydepunkter venter i
                     <temp>\Highlights\<spill> til de lagres)
Highlights\<spill>\config.json  høydepunkttypene et spill har registrert:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: tekst}}}, profileName, drsName, shortName}
```
og selve klippfilene, `<opptaksmappe>\<Spill>\<Spill> åååå.mm.dd -
tt.mm.ss.hh.DVR.mp4` (skjermbilder: `<Spill> Screenshot åååå.mm.dd - ...png`). Tidspunktet i filnavnet er lokal tid da klippet ble lagret. Spill som bruker GfeSDK logger også høydepunktkallene sine i `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Hva dette kan og ikke kan levere: et spill som støtter NVIDIA Highlights
(GfeSDK) registrerer høydepunkttyper én gang - en id som "kill", en
betydning, tagger, et visningsnavn - og sier senere bare "highlight <id>,
fra <ms> før nå til <ms> etter". Det finnes ingen posisjoner, ingen kamp eller
runde, ingen motstander, ingen egne data: SDK-en har ikke felt for noe av dette.
Et lagret klipp gir en fil, et spillnavn, en lengde og et tidspunkt. Det som
tas opp er altså "denne typen øyeblikk, i dette spillet, på dette tidspunktet" -
og et sted bare ved å slå opp tidspunktet i en annen adapters opptak av det
samme spillet (`position_at`), noe denne adapteren gjør for hvert klipp den tar opp.
<https://developer.nvidia.com/highlights>

Hver adapter lagrer det den allerede har sett i `<data>\state\<id>.json`, så en
omstart tar ikke opp noe to ganger.

Hver økt lagrer også hele kildene til radene sine (3DHeat-konverterens regel,
docs/converters.md i viewerens repo), i `heat.raw.parquet`: statistikkfilen og
skjemaets bytes og spillets localconfig-blokk (steam-stats; en statistikkfil
dekoderen ikke kan lese får en økt som bare inneholder bytene), tidslinjefilens
header og hver oppføring som JSON (steam-timeline), hver klippoppføring i
galleriindeksen, spillets høydepunktdefinisjoner og hver GfeSDK-loggline, også
de som ikke er høydepunktforespørsler (nvidia-highlights).

Den samme modulen leverer også: [Steam-statistikk (plattform)](game-steam-stats.md), [Steam Timeline (plattform)](game-steam-timeline.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner som tas opp | bare lånt: stedet en annen opptak av det samme spillet har for det tidspunktet |
| Opp-akse | `y` |
| Enheter | meter |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med denne) | 1 |

Dette går inn i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **nei**. `games --markdown` viser dette som "single-player".
- Type `platform`: den leser bare det spillet eller plattformen gir ut (det Steam eller grafikkdriveren tar vare på), så den tar opp også i nettspill, både offline og online; flagget avgjør bare om minnet noen gang får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som tas opp {#statistics-recorded}

Statistikknøkler som denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

En nøkkel i klammer fylles ut under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcher følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder blir lest eller tatt vare på, aldri droppet. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar lagret hel i økten sin `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, pluss eventuelle felt som er tatt vare på med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Lest**

- hvert nytt klipp og skjermbilde: spill, fil, type, medium, lengde (indeks, ellers MP4-headeren), tidspunktet fra filnavnet, høydepunktets id og navn der spillet registrerte dem, og spillerens sted da fra en annen adapters opptak
- GfeSDK-høydepunktforespørsler (hver `Posted Request HL...` unntatt konfigurasjonskall) med tidspunkt

**Lagret rått**

- `UGC`: klippets hele oppføring i galleriindeksen UGCTracker.json, hvert felt NVIDIA skriver
- `clip_file`: for et klipp indeksen ikke lister, filens sti, størrelse, tid og mappe
- `highlights_config`: spillets `Highlights\<spill>\config.json` slik den er skrevet (betydning, tagger, navn på alle språk), én gang per økt
- `gfesdk_log`: hver linje i GfeSDK-loggene som ble lest etter første kjøring, `used` sann for høydepunktforespørslene og usann for resten (konfigurasjon, videoinnstillinger, SDK-ens egne meldinger)

**Ikke tilgjengelig**

- selve klippene og skjermbildene: video og bilder blir liggende der NVIDIA lagret dem; radene nevner filen
- det som fantes før adapterens første kjøring: regnes som allerede sett, så år med klipp blir ikke til økter på en gang (`baseline`; False tar dem opp)
- UGCTracker.json sine `apps` og `info` og GallerySettings.json: appens innstillinger, ikke øyeblikk i spillingen; opptaksmappen de nevner brukes
- posisjoner, runder, motstandere: GfeSDK har ingen felt for dem

**Størrelse**: rundt 1 KB per klipp og noen få KB med definisjoner og loggelinjer per spillstart: godt under 1 MB per time

## Verifisert {#verified}

testet på en ekte galleriindeks, innstillinger, høydepunktdefinisjoner og klipp fra en lokal installasjon; GfeSDK-linjer for høydepunktforespørsler og høydepunkt-id-er i klipp er ikke testet

## Kilde {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generert fra adapteren av tools/gen_game_pages.py; endre adapteren og kjør den på nytt i stedet for å redigere denne siden. -->
