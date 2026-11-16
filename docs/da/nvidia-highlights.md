---
title: NVIDIA Highlights
nav_order: 8
lang: "da"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Nogle spil beder din NVIDIA-grafikdriver om at gemme en kort video, når noget sker, f.eks. et drab.
Watcheren noterer hvert af disse øjeblikke og sætter, når den kan, det på kortet, hvor det skete.

Adapteren `nvidia-highlights` optager de klip, highlights og skærmbilleder, NVIDIA-appen (eller GeForce Experience) gemmer, og giver hvert af dem et sted på kortet, når den kan. Denne side forklarer, hvad NVIDIA Highlights kan levere og hvad ikke, hvilke filer watcheren læser, og hvordan et highlight får en position. Adapterens genererede side er [NVIDIA highlights (platform)](game-nvidia-highlights.md).

## Hvad NVIDIA Highlights kan og ikke kan levere {#what-nvidia-highlights-can-and-cannot-deliver}

Et spil, der understøtter NVIDIA Highlights, taler med NVIDIA-appen gennem NVIDIAs GfeSDK. SDK'et bærer kun to slags beskeder:

1. **Én gang, ved start**: de highlight-slags spillet vil bruge - et id (f.eks. `kill`), en betydning, tags og et visningsnavn pr. sprog. NVIDIA-appen gemmer dem pr. spil.
2. **På et øjeblik i spillet**: "highlight `<id>`, fra `<ms>` før nu til `<ms>` efter". Det er hele beskeden: id'et på en slags, spillet har registreret, og to tidsforskydninger, der fortæller NVIDIA-appen, hvilket stykke af dens løbende optagelse der skal gemmes.

SDK'et har **intet felt til noget andet**: ingen position, ingen kamp eller runde, ingen modstander, intet våben, ingen score, ingen tilpassede data af nogen art. Et spil kan ikke lægge en position ind i et highlight, selv om det ville. Når klippet gemmes, tilføjer NVIDIA-appen en fil, et spilnavn, en længde og et tidspunkt.

Et highlight kan altså kun sige "denne slags øjeblik, i dette spil, på dette tidspunkt". Alt mere skal komme fra et andet sted.

## Hvad watcheren læser {#what-the-watcher-reads}

Alt læses fra filer, NVIDIA-appen skriver til sit eget galleri. Intet taler med driveren eller appen. NVIDIA Overlay-mappen er
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Fil | Hvad der tages fra den |
|---|---|
| `UGCTracker.json` | galleriets indeks: hvert klip og skærmbillede med sin sti, type (video, billede), undertype (`InstantReplay`, ...), dato, spillets profilnavn, eksekverbar og kortnavn, og længde (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, optagemappen, og `settings.tempDirectory`, hvor highlights venter (`<temp>\Highlights\<game>`), indtil de gemmes |
| `Highlights\<game>\config.json` | de highlight-slags hvert spil har registreret: id, og det engelske visningsnavn (eller id'et, hvor spillet ikke gav et) |
| optagemappen (standard `%USERPROFILE%\Videos\NVIDIA`) og `<temp>\Highlights` | selve klip- og skærmbilledfilerne (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), én mappe pr. spil |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | de forespørgsler, GfeSDK-spil logger - `Posted Request HL...`-linjer - så et highlight spillet bad om registreres, selv når intet klip blev gemt. Konfigurationsforespørgsler (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) springes over. |

For hvert nyt element skriver adapteren én række: `highlight` for en video, `screenshot` for et billede, eller `highlight_request` for en GfeSDK-logllinje. Dens felter:

| Felt | Hvad det er |
|---|---|
| `ms` | øjeblikket: tidspunktet i filnavnet (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, lokal tid da klippet blev gemt), ellers indeksets dato, ellers filens ændringstidspunkt |
| `game` | NVIDIA-profilnavnet, mappens navn eller filnavnets spil |
| `clip`, `media` | filens sti; `video`, `image` eller `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (fra den midlertidige highlights-mappe) eller indeksets undertype |
| `duration_s`, `clip_start_ms` | længden, fra indekset eller fra videoens egen header (`moov/mvhd`, fundet uden at læse videoen); det øjeblik klippet begynder |
| `highlight_id`, `highlight_name` | highlight-slagen, når noget navngiver den (se nedenfor) |
| `exe` | spillets eksekverbare fil, fra indekset |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | den lånte position, når en blev fundet (se nedenfor) |

Sessionens statistik er `clips`, `screenshots`, `clip_seconds` og `placed` (elementer, der fik en position).

**Highlight-id'et** står ikke skrevet nogen dokumenteret sted. Adapteren prøver to udokumenterede veje: et felt i galleriets post, hvis navn indeholder "highlight", og - kun for filer i den midlertidige highlights-mappe - et af spillets registrerede id'er (mindst 4 tegn langt), der står i filnavnet. Et gemt klip er navngivet efter spillet, som tilfældigvis kunne indeholde et id som "kill", så dets navn bliver ikke søgt. Ingen af de to veje har endnu vist sig at virke på en rigtig maskine: der er ikke set et klip med et highlight-id, og ingen GfeSDK-forespørgselslinje, der, hvor adapteren blev testet. Galleriets indeks, indstillinger, highlight-definitioner og klip er testet på rigtige filer.

### Hvornår elementer optages {#when-items-are-recorded}

- Et klip bliver ved med at blive skrevet et stykke tid efter tastetrykket. Adapteren venter, til en fil har samme størrelse og tidspunkt ved to kig (hver 10. s), og er mindst 5 s gammel.
- Første gang adapteren kører, noteres alt, der allerede er i galleriet og logfilerne, kun, ikke optages, så års gamle klip ikke oversvømmer statistikken. Det den har set, gemmes i `<data>\state\nvidia-highlights.json`, så en genstart ikke optager noget to gange.
- Elementer grupperes i én session pr. spil. Et spils session lukker efter 30 minutter uden et nyt element og slutter ved sit sidste øjeblik i stedet for, når det lukkede. Øjeblikke der ligger mere end 30 minutter fra hinanden, går i separate sessioner.

## Sådan får et highlight en position {#how-a-highlight-gets-a-position}

Selve highlightet har intet sted. Adapteren slår øjeblikket op i de andre optagelser, watcheren har lavet af samme spil på samme tidspunkt:

1. **Samme spil**: sessionmapperne under `<data>\sessions\`, hvis spilnavn matcher highlightets. Navne sammenlignes med små bogstaver, kun bogstaver og cifre. De matcher, når de er ens, eller når det korteste har mindst 5 tegn og er indeholdt i det længste (`Counter-Strike 2` og `Counter-Strike-2`).
2. **Samme tidspunkt**: sessioner, hvis start og slut (fra `meta.json`, med et sekunds slør i begge ender) dækker øjeblikket. Sessioner, der sluttede uden positioner, og adapterens egne sessioner springes over.
3. **Spillerens egen række**: i deres `events.jsonl` den seneste af spillerens egne rækker med en position, på eller før øjeblikket og højst 5 sekunder før. En række er spillerens egen, når dens kilde siger det: `"player": "me"`, eller `"own_car": 1` (racingspil, der optager hver bil efter sin fører), eller en `player`, der er sessionens `player` i `meta.json` (det navn kilden giver spilleren). Se [Spillerens egne rækker](the-data.md#the-players-own-rows).

Hvis en række findes, får highlightet sine `x`, `y`, `z`, sin `session` (eller mappens navn), `position_from` (mappen den kom fra) og `position_lag_ms` (hvor længe før øjeblikket den række var). Highlight-sessionen tager den optagelses akser, så den tegnes på samme måde. Findes ingen række, bliver highlightet et øjeblik på tidslinjen uden et sted.

Ting at vide om den lånte position:

- **Det er, hvor du var, da klippet blev gemt**, ikke hvor handlingen begyndte. Øjeblikket er gemmetidspunktet i filnavnet, som for en Instant Replay er dens slut. `clip_start_ms` siger, hvornår klippet begynder.
- **En anden adapter skal have optaget det samme spil på det tidspunkt.** De, der markerer spillerens egne rækker og dermed kan placere et highlight: Counter-Strike 2 og Dota 2 game-state integration, Forza, Assetto Corsa-spillene, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft og hukommelsesprofiler (som `me`); F1 23/24/25, RaceRoom, Automobilista 2 og Project CARS 2 (dine bils rækker bærer `own_car` 1, efter spilets bilindeks, dens egen plads eller den viste deltager); Elite Dangerous (kommandørens navn, i `meta.json` som `player`, fordi journalen altid er spillerens).
- **En replay konverteres efter kampen**, så den kan kun placere et klip, der slås op efter konverteringen: klippet placeres, når det optages, og et replay gemt senere kigges der ikke på igen. League of Legends-replays navngiver dine rækker efter Riot-ID'et i indstillingerne, og med en Riot API-nøgle giver de dem det vægtursklokkeslæt, kampens tidslinje oplyser, så de findes da. Et CS2-demo kan slet ikke placere et highlight: dets positioner ligger i konverterens egen tabel, ikke i `events.jsonl`, og et demo har spillets ticks men ingen vægtursklokkeslæt at matche et klips' øjeblik med.
- I Rocket League er de eneste rækker med et sted boldhændelser. Et bold-slag fra dig er en række med din egen, så et highlight kan placeres der, hvor du sidst ramte bolden.
- Spil uden nogen positionskilde overhovedet (Overwatch 2, Call of Duty, Hunt: Showdown, ...) beholder deres highlights som en tidslinje af øjeblikke.

## Hvorfor hukommelse ikke kan give en position i multiplayer {#why-memory-cannot-give-a-position-in-multiplayer}

Den anden måde at få en position på ville være at læse den ud af hukommelsen. Ingen af hukommelserne virker:

- **NVIDIAs hukommelse har ingen position i sig.** NVIDIA-appen modtager det, GfeSDK bærer - et highlight-id og to tidsforskydninger - plus videoen den optager. Der er ingen position nogen steder på NVIDIAs side at læse. (Watcheren læser alligevel ikke NVIDIAs hukommelse; den læser filerne ovenfor.)
- **Spillets hukommelse er utilgængelig i multiplayer.** Positionen ligger i spillets proces, men watcheren læser aldrig et multiplayer-spils hukommelse: en hukommelsesadapter for et spil markeret som spillet online afvises, før noget åbnes (se [Læsning af hukommelse](memory-reading.md)). Multiplayer-spil kører under anti-cheats (Easy Anti-Cheat, BattlEye, Vanguard, ...), der behandler et andet program, der åbner spillets proces, som snyd, hvilket kan give kontoen et forbud. Et highlight i et multiplayer-spil får derfor kun et sted ud fra det, spillet selv udgiver: dets game-state integration eller telemetri, optaget af en anden adapter på samme tidspunkt.
