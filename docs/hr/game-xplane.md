---
title: "X-Plane (živi podaci)"
nav_order: 50
lang: "hr"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (živi podaci) {#x-plane-live-data}

Dok igrate X-Plane, watcher sprema podatke koje sama igra šalje van, pa ih kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `xplane`, vrsta [`telemetry`](sources-and-rules.md); radi dok je `X-Plane.exe` pokrenut i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- vlastiti položaj 10 puta u sekundi (geografska širina/dužina/visina kao metri istok/gore/sjever od prve točke; geografska širina, dužina i visina kao stupci)
- stav, indicirana i stvarna zračna brzina, put nad tlom, Mach, vertikalna brzina, AoA, klizanje, magnetski kurs, AGL, g (normalni, uzdužni, bočni), brzine i kutne brzine, zakrilci, aerokočnice, gas, na tlu
- težine (ukupna, gorivo, teret), ručica stajnog trapa, autopilot, broj okretaja motora i N1, vrijeme i datum simulacije, pauza, brzina simulacije, repriza, vanjska temperatura i tlak na razini mora (X-Plane 12) jednom u sekundi
- polijetanja, slijetanja, padovi, poništavanja leta (session_start/session_end po letu)
- vrijeme leta, vrijeme u zraku, udaljenost, najveća visina, najveći g, slijetanja
- svaki odgovor koji X-Plane pošalje cijel u heat.raw.parquet

## Odakle dolaze {#where-it-comes-from}

UDP sučelje X-Plane-a na 127.0.0.1:49000 (RREF datarefi i RPOS položaj, odgovara watcheru)

## Kako ga uključiti {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 odgovara zadano)

## Kako radi {#how-it-works}

X-Plane 11 i 12: vlastito UDP sučelje simulatora na portu 49000.

X-Plane odgovara svakome tko pita na 127.0.0.1:49000, pri traženoj brzini, na
adresu i port s kojih je zahtjev stigao (dokument X-Plane-a "Exchanging Data with
X-Plane", isporučen u `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS daje geografsku širinu i dužinu kao double-ove, pa on pokreće položaj; RREF
donosi ostalo i zamjenjuje ga kad RPOS ne dođe (RREF ima samo floatove, pola metra
međusobno). Datarefi (nazivi kao u X-Plane 12 `Resources\plugins\DataRefs.txt`,
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

a ostatak leta istom brzinom (stvarna zračna brzina, vertikalna brzina, AoA,
klizanje, magnetski kurs, Mach, uzdužni i bočni g, kutne brzine, zakrilci,
aerokočnice, gas: `DATAREFS`), uz sporije stanje letjelice jednom u sekundi
(težine, ručica stajnog trapa, servo autopilota, motori, vrijeme simulacije, pauza i
brzina, vrijeme: `SLOW_DATAREFS`). Svaki datagram čuva se cijel u sesijskoj sirovoj
pomoćnoj datoteci, a meta.json navodi koji dataref stoji iza svakog RREF indeksa.

X-Plane 12 prihvaća ovo samo uz Settings > Network > "Accept incoming connections"
uključeno. Položaji idu u ravnu kartu oko prvog položaja sesije (`Tangent`): x istok,
z sjever u metrima, y visina iznad srednje razine mora - pa ravan let ostaje ravan
koliko god bio dug, dok bi se stvarna tangencijalna ravnina s Zemljom savijala prema dolje. Ishodište karte je `geo` sesije: meta.json i podnožje tablice ga nose, pa
preglednik može položiti stvarni svijet ispod leta.

Ovaj modul također sadrži ono što dijele ostali letački simulatori: ravnu kartu,
evidenciju leta (polijetanja, slijetanja, padovi, udaljenost), UDP utičnicu i
popis Steam biblioteke.

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os gore | `y` |
| Jedinice | metri (istok, visina, sjever od prve točke) |
| Zrcaljenje za preglednik | `z` |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **ne**. `games --markdown` to prikazuje kao "jedan igrač".
- Vrsta `telemetry`: čita samo ono što igra ili platforma predaje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- RPOS (10 Hz): geografska dužina, širina, visina, AGL, pitch, pravi kurs, roll, brzina (istok, gore, jug) i kutne brzine P/Q/R - sve na retcima
- RREF (10 Hz): 27 datarefa iz `DATAREFS` - položaj, stav, IAS, put nad tlom, TAS, vertikalna brzina, AoA, klizanje, magnetski kurs, Mach, g normalni/uzdužni/bočni, kutne brzine, zakrilci, aerokočnice, gas, AGL, pad, na tlu, vrijeme leta - na retcima
- RREF (1 Hz): 20 datarefa iz `SLOW_DATAREFS` - težine, ručica stajnog trapa, servo autopilota, vrijeme i datum simulacije, pauza, brzina simulacije, repriza, broj motora, okretaji motora 1-4, N1 motora 1-2, vanjska temperatura zraka, tlak na razini mora - na retcima kako su zadnji put stigli

**Čuva se sirovo**

- svaki datagram cijel kao `payload`, pod svojim četveroslovnim zaglavljem: `RREF` i `RPOS` (korišteni kad je očitavanje napravilo redak; u izbornicima, bez položaja, ne naprave ništa), sve drugo što X-Plane šalje watcherovom portu pod vlastitim zaglavljem ili `unknown`; `requests` u meta.json kaže koji je dataref svaki RREF indeks, pa se odgovori čitaju i bez ovog modula

**Nije dostupno**

- svaki ostali dataref (X-Plane ih ima tisuće): RREF šalje samo ono što se traži, jednu pretplatu po stavci; popis traži let, stanje letjelice i vrijeme simulacije - više detalja kabine (radiji, svjetla, svaki pokazivač motora, kvarovi) višestruko bi povećalo zahtjeve
- ime letjelice i ICAO tip: datarefi s nizom bajtova, koje RREF šalje kao jedan float po znaku
- drugi zrakoplovi (AI i više igrača): datarefi sim/multiplayer/position nisu traženi
- izlaz DATA (Settings > Data Output): šalje na fiksnu adresu odabranu u simulatoru, ne onome tko pita; RREF i RPOS pokrivaju ono što watcher čita

**Veličina**: oko 17 MB po satu prije zstd-a (RREF i RPOS 10 Hz, oko 220 i 70 bajtova plus okvir svaki, spori RREF jednom u sekundi), ako X-Plane šalje vrijednosti svakog očitavanja u jednom paketu kao što to radi; zstd smanjuje floatove nekoliko puta

## Provjereno {#verified}

testirano na lažnom X-Plane-u koji odgovara na RREF/RPOS prema 'Exchanging Data with X-Plane' iz X-Plane 12; nazivi datarefa provjereni prema DataRefs.txt iz X-Plane 12; nije testirano na pokrenutom simulatoru

## Izvor {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
