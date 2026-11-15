---
title: "iRacing (podaci uživo)"
nav_order: 28
lang: "bs"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (podaci uživo) {#iracing-live-data}

Dok igrate iRacing, watcher sprema podatke koje igra sama šalje, da ih kasnije možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `iracing`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `iRacingSim64DX11.exe` ili `iRacingSim64.exe` i svakih 0,1 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- vožnja na 5 Hz bez položaja (iRacing ga uživo ne daje): brzina, stepen prijenosa, gas, kočnica, krug, udio kruga, pozicija u trci i u klasi, incidenti
- početak sesije, ulazak u auto i izlazak iz njega, ulazak u pit lane i izlazak iz njega, krugovi s vremenom kruga, incidenti s bodovima, kockasta zastava, cilj
- .ibt telemetrijske datoteke zapisane tokom vožnje (geografska širina, dužina, visina - preglednik ih čita)
- krugovi, najbolji krug, incidenti, pozicija u trci, zaustavljanja u boksu, distanca, najveća brzina
- cijela dijeljena memorija u `heat.raw.parquet`: zaglavlje, zaglavlja varijabli, informacije o sesiji, svaki pročitani telemetrijski red

## Odakle dolazi {#where-it-comes-from}

dijeljena memorija Local\IRSDKMemMapFileName (iRacing SDK); .ibt datoteke u %USERPROFILE%\Documents\iRacing\telemetry

## Kako ga uključiti {#how-to-switch-it-on}

Ništa za podatke uživo. Za položaje: uključite bilježenje telemetrije u autu (Alt+L) ili postavite irsdkLog=1 u app.ini

## Kako radi {#how-it-works}

iRacing, uživo: dijeljena memorija iRacing SDK-a, čita se izvorno.

iRacing objavljuje svoju telemetriju za aplikacije u imenovanom mapiranju datoteke,
`Local\IRSDKMemMapFileName`, koje simulator pravi dok radi (a pri svakom ažuriranju signalizira
`Local\IRSDKDataValidEvent`, što ovdje nije potrebno: watcher
gleda deset puta u sekundi). Raspored je onaj iz SDK-ovog `irsdk_defines.h`,
koji slijedi i pyirsdk (MIT) - ovdje ponovo napisan iz tih činjenica:

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

Simulator piše `numBuf` redova kružno; najnoviji je onaj s najvećim
tickCount, a red se uzima ponovo ako se njegov tickCount promijenio dok
se kopirao.

Podaci uživo nemaju svjetski položaj - geografska širina, dužina i visina nalaze se samo u
`.ibt` datotekama koje iRacing bilježi u `Documents\iRacing\telemetry` (Alt+L u
autu, ili `irsdkLog=1`), a preglednik 3DHeat ih čita sam. Zato ovo bilježi
vožnju kao događaje bez koordinata - brzina, krug, završeni udio kruga,
pozicija u trci, incidenti - plus krugove, incidente, zaustavljanja u boksu i
kockastu zastavu, a na kraju `.ibt` datoteke zapisane tokom vožnje kao
događaje `telemetry_file`, da ih preglednik otvori.

Pored redova čuva se cijela memorijska mapa, u sirovom sidecar-u sesije
(`heat.raw.parquet`): fiksni dio zaglavlja (`header`, svaki put kad se
promijeni), zaglavlja varijabli (`var_headers`, cijela, i kao JSON u `text`,
svaki put kad se raspored promijeni), YAML s informacijama o sesiji (`session_info`, njegov
tekst svaki put kad se `sessionInfoUpdate` pomakne) i najnoviji telemetrijski red
(`telemetry`, svaka njegova varijabla, pri svakom čitanju koje nađe novi tick). Zaglavlja
varijabli i jedan red sve su što kasnijem dekoderu treba da pročita bilo koju varijablu.

Izvor: iRacing SDK (irsdk_defines.h, dokumentacija na forumu "iRacing SDK");
kutu/pyirsdk (MIT) za potvrdu pomaka.

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Osa gore | `y` |
| Jedinice | nema položaja uživo; .ibt datoteke nose geografsku širinu/dužinu/visinu |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljenu memoriju koju igra objavljuje), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- iz najnovijeg telemetrijskog reda: vrijeme sesije, broj, stanje i id, na stazi, replay, krug, završeni krugovi, udio i metri kruga, zadnji i najbolji krug, brzina, stepen prijenosa, gas, kočnica, RPM, pit road, površina staze, pozicija u trci i klasi, vlastiti broj incidenata (redovi `driving` na 5 Hz i događaji)
- sada i na redovima `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (stepeni, iz radijana simulatora - samo kad zaglavlje varijable daje jedinicu kao rad), `fuel_l` (jedinica l), `lat_accel` i `lon_accel` (jedinica m/s^2)
- iz YAML-a s informacijama o sesiji: indeks igračevog auta, staza i konfiguracija, vrste sesija, ime, auto, tim i broj svakog vozača (redovi session_start, meta.json)
- provjereno prema bloku izgrađenom iz irsdk_defines.h u testovima; još ne prema simulatoru

**Čuva se sirovo**

- `telemetry`: najnoviji red cijel, svaka varijabla koju simulator objavljuje (CarIdx nizovi svakog auta, gume, ovjes, `_ST` nizovi visoke frekvencije gdje ih simulator ima ...), pri svakom čitanju koje nađe novi tick; `tick` je brojač tickova simulatora; `used` je false dok se reproducira replay
- `var_headers`: zaglavlja varijabli cijela (po 144 bajta) i, u `text`, kao JSON (name, type, offset, count, unit, description), svaki put kad se raspored promijeni - dovoljno da se pročita svaka varijabla svakog sačuvanog reda
- `session_info`: YAML tekst cijel svaki put kad se njegov brojač ažuriranja pomakne (vikend, sesije i rezultati, vozači, setup auta, radio, popisi kamera), `update` je brojač
- `header`: irsdk zaglavlje od 112 bajta cijelo svaki put kad se promijeni (verzija, status, tick rate, pomaci, tickovi redova)

**Nije dostupno**

- svjetski položaj uživo: dijeljena memorija ga nema; geografska širina, dužina i visina nalaze se samo u .ibt datotekama (uz uključeno bilježenje), koje preglednik čita - watcher imenuje one zapisane tokom vožnje
- tickovi između dva čitanja: simulator piše 60 redova u sekundi u 3 ili 4 slota, a watcher čita 10 puta u sekundi, pa je većina tickova prepisana prije nego što je mogla biti pročitana; .ibt datoteka ima svaki tick kad je bilježenje uključeno

**Veličina**: telemetrijski red je nekoliko KB (oko 5 do 10 KB sa nizovima svakog auta), čuva se do 10 puta u sekundi, plus zaglavlje (112 bajta) jednako često i YAML s informacijama o sesiji (desetine KB) kad se promijeni: oko 0,2 do 0,4 GB na sat na stazi prije kompresije; zstd to svodi na mali dio (još nije izmjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na bloku dijeljene memorije izgrađenom u testu iz irsdk rasporeda; nije testirano na simulatoru

## Izvor {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
