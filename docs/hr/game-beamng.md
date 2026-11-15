---
title: "BeamNG.drive (živi podaci)"
nav_order: 7
lang: "hr"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (živi podaci) {#beamngdrive-live-data}

Dok igrate BeamNG.drive, watcher sprema podatke koje sama igra šalje, pa ih kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički detalji: adapter `beamng`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `BeamNG.drive.x64.exe` ili `BeamNG.drive.exe` i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- pozicija vašeg automobila (svjetska, m, okrenuta na Y gore) 10 puta u sekundi uz brzinu, stupanj prijenosa, gas i kočnicu
- početak vožnje, ponovna postavljanja (respawn), krugovi nakon mjesta gdje je vožnja počela
- krugovi, najbolji krug, prijeđena udaljenost, najveća brzina

## Odakle dolazi {#where-it-comes-from}

UDP 127.0.0.1:4460 iz heat3d protokol-modifikacije (mods/beamng/heat3d u ovom repozitoriju)

## Kako to uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` instalira modifikaciju; zatim Options > Other > Protocols > "others"

Naredbu upišite u terminalu otvorenom u mapi watchera (vidi [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje uobičajene uzroke.

`python -m heat3d_watch setup beamng` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup beamng --apply` ih mijenja, a original čuva kao `<file>.heat3d-backup` (vidi [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `beamng: changed: ...`, ili `beamng: nothing to change` kad je već uključeno.

## Kako radi {#how-it-works}

Telemetrija vlastitih igara za utrke: Forza, igre Assetto Corsa, rally igre i BeamNG, zapisane kao trase, krugovi i etape.

Svaka igra ovdje objavljuje svoju telemetriju namjerno, za nadzorne ploče i pokretne simulatore; ništa se ne ubacuje i ne čita se ono što igra ne predaje van. Dekodiranje se ne piše dvaput: to su snimači krugova iz gamecapture, u 3DHeat GameCapture u `heat3d_capture/telemetry`, kopirani u `heat3d_watch/decoders` (tamo testirani na paketima izrađenim prema objavljenim rasporedima). Ovaj modul njihove okvire pretvara u retke watchera: pozicija automobila nekoliko puta u sekundi, uz brzinu, stupanj prijenosa i pedale, događaj po krugu ili etapi te brojke koje vozač zapisuje: krugovi, najbolji krug, udaljenost i najveća brzina.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out“ UDP, uključen u postavkama HUD-a i igranja, na 127.0.0.1 port 5300, format Dash. Jedan paket po simulacijskom taktu; pomak bloka `dash` nalazi se iz samih paketa (`forza.detect_layout`). Svjetski metri, Y prema gore; svijet je lijevoruk i crta se onako kako je poslan, kao što to radi snimač krugova (dokumentacija igre „Data Out“ za Forza Motorsport i Forza Horizon).
Igra šalje na jedan port, a FH Companion i druge aplikacije „Data Out“ slušaju na istom portu. Dva programa ne mogu dijeliti taj port: na Windowsu utičnica vezana na 127.0.0.1 dobiva pakete, a onaj vezan na sve adrese na istom portu ne dobiva nijedan, bez obzira tko je prvi počeo. Zato watcher pričeka malo nakon pokretanja igre prije nego zauzme port, nikad ga ne otme aplikaciji koja ga drži i pusti ga čim druga aplikacija počne slušati na njemu. Dok drži port, svaki paket prosljeđuje nepromijenjen na 127.0.0.1:5301 - postavite polje porta u FH Companionu (kartica telemetrije) na 5301 i oboje će snimati.

#### BeamNG.drive {#beamngdrive}

Protokol-modifikacija `heat3d` koju isporučuje gamecapture (UDP 4460, Options > Other > Protocols > "others"); Z-gore svijet BeamNG-a okrenut je na Y gore kao što to radi `beamng.py`.

#### Sve se čuva {#everything-kept}

Redaka je nekoliko u sekundi; igre šalju daleko više. Svaki UDP paket koji stigne - u izbornicima, između krugova, oni koje nijedan dekoder ne čita - čuva se cijel u `heat.raw.parquet` sesije pod svojim formatom (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Svaka stranica dijeljene memorije (cijelo preslikavanje, ne samo dekodirani bajtovi) čuva se svaki put kad se promijeni, pod imenom svog preslikavanja (`acpmf_physics`, ...). `used` označava što je postalo i retkom; `selfCheck.completeness` u `meta.json`-u broji svaku vrstu (pravilo pretvarača 3DHeat).

Isti modul služi i: [Assetto Corsa (živi podaci)](game-assetto-corsa.md), [Assetto Corsa Competizione (živi podaci)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živi podaci)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živi podaci)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (živi podaci)](game-dirt-rally-2.md), [EA SPORTS WRC (živi podaci)](game-ea-wrc.md), [Forza Horizon 4 (živi podaci)](game-forza-horizon-4.md), [Forza Horizon 5 (živi podaci)](game-forza-horizon-5.md), [Forza Horizon 6 (živi podaci)](game-forza-horizon-6.md), [Forza Motorsport (živi podaci)](game-forza-motorsport.md), [Richard Burns Rally (živi podaci)](game-richard-burns-rally.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | da |
| Os prema gore | `y` |
| Jedinice | metri (Z-gore svijet BeamNG-a okrenut oko X, kao što to radi snimač krugova) |
| Zrcaljeno za preglednik | nema |
| Mjerilo jedinice (`scale`: preglednik ovim množi pozicije) | 1 |

Ovo ide u `meta.json` (`axes`) svake sesije i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **ne**. `games --markdown` to prikazuje kao "single-player".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: adapter je **nikad** ne čita. Memoriju čitaju samo adapteri vrste `memory`, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` u `meta.json` svake sesije i tablica `stats` u `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- redci po 10 Hz: pozicija, brzina, mjenjač, gas, kočnica, yaw, rpm, upravljanje; početak vožnje, ponovna postavljanja, krugovi

**Čuva se sirovo**

- svaki paket koji stigne na port, cijel, po taktu modifikacije od 100 Hz: `H3D1` (struktura modifikacije od 160 bajtova: sat, pozicija, brzina, osi automobila, brzina zakretanja, devet ulaza, brzina površine po kotaču, rotacija, opterećenje i materijal podloge), `<n>-byte` za sve ostalo

**Nije dostupno**

- ono što modifikacija ne šalje: BeamNG nema fiksni telemetrijski paket, pa su kanali oni koje je modifikacija heat3d odabrala (ostala vozila, oštećenja, naziv karte nisu u njemu)

**Veličina**: oko 80 MB po satu prije sažimanja (100 paketa u sekundi od 160 bajtova plus zaglavlje stavke od 70 bajtova)

## Provjereno {#verified}

dekodiranje je snimača krugova iz gamecapture-a (testirano na paketima izrađenim prema strukturi modifikacije); adapter testiran na takvim paketima; modifikacija nije testirana u samoj igri

## Izvor {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
