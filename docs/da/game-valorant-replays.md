---
title: "VALORANT (replays)"
nav_order: 44
lang: "da"
source: game-valorant-replays.md
source_hash: "a2c4144797e9"
nav_exclude: true
search_exclude: true
---
# VALORANT (replays) {#valorant-replays}

Efter en kamp i VALORANT omdanner watcheren den replay, spillet har gemt, til filer, du kan se som statistik og en tidslinje.

*Tekniske detaljer: adapter `valorant-replays`, type [`replay`](sources-and-rules.md); den kører hele tiden (den venter ikke på, at et spil starter) og leder efter nye data hver 5 s.*

## Hvad der registreres {#what-is-recorded}

- kortet, kampens id og de valgte agenter; replayens infoblok (længde, versioner, navn, optagelsestidspunkt, komprimerings- og krypteringsflag)
- serverens hændelsestidslinje: drab (dræber og offer som netværks-id'er), runder der starter, spikes plantet, defuset og eksploderet, ultimates brugt, sider der skifter - hver med sit id og sine metadata
- hver chunk i filen gemt hel i heat.raw.parquet; ikke afkodet: positioner, navne eller score - de ligger i den forvanskede strøm

## Hvor data kommer fra {#where-it-comes-from}

replays, VALORANT gemmer: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (kun de dele, der ikke er forvanskede)

## Sådan slår du det til {#how-to-switch-it-on}

gem en replay i VALORANT (karriere > kamp > download replay) og installer læseren: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Indstillinger fra miljøvariabler:

- `HEAT3D_RIOT_REPLAYS`: læserens mappe (en klon eller udpakket udgivelse), når den ikke er installeret eller ligger ved siden af watcheren

## Sådan virker det {#how-it-works}

League of Legends og Valorant replays: det, der kan læses af dem som de er.

Begge spil gemmer replays på spillerens disk, og begge beskytter det, der er indeni:
spilledata i bevægelse er forvansket, og forskelligt med hver patch,
for at forhindre, at det bruges til at snyde. Den del afkodes ingen
steder i 3DHeat. Det, hver fil bærer åbent, læses, og resten
gemmes, som den er: hver del af filen, hel, i sessionens `heat.raw.parquet` (3DHeats
konverterregel, docs/converters.md i viewerens repository), talt i meta.jsons `selfCheck.completeness`.

Watcheren læser ikke filerne selv: det gør en ekstern læser (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
kommandoen `heat3d-riot-replays`), et projekt for sig. Findes den på PATH, er installeret eller ligger ved siden af watcheren, læser den
hver ny replay; mangler den, siger watcheren én gang, hvordan den installeres. Det, den
læser, lægger watcheren ind i sessionen; Match-V5-tidslinjen nedenfor hentes af
watcheren selv, da den ikke findes i filen.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, en Unreal Engine-lokal replay. Åbent:
replayens infoblok (længde, netværksversion, changelist, dens navn, hvornår den
blev optaget, om den er komprimeret eller krypteret), kortet, kampens id og
de valgte agenter (i headeren), og serverens egen hændelsestidslinje - drab
(dræber og offer som netværks-id'er, ikke navne), runder der starter, spikes plantet,
defuset og eksploderet, ultimates brugt, sider der skifter - hver med sit tidspunkt,
id og metadata. Positioner, navne, score og alt andet ligger i den forvanskede strøm
(replaydata- og checkpoint-chunks), som gemmes hel og ikke læses.

Modulet dækker også: [League of Legends (replays)](game-lol-replays.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | nej |
| Op-akse | `z` |
| Enheder | VALORANT-verdensenheder |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det spillet udleverer)".
- Type `replay`: den læser kun det, spillet eller platformen udleverer (replays og optagelser spillet gemmer), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- infoblokken, hvert felt (meta.json `vrf`): filversion, brugerdefinerede versioner, længde, netværksversion, changelist, navn, live-flag, optagelsestidspunkt, komprimerings- og krypteringsflag, nøglen som den er gemt
- headerchunken: kortet, kampens id og de valgte agenter (fundet ud fra deres form)
- hver hændelseschunk: id, gruppe, metadata, start- og sluttidspunkt, og af dens data hændelsens navn, dens tidspunkt i sekunder og tallene før det (dræber- og offer-netværks-id'er) - en række hver

**Gemt råt**

- hver chunk hel, i filens rækkefølge (`offset`), så delene er filen: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` for en type layoutet ikke navngiver, `trailing` for bytes efter den sidste hele chunk

**Ikke tilgængeligt**

- positioner, navne, score, evner, hver frame af spillet: replaydata- og checkpoint-chunks er forvanskede. Gemt hel, ikke læst
- indholdet af en krypteret replay: gennemgået og gemt hel, ikke læst indeni

**Størrelse**: det rå sidefil er cirka replayens egen størrelse: den forvanskede strøm komprimerer ikke

## Verificeret {#verified}

læseren (heat3d-riot-replays) er bygget ud fra containerlayoutet dokumenteret af vrfkit (Apache-2.0); ikke testet på en rigtig replay, ingen var tilgængelig - den kontrollerer før læsning og springer over det, der ikke passer

## Kilde {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
