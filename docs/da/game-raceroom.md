---
title: "RaceRoom Racing Experience (live-data)"
nav_order: 37
lang: "da"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (live-data) {#raceroom-racing-experience-live-data}

Mens du spiller RaceRoom Racing Experience, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `raceroom`, type [`telemetry`](sources-and-rules.md); den kører, mens `RRRE64.exe` eller `RRRE.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- hver bils position (verdens XYZ, m) 10 gange i sekundet pr. kørernavn, egen bil markeret, med hastighed og løbsplacering; egen gear, gas, bremse
- kørslens start med banen, spillet angiver; runder pr. bil med rundetid; mål; egne depotstop
- teleportering (tilbage til depotet, en genstart): `teleport` der hvor bilen var, `spawn` der hvor den er nu
- egne runder, bedste runde, løbsplacering, distance, topfart
- spillets hele side med delt hukommelse i `heat.raw.parquet`, hver gang den ændrer sig
- egne hændelsespoint

## Hvor data kommer fra {#where-it-comes-from}

delt hukommelse $R3E (Sector3's r3e.h, version 3)

## Sådan slår du det til {#how-to-switch-it-on}

Der skal ikke slås noget til: watcheren læser kilden, som spillet eller platformen udleverer den.

## Sådan virker det {#how-it-works}

Delt hukommelse, som racingspil udgiver til dashboards, åbnet skrivebeskyttet - og
aldrig oprettet.

Flere simulatorer udleverer deres telemetri som en navngivet Windows-filmapning, som
spillet opretter, og som alle må læse: Kunos' `Local\acpmf_*`-sider (Assetto Corsa,
ACC, AC Rally, AC EVO's `Local\acevo_pmf_*`), iRacings
`Local\IRSDKMemMapFileName`, RaceRooms `$R3E`, Automobilista 2 / Project CARS 2's
`$pcars2$`.

Hvorfor ikke `mmap.mmap(-1, size, tagname=...)`, den sædvanlige måde i Python: når
mappingen ikke findes endnu, *opretter* den en - her skrivebeskyttet. Et spil, der
starter bagefter, åbner watcherens mapping i stedet for at lave sin egen og
kan så ikke skrive til den, så dets telemetri er død, indtil watcheren giver slip.
Watcheren starter en adapter, så snart spillets proces dukker op, og det er
præcis det øjeblik, hvor spillet endnu ikke har lavet sin mapping. Derfor åbnes der med
`OpenFileMappingW`, som kun finder en eksisterende mapping, mappes med
`FILE_MAP_READ`, og ellers meldes "ikke der endnu"; adapterne prøver igen et øjeblik senere.

Intet her kan skrive: visningen er mappet skrivebeskyttet og kopieres kun ud af med
`ctypes.string_at`.

To spil læses også her; hver bil på banen er på deres sider.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3's `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
version 3.6), `#pragma pack(1)`. Headeren angiver, hvor kørerdataene starter
og hvor store de er (`all_drivers_offset`, `driver_data_size`), så den pr.-fører-del -
navn, plads, placering, verdensposition (float x y z, m), gennemførte runder, aktuel rundetid,
målstatus, depotbane, hastighed - læses ud fra dem. Spillerens egne felter (bedste og forrige
runde, løbsplacering, hændelsespoint, gear, pedaler, bane- og layoutnavne) læses
på deres 3.6-forskydninger kun, når `all_drivers_offset` er den 2008, layoutet placerer den på.
Y tages som op; headeren siger det ikke.

Det samme modul bruges også af: [Automobilista 2 (live-data)](game-automobilista-2.md), [Project CARS 2 (live-data)](game-project-cars-2.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | meter; Y op antaget (r3e.h siger det ikke) |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser det som "tilladt (læser kun det spillet udgiver)".
- Type `telemetry`: den læser kun det spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- pr. førerplads (ud fra headerens egen forskydning og størrelse): navn, plads, målstatus, placering, verdensposition, gennemførte runder, aktuel rundetid, depotbane, hastighed
- spillerens egne felter, kun når siden har r3e.h 3.6-layoutet: bane- og layoutnavne, sessionstype, løbsplacering, bedste og forrige runde, hændelsespoint, gear, gas, bremse, spillerens plads
- forskydninger udledt af Sector3's r3e.h 3.6 og kontrolleret på en side bygget ud fra den i testene; endnu ikke mod spillet

**Gemt råt**

- `r3e`: hele $R3E-mappingen, hver læsning hvis bytes afviger fra den kopi, der sidst blev gemt - hvert felt i r3e.h: spillerens fysik (orientering, hastigheder, accelerationer, g-kræfter), motor, brændstof, dæk, bremser, skader, flag, depotmenu, sektortider, hver førerplads' hele førerdata (klasse, model, hold, sektortider, mellemrum, straffe, dæk)
- `used` er sand for en side læst til rækker; falsk for en i menuerne, på pause, i et replay, af et andet layout, eller fanget midt i en skrivning (`torn` 1); `unchanged_reads` i meta.json tæller de læsninger, der var byte for byte den kopi, der var gemt før

**Ikke tilgængeligt**

- andre kørere's input og fysik: siden giver kun spillerens egen
- andre bilers præcise rundetider: en plads har kun sin løbende rundetid, så en runde er den sidste løbende tid, der er set (ned til cirka 0,1 s)
- spillerens egne felter på et andet layout end 3.6: gemt råt, ikke læst, før de er kontrolleret

**Størrelse**: siden er 44 KB (r3e.h 3.6; mappingen rundes op til hele 4 KB-sider), op til 10 gange i sekundet under kørsel: cirka 1,6 GB i timen før komprimering; tomme førerpladser og uændrede felter komprimerer meget godt med zstd (endnu ikke målt på en rigtig kørsel)

## Verificeret {#verified}

testet på en side bygget i testen ud fra r3e.h 3.6 (forskydningerne udledt af den officielle header); ikke testet mod spillet; andre bilers rundetider er den sidste løbende rundetid, der er set (ned til cirka 0,1 s)

## Kilde {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
