---
title: "iRacing (live-data)"
nav_order: 28
lang: "da"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (live-data) {#iracing-live-data}

Mens du spiller iRacing, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem som statistik og en tidslinje.

*Tekniske detaljer: adapter `iracing`, type [`telemetry`](sources-and-rules.md); den kører, mens `iRacingSim64DX11.exe` eller `iRacingSim64.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- kørslen 5 gange i sekundet uden position (iRacing giver ingen live): hastighed, gear, gas, bremse, runde, andel af runden, løbs- og klasseplacering, incidents
- kørslens start, stige ind og ud af bilen, pitbanen ind og ud, runder med rundetid, incidents med deres point, ternet flag, mål
- .ibt-telemetrifilerne skrevet under sessionen (breddegrad, længdegrad, højde - vieweren læser dem)
- runder, bedste runde, incidents, løbsplacering, pitstop, distance, topfart
- hele den delte hukommelse i `heat.raw.parquet`: header, variabelheaders, sessionsinfo, hver telemetrilinje der læses

## Hvor data kommer fra {#where-it-comes-from}

delt hukommelse Local\IRSDKMemMapFileName (iRacing SDK); .ibt-filer i %USERPROFILE%\Documents\iRacing\telemetry

## Sådan slår du det til {#how-to-switch-it-on}

Intet for live-data. For positioner: log telemetri i bilen (Alt+L) eller sæt irsdkLog=1 i app.ini

## Sådan virker det {#how-it-works}

iRacing, live: iRacing SDK'ens delte hukommelse, læst direkte.

iRacing udgiver sin telemetri til apps i en navngiven filmapning,
`Local\IRSDKMemMapFileName`, som simulatoren opretter, mens den kører (og signalerer
`Local\IRSDKDataValidEvent` ved hver opdatering, hvilket ikke er nødvendigt her:
watcheren læser ti gange i sekundet). Layoutet er SDK'ens `irsdk_defines.h`,
også fulgt af pyirsdk (MIT) - skrevet igen her ud fra disse fakta:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Simulatoren skriver `numBuf` linjer i rund orden; den nyeste er den med den højeste
tickCount, og en linje læses igen, hvis dens tickCount ændrede sig, mens den blev kopieret.

Live-data har ingen verdensposition - breddegrad, længdegrad og højde findes kun i
.ibt-filerne, som iRacing logger til `Documents\iRacing\telemetry` (Alt+L i
bilen, eller `irsdkLog=1`), og som 3DHeat-vieweren læser selv. Så dette optager
kørslen som hændelser uden koordinater - hastighed, runde, andelen af runden
kørt, løbsplacering, incidents - plus runder, incidents, pitstop og det ternede flag, og til sidst
de .ibt-filer, der er skrevet under sessionen, som `telemetry_file`-hændelser, så vieweren kan åbne dem.

Ved siden af rækkerne gemmes hele hukommelseskortet i sessionens råsidefil
(`heat.raw.parquet`): headerens faste del (`header`, hver gang den ændrer sig), variabelheaderne
(`var_headers`, hele, og som JSON i `text`, hver gang layoutet ændrer sig), sessionsinfo-YAML'en
(`session_info`, dens tekst hver gang `sessionInfoUpdate` rykker sig) og den nyeste telemetrilinje
(`telemetry`, hver variabel i den, ved hver læsning der finder et nyt tick). Variabelheaderne
og en linje er alt, en senere afkoder behøver for at læse enhver variabel.

Kilde: iRacing SDK (irsdk_defines.h, "iRacing SDK"-forummets dokumentation);
kutu/pyirsdk (MIT) til bekræftelse af forskydningerne.

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | nej |
| Op-akse | `y` |
| Enheder | ingen positioner live; .ibt-filerne bærer breddegrad/længdegrad/højde |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det spillet udleverer)".
- Type `telemetry`: den læser kun det, spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- fra den nyeste telemetrilinje: sessionstid, nummer, tilstand og id, på banen, replay, runde, gennemførte runder, andel og meter af runden, sidste og bedste runde, hastighed, gear, gas, bremse, omdrejninger, pitbane, banens underlag, løbs- og klasseplacering, egen incident-tæller (`driving`-rækkerne 5 gange i sekundet og hændelserne)
- nu også på `driving`-rækkerne: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (grader, omregnet fra simulatorens radianer - kun når variabelheaderen angiver enheden som rad), `fuel_l` (enhed l), `lat_accel` og `lon_accel` (enhed m/s^2)
- fra sessionsinfo-YAML'en: spillerens bilindeks, bane og konfiguration, sessionstyper, hver førers navn, bil, hold og nummer (session_start-rækker, meta.json)
- kontrolleret mod en blok bygget ud fra irsdk_defines.h i testene; endnu ikke mod simulatoren

**Gemt råt**

- `telemetry`: den nyeste linje hel, hver variabel simulatoren udgiver (CarIdx-arrays for alle biler, dæk, ophæng, de højfrekvente `_ST`-arrays hvor simulatoren har dem ...), ved hver læsning der finder et nyt tick; `tick` simulatorens tælle for ticks; `used` er falsk, mens et replay afspilles
- `var_headers`: variabelheaderne hele (144 bytes hver) og, i `text`, som JSON (navn, type, forskydning, antal, enhed, beskrivelse), hver gang layoutet ændrer sig - nok til at læse enhver variabel i enhver gemt linje
- `session_info`: YAML-teksten hel, hver gang dens opdateringstæller rykker sig (weekend, sessioner og resultater, førere, bilopsætning, radio, kameralister), `update` tælleren
- `header`: de 112 bytes af irsdk-headeren hele, hver gang den ændrer sig (version, status, tickrate, forskydninger, linjernes ticks)

**Ikke tilgængeligt**

- en verdensposition live: den delte hukommelse har ingen; breddegrad, længdegrad og højde findes kun i .ibt-filerne (når logging er slået til), som vieweren læser - watcheren navngiver dem, der er skrevet under sessionen
- ticks mellem to læsninger: simulatoren skriver 60 linjer i sekundet i 3 eller 4 pladser, og watcheren læser 10 gange i sekundet, så de fleste ticks overskrives, før de kan læses; .ibt-filen har hvert tick, når logging er slået til

**Størrelse**: en telemetrilinje er cirka 5 til 10 KB (med alle bilers arrays), gemt op til 10 gange i sekundet, plus headeren (112 bytes) lige så ofte og sessionsinfo-YAML'en (titusinder af KB), når den ændrer sig: cirka 0.2 til 0.4 GB i timen på banen før komprimering; zstd bringer det ned til en brøkdel (endnu ikke målt på en rigtig session)

## Verificeret {#verified}

testet på en delt hukommelsesblok bygget i testen ud fra irsdk-layoutet; ikke testet mod simulatoren

## Kilde {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
