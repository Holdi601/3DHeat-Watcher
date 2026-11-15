---
title: "EA SPORTS WRC (podaci uživo)"
nav_order: 17
lang: "bs"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (podaci uživo) {#ea-sports-wrc-live-data}

Dok igrate EA SPORTS WRC, watcher sprema podatke koje igra sama šalje, da ih kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `ea-wrc`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `WRC.exe` i svakih 0,1 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- položaj vlastitog auta (svjetski XYZ, m) na 10 Hz, s brzinom, stepenom prijenosa, gasom, kočnicom i distancom etape
- početak etape (kad krene sat etape), cilj s vremenom etape, restarti
- teleportacije (vraćanje na cestu): `teleport` gdje je auto bio, `spawn` gdje je sada
- etape, najbolje vrijeme etape, distanca, najveća brzina

## Odakle dolazi {#where-it-comes-from}

UDP 127.0.0.1:20777, paket session_update zadane strukture `wrc` (Documents\My Games\WRC\telemetry\config.json); dok port 20777 drži neka druga aplikacija, watcher joj ga prepušta

## Kako ga uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` uključuje paket session_update u config.json (prvo se pravi sigurnosna kopija)

Upišite komandu u terminal otvoren u folderu watcher-a (vidite [Prije nego počnete](before-you-start.md)). Ako ne uspije, zadnji red kaže zašto; [Instalacija i pokretanje](installing-and-running.md) pokriva uobičajene uzroke.

`python -m heat3d_watch setup ea-wrc` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup ea-wrc --apply` ih mijenja, a original čuva kao `<file>.heat3d-backup` (vidite [Komande](commands.md#setup)). Ispisuje `ea-wrc: changed: ...` za svaku promjenu, ili `ea-wrc: nothing to change` kad je već uključeno.

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

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC-ov `Documents/My Games/WRC/telemetry/config.json` (paket `session_update`
strukture `wrc`), DiRT-ov `hardware_settings_config.xml`
(`<udp enabled="true" extradata="3" port="20777">`), RBR-ov NGP dodatak
(`udpTelemetry=1`, port 6776). Etape prema satu etape u igri
(`rally.StageSplitter`). RBR ne dokumentira svoje ose: osa gore je
ona duž koje se etapa najmanje mijenja, odlučuje se kad se sesija zatvori.

#### Sve se čuva {#everything-kept}

Redova je nekoliko u sekundi; igre šalju mnogo više. Svaki UDP paket koji
stigne - u menijima, između krugova, i oni koje nijedan dekoder ne čita - čuva se cijel
u `heat.raw.parquet` sesije pod svojim formatom (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), a svaka stranica dijeljene memorije
(cijelo mapiranje, ne samo dekodirani bajtovi) pri svakoj promjeni, pod
imenom svog mapiranja (`acpmf_physics`, ...). `used` označava šta je također postalo
redovi; `selfCheck.completeness` u `meta.json` broji svaku vrstu (3DHeat-ovo
pravilo konvertera).

Isti modul služi i za: [Assetto Corsa (podaci uživo)](game-assetto-corsa.md), [Assetto Corsa Competizione (podaci uživo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (podaci uživo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (podaci uživo)](game-assetto-corsa-rally.md), [BeamNG.drive (podaci uživo)](game-beamng.md), [DiRT Rally 2.0 (podaci uživo)](game-dirt-rally-2.md), [Forza Horizon 4 (podaci uživo)](game-forza-horizon-4.md), [Forza Horizon 5 (podaci uživo)](game-forza-horizon-5.md), [Forza Horizon 6 (podaci uživo)](game-forza-horizon-6.md), [Forza Motorsport (podaci uživo)](game-forza-motorsport.md), [Richard Burns Rally (podaci uživo)](game-richard-burns-rally.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljenu memoriju koju igra objavljuje), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- redovi na 10 Hz: položaj, brzina, stepen prijenosa, gas, kočnica, distanca etape, yaw, rpm, upravljač; početak etape, cilj s vremenom etape, restarti

**Čuva se sirovo**

- svaki paket koji stigne na port, cijel, brzinom igre, pod svojim formatom: `session_update` (zadana struktura `wrc`, 237 bajta), `wrc <n>-byte` za svaki drugi paket koji config šalje
- u paketu povrh redova: svjetska brzina i ubrzanje, ose auta, po točku položaj i brzina glavčine, brzina tačke kontakta, temperatura kočnice, kvačilo, ručna kočnica, sat igre; 22 bajta (pomaci 16-36 i 40) koje nijedan objavljeni popis kanala ne imenuje

**Nije dostupno**

- drugi auti: igre šalju samo igračev auto
- druge strukture i paketi koje telemetrijski config može definirati (session_start, session_end, pause): `setup` uključuje samo `session_update`; svaki drugi paket poslan na port se čuva

**Veličina**: oko 65 MB na sat pri 60 paketa u sekundi (237 bajta plus zaglavlje stavke od 70 bajta; stopa -1 u config-u šalje jedan po frejmu, dakle više pri većem broju frejmova); zstd zadržava mali dio

## Provjereno {#verified}

dekodiranje je ono iz gamecapture-ovog snimača krugova (testirano na paketima izgrađenim iz dokumentiranih rasporeda); adapter testiran na paketima izgrađenim u testu i poslanim preko UDP-a; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
