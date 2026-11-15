---
title: "X-Plane (živá data)"
nav_order: 50
lang: "cs"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (živá data) {#x-plane-live-data}

Když hrajete X-Plane, Watcher ukládá data, která hra sama posílá ven, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `xplane`, druh [`telemetry`](sources-and-rules.md); běží, když je spuštěný `X-Plane.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- vlastní pozice 10krát za sekundu (zeměpisná šířka/délka/výška jako metry na východ, nahoru a na sever od prvního určení polohy; zeměpisná šířka a délka a výška uložené jako sloupce)
- natočení, indikovaná a pravá vzdušná rychlost, rychlost vůči zemi, Mach, vertikální rychlost, AoA, boční skluz, magnetický kurz, AGL, g (normální, osové, boční), rychlosti a úhlové rychlosti, klapky, vzduchové brzdy, plyn, na zemi
- hmotnosti (celková, palivo, náklad), páka podvozku, autopilot, otáčky motoru a N1, herní čas a datum, pauza, rychlost simulace, replay, venkovní teplota a tlak na hladině moře (X-Plane 12) jednou za sekundu
- vzlety, přistání, havárie, resety letu (session_start/session_end pro každý let)
- doba letu, doba ve vzduchu, vzdálenost, nejvyšší výška, nejvyšší g, přistání
- každá odpověď, kterou X-Plane pošle, celá v heat.raw.parquet

## Odkud to pochází {#where-it-comes-from}

UDP rozhraní X-Plane na 127.0.0.1:49000 (RREF datarefy a RPOS pozice, odpovídá Watcheru)

## Jak to zapnout {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 odpovídá ve výchozím nastavení)

## Jak to funguje {#how-it-works}

X-Plane 11 a 12: vlastní UDP rozhraní simulátoru na portu 49000.

X-Plane odpovídá každému, kdo se zeptá na 127.0.0.1:49000, rychlostí, o kterou se žádá,
na adresu a port, odkud žádost přišla (dokument X-Plane „Exchanging Data with
X-Plane“, dodávaný v `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS dává zeměpisnou šířku a délku jako double (RREF jen jako float, asi půl metru
od sebe), takže pohání pozici; RREF přináší zbytek a zastupuje, když RPOS nepřijde.
Datarefy (názvy jako v `Resources\plugins\DataRefs.txt` X-Plane 12,
<https://developer.x-plane.com/datarefs/>):

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

a zbytek letu ve stejné rychlosti (pravá vzdušná rychlost, vertikální rychlost, AoA,
boční skluz, magnetický kurz, Mach, osové a boční g, úhlové rychlosti, klapky,
vzduchové brzdy, plyn: `DATAREFS`), a pomalejší stav letadla jednou za sekundu
(hmotnosti, páka podvozku, autopilot, motory, herní čas, pauza a rychlost,
počasí: `SLOW_DATAREFS`). Každý datagram se také uloží celý do surové přílohy
relace a meta.json pojmenovává dataref za každým indexem RREF.

X-Plane 12 tyto zprávy přijme jen tehdy, když je v Settings > Network zapnuto „Accept incoming
connections“. Pozice se ukládají do ploché mapy kolem prvního určení polohy
v relaci (`Tangent`): x na východ, z na sever v metrech, y je výška nad hladinou moře –
takže vodorovný let zůstane vodorovný, ať je jakkoli dlouhý, což by skutečná tečná
rovina ohýbala směrem dolů s zakřivením Země. Počátek mapy je `geo` relace: meta.json
a zápatí tabulky ho nesou, takže prohlížeč může skutečný svět položit pod let.

Tento modul také obsahuje to, co sdílejí ostatní letecké simulátory: plochou mapu,
evidenci letů (vzlety, přistání, havárie, vzdálenost), socket UDP a hledání
knihoven Steamu.

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry (na východ, výška, na sever od prvního určení polohy) |
| Zrcadleno pro prohlížeč | `z` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ne**. `games --markdown` to ukazuje jako „single-player“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- RPOS (10 Hz): zeměpisná délka, šířka, výška, AGL, pitch, pravý kurz, roll, rychlost (na východ, nahoru, na jih) a úhlové rychlosti P/Q/R – vše na řádcích
- RREF (10 Hz): 27 datarefů z `DATAREFS` – pozice, natočení, IAS, rychlost vůči zemi, TAS, vertikální rychlost, AoA, boční skluz, magnetický kurz, Mach, g normální/osové/boční, úhlové rychlosti, klapky, vzduchové brzdy, plyn, AGL, havárie, na zemi, doba letu – na řádcích
- RREF (1 Hz): 20 datarefů z `SLOW_DATAREFS` – hmotnosti, páka podvozku, servo autopilotu, herní čas a datum, pauza, rychlost simulace, replay, počet motorů, otáčky motorů 1–4, N1 motorů 1–2, venkovní teplota vzduchu, tlak na hladině moře – na řádcích jako poslední přijaté

**Uchováno surové**

- každý datagram celý jako `payload`, pod svou čtyřpísmennou hlavičkou: `RREF` a `RPOS` (použito, když dotaz vytvořil řádek; v menu, bez určení polohy, žádný nevytvoří), cokoli jiného, co X-Plane pošle na port Watcheru, pod svou vlastní hlavičkou nebo `unknown`; `requests` v meta.json říká, který dataref je za každým indexem RREF, takže se payloady čtou i bez tohoto modulu

**Nedostupné**

- každý jiný dataref (X-Plane jich má tisíce): RREF posílá jen to, o co se žádá, jedno předplatné za každý; seznam žádá let, stav letadla a herní čas – víc detailů kokpitu (radia, světla, každý ukazatel motoru, poruchy) by násobilo žádosti
- jméno letadla a typ ICAO: datarefy s polem bajtů, které RREF posílá jako jeden float na každý znak
- jiná letadla (AI a více hráčů): datarefy sim/multiplayer/position nejsou vyžádány
- výstup DATA (Settings > Data Output): posílá na pevnou adresu zvolenou v simulátoru, ne tomu, kdo se zeptá; RREF a RPOS pokrývají to, co Watcher čte

**Velikost**: asi 17 MB za hodinu před zstd (RREF a RPOS 10krát za sekundu, asi 220 a 70 bajtů plus rámec každý, pomalé RREF jednou za sekundu), pokud X-Plane pošle hodnoty každého dotazu v jednom paketu, jak to dělá; zstd snižuje floaty několikanásobně

## Ověřeno {#verified}

testováno proti falešnému X-Plane, který odpovídá na RREF/RPOS podle dokumentu X-Plane 12 „Exchanging Data with X-Plane“; názvy datarefů ověřeny podle DataRefs.txt z X-Plane 12; netestováno proti běžícímu simulátoru

## Zdroj {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
