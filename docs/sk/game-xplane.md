---
title: "X-Plane (živé dáta)"
nav_order: 50
lang: "sk"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (živé dáta) {#x-plane-live-data}

Počas hry X-Plane watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `xplane`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `X-Plane.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- vlastná poloha 10-krát za sekundu (zemepisná šírka/dĺžka/výška ako metre na východ/nahor/na sever od prvého zamerania; šírka, dĺžka a výška uchované ako stĺpce)
- postoj, indikovaná a pravá vzdušná rýchlosť, zemná rýchlosť, Mach, vertikálna rýchlosť, AoA, bočný sklz, magnetický kurz, AGL, g (normálové, osové, bočné), rýchlosti a rotácie, klapky, brzdové klapky, plyn, na zemi
- hmotnosti (celková, palivo, náklad), páka podvozku, autopilot, otáčky motora a N1, herný čas a dátum, pauza, rýchlosť simulácie, replay, vonkajšia teplota a tlak na hladine mora (X-Plane 12) raz za sekundu
- vzlety, pristátia, havárie, resety letu (session_start/session_end pre každý let)
- čas letu, čas vo vzduchu, vzdialenosť, najvyššia výška, najvyššie g, pristátia
- každá odpoveď, ktorú X-Plane pošle, celá v heat.raw.parquet

## Odkiaľ to berie {#where-it-comes-from}

UDP rozhranie X-Plane na 127.0.0.1:49000 (RREF dátové referencie a RPOS poloha, na ktoré odpovedá watcher)

## Ako to zapnúť {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 odpovedá predvolene)

## Ako to funguje {#how-it-works}

X-Plane 11 a 12: vlastné UDP rozhranie simulátora na porte 49000.

X-Plane odpovedá každému, kto sa pýta na 127.0.0.1:49000, rýchlosťou, akú si vypýta, na adresu a port, z ktorých prišla žiadosť (dokument X-Plane „Exchanging Data with X-Plane", dodávaný v `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS dáva zemepisnú šírku a dĺžku ako double, RREF len ako float (pol metra od seba), takže poháňa polohu; RREF prináša zvyšok a nahrádza RPOS, keď RPOS nepríde. Dátové referencie (názvy ako v `Resources\plugins\DataRefs.txt` X-Plane 12, <https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

a zvyšok letu rovnakou rýchlosťou (pravá vzdušná rýchlosť, vertikálna rýchlosť, AoA, bočný sklz, magnetický kurz, Mach, osové a bočné g, rýchlosti rotácie, klapky, brzdové klapky, plyn: `DATAREFS`), so stavom pomalšieho lietadla raz za sekundu (hmotnosti, páka podvozku, autopilot, motory, čas simulácie, pauza a rýchlosť, počasie: `SLOW_DATAREFS`). Každý datagram sa uchová celý v surovom sprievodnom súbore relácie a meta.json pomenúva dátovú referenciu za každým indexom RREF.

X-Plane 12 tieto odpovede prijíma len so zapnutým Settings > Network > „Accept incoming connections". Polohy idú do plochej mapy okolo prvého zamerania relácie (`Tangent`): x na východ, z na sever v metroch, y výška nad hladinou mora - takže rovný let zostane rovný, nech je akokoľvek dlhý, čo by pravá tangenciálna rovina ohla smerom dole so Zemou. Počiatok mapy je `geo` relácie: meta.json a päta tabuľky ho nesú, takže prehliadač vie položiť skutočný svet pod let.

Tento modul zdieľajú aj ďalšie letové simulátory: plochú mapu, účtovanie letov (vzlety, pristátia, havárie, vzdialenosť), UDP soket a zoznam knižnice Steam.

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Osa nahor | `y` |
| Jednotky | metre (na východ, výška, na sever od prvého zamerania) |
| Zrkadlenie pre prehliadač | `z` |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **nie**. `games --markdown` to zobrazí ako „jednohráčová".
- Druh `telemetry`: číta len to, čo hra alebo platforma sprístupňuje (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- RPOS (10 Hz): zemepisná dĺžka, šírka, výška, AGL, pitch, pravý kurz, roll, rýchlosť (východ, nahor, juh) a rotácie P/Q/R - všetko na riadkoch
- RREF (10 Hz): 27 dátových referencií `DATAREFS` - poloha, postoj, IAS, zemná rýchlosť, TAS, vertikálna rýchlosť, AoA, bočný sklz, magnetický kurz, Mach, g normálové/osové/bočné, rýchlosti rotácie, klapky, brzdové klapky, plyn, AGL, havária, na zemi, čas letu - na riadkoch
- RREF (1 Hz): 20 dátových referencií `SLOW_DATAREFS` - hmotnosti, páka podvozku, servá autopilota, čas a dátum simulácie, pauza, rýchlosť simulácie, replay, počet motorov, otáčky motorov 1-4, N1 motorov 1-2, vonkajšia teplota vzduchu, tlak na hladine mora - na riadkoch tak, ako boli naposledy prijaté

**Uchované surové**

- každý datagram celý ako `payload`, pod svojou štvorpísmenovou hlavičkou: `RREF` a `RPOS` (použité, keď dotaz vytvoril riadok; v menu, bez zamerania, riadok nevytvoria), čokoľvek iné, čo X-Plane pošle na port watchera, pod svojou hlavičkou alebo ako `unknown`; `requests` v meta.json hovorí, ktorá dátová referencia je za každým indexom RREF, takže payloady sa čítajú aj bez tohto modulu

**Nie je k dispozícii**

- každá iná dátová referencia (X-Plane ich má tisíce): RREF posiela len to, o čo sa pýtate, jedno predplatné naraz; zoznam sa pýta na let, stav lietadla a čas simulácie - viac detailov kokpitu (rádiá, svetlá, každý ukazovateľ motora, poruchy) by násobilo žiadosti
- názov lietadla a ICAO typ: dátové referencie typu bajtové pole, ktoré RREF posiela po jednom float na znak
- iné lietadlá (AI a multiplayer): dátové referencie sim/multiplayer/position nie sú vyžiadané
- výstup DATA (Settings > Data Output): posiela na pevnú adresu zvolenú v simulátore, nie tomu, kto sa pýta; RREF a RPOS pokrývajú to, čo watcher číta

**Veľkosť**: približne 17 MB za hodinu pred zstd (RREF a RPOS 10-krát za sekundu, okolo 220 a 70 bajtov plus rámec každý, pomalý RREF raz za sekundu), ak X-Plane pošle hodnoty každej odpovede v jednom pakete, ako to robí; zstd zmenší floaty niekoľkonásobne

## Overené {#verified}

overené na falošnom X-Plane, ktorý odpovedal na RREF/RPOS podľa „Exchanging Data with X-Plane" z X-Plane 12; názvy dátových referencií overené podľa DataRefs.txt z X-Plane 12; nevyskúšané na bežiacom simulátore

## Zdroj {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
