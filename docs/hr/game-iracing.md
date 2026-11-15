---
title: "iRacing (živi podaci)"
nav_order: 28
lang: "hr"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (živi podaci) {#iracing-live-data}

Dok igrate iRacing, watcher sprema podatke koje sama igra šalje van, pa ih kasnije možete pogledati kao statistiku i vremensku crtu.

*Tehnički podaci: adapter `iracing`, vrsta [`telemetry`](sources-and-rules.md); radi dok su `iRacingSim64DX11.exe` ili `iRacingSim64.exe` pokrenuti i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- vožnja 5 puta u sekundi bez položaja (iRacing ga ne daje uživo): brzina, stupanj prijenosa, gas, kočnica, krug, udio kruga, pozicija u utrci i u klasi, incidenti
- početak sesije, ulazak i izlazak iz automobila, ulazak i izlazak iz boksa, krugovi s vremenom kruga, incidenti s bodovima, karirana zastava, cilj
- datoteke telemetrije .ibt zapisane tijekom sesije (geografska širina, dužina, visina - preglednik ih čita)
- krugovi, najbolji krug, incidenti, pozicija u utrci, zaustavljanja u boksu, udaljenost, najveća brzina
- cijela dijeljena memorija u `heat.raw.parquet`: zaglavlje, zaglavlja varijabli, podaci o sesiji, svaki redak telemetrije koji je pročitan

## Odakle dolaze {#where-it-comes-from}

dijeljena memorija Local\IRSDKMemMapFileName (iRacing SDK); datoteke .ibt u %USERPROFILE%\Documents\iRacing\telemetry

## Kako ga uključiti {#how-to-switch-it-on}

Za podatke uživo ništa ne treba. Za položaje: snimajte telemetriju u automobilu (Alt+L) ili postavite irsdkLog=1 u app.ini

## Kako radi {#how-it-works}

iRacing, uživo: SDK-ova dijeljena memorija iRacinga, čita se izvorno.

iRacing objavljuje svoju telemetriju za aplikacije u imenovanom preslikavanju datoteke,
`Local\IRSDKMemMapFileName`, koje simulator stvara dok radi (i signalizira
`Local\IRSDKDataValidEvent` pri svakom ažuriranju, što ovdje nije potrebno: watcher
gleda deset puta u sekundi). Raspored je iz `irsdk_defines.h` SDK-a, a slijedi ga
i pyirsdk (MIT) - ovdje ponovno zapisan prema tim činjenicama:

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

Simulator piše `numBuf` redaka kružno; najnoviji je onaj s najvećim tickCount,
a redak se ponovno uzima ako se njegov tickCount pomaknuo dok je bio kopiran.

Podaci uživo nemaju svjetski položaj - geografska širina, dužina i visina postoje
samo u datotekama `.ibt` koje iRacing bilježi u `Documents\iRacing\telemetry`
(Alt+L u automobilu ili `irsdkLog=1`), a preglednik 3DHeat ih čita sam. Zato se
vožnja bilježi kao događaji bez koordinata - brzina, krug, udio kruga, pozicija
u utrci, incidenti - uz krugove, incidente, zaustavljanja u boksu i kariranu zastavu,
a na kraju datoteke `.ibt` zapisane tijekom sesije kao događaji `telemetry_file`,
koje preglednik otvara.

Uz retke čuva se cijela mapa memorije, u sirovoj pomoćnoj datoteci sesije
(`heat.raw.parquet`): fiksni dio zaglavlja (`header`, svaki put kad se promijeni),
zaglavlja varijabli (`var_headers`, cijela, i kao JSON u `text`, svaki put kad se
raspored promijeni), YAML podataka o sesiji (`session_info`, njegov tekst svaki put
kad se brojač `sessionInfoUpdate` pomakne) i najnoviji redak telemetrije
(`telemetry`, svaka varijabla iz njega, pri svakom čitanju koje nađe novi tick).
Zaglavlja varijabli i jedan redak sve su što kasniji dekoder treba da pročita bilo
koju varijablu.

Izvor: iRacing SDK (irsdk_defines.h, dokumentacija "iRacing SDK" na forumu);
kutu/pyirsdk (MIT) za potvrdu pomaka.

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Os gore | `y` |
| Jedinice | nema položaja uživo; datoteke .ibt nose geografsku širinu/dužinu/visinu |
| Zrcaljenje za preglednik | nema |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma predaje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- iz najnovijeg retka telemetrije: vrijeme sesije, broj, stanje i ID, na stazi, reprizi, krug, završeni krugovi, udio i metri kruga, zadnji i najbolji krug, brzina, stupanj prijenosa, gas, kočnica, okretaji, cesta u boksu, podloga staze, pozicija u utrci i u klasi, vlastiti broj incidenata (retci `driving` 5 puta u sekundi i događaji)
- sada i na retcima `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (stupnjevi, iz radijana simulatora - samo kad zaglavlje varijable navodi jedinicu rad), `fuel_l` (jedinica l), `lat_accel` i `lon_accel` (jedinica m/s^2)
- iz YAML-a podataka o sesiji: indeks igračeva automobila, staza i konfiguracija, vrste sesija, ime, automobil, tim i broj svakog vozača (retci session_start, meta.json)
- provjereno na bloku izgrađenom iz irsdk_defines.h u testovima; još nije provjereno na simulatoru

**Čuva se sirovo**

- `telemetry`: najnoviji redak cijel, svaka varijabla koju simulator objavljuje (nizovi CarIdx svakog automobila, gume, ovjes, nizovi visoke frekvencije `_ST` tamo gdje ih simulator ima ...), pri svakom čitanju koje nađe novi tick; `tick` je brojač ticka simulatora; `used` je netočno dok se replay reproducira
- `var_headers`: zaglavlja varijabli cijela (144 bajta svako) i, u `text`, kao JSON (naziv, tip, pomak, broj, jedinica, opis), pri svakoj promjeni rasporeda - dovoljno za čitanje svake varijable svakog sačuvanog retka
- `session_info`: YAML tekst cijel svaki put kad se njegov brojač ažuriranja pomakne (vikend, sesije i rezultati, vozači, postavke automobila, radio, popisi kamera), `update` je brojač
- `header`: zaglavlje od 112 bajta cijelo svaki put kad se promijeni (verzija, stanje, brzina ticka, pomaci, tickovi redaka)

**Nije dostupno**

- svjetski položaj uživo: dijeljena memorija ga nema; geografska širina, dužina i visina postoje samo u datotekama .ibt (kad je snimanje uključeno), koje čita preglednik - watcher imenuje one zapisane tijekom sesije
- tickovi između dva čitanja: simulator piše 60 redaka u sekundi u 3 ili 4 utora, a watcher čita 10 puta u sekundi, pa je većina ticka prepisana prije nego što se može pročitati; datoteka .ibt ima svaki tick kad je snimanje uključeno

**Veličina**: redak telemetrije je nekoliko KB (oko 5 do 10 KB sa svim nizovima svakog automobila), čuva se do 10 puta u sekundi, plus zaglavlje (112 bajta) jednako često i YAML podataka o sesiji (desetke KB) kad se promijeni: oko 0,2 do 0,4 GB po satu na stazi prije sažimanja; zstd ga svodi na djelić (još nije izmjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na bloku dijeljene memorije izgrađenom u testu prema rasporedu irsdk; nije testirano na simulatoru

## Izvor {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
