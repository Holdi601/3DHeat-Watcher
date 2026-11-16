---
title: NVIDIA Highlights
nav_order: 8
lang: "sv"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Vissa spel ber din NVIDIA-grafikdrivrutin att spara en kort video när något händer, till exempel en kill.
Watchern noterar varje sådant ögonblick och, när den kan, lägger det på kartan där det hände.

Adaptern `nvidia-highlights` spelar in klippen, highlights och skärmbilderna som NVIDIA-appen (eller GeForce Experience) sparar, och ger varje en plats på kartan när den kan. Den här sidan förklarar vad NVIDIA Highlights kan leverera och vad det inte kan, vilka filer watchern läser, och hur en highlight får en position. Adapterns genererade sida är [NVIDIA highlights (plattform)](game-nvidia-highlights.md).

## Vad NVIDIA Highlights kan och inte kan leverera {#what-nvidia-highlights-can-and-cannot-deliver}

Ett spel som stödjer NVIDIA Highlights pratar med NVIDIA-appen genom NVIDIAs GfeSDK. SDK:n bär bara två slags meddelanden:

1. **En gång, vid start**: de highlight-typer spelet kommer att använda - ett id (som `kill`), en betydelse, taggar, och ett visningsnamn per språk. NVIDIA-appen sparar dessa per spel.
2. **Vid ett ögonblick i spelet**: "highlight `<id>`, från `<ms>` före nu till `<ms>` efter". Det är hela meddelandet: id:t för en typ spelet registrerat, och två tidsförskjutningar som säger åt NVIDIA-appen vilken sträcka av dess rullande inspelning som ska behållas.

SDK:n har **inget fält för något annat**: ingen position, ingen match eller rond, ingen motståndare, inget vapen, ingen poäng, ingen egen data av något slag. Ett spel kan inte lägga en position i en highlight, även om det ville. När klippet sparas lägger NVIDIA-appen till en fil, ett spelnamn, en längd och en tid.

Så allt en highlight kan säga är "den här typen av ögonblick, i det här spelet, vid den här tiden". Allt mer måste komma från något annat ställe.

## Vad watchern läser {#what-the-watcher-reads}

Allt läses från filer som NVIDIA-appen skriver för sitt eget galleri. Inget pratar med drivrutinen eller appen. NVIDIA Overlay-mappen är `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Fil | Vad som tas från den |
|---|---|
| `UGCTracker.json` | galleriindexet: varje klipp och skärmbild med sin sökväg, typ (video, bild), undertyp (`InstantReplay`, ...), datum, spelets profilnamn, körbar fil och kortnamn, och längd (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, inspelningsmappen, och `settings.tempDirectory`, där highlights väntar (`<temp>\Highlights\<game>`) tills de sparas |
| `Highlights\<game>\config.json` | de highlight-typer varje spel registrerat: id, och det engelska visningsnamnet (eller id:t där spelet inte gav något) |
| inspelningsmappen (standard `%USERPROFILE%\Videos\NVIDIA`) och `<temp>\Highlights` | själva klipp- och skärmbildsfilerna (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), en mapp per spel |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | de begäranden GfeSDK-spel loggar - `Posted Request HL...`-raderna - så att en highlight som spelet begärt registreras även när inget klipp sparades. Konfigurationsbegäranden (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) hoppas över. |

För varje ny post skriver adaptern en rad: `highlight` för en video, `screenshot` för en bild, eller `highlight_request` för en GfeSDK-loggrad. Dess fält:

| Fält | Vad det är |
|---|---|
| `ms` | ögonblicket: tiden i filnamnet (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, den lokala tiden då klippet sparades), annars indexets datum, annars filens ändringstid |
| `game` | NVIDIA-profilnamnet, mappens namn eller spelet i filnamnet |
| `clip`, `media` | filens sökväg; `video`, `image` eller `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (från den tillfälliga highlight-mappen) eller indexets undertyp |
| `duration_s`, `clip_start_ms` | längden, från indexet eller från videons egen header (`moov/mvhd`, hittad utan att läsa videon); det ögonblick klippet börjar |
| `highlight_id`, `highlight_name` | highlight-typen, när något namnger den (se nedan) |
| `exe` | spelets körbara fil, från indexet |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | den lånade positionen, när en hittades (se nedan) |

Sessionsstatistiken är `clips`, `screenshots`, `clip_seconds` och `placed` (poster som fick en position).

**Highlight-id:t** står inte skrivet på någon dokumenterad plats. Adaptern prövar två odokumenterade vägar: ett fält i galleriposten vars namn innehåller "highlight", och - bara för filer i den tillfälliga highlight-mappen - ett av spelets registrerade id (minst 4 tecken långt) som finns i filnamnet. Ett sparat klipp är namngivet efter spelet, som kunde innehålla ett id som "kill" av en slump, så dess namn söks inte. De två vägarna har ännu inte visat sig fungera på en riktig dator: inget klipp med ett highlight-id, och ingen GfeSDK-begäranrad, har förekommit där adaptern testats. Galleriindexet, inställningarna, highlight-definitionerna och klippen testades på riktiga filer.

### När poster spelas in {#when-items-are-recorded}

- Ett klipp skrivs fortfarande en stund efter tangenttryckningen. Adaptern väntar tills en fil har samma storlek och tid vid två kontroller (var 10 s) och är minst 5 s gammal.
- Första gången adaptern körs noteras bara allt som redan finns i galleriet och loggarna, inte spelas in, så att år av gamla klipp inte översvämmar statistiken. Det den har sett sparas i `<data>\state\nvidia-highlights.json`, så att en omstart inte registrerar något två gånger.
- Poster grupperas i en session per spel. Ett spels session stängs efter 30 minuter utan en ny post, och slutar vid sitt sista ögonblick i stället för när spelet stängdes. Ögonblick mer än 30 minuter isär hamnar i separata sessioner.

## Så får en highlight en position {#how-a-highlight-gets-a-position}

Highlighten i sig har ingen plats. Adaptern slår upp ögonblicket i de andra inspelningar watchern gjort av samma spel vid samma tid:

1. **Samma spel**: sessionsmapparna under `<data>\sessions\` vars spelnamn matchar highlightens. Namn jämförs med små bokstäver, bara bokstäver och siffror. De matchar när de är lika, eller när det kortare har minst 5 tecken och finns i det längre (`Counter-Strike 2` och `Counter-Strike-2`).
2. **Samma tid**: sessioner vars start och slut (från `meta.json`, med en sekunds marginal i båda ändar) täcker ögonblicket. Sessioner som slutade utan positioner, och adapterns egna sessioner, hoppas över.
3. **Spelarens egen rad**: i deras `events.jsonl`, den senaste av spelarens egna rader med en position, vid eller före ögonblicket och högst 5 sekunder före det. En rad är spelarens egen när dess källa säger det: `"player": "me"`, eller `"own_car": 1` (racingspel som spelar in varje bil efter sin förare), eller en `player` som är sessionens `player` i `meta.json` (namnet källan ger spelaren). Se [Spelarens egna rader](the-data.md#the-players-own-rows).

Om en rad hittas får highlighten sina `x`, `y`, `z`, sin `session` (eller mappens namn), `position_from` (mappen den kom från) och `position_lag_ms` (hur länge före ögonblicket den raden var). Highlight-sessionen tar den inspelningens axlar, så att den ritas på samma sätt. Om ingen rad hittas blir highlighten ett ögonblick på tidslinjen utan plats.

Saker att veta om den lånade positionen:

- **Det är där du var när klippet sparades**, inte där handlingen började. Ögonblicket är sparningstiden i filnamnet, vilket för en Instant Replay är dess slut. `clip_start_ms` säger när klippet börjar.
- **En annan adapter måste ha spelat in samma spel vid tiden.** De som markerar spelarens egna rader, och därmed kan placera en highlight: Counter-Strike 2 och Dota 2 game-state integration, Forza, Assetto Corsa-spelen, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft och minnesprofiler (som `me`); F1 23/24/25, RaceRoom, Automobilista 2 och Project CARS 2 (dina bilars rader har `own_car` 1, efter spelets spelarbilindex, dess egen plats eller den betraktade deltagaren); Elite Dangerous (befälhavarens namn, i `meta.json` som `player`, eftersom journalen alltid är spelarens).
- **En replay omvandlas efter matchen**, så den kan bara placera ett klipp som slås upp efter omvandlingen: klippet placeras när det spelas in, och en replay som sparas senare tittas inte på igen. League of Legends-replayer namnger dina rader efter Riot-ID:t i inställningarna och, med en Riot API-nyckel, ger dem den väggklocketid som matchens tidslinje anger, så att de hittas då. En CS2-demo kan inte placera en highlight alls: dess positioner finns i omvandlarens egen tabell, inte i `events.jsonl`, och en demo har spelets ticks men ingen väggklocketid att matcha ett klipps ögonblick mot.
- I Rocket League är de enda raderna med en plats bollhändelser. En bollträff av dig är en rad av dig, så en highlight kan placeras där du senast träffade bollen.
- Spel utan någon positionskälla alls (Overwatch 2, Call of Duty, Hunt: Showdown, ...) behåller sina highlights som en tidslinje av ögonblick.

## Varför minnet inte kan ge en position i flerspelar {#why-memory-cannot-give-a-position-in-multiplayer}

Det andra sättet att få en position skulle vara att läsa den ur minnet. Inget av minnena fungerar:

- **NVIDIAs minne har ingen position i sig.** NVIDIA-appen tar emot det GfeSDK bär - ett highlight-id och två tidsförskjutningar - plus videon den spelar in. Det finns ingen position någonstans på NVIDIAs sida att läsa. (Watchern läser inte NVIDIAs minne ändå; den läser filerna ovan.)
- **Spelets minne är utom räckhåll i flerspelar.** Positionen finns i spelets process, men watchern läser aldrig ett flerspelarspels minne: en minnesadapter för ett spel markerat som spelat online avvisas innan något öppnas (se [Läsa minne](memory-reading.md)). Flerspelarspel körs under fusksskydd (Easy Anti-Cheat, BattlEye, Vanguard, ...) som behandlar att ett annat program öppnar spelets process som fusk, vilket kan leda till att kontot blir avstängt. En highlight i ett flerspelarspel får därför bara en plats från det spelet publicerar: dess game-state integration eller telemetri, inspelad av en annan adapter vid samma tid.
