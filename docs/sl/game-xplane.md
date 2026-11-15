---
title: "X-Plane (živi podatki)"
nav_order: 50
lang: "sl"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (živi podatki) {#x-plane-live-data}

Medtem ko igrate X-Plane, watcher shrani podatke, ki jih igra sama pošilja, da jih lahko kasneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `xplane`, vrsta [`telemetry`](sources-and-rules.md); teče, ko je `X-Plane.exe` zagnan, in išče nove podatke vsakih 0,1 s.*

## Kaj se zapiše {#what-is-recorded}

- lasten položaj na 10 Hz (zemljepisna širina/dolžina/višina kot metri vzhodno/gor/severno od prvega zajema; lat/lon/alt shranjeni kot stolpci)
- odnos, indicirana in prava zračna hitrost, hitrost nad tlemi, Mach, navpična hitrost, AoA, zdrs, magnetni kurz, AGL, g (normalni, osni, stranski), hitrosti in vrtenja, zakrilca, zračne zavore, plin, na tleh
- teže (skupna, gorivo, tovor), ročica podvozja, avtopilot, vrtljaji motorja in N1, simulacijski čas in datum, pavza, hitrost simulacije, ponovitev, zunanja temperatura in tlak na morski gladini (X-Plane 12) enkrat na sekundo
- vzleti, pristanki, trki, ponastavitve leta (session_start/session_end za vsak let)
- čas letenja, čas v zraku, razdalja, najvišja višina, najvišji g, pristanki
- vsak odgovor, ki ga X-Plane pošlje, cel v heat.raw.parquet

## Od kod prihaja {#where-it-comes-from}

UDP vmesnik X-Plane na 127.0.0.1:49000 (RREF datarefs in RPOS položaj, odgovorjeno watcherju)

## Kako vklopiti {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 odgovarja privzeto)

## Kako deluje {#how-it-works}

X-Plane 11 in 12: simulatorjev lasten UDP vmesnik na vratih 49000.

X-Plane odgovori vsakomur, ki vpraša na 127.0.0.1:49000, s zahtevano hitrostjo, na naslov in vrata, od koder je prišla zahteva (dokument X-Plane "Exchanging Data with X-Plane", priložen v `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS daje zemljepisno širino in dolžino kot dvojne vrednosti (RREF samo kot floate, pol metra narazen), zato nosi položaj; RREF prinese ostalo in nadomesti, kadar RPOS ne pride. Datarefs (imena kot v X-Planu 12 `Resources\plugins\DataRefs.txt`, <https://developer.x-plane.com/datarefs/>):

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

in preostanek leta z isto hitrostjo (prava zračna hitrost, navpična hitrost, AoA, zdrs, magnetni kurz, Mach, osni in stranski g, vrtenja, zakrilca, zračne zavore, plin: `DATAREFS`), s počasnejšim stanjem letala enkrat na sekundo (teže, ročica podvozja, servi avtopilota, motorji, simulacijski čas, pavza in hitrost, vreme: `SLOW_DATAREFS`). Vsak datagram se shrani cel v surovem spremljevalnem zapisu seje, meta.json pa navaja dataref za vsak indeks RREF.

X-Plane 12 to sprejme samo, ko je Settings > Network > "Accept incoming connections" vklopljen. Položaji gredo v ravni zemljevid okoli prvega zajema seje (`Tangent`): x vzhod, z sever v metrih, y višina nad morsko gladino - tako raven let ostane raven, ne glede na to, kako daleč gre, kar bi prava tangentna ravnina ukrivila navzdol z Zemljo. Izhodišče karte je `geo` seje: meta.json in noga tabele ju nosita, da lahko pregledovalnik pravi svet postavi pod let.

Ta modul vsebuje tudi, kar si delijo ostali leteči simulatorji: ravni zemljevid, knjigovodstvo leta (vzleti, pristanki, trki, razdalja), UDP vtičnico in seznam knjižnice Steam.

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | da |
| Navpična os | `y` |
| Enote | metri (vzhod, višina, sever od prvega zajema) |
| Zrcaljeno za pregledovalnik | `z` |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **ne**. `games --markdown` to prikaže kot "enoigralska".
- Vrsta `telemetry`: bere samo to, kar igra ali platforma ponudi (vrata UDP ali skupni pomnilnik, ki ga igra objavi), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- RPOS (10 Hz): zemljepisna dolžina, širina, višina, AGL, nagib, pravi kurz, zvitje, hitrost (vzhod, gor, jug) in vrtenja P/Q/R - vse na vrsticah
- RREF (10 Hz): 27 datarefs iz `DATAREFS` - položaj, odnos, IAS, hitrost nad tlemi, TAS, navpična hitrost, AoA, zdrs, magnetni kurz, Mach, g normalni/osni/stranski, vrtenja, zakrilca, zračne zavore, plin, AGL, trk, na tleh, čas letenja - na vrsticah
- RREF (1 Hz): 20 datarefs iz `SLOW_DATAREFS` - teže, ročica podvozja, servi avtopilota, simulacijski čas in datum, pavza, hitrost simulacije, ponovitev, število motorjev, vrtljaji motorjev 1-4, N1 motorjev 1-2, zunanja temperatura zraka, tlak na morski gladini - na vrsticah, kot zadnjič prejete

**Shranjeno surovo**

- vsak datagram cel kot `payload`, pod svojo štiričrkovno glavo: `RREF` in `RPOS` (uporabljeno, kadar je anketa ustvarila vrstico; v menijih, brez položaja, ne ustvarita nobene), vse drugo, kar X-Plane pošlje na vrata watcherja, pod svojo glavo ali `unknown`; `requests` v meta.json pove, kateri dataref je za vsak indeks RREF, da se koristne obremenitve berejo brez tega modula

**Ni na voljo**

- vsak drug dataref (X-Plane jih ima tisoče): RREF pošlje samo, kar je zahtevano, po ena naročnina za vsakega; seznam zahteva let, stanje letala in simulacijski čas - več podrobnosti kokpita (radia, lučke, vsak merilnik motorja, okvare) bi pomnožilo zahteve
- ime letala in ICAO tip: datarefs z nizom bajtov, ki jih RREF pošlje kot en float na znak
- drugi letalniki (AI in več igralcev): datarefs sim/multiplayer/position niso zahtevani
- izhod DATA (Settings > Data Output): pošilja na fiksen naslov, izbran v simulatorju, ne tistemu, ki vpraša; RREF in RPOS pokrijeta, kar watcher bere

**Velikost**: približno 17 MB na uro pred zstd (RREF in RPOS na 10 Hz, okoli 220 in 70 bajtov plus okvir vsak, počasni RREF enkrat na sekundo), če X-Plane pošlje vrednosti vsake ankete v enem paketu, kot to naredi; zstd zmanjša floate večkrat

## Preverjeno {#verified}

preizkušeno proti lažnemu X-Planu, ki odgovarja na RREF/RPOS po dokumentu 'Exchanging Data with X-Plane' iz X-Plane 12; imena datarefs preverjena z DataRefs.txt iz X-Plane 12; še nepreizkušeno s tekočim simulatorjem

## Vir {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
