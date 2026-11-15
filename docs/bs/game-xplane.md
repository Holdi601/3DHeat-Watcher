---
title: "X-Plane (podaci uživo)"
nav_order: 50
lang: "bs"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (podaci uživo) {#x-plane-live-data}

Dok igrate X-Plane, watcher sprema podatke koje igra sama šalje, da ih kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `xplane`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `X-Plane.exe` i svakih 0,1 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- vlastiti položaj na 10 Hz (geografska širina/dužina/visina kao metri istok/gore/sjever od prve tačke; lat/lon/alt čuvaju se kao kolone)
- položaj aviona u prostoru, indicirana i prava brzina zraka, brzina u odnosu na tlo, Mach, vertikalna brzina, AoA, bočno klizanje, magnetni kurs, AGL, g (normalno, aksijalno, bočno), brzine kretanja i rotacije, zakrilca, kočnice zraka, gas, na tlu
- mase (ukupna, gorivo, teret), ručica stajnog trapa, autopilot, broj okretaja motora i N1, vrijeme i datum simulatora, pauza, brzina simulacije, replay, vanjska temperatura i pritisak na nivou mora (X-Plane 12) jednom u sekundi
- polijetanja, slijetanja, padovi, resetiranja leta (session_start/session_end po letu)
- vrijeme leta, vrijeme u zraku, distanca, najveća visina, najveći g, slijetanja
- svaki odgovor koji X-Plane pošalje čuva se cijel u heat.raw.parquet

## Odakle dolazi {#where-it-comes-from}

UDP sučelje X-Plane-a na 127.0.0.1:49000 (RREF datarefs i RPOS položaj, odgovara se watcher-u)

## Kako ga uključiti {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 odgovara po zadanom)

## Kako radi {#how-it-works}

X-Plane 11 i 12: vlastito UDP sučelje simulatora na portu 49000.

X-Plane odgovara svakome ko pita na 127.0.0.1:49000, brzinom koja se traži, na
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

RPOS daje geografsku širinu i dužinu kao double (RREF samo kao float, pola metra
razmaka), pa on vodi položaj; RREF donosi ostalo i priskače kad
RPOS ne stiže. Datarefs (nazivi kao u `Resources\plugins\DataRefs.txt` iz X-Plane-a 12,
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

i ostatak leta istom brzinom (prava brzina zraka, vertikalna brzina, AoA,
bočno klizanje, magnetni kurs, Mach, aksijalni i bočni g, brzine rotacije, zakrilca,
kočnice zraka, gas: `DATAREFS`), uz sporije stanje aviona jednom u
sekundi (mase, ručica stajnog trapa, autopilot, motori, vrijeme simulatora, pauza i
brzina, vrijeme: `SLOW_DATAREFS`). Svaki datagram se također čuva cijel u
sirovom sidecar-u sesije, a meta.json imenuje dataref iza svakog RREF indeksa.
X-Plane 12 ih prihvata samo kad je uključeno Settings > Network > "Accept incoming
connections". Položaji idu u ravnu mapu oko prve tačke sesije
(`Tangent`): x istok, z sjever u metrima, y je visina iznad nivoa mora - pa
horizontalan let ostaje horizontalan koliko god daleko ide, a pravu tangencijalnu ravan
bi zakrivljenost Zemlje savila prema dolje. Ishodište mape je `geo` sesije: meta.json
i podnožje tabele ga nose, pa preglednik može podmetnuti stvarni svijet ispod
leta.

Ovaj modul sadrži i ono što dijele ostali simulatori leta: ravnu mapu,
vođenje leta (polijetanja, slijetanja, padovi, distanca), UDP socket i
popis Steam biblioteka.

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | metri (istok, visina, sjever od prve tačke) |
| Zrcaljeno za preglednik | `z` |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **ne**. `games --markdown` to prikazuje kao "single-player".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljenu memoriju koju igra objavljuje), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- RPOS (10 Hz): geografska dužina, širina, nadmorska visina, AGL, pitch, pravi kurs, roll, brzina (istok, gore, jug) i brzine rotacije P/Q/R - sve na redovima
- RREF (10 Hz): 27 datarefs iz `DATAREFS` - položaj, položaj aviona u prostoru, IAS, brzina u odnosu na tlo, TAS, vertikalna brzina, AoA, bočno klizanje, magnetni kurs, Mach, g normalno/aksijalno/bočno, brzine rotacije, zakrilca, kočnice zraka, gas, AGL, pad, na tlu, vrijeme leta - na redovima
- RREF (1 Hz): 20 datarefs iz `SLOW_DATAREFS` - mase, ručica stajnog trapa, servoi autopilota, vrijeme i datum simulatora, pauza, brzina simulacije, replay, broj motora, broj okretaja motora 1-4, N1 motora 1-2, vanjska temperatura zraka, pritisak na nivou mora - na redovima kako su zadnji put primljeni

**Čuva se sirovo**

- svaki datagram cijel kao `payload`, pod svojim zaglavljem od četiri slova: `RREF` i `RPOS` (used kad je upit dao red; u menijima, bez fiksa, ne daju nijedan), sve drugo što X-Plane pošalje na watcher-ov port pod svojim zaglavljem ili `unknown`; `requests` u meta.json kaže koji je dataref svaki RREF indeks, pa se payloadi čitaju i bez ovog modula

**Nije dostupno**

- svaki drugi dataref (X-Plane ih ima hiljade): RREF šalje samo ono što se traži, po jedna pretplata; popis traži let, stanje aviona i vrijeme simulatora - više detalja kokpita (radiji, svjetla, mjerači svakog motora, kvarovi) umnožilo bi zahtjeve
- ime aviona i njegov ICAO tip: datarefs kao nizovi bajtova, koje RREF šalje kao po jedan float za svaki znak
- drugi avioni (AI i multiplayer): datarefs sim/multiplayer/position nisu traženi
- izlaz DATA (Settings > Data Output): šalje na fiksnu adresu odabranu u simulatoru, a ne onome ko pita; RREF i RPOS pokrivaju ono što watcher čita

**Veličina**: oko 17 MB na sat prije zstd (RREF i RPOS na 10 Hz, oko 220 i 70 bajta plus okvir svaki, spori RREF jednom u sekundi), ako X-Plane šalje vrijednosti svakog upita u jednom paketu kao što to radi; zstd smanjuje floatove nekoliko puta

## Provjereno {#verified}

testirano na lažnom X-Plane-u koji odgovara na RREF/RPOS prema dokumentu 'Exchanging Data with X-Plane' iz X-Plane-a 12; nazivi datarefs provjereni prema DataRefs.txt iz X-Plane-a 12; nije testirano na pokrenutom simulatoru

## Izvor {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
