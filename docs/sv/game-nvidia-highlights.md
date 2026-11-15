---
title: "NVIDIA-höjdpunkter (plattform)"
nav_order: 34
lang: "sv"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA-höjdpunkter (plattform) {#nvidia-highlights-platform}

Watchern sparar det NVIDIA-höjdpunkter sparar om dina spel, så att du senare kan titta på din historik på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `nvidia-highlights`, slag [`platform`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel startar) och letar efter ny data var 10 s.*

## Vad som spelas in {#what-is-recorded}

- varje nytt klipp, höjdpunkt eller skärmbild: spel, fil, slag, längd och tidpunkt (väggklockans ms)
- höjdpunktens id och namn när spelet registrerat den hos NVIDIA
- var spelaren var vid det ögonblicket, när en annan adapter spelade in samma spel då
- höjdpunktsbegäranden som GfeSDK-spel loggar, även när inget klipp sparas

## Var datan kommer ifrån {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; klipp i inspelningsmappen (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) och &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Så slår du på det {#how-to-switch-it-on}

NVIDIA-appen: Instant Replay eller Highlights påslaget, klipp sparade med snabbtangent eller av spelet

## Så fungerar det {#how-it-works}

Det startprogrammet och grafikdrivrutinen sparar om spelandet: Steams statistik, prestationer, speltid och tidslinjer, och NVIDIA:s höjdpunkter och klipp.

Ingen av dessa källor behöver att ett spel samarbetar eller kör, så de tre adaptrarna här är alltid på och tittar på några filer var några sekunder.

#### NVIDIA-höjdpunkter och klipp (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Det NVIDIA-appen / GeForce Experience sparar, allt under `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      the gallery index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (where clips are saved),
                     settings.tempDirectory (highlights wait in
                     <temp>\Highlights\<game> until saved)
Highlights\<game>\config.json  the highlight kinds a game registered:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
och själva klippfilerna, `<capture folder>\<Game>\<Game> yyyy.mm.dd - hh.mm.ss.ff.DVR.mp4` (skärmbilder: `<Game> Screenshot yyyy.mm.dd - ...png`), där tiden i namnet är lokal tid när klippet sparades. GfeSDK-spel loggar också sina höjdpunktsanrop i `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Vad detta kan och inte kan leverera: ett spel som stödjer NVIDIA Highlights (GfeSDK) registrerar höjdpunktstyper en gång - ett id som "kill", en betydelse, taggar, ett visningsnamn - och säger senare bara "highlight &lt;id>, from &lt;ms> before now to &lt;ms> after". Det finns inga positioner, ingen match eller runda, ingen motståndare, inga egna data: SDK:n har inget fält för något av det. Ett sparat klipp lägger till en fil, ett spelnamn, en längd och en tid. Så det som sparas är "den här sortens ögonblick, i det här spelet, vid den här tiden" - och en plats bara genom att slå upp tiden i en annan adapters inspelning av samma spel (`position_at`), vilket den här adaptern gör för varje klipp den sparar. <https://developer.nvidia.com/highlights>

Varje adapter sparar det den redan har sett i `<data>\state\<id>.json`, så en omstart spelar inte in något två gånger.

Varje session sparar också, helt, det som dess rader kom ifrån (3DHeats konverterarregel, docs/converters.md i visarens förråd), i `heat.raw.parquet`: statistikfilens och dess schemas byte och spelets localconfig-block (steam-stats; en statistikfil avkodaren inte kan läsa får en session som bara håller dess byte), tidslinjefilens huvud och varje post som JSON (steam-timeline), varje klipps post i galleriindex, spelets höjdpunktsdefinitioner och varje GfeSDK-loggrad, även de som inte är höjdpunktsbegäranden (nvidia-highlights).

Samma modul används också av: [Steam-statistik (plattform)](game-steam-stats.md), [Steam Timeline (plattform)](game-steam-timeline.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | bara lånade: platsen som en annan inspelning av samma spel har för det ögonblicket |
| Upp-axel | `y` |
| Enheter | meter |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **nej**. `games --markdown` visar detta som "single-player".
- Slag `platform`: den läser bara det spelet eller plattformen lämnar ut (det Steam eller grafikdrivrutinen sparar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- varje nytt klipp och skärmbild: spel, fil, slag, media, längd (från indexet, annars MP4-huvudet), tidpunkten från filnamnet, höjdpunktens id och namn där spelet registrerat dem, och spelarens plats då från en annan adapters inspelning
- GfeSDK-höjdpunktsbegäranden (varje `Posted Request HL...` utom konfigurationsanrop) med deras tid

**Sparas råa**

- `UGC`: klippets hela post i galleriindexet UGCTracker.json, varje fält NVIDIA skriver
- `clip_file`: för ett klipp som indexet inte listar, filens sökväg, storlek, tid och mapp
- `highlights_config`: spelets `Highlights\<game>\config.json` så som den är skriven (betydelse, taggar, namn på varje språk), en gång per session
- `gfesdk_log`: varje rad i GfeSDK-loggarna som lästs efter första körningen, `used` sann för höjdpunktsbegäranden och falsk för resten (konfiguration, videoinställningar, SDK:ns egna meddelanden)

**Finns inte**

- själva klippen och skärmbilderna: video och bilder ligger kvar där NVIDIA sparade dem; raderna anger filen
- det som fanns före adapterns första körning: räknas som redan sett, så år av klipp blir inte sessioner på en gång (`baseline`; False spelar in dem)
- UGCTracker.json:s `apps` och `info` och GallerySettings.json: appens inställningar, inte ögonblick från spelet; mappen för inspelning som de anger används
- positioner, rundor, motståndare: GfeSDK har inget fält för dem

**Storlek**: ungefär 1 KB per klipp och några KB definitioner och loggrader per spelstart: klart under 1 MB per timme

## Verifierat {#verified}

testad på ett verkligt galleriindex, inställningar, höjdpunktsdefinitioner och klipp från en lokal installation; GfeSDK-höjdpunktsbegäranlinjer och höjdpunkts-id i klipp är ännu inte testade

## Källa {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
