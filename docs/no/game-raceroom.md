---
title: "RaceRoom Racing Experience (direkte data)"
nav_order: 37
lang: "no"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (direkte data) {#raceroom-racing-experience-live-data}

Mens du spiller RaceRoom Racing Experience, lagrer watcheren dataene spillet selv sender ut, slik at du senere kan se på dem på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `raceroom`, type [`telemetry`](sources-and-rules.md); den kjører mens `RRRE64.exe` eller `RRRE.exe` går og ser etter nye data hvert 0,1 s.*

## Hva som tas opp {#what-is-recorded}

- hver bils posisjon (verdensposisjon XYZ, m) 10 ganger i sekundet etter sjåførens navn, egen bil markert, med fart og posisjon i løpet; eget gir, gass og brems
- øktstart med banen spillet oppgir; runder per bil med rundetid; målgang; egne pit-stopp
- teleporteringer (tilbake til boksen, en omstart): `teleport` der bilen var, `spawn` der den er nå
- egne runder, beste runde, posisjon i løpet, distanse, toppfart
- spillets hele delte minneside i `heat.raw.parquet`, hver gang den endrer seg
- egne hendelsespoeng

## Hvor det kommer fra {#where-it-comes-from}

delt minne $R3E (Sector3s r3e.h, versjon 3)

## Slik slår du det på {#how-to-switch-it-on}

Ingenting må slås på: watcheren leser kilden slik spillet eller plattformen gir den.

## Slik fungerer det {#how-it-works}

Delt minne som racingspill publiserer for dashbord, åpnet skrivebeskyttet - og aldri opprettet.

Flere simulatorer leverer telemetrien sin som en navngitt Windows-filmapping som spillet oppretter og alle kan lese: Kunos' `Local\acpmf_*`-sider (Assetto Corsa, ACC, AC Rally, AC EVOs `Local\acevo_pmf_*`), iRacings `Local\IRSDKMemMapFileName`, RaceRooms `$R3E`, Automobilista 2 / Project CARS 2s `$pcars2$`.

Hvorfor ikke `mmap.mmap(-1, size, tagname=...)`, som er den vanlige måten i Python: når mappingen ikke finnes ennå, *oppretter* den en - her skrivebeskyttet. Et spill som startes etterpå åpner watcherens mapping i stedet for å lage sin egen, og kan da ikke skrive til den, så telemetrien er død til watcheren slipper den. Watcheren starter en adapter så snart spillets prosess dukker opp, og det er nettopp øyeblikket spillet ikke har laget sin mapping ennå. Derfor åpner dette med `OpenFileMappingW`, som bare finner en eksisterende mapping, mapper den med `FILE_MAP_READ`, og melder "ikke der ennå" ellers; adapterne prøver igjen litt senere.

Ingenting her kan skrive: visningen er mappet skrivebeskyttet og kopieres bare ut av med `ctypes.string_at`.

To spill leses her også; hver bil på banen står i deres sider.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3s `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, versjon 3.6), `#pragma pack(1)`. Headeren sier hvor sjåførene starter og hvor stor en er (`all_drivers_offset`, `driver_data_size`), så sjåførdelen - navn, plass, posisjon i løpet, verdensposisjon (float x y z, m), fullførte runder, nåværende rundetid, målstatus, pit lane og fart - leses etter disse. Spillerens egne felt (beste og forrige runde, posisjon i løpet, hendelsespoeng, gir, pedaler, bane- og løype-navn) leses på sine 3.6-forskyvninger bare når `all_drivers_offset` er 2008, som den layouten plasserer den på. Y regnes som opp; headeren sier ikke det.

Samme modul brukes også av: [Automobilista 2 (direkte data)](game-automobilista-2.md), [Project CARS 2 (direkte data)](game-project-cars-2.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | ja |
| Opp-akse | `y` |
| Enheter | meter; Y regnes som opp (r3e.h sier det ikke) |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- per sjåførplass (etter overskriftens egen forskyvning og størrelse): navn, plass, målstatus, posisjon, fullførte runder, nåværende rundetid, pit lane, fart
- spillerens egne felt, bare når siden er r3e.h 3.6-layouten: bane- og løype-navn, øktype, posisjon i løpet, beste og forrige runde, hendelsespoeng, gir, gass, brems og spillerens plass
- forskyvninger utarbeidet fra Sector3s r3e.h 3.6 og kontrollert på en side bygd fra den i testene; ikke ennå mot spillet

**Tatt vare på rått**

- `r3e`: hele $R3E-minneområdet, hver lesing hvis bytes avviker fra kopien sist tatt vare på - hvert felt i r3e.h: spillerens fysikk (holdning, hastigheter, akselerasjoner, g-krefter), motor, drivstoff, dekk, bremser, skade, flagg, pit-meny, sektortider, og hver sjåførplass' hele sjåførdata (klasse, modell, lag, sektortider, avstander, straffer, dekk)
- `used` er sann for en side lest til rader; usann for en i menyene, på pause, i en repriser, av en annen layout, eller skrevet midt i (`torn` 1); `unchanged_reads` i meta.json teller lesingene som var byte for byte kopien tatt før

**Ikke tilgjengelig**

- andre sjåføres innganger og fysikk: siden gir bare spillerens egen
- andre biler' eksakte rundetider: en plass har bare sin løpende rundetid, så en runde er den siste løpende tiden sett (til ca. 0,1 s)
- spillerens egne felt på en annen layout enn 3.6: tatt vare på rått, ikke lest, før de er kontrollert

**Størrelse**: siden er 44 KB (r3e.h 3.6; minneområdet rundes opp til hele 4 KB-sider), opptil 10 ganger i sekundet mens man kjører: omtrent 1,6 GB i timen før komprimering; tomme sjåførplasser og felt som ikke endrer seg komprimeres veldig godt med zstd (ikke ennå målt på en ekte økt)

## Verifisert {#verified}

testet på en side bygd i testen fra r3e.h 3.6 (forskyvninger utarbeidet fra den offisielle headeren); ikke testet mot spillet; andre biler' rundetider er siste løpende rundetid sett (til ca. 0,1 s)

## Kilde {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
