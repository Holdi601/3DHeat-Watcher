---
title: "Forza Horizon 5 (živi podaci)"
nav_order: 22
lang: "hr"
source: game-forza-horizon-5.md
source_hash: "0083724478e7"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 5 (živi podaci) {#forza-horizon-5-live-data}

Dok igrate Forza Horizon 5, watcher sprema podatke koje sama igra šalje van, pa ih kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `forza-horizon-5`, vrsta [`telemetry`](sources-and-rules.md); radi dok je `ForzaHorizon5.exe` pokrenut i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- položaj vašeg automobila (svjetske koordinate XYZ, m) 10 puta u sekundi, s brzinom, stupnjem prijenosa, gasom, kočnicom i krugom
- početak i kraj vožnje (session_start/session_end), krugovi s vremenom kruga iz igre
- početak i završetak utrke s pozicijom u utrci
- teleportacije (premotavanje, brzo putovanje): `teleport` gdje je automobil bio, `spawn` gdje je sada
- krugovi, najbolji krug, udaljenost, najveća brzina, utrke

## Odakle dolaze {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (format Dash); svaki paket prosljeđuje se nepromijenjen na 127.0.0.1:5301

## Kako ga uključiti {#how-to-switch-it-on}

U igri: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, port 5300 (Motorsport: format Dash). FH Companion ili druga aplikacija Data Out: postavite njezin port na 5301 - watcher prosljeđuje svaki paket; dok druga aplikacija sluša na 5300, watcher port prepušta njoj i ništa ne bilježi

## Kako radi {#how-it-works}

Vlastita telemetrija utrka: Forza, igre Assetto Corsa, rally igre i BeamNG, snimljene kao putanje, krugovi i etape.

Svaka igra ovdje namjerno objavljuje svoju telemetriju, za nadzorne ploče i upravljačke uređaje za pokret; ništa se ne ubacuje i ne čita se ono što igra ne predaje. Dekodiranje se ne piše dvaput: to su snimači krugova iz gamecapture-a u 3DHeat GameCapture `heat3d_capture/telemetry`, kopirani u `heat3d_watch/decoders` (tamo testirani na paketima izgrađenima prema objavljenim rasporedima), a ovaj modul pretvara njihove okvire u retke watchera - položaj automobila nekoliko puta u sekundi s njegovom brzinom, stupnjem prijenosa i pedalama, događaj po krugu ili etapi, te brojke koje vozač zadržava: krugove, najbolji krug, udaljenost i najveću brzinu.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, uključen u HUD i postavkama igre (Gameplay), na
127.0.0.1 port 5300, format Dash. Jedan paket po simulacijskom taktu; pomak
bloka dash-a pronalazi se iz paketa (`forza.detect_layout`). Svjetski
metri, Y gore; svijet je lijevorukan i crta se onako kako dolazi, kao što to
radi snimač krugova (dokumentacija Forza Motorsport i Forza Horizon "Data Out").
Igra šalje na jedan port, a FH Companion i druge aplikacije Data Out slušaju
na istom. Dva programa ne mogu dijeliti taj port: na Windowsu utičnica vezana
na 127.0.0.1 dobiva pakete, a ona vezana na sve adrese na istom portu ne dobiva
nijedan, bez obzira na to koja je prva. Zato watcher pričeka malo nakon što
igra krene prije nego što zauzme port, nikad ga ne otima aplikaciji koja ga drži,
i odmah ga ustupa čim druga aplikacija počne slušati na njemu. Dok drži port,
svaki paket prosljeđuje nepromijenjen na 127.0.0.1:5301 - postavite polje porta
u FH Companionu (njegova kartica telemetrije) na 5301 i oba će snimati.

#### Sve što se čuva {#everything-kept}

Redaka ima nekoliko u sekundi; igre šalju mnogo više. Svaki UDP paket koji
stigne - u izbornicima, između krugova, oni koje nijedan dekoder ne čita - čuva se
cijel u sesijskoj datoteci `heat.raw.parquet` pod svojim formatom (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), a svaka stranica dijeljene memorije
(cijelo preslikavanje, ne samo bajtovi koji su dekodirani) svaki put kad se promijeni,
pod nazivom svog preslikavanja (`acpmf_physics`, ...). `used` označava što je
ujedno postalo retcima; `selfCheck.completeness` u `meta.json` broji svaku vrstu
(pravilo pretvarača 3DHeat).

Isti modul služi i: [Assetto Corsa (živi podaci)](game-assetto-corsa.md), [Assetto Corsa Competizione (živi podaci)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živi podaci)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živi podaci)](game-assetto-corsa-rally.md), [BeamNG.drive (živi podaci)](game-beamng.md), [DiRT Rally 2.0 (živi podaci)](game-dirt-rally-2.md), [EA SPORTS WRC (živi podaci)](game-ea-wrc.md), [Forza Horizon 4 (živi podaci)](game-forza-horizon-4.md), [Forza Horizon 6 (živi podaci)](game-forza-horizon-6.md), [Forza Motorsport (živi podaci)](game-forza-motorsport.md), [Richard Burns Rally (živi podaci)](game-richard-burns-rally.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os gore | `y` |
| Jedinice | metri; Forzin svijet je lijevorukan, crta se onako kako dolazi, kao što to radi snimač krugova |
| Zrcaljenje za preglednik | nema |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma predaje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- retci po 10 Hz: položaj, brzina, stupanj prijenosa, gas, kočnica, krug, yaw/pitch/roll (rad), okretaji, upravljanje (-1..1); session_start s rednim brojem automobila, klasom, PI-jem i pogonom; krugovi s vremenom kruga iz igre; pozicija u utrci

**Čuva se sirovo**

- svaki paket koji stigne na port, cijel, po brzini igre (jedan po simulacijskom taktu), pod svojim formatom: `dash-horizon` (324 bajta, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: habanje guma i ID staze), `sled` (232, bez položaja), `<n>-byte` za sve ostalo - uključujući pakete izbornika (isRaceOn 0), pakete zadržane dok se raspored dash-a ne potvrdi, i ~13 bajta paketa Horizon koje nijedan objavljeni raspored ne imenuje
- svaki kanal kotača bloka Sled (koeficijent klizanja, kut klizanja, kombinirano klizanje, ovjes, brzina kotača, rumble, puddle), ubrzanja, kutna brzina, snaga, moment, pojačanje, gorivo, temperature guma, kačilo, ručna kočnica, linija vožnje, razlika kočenja AI-ja: sve je u paketima, a dekodira ih `decoders/fulllap.decode_full`

**Nije dostupno**

- drugi automobili: Data Out opisuje samo automobil igrača
- naziv staze ili rute: Forza Horizon ih nikad ne šalje; Motorsport 2023 šalje samo broj staze
- paketi dok druga aplikacija (FH Companion) drži UDP 5300: watcher port prepušta njoj

**Veličina**: oko 85 MB po satu prije sažimanja (60 paketa u sekundi od 324 bajta plus 70-bajtno zaglavlje stavke); uzastopni paketi se malo razlikuju, pa zstd zadržava djelić

## Provjereno {#verified}

dekodiranje je snimača krugova iz gamecapture-a (testirano na paketima izgrađenima prema rasporedu Data Out); adapter testiran na sintetičkim paketima i na snimljenim putanjama krugova puštenim kao paketi; nije testirano na samoj igri

## Izvor {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
