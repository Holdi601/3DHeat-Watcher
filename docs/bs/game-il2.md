---
title: "IL-2 Sturmovik: Great Battles (podaci uživo)"
nav_order: 26
lang: "bs"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (podaci uživo) {#il-2-sturmovik-great-battles-live-data}

Dok igrate IL-2 Sturmovik: Great Battles, watcher sprema podatke koje igra sama šalje, da ih kasnije možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `il2`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `Il-2.exe` ili `IL2Series.exe` i svakih 0,1 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- naleti (sortie): uzeti avion (spawn) i kad izlaz stane (session_end) - bez svjetskog položaja: igra ga ne šalje
- ispuštene bombe i lansirane rakete (masa), pogoci i primljena šteta, eksplozije, rafali iz oružja - položaji lokalni u odnosu na avion
- ekvivalentna brzina zraka, AGL, vertikalna brzina, g, broj okretaja motora jednom u sekundi, sa svakim drugim indikatorom koji paket nosi (pritisak u usisnoj grani, podrhtavanje motora, stanje i pritisak stajnog trapa, AoA, bočno klizanje, ubrzanje x/y/z, podrhtavanje kokpita, zakrilca, kočnice zraka)
- naleti, ispaljeni meci, bombe, rakete, primljeni pogoci, najveća brzina, najveći g, vrijeme leta; naziv servera i ime pilota online
- svaki telemetrijski paket čuva se cijel u heat.raw.parquet

## Odakle dolazi {#where-it-comes-from}

UDP telemetrijski izlaz igre na 127.0.0.1:41995 ([KEY = telemetrydevice] u &lt;game>\data\startup.cfg)

## Kako ga uključiti {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (dodaje addrN = "127.0.0.1:41995", enable = true), ponovo pokrenite IL-2

Upišite komandu u terminal otvoren u folderu watcher-a (vidite [Prije nego počnete](before-you-start.md)). Ako ne uspije, zadnji red kaže zašto; [Instalacija i pokretanje](installing-and-running.md) pokriva uobičajene uzroke.

`python -m heat3d_watch setup il2` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup il2 --apply` ih mijenja, a original čuva kao `<file>.heat3d-backup` (vidite [Komande](commands.md#setup)). Ispisuje `il2: changed: ...` za svaku promjenu, ili `il2: nothing to change` kad je već uključeno.

## Kako radi {#how-it-works}

IL-2 Sturmovik: Great Battles - UDP telemetrijski izlaz igre i njene vlastite Tacview snimke.

1. Telemetrija ("Telemetry output of IL2 v4.003", revizija 1.2, isporučuje se kao
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Uključuje se u
   `<game>\data\startup.cfg`, sekcija `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:port]" (više odredišta odjednom), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` dodaje jedno odredište, 127.0.0.1:41995 (JoyPro koristi
   41994, zadani port igre je 4322), i uključuje izlaz. Paketi,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indikatori: 0 ENG_RPM, 1 ENG_MP, 2/3 podrhtavanje motora, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz uključujući gravitaciju),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Događaji (pakovani na 2 bajta): 0 SET_FOCUS (STRING: bajt
   dužine + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB i 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT i 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Položaji događaja su lokalni u odnosu na igračev avion; tok
   uopće nema svjetski položaj - dakle ovo su događaji i brojke, ne putanja.

2. Tacview snimka: `tacviewrecord = 1` u `[KEY = track_record]` tjera
   igru da piše `<game>\data\Tracks\*.acmi` (u multiplayeru odlučuje server).
   Gotova datoteka se pretvara: svaki avion, vozilo i brod s njegovim
   položajima, pojavljivanjem i uklanjanjem (uništen ili otišao), polijetanjima i slijetanjima kad
   ih snimka ima. ACMI 2.x tekstualni format, običan ili zipovan, prema
   <https://www.tacview.net/documentation/acmi/en/> - linije "#t" pomjeraju sat,
   linije "id,Key=Value,..." postavljaju svojstva (heksadecimalni id-ovi, zarezi se escapeaju "\\,", završna
   "\\" nastavlja liniju), "-id" uklanja objekt, objekt 0 nosi
   globalne vrijednosti (ReferenceLongitude/Latitude, RecordingTime, ...) i događaje
   ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] ili
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], geografska dužina i širina relativne u odnosu na
   referencu, prazna polja ostaju nepromijenjena. Položaji idu u ravnu mapu oko
   referentne tačke: x istok, y visina, z sjever, metri. Referentna
   tačka je `geo` sesije, nosi se u meta.json i podnožju tabele,
   pa preglednik može podmetnuti stvarni svijet ispod putanja.

Isti modul služi i za: [IL-2 Sturmovik: Great Battles (snimke)](game-il2-tacview.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Osa gore | `y` |
| Jedinice | nema: telemetrija nema svjetske položaje |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljenu memoriju koju igra objavljuje), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- SET_FOCUS (uzeti avion: nalet), DROP_BOMB i ROCKET_LAUNCH (masa, lokalni položaj), HIT i DAMAGE (lokalni položaj, sila), EXPLOSION (lokalni položaj, radijus), GUN_FIRE (meci po upitu) kao redovi
- SETUP_ENG (index, id, lokalni položaj, maksimalni broj okretaja), SETUP_GUN (index, lokalni položaj, masa projektila, početna brzina) i SETUP_LGEAR (index, id, lokalni položaj) kao redovi: motori, oružje i noge stajnog trapa aviona na početku naleta
- SRV_TITLE, SRV_ADDR, SRS_ADDR i CLIENT_DAT (ime pilota) u meta.json; koalicija iz CTRL_DAT kao tim naleta
- svih petnaest indikatora iz specifikacije u redu `state` jednom u sekundi (jedna vrijednost kao broj, po jedna za svaki motor, nogu trapa ili osu kao lista); najveća brzina, g i AGL iz svakog paketa

**Čuva se sirovo**

- svaki datagram cijel kao `payload`, pod svojim Packet_ID: `0x54000101` za telemetriju (used kad je dao red ili unos u meta.json), svaki drugi id pod samim sobom, datagram prekratak za jedan kao `short`
- ono što drži samo sirovi sidecar: indikatori između redova jednom u sekundi (igra ih šalje na 50 Hz / decimation), SETUP događaj kraći od rasporeda iz specifikacije, id-ovi događaja koje specifikacija ne navodi

**Nije dostupno**

- svjetski položaj: telemetrijski izlaz ga nema (položaji događaja su lokalni u odnosu na avion); adapter il2-tacview čita položaje iz vlastitih Tacview snimaka igre
- drugi avioni i igrači: izlaz opisuje samo igračev vlastiti avion

**Veličina**: oko 8 MB na sat pri 10 Hz iz `setup` (decimation 5; paket je oko 160 bajta plus okvir), 40 MB pri punih 50 Hz igre, prije zstd; zstd svodi ponavljajuće floatove na mali dio

## Provjereno {#verified}

testirano na paketima izgrađenim iz vlastite specifikacije igre Il2_TeleOutput (rev 1.2); izmjene startup.cfg testirane na kopiji datoteke; nije testirano na pokrenutoj igri

## Izvor {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
