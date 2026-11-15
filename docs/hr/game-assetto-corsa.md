---
title: "Assetto Corsa (živi podaci)"
nav_order: 2
lang: "hr"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (živi podaci) {#assetto-corsa-live-data}

Dok igrate Assetto Corsa, watcher sprema podatke koje sama igra šalje van, pa ih kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `assetto-corsa`, vrsta [`telemetry`](sources-and-rules.md); radi dok su `acs.exe` ili `acs_x86.exe` pokrenuti i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- položaj vašeg automobila (svjetske koordinate XYZ, m: srednja vrijednost točaka dodira guma) 10 puta u sekundi, s brzinom, stupnjem prijenosa, gasom i kočnicom
- početak i kraj sesije s nazivom staze i automobila koje igra navodi
- krugovi prema brojaču kruga u igri, s njegovim vremenom
- teleportacije (povratak u boks, ponovno pokretanje): `teleport` gdje je automobil bio, `spawn` gdje je sada
- krugovi, najbolji krug, udaljenost, najveća brzina

## Odakle dolaze {#where-it-comes-from}

dijeljena memorija Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

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

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Dijeljena memorija koju igra piše za aplikacije: `Local\acpmf_physics`,
`Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`).
Otvara se samo za čitanje i tek kad je igra napravi (`simracing_shm`). Položaj
je srednja vrijednost četiriju točaka dodira guma, svjetski metri, Y gore.
Krugovi prema brojaču igre (AC, ACC) ili prolaskom početne točke ponovno
(AC EVO, AC Rally), kao što to radi `kunos.py` za snimač krugova.

#### Sve što se čuva {#everything-kept}

Redaka ima nekoliko u sekundi; igre šalju mnogo više. Svaki UDP paket koji
stigne - u izbornicima, između krugova, oni koje nijedan dekoder ne čita - čuva se
cijel u sesijskoj datoteci `heat.raw.parquet` pod svojim formatom (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), a svaka stranica dijeljene memorije
(cijelo preslikavanje, ne samo bajtovi koji su dekodirani) svaki put kad se promijeni,
pod nazivom svog preslikavanja (`acpmf_physics`, ...). `used` označava što je
ujedno postalo retcima; `selfCheck.completeness` u `meta.json` broji svaku vrstu
(pravilo pretvarača 3DHeat).

Isti modul služi i: [Assetto Corsa Competizione (živi podaci)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živi podaci)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živi podaci)](game-assetto-corsa-rally.md), [BeamNG.drive (živi podaci)](game-beamng.md), [DiRT Rally 2.0 (živi podaci)](game-dirt-rally-2.md), [EA SPORTS WRC (živi podaci)](game-ea-wrc.md), [Forza Horizon 4 (živi podaci)](game-forza-horizon-4.md), [Forza Horizon 5 (živi podaci)](game-forza-horizon-5.md), [Forza Horizon 6 (živi podaci)](game-forza-horizon-6.md), [Forza Motorsport (živi podaci)](game-forza-motorsport.md), [Richard Burns Rally (živi podaci)](game-richard-burns-rally.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os gore | `y` |
| Jedinice | metri |
| Zrcaljenje za preglednik | nema |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma predaje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- retci po 10 Hz sa stranice fizike: položaj (srednja vrijednost točaka dodira guma), brzina, stupanj prijenosa, gas, kočnica, yaw/pitch/roll (rad), okretaji, upravljanje (kako ga stranica ima); početak sesije sa stazom i automobilom sa statične stranice; krugovi, pozicija u utrci

**Čuva se sirovo**

- svaka stranica cijela - cijelo preslikano područje, ne samo dekodirani bajtovi - svaki put kad se njeni bajtovi promijene, pri čitanju watchera od 10 Hz: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; ponovno čitanje koje je bajt po bajt isto kao prošlo broji se u `unchanged_reads` u meta.json-u, a ne sprema se ponovno
- sve dekodirano samo za datoteke krugova (`decoders/kunos.py`: klizanje, opterećenje, tlak i temperature svakog kotača, kut, ovjes, točke dodira, temperature kočnica, omjer i kut klizanja; brzina svjetska i lokalna, kutna brzina, pomoćna sredstva) nalazi se na tim stranicama

**Nije dostupno**

- položaji drugih automobila: stranice opisuju samo automobil igrača (ACC-ova grafička stranica u nekim verzijama ima ID-e automobila i koordinate za ostale - čuvaju se u sirovoj stranici, ne dekodiraju se)
- fizički ticovi između watcherovih čitanja: igra piše stranicu svojom fizičkom brzinom (do 333 Hz), a watcher čita 10 puta u sekundi

**Veličina**: oko 150-300 MB po satu prije sažimanja (područje od 4 KB po stranici, do 10 promjena u sekundi); stranice su uglavnom nule, a zstd zadržava mali dio

## Provjereno {#verified}

dekodiranje je snimača krugova iz gamecapture-a (testirano na sintetičkim stranicama); adapter testiran na dijeljenoj memoriji izgrađenoj u testu prema dokumentiranom rasporedu; nije testirano na samoj igri

## Izvor {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
