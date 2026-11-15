---
title: "Assetto Corsa Competizione (živi podaci)"
nav_order: 3
lang: "hr"
source: game-assetto-corsa-competizione.md
source_hash: "08033208b212"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa Competizione (živi podaci) {#assetto-corsa-competizione-live-data}

Dok igrate Assetto Corsa Competizione, watcher sprema podatke koje sama igra šalje, pa ih kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički detalji: adapter `assetto-corsa-competizione`, vrsta [`telemetry`](sources-and-rules.md); radi dok je `AC2-Win64-Shipping.exe` pokrenut i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- pozicija vašeg automobila (svjetske XYZ, m: sredina točaka dodira guma) 10 puta u sekundi, uz brzinu, stupanj prijenosa, gas i kočnicu
- početak i kraj sesije, sa stazom i automobilom koje igra navodi
- krugovi prema brojaču krugova u igri, s vremenom kruga; pozicija u utrci
- teleportacije (povratak u boks, ponovno pokretanje): `teleport` gdje je automobil bio, `spawn` gdje je sada
- krugovi, najbolji krug, prijeđena udaljenost, najveća brzina

## Odakle dolazi {#where-it-comes-from}

dijeljena memorija Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Kako to uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Telemetrija vlastitih igara za utrke: Forza, igre Assetto Corsa, rally igre i BeamNG, zapisane kao trase, krugovi i etape.

Svaka igra ovdje objavljuje svoju telemetriju namjerno, za nadzorne ploče i pokretne simulatore; ništa se ne ubacuje i ne čita se ono što igra ne predaje van. Dekodiranje se ne piše dvaput: to su snimači krugova iz gamecapture, u 3DHeat GameCapture u `heat3d_capture/telemetry`, kopirani u `heat3d_watch/decoders` (tamo testirani na paketima izrađenim prema objavljenim rasporedima). Ovaj modul njihove okvire pretvara u retke watchera: pozicija automobila nekoliko puta u sekundi, uz brzinu, stupanj prijenosa i pedale, događaj po krugu ili etapi te brojke koje vozač zapisuje: krugovi, najbolji krug, udaljenost i najveća brzina.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out“ UDP, uključen u postavkama HUD-a i igranja, na 127.0.0.1 port 5300, format Dash. Jedan paket po simulacijskom taktu; pomak bloka `dash` nalazi se iz samih paketa (`forza.detect_layout`). Svjetski metri, Y prema gore; svijet je lijevoruk i crta se onako kako je poslan, kao što to radi snimač krugova (dokumentacija igre „Data Out“ za Forza Motorsport i Forza Horizon).
Igra šalje na jedan port, a FH Companion i druge aplikacije „Data Out“ slušaju na istom portu. Dva programa ne mogu dijeliti taj port: na Windowsu utičnica vezana na 127.0.0.1 dobiva pakete, a onaj vezan na sve adrese na istom portu ne dobiva nijedan, bez obzira tko je prvi počeo. Zato watcher pričeka malo nakon pokretanja igre prije nego zauzme port, nikad ga ne otme aplikaciji koja ga drži i pusti ga čim druga aplikacija počne slušati na njemu. Dok drži port, svaki paket prosljeđuje nepromijenjen na 127.0.0.1:5301 - postavite polje porta u FH Companionu (kartica telemetrije) na 5301 i oboje će snimati.

#### Sve se čuva {#everything-kept}

Redaka je nekoliko u sekundi; igre šalju daleko više. Svaki UDP paket koji stigne - u izbornicima, između krugova, oni koje nijedan dekoder ne čita - čuva se cijel u `heat.raw.parquet` sesije pod svojim formatom (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Svaka stranica dijeljene memorije (cijelo preslikavanje, ne samo dekodirani bajtovi) čuva se svaki put kad se promijeni, pod imenom svog preslikavanja (`acpmf_physics`, ...). `used` označava što je postalo i retkom; `selfCheck.completeness` u `meta.json`-u broji svaku vrstu (pravilo pretvarača 3DHeat).

Isti modul služi i: [Assetto Corsa (živi podaci)](game-assetto-corsa.md), [Assetto Corsa EVO (živi podaci)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živi podaci)](game-assetto-corsa-rally.md), [BeamNG.drive (živi podaci)](game-beamng.md), [DiRT Rally 2.0 (živi podaci)](game-dirt-rally-2.md), [EA SPORTS WRC (živi podaci)](game-ea-wrc.md), [Forza Horizon 4 (živi podaci)](game-forza-horizon-4.md), [Forza Horizon 5 (živi podaci)](game-forza-horizon-5.md), [Forza Horizon 6 (živi podaci)](game-forza-horizon-6.md), [Forza Motorsport (živi podaci)](game-forza-motorsport.md), [Richard Burns Rally (živi podaci)](game-richard-burns-rally.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | da |
| Os prema gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nema |
| Mjerilo jedinice (`scale`: preglednik ovim množi pozicije) | 1 |

Ovo ide u `meta.json` (`axes`) svake sesije i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: adapter je **nikad** ne čita. Memoriju čitaju samo adapteri vrste `memory`, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` u `meta.json` svake sesije i tablica `stats` u `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- redci po 10 Hz iz stranice fizike: pozicija (sredina točaka dodira guma), brzina, mjenjač, gas, kočnica, yaw/pitch/roll (rad), rpm, upravljanje (kako ga stranica ima); početak sesije sa stazom i automobilom iz statičke stranice; krugovi, pozicija u utrci

**Čuva se sirovo**

- svaka stranica cijela - cijelo područje preslikavanja, ne samo dekodirani bajtovi - svaki put kad se njezini bajtovi promijene, pri čitanju watchera od 10 Hz: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; čitanje koje je bajt po bajt isto kao prethodno broji se u `unchanged_reads` u meta.json-u i ne sprema se ponovno
- sve dekodirano samo za datoteke krugova (`decoders/kunos.py`: klizanje, opterećenje, tlak i temperature po kotaču, kut i hod ovjesa, točke dodira, temperature kočnica, omjer i kut klizanja; brzina po svijetu i lokalna, kutna brzina, pomagala) nalazi se na tim stranicama

**Nije dostupno**

- pozicije drugih automobila: stranice opisuju samo igračev automobil (grafička stranica ACC-a u nekim verzijama ima ID-jeve i koordinate drugih automobila - čuvaju se u sirovoj stranici, ne dekodiraju se)
- takti fizike između čitanja watchera: igra prepisuje stranicu na svojoj frekvenciji fizike (do 333 Hz), a watcher čita 10 puta u sekundi

**Veličina**: oko 150-300 MB po satu prije sažimanja (područje od 4 KB po stranici, do 10 promjena u sekundi); stranice su uglavnom nule, a zstd zadržava mali dio

## Provjereno {#verified}

dekodiranje je snimača krugova iz gamecapture-a (testirano na sintetičkim stranicama); adapter testiran na dijeljenoj memoriji izrađenoj u testu prema dokumentiranom rasporedu; neprovjereno u samoj igri

## Izvor {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
