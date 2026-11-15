---
title: "EA SPORTS WRC (živi podaci)"
nav_order: 17
lang: "hr"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (živi podaci) {#ea-sports-wrc-live-data}

Dok igrate EA SPORTS WRC, watcher sprema podatke koje sama igra šalje van, pa ih kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `ea-wrc`, vrsta [`telemetry`](sources-and-rules.md); radi dok je `WRC.exe` pokrenut i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- položaj vašeg automobila (svjetske koordinate XYZ, m) 10 puta u sekundi, s brzinom, stupnjem prijenosa, gasom, kočnicom i udaljenosti u etapi
- početak etape (kad počne štoperica etape), kraj s vremenom etape, ponovna pokretanja
- teleportacije (vraćanje na cestu): `teleport` gdje je automobil bio, `spawn` gdje je sada
- etape, najbolje vrijeme etape, udaljenost, najveća brzina

## Odakle dolaze {#where-it-comes-from}

UDP 127.0.0.1:20777, paket `session_update` zadane strukture `wrc` (Documents\My Games\WRC\telemetry\config.json); dok druga aplikacija drži 20777, watcher port prepušta njoj

## Kako ga uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` uključuje paket `session_update` u config.json (prvo se pravi sigurnosna kopija)

Naredbu upišite u terminal otvoren u mapi watchera (pogledajte [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) pokriva uobičajene uzroke.

`python -m heat3d_watch setup ea-wrc` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup ea-wrc --apply` ih mijenja, a izvornik čuva kao `<file>.heat3d-backup` (pogledajte [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `ea-wrc: changed: ...`, ili `ea-wrc: nothing to change` kad je već uključeno.

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

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC-ov `Documents/My Games/WRC/telemetry/config.json` (paket `session_update`
strukture `wrc`), DiRT-ov `hardware_settings_config.xml`
(`<udp enabled="true" extradata="3" port="20777">`), RBR-ov NGP dodatak
(`udpTelemetry=1`, port 6776). Etape po štoperici etape u igri
(`rally.StageSplitter`). RBR ne dokumentira svoje osi: os gore je ona duž koje
etapa najmanje varira, odlučuje se kad se sesija zatvori.

#### Sve što se čuva {#everything-kept}

Redaka ima nekoliko u sekundi; igre šalju mnogo više. Svaki UDP paket koji
stigne - u izbornicima, između krugova, oni koje nijedan dekoder ne čita - čuva se
cijel u sesijskoj datoteci `heat.raw.parquet` pod svojim formatom (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), a svaka stranica dijeljene memorije
(cijelo preslikavanje, ne samo bajtovi koji su dekodirani) svaki put kad se promijeni,
pod nazivom svog preslikavanja (`acpmf_physics`, ...). `used` označava što je
ujedno postalo retcima; `selfCheck.completeness` u `meta.json` broji svaku vrstu
(pravilo pretvarača 3DHeat).

Isti modul služi i: [Assetto Corsa (živi podaci)](game-assetto-corsa.md), [Assetto Corsa Competizione (živi podaci)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živi podaci)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živi podaci)](game-assetto-corsa-rally.md), [BeamNG.drive (živi podaci)](game-beamng.md), [DiRT Rally 2.0 (živi podaci)](game-dirt-rally-2.md), [Forza Horizon 4 (živi podaci)](game-forza-horizon-4.md), [Forza Horizon 5 (živi podaci)](game-forza-horizon-5.md), [Forza Horizon 6 (živi podaci)](game-forza-horizon-6.md), [Forza Motorsport (živi podaci)](game-forza-motorsport.md), [Richard Burns Rally (živi podaci)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- retci po 10 Hz: položaj, brzina, stupanj prijenosa, gas, kočnica, udaljenost u etapi, yaw, okretaji, upravljanje; početak etape, završetak s vremenom etape, ponovna pokretanja

**Čuva se sirovo**

- svaki paket koji stigne na port, cijel, po brzini igre, pod svojim formatom: `session_update` (zadana struktura `wrc`, 237 bajtova), `wrc <n>-byte` za svaki ostali paket koji konfiguracija šalje
- u paketu, osim redaka: svjetska brzina i ubrzanje, osi automobila, položaj i brzina čvorišta svakog kotača, brzina točke dodira, temperatura kočnice, kačilo, ručna kočnica, sat igre; 22 bajta (pomaci 16-36 i 40) koje nijedan objavljeni popis kanala ne imenuje

**Nije dostupno**

- drugi automobili: igra šalje samo automobil igrača
- ostale strukture i paketi koje konfiguracija telemetrije može definirati (session_start, session_end, pause): `setup` uključuje samo `session_update`; svaki ostali paket poslan na port čuva se

**Veličina**: oko 65 MB po satu pri 60 paketa u sekundi (237 bajtova plus 70-bajtno zaglavlje stavke; konfiguracijska brzina -1 šalje jedan po okviru, pa ih je više pri većoj brzini sličica); zstd zadržava djelić

## Provjereno {#verified}

dekodiranje je snimača krugova iz gamecapture-a (testirano na paketima izgrađenima prema dokumentiranim rasporedima); adapter testiran na paketima izgrađenima u testu i poslanima preko UDP-a; nije testirano na samoj igri

## Izvor {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
