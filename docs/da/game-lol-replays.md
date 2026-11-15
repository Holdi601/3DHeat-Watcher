---
title: "League of Legends (replays)"
nav_order: 30
lang: "da"
source: game-lol-replays.md
source_hash: "ed26619fa904"
nav_exclude: true
search_exclude: true
---
# League of Legends (replays) {#league-of-legends-replays}

Efter en kamp i League of Legends omdanner watcheren den replay, spillet har gemt, til filer, du kan se på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `lol-replays`, type [`replay`](sources-and-rules.md); den kører hele tiden (den venter ikke på, at et spil starter) og leder efter nye data hver 5 s.*

## Hvad der registreres {#what-is-recorded}

- hver spillers champion, rolle, hold, drab, dødsfald, assists, guld, skade på champions og resultat, og hver anden tal i kampens slutbox
- din egen linje som statistik, og dine rækker navngivet som dine (meta.json `player`), med dit Riot-ID i indstillingerne
- med din egen Riot API-nøgle: hver spillers position hvert minut med minuttets statistik, og hver hændelse på tidslinjen (drab, hvor de skete, bygninger, monstre, wards, items, evner), på vægurstidspunktet tidslinjen angiver
- hver del af replay-filen gemt hel i heat.raw.parquet; ikke afkodet: det spil-for-spil-forløb, som er krypteret og forvansket mod snyd

## Hvor data kommer fra {#where-it-comes-from}

replays, League-klienten gemmer: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (kun de almindelige metadata fra kampens slutning); med din egen Riot API-nøgle kampens officielle tidslinje fra Riots Match-V5-API

## Sådan slår du det til {#how-to-switch-it-on}

gem en replay i League-klienten (kamphistorik > download) og installer læseren: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`); for positioner sæt riot_api_key og riot_platform med `config --set`

Indstillinger fra miljøvariabler:

- `HEAT3D_RIOT_REPLAYS`: læserens mappe (en klon eller udpakket udgivelse), når den ikke er installeret eller ligger ved siden af watcheren

## Sådan virker det {#how-it-works}

League of Legends og Valorant replays: det, der kan læses af dem som de er.

Begge spil gemmer replays på spillerens disk, og begge beskytter det, der er indeni:
spilledata i bevægelse er forvansket, og forskelligt med hver patch,
for at forhindre, at det bruges til at snyde. At komme igennem det betyder at adskille
spillets egen kode, hvilket Riots vilkår forbyder (Terms of Service 3.1 og 7.1)
- så det gøres ingen steder i 3DHeat. Det, hver fil bærer åbent, læses, og resten
gemmes, som den er: hver del af filen, hel, i sessionens `heat.raw.parquet` (3DHeats
konverterregel, docs/converters.md i viewerens repository), talt i meta.jsons `selfCheck.completeness`.

Watcheren læser ikke filerne selv: det gør en ekstern læser (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
kommandoen `heat3d-riot-replays`), holdt adskilt, så et problem med Riots
vilkår kun rammer den læser. Findes den på PATH, er installeret eller ligger ved siden af watcheren, læser den
hver ny replay; mangler den, siger watcheren én gang, hvordan den installeres. Det, den
læser, lægger watcheren ind i sessionen; Match-V5-tidslinjen nedenfor hentes af
watcheren selv, da den ikke findes i filen.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Begge containerversioner bærer
kampens slutbox som almindelig JSON (`statsJson`): for hver af de ti spillere
champion, drab, dødsfald, assists, guld, skade på champions, items, hold, rolle, sejr, deres Riot-ID og hvert andet
tal spillet summerer (over hundrede pr. spiller); alle bliver spillerens
`player_result`-række. ROFL1 (patch 14.9 og tidligere) har den efter en fast header
(`RIOT\0\0`, en 256-byte signatur, så længderne); ROFL2 (14.11 og senere,
`RIOT\2\0`) i filens ende, dens længde i de sidste fire bytes (oplyst
af en Riot-ingeniør, ReplayBook issue 299). ROFL1's payload-header (spil-id,
længde, antal chunks og keyframes, længden af chunk-nøglen) og dens tabel over
chunks (id, type, længde, næste chunk, forskydning) ligger åbent og læses; selve
chunksene er krypteret og gemmes hele uden at blive læst.

Positioner kommer ikke fra filen. Med en Riot-udviklernøgle tilhørende spilleren selv (`riot_api_key` i indstillingerne; en personlig nøgle er til netop dette,
"showing (self) player stats"), hentes kampens officielle tidslinje fra
Riots Match-V5-API: hver spillers position hvert minut med alt, minuttets billede siger om dem
(guld, erfaring, niveau, minions, champion- og skadestatistik), og hver hændelse på tidslinjen - drab, bygninger, elitemonstre, wards, items, evner, niveauer - hver en række, hvor den skete, når den har et sted. Uden nøgle hentes intet, og intet sendes.

Modulet dækker også: [VALORANT (replays)](game-valorant-replays.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | Summoner's Rift-kortenheder (cirka 15000 på tværs) |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det spillet udleverer)".
- Type `replay`: den læser kun det, spillet eller platformen udleverer (replays og optagelser spillet gemmer), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`champion`, `game_seconds`, `won`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- metadata-JSON: spillets længde, version, id'er for sidste chunk og keyframe, og `statsJson` - hvert felt i hver spillers slutbox på deres `player_result`-række (tal givet som tekst læses som tal)
- ROFL1: længdeblokken, payload-headeren (spil-id, spillets længde, antal keyframes og chunks, id'er for start- og spilstart-chunk, keyframe-interval, chunk-nøglen som den er gemt) og chunk-tabellen (id, type, længde, næste chunk, forskydning) - i meta.json `rofl` og rå-rækkernes `text`
- ROFL2: versionsstrengen
- Match-V5-tidslinjen (kun med egen API-nøgle): hver deltagerramme på en `position`-række (eller `participant_frame` uden sted) med alle sine felter flad (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); hver hændelse som en række navngivet efter sin type, placeret hvor den har en `position`, CHAMPION_KILL som et drab og et dødsfald

**Gemt råt**

- hver del af .rofl'en, hel, i filens rækkefølge (`offset`), så delene er filen: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); ethvert stykke ingen del dækker som `unknown`
- tidslinjen hel: `timeline <type>` for hver hændelse, `timeline participantFrame` for hver spillers ramme (`participant` dens id), `timeline` for resten

**Ikke tilgængeligt**

- selve spillet (positioner, evner, hver enhed, øjeblik for øjeblik): ROFL1's chunks og ROFL2's body er krypteret, og pakkerne indeni forvanskes med hver patch; at komme igennem betyder at adskille klienten, hvilket Riots vilkår forbyder (3.1, 7.1). Gemt hel, ikke læst
- positioner uden din egen Riot API-nøgle: filen har ingen åbent

**Størrelse**: det rå sidefil er cirka replayens egen størrelse: de krypterede chunks komprimerer ikke

## Verificeret {#verified}

læseren (heat3d-riot-replays) testet på filer bygget efter layouterne i roflxd.cs (MIT); tidslinjen efter Match-V5's dokumenterede JSON; ingen rigtig replay var tilgængelig at kontrollere mod

## Kilde {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
