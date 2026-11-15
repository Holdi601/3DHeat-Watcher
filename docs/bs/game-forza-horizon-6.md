---
title: "Forza Horizon 6 (podaci uživo)"
nav_order: 23
lang: "bs"
source: game-forza-horizon-6.md
source_hash: "164d188cb521"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 6 (podaci uživo) {#forza-horizon-6-live-data}

Dok igrate Forza Horizon 6, watcher sprema podatke koje igra sama šalje, da ih kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `forza-horizon-6`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `forzahorizon6.exe` i svakih 0,1 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- položaj vlastitog auta (svjetski XYZ, m) na 10 Hz, s brzinom, stepenom prijenosa, gasom, kočnicom i krugom
- početak i kraj vožnje (session_start/session_end), krugovi s vremenom kruga iz igre
- početak i cilj trke s pozicijom u trci
- teleportacije (premotavanje, brzo putovanje): `teleport` gdje je auto bio, `spawn` gdje je sada
- krugovi, najbolji krug, distanca, najveća brzina, trke

## Odakle dolazi {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (format Dash); svaki paket se nepromijenjen prosljeđuje na 127.0.0.1:5301

## Kako ga uključiti {#how-to-switch-it-on}

U igri: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, port 5300 (Motorsport: format Dash). FH Companion ili druga Data Out aplikacija: postavite njen port na 5301 - watcher prosljeđuje svaki paket; dok na 5300 sluša neka druga aplikacija, watcher joj prepušta port i ne snima ništa

## Kako radi {#how-it-works}

Vlastita telemetrija trkaćih igara: Forza, igre iz serije Assetto Corsa, rally igre
i BeamNG, bilježena kao rute, krugovi i etape.

Svaka igra ovdje namjerno objavljuje svoju telemetriju, za instrument table i
simulatore pokreta; ništa se ne ubacuje i ne čita se ništa što igra ne daje. Dekodiranje
se ne piše dvaput: to su gamecapture-ovi snimači krugova iz
`heat3d_capture/telemetry` u 3DHeat GameCapture, kopirani u `heat3d_watch/decoders` (tamo testirani na paketima izgrađenim iz
objavljenih rasporeda), a ovaj modul njihove frejmove pretvara u redove watcher-a -
položaj auta nekoliko puta u sekundi s brzinom, stepenom prijenosa i pedalama,
događaj za svaki krug ili etapu, i brojke koje vozač čuva: krugovi, najbolji krug,
distanca, najveća brzina.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, uključen u postavkama HUD-a i igre (Gameplay), prema
127.0.0.1 na port 5300, format Dash. Jedan paket po koraku simulacije; pomak
dash bloka nalazi se iz paketa (`forza.detect_layout`). Svjetski
metri, Y gore; svijet je lijevoruki i crta se onako kako je poslan, kao što to
radi snimač krugova (dokumentacija "Data Out" za Forza Motorsport i Forza Horizon).
Igra šalje na jedan port, a FH Companion i druge Data Out aplikacije slušaju
na istom. Dva programa ga ne mogu dijeliti: na Windowsu utičnica vezana
na 127.0.0.1 dobija pakete, a ona vezana na sve adrese na istom
portu ne dobija ništa, bez obzira ko je prvi. Zato watcher nakon pokretanja igre
malo pričeka prije nego uzme port, nikad ga ne uzima aplikaciji koja
ga drži, i pušta ga čim neka druga aplikacija počne slušati na njemu.
Dok drži port, svaki paket prosljeđuje nepromijenjen na
127.0.0.1:5301 - postavite polje za port u FH Companion-u (njegov tab telemetrije) na 5301 i
oboje snimaju.

#### Sve se čuva {#everything-kept}

Redova je nekoliko u sekundi; igre šalju mnogo više. Svaki UDP paket koji
stigne - u menijima, između krugova, i oni koje nijedan dekoder ne čita - čuva se cijel
u `heat.raw.parquet` sesije pod svojim formatom (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), a svaka stranica dijeljene memorije
(cijelo mapiranje, ne samo dekodirani bajtovi) pri svakoj promjeni, pod
imenom svog mapiranja (`acpmf_physics`, ...). `used` označava šta je također postalo
redovi; `selfCheck.completeness` u `meta.json` broji svaku vrstu (3DHeat-ovo
pravilo konvertera).

Isti modul služi i za: [Assetto Corsa (podaci uživo)](game-assetto-corsa.md), [Assetto Corsa Competizione (podaci uživo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (podaci uživo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (podaci uživo)](game-assetto-corsa-rally.md), [BeamNG.drive (podaci uživo)](game-beamng.md), [DiRT Rally 2.0 (podaci uživo)](game-dirt-rally-2.md), [EA SPORTS WRC (podaci uživo)](game-ea-wrc.md), [Forza Horizon 4 (podaci uživo)](game-forza-horizon-4.md), [Forza Horizon 5 (podaci uživo)](game-forza-horizon-5.md), [Forza Motorsport (podaci uživo)](game-forza-motorsport.md), [Richard Burns Rally (podaci uživo)](game-richard-burns-rally.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | metri; Forzin svijet je lijevoruki, crta se onako kako je poslan, kao što to radi snimač krugova |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljenu memoriju koju igra objavljuje), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- redovi na 10 Hz: položaj, brzina, stepen prijenosa, gas, kočnica, krug, yaw/pitch/roll (rad), rpm, upravljač (-1..1); session_start s rednim brojem auta, klasom, PI i pogonom; krugovi s vremenom kruga iz igre; pozicija u trci

**Čuva se sirovo**

- svaki paket koji stigne na port, cijel, brzinom igre (jedan po koraku simulacije), pod svojim formatom: `dash-horizon` (324 bajta, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: habanje guma i id staze), `sled` (232, bez položaja), `<n>-byte` za sve ostalo - uključujući pakete menija (isRaceOn 0), pakete zadržane dok se raspored dasha ne dokaže, i ~13 bajta paketa Horizon koje nijedan objavljeni raspored ne imenuje
- svaki kanal točkova iz Sled bloka (omjer proklizavanja, ugao proklizavanja, kombinovano proklizavanje, ovjes, brzina točka, rumble, lokva), ubrzanja, ugaona brzina, snaga, obrtni moment, boost, gorivo, temperature guma, kvačilo, ručna kočnica, linija vožnje, razlika kočenja AI-ja: sve je u paketima, a `decoders/fulllap.decode_full` ih iz njih dekodira

**Nije dostupno**

- drugi auti: Data Out opisuje samo igračev auto
- ime staze ili rute: Forza Horizon ga nikad ne šalje; Motorsport 2023 šalje samo broj staze
- paketi dok UDP 5300 drži neka druga aplikacija (FH Companion): watcher joj prepušta port

**Veličina**: oko 85 MB na sat prije kompresije (60 paketa u sekundi od 324 bajta plus zaglavlje stavke od 70 bajta); uzastopni paketi se malo razlikuju, pa zstd zadržava mali dio

## Provjereno {#verified}

dekodiranje je ono iz gamecapture-ovog snimača krugova (testirano na paketima izgrađenim iz rasporeda Data Out); adapter testiran na sintetičkim paketima i na snimljenim putanjama krugova puštenim kao paketi; nije testirano na samoj igri

## Izvor {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
