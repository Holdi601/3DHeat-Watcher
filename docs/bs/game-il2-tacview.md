---
title: "IL-2 Sturmovik: Great Battles (snimke)"
nav_order: 27
lang: "bs"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (snimke) {#il-2-sturmovik-great-battles-replays}

Nakon meča u IL-2 Sturmovik: Great Battles, watcher pretvara snimku koju je igra sačuvala u datoteke koje možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `il2-tacview`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da se igra pokrene) i svakih 5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- svaki avion, vozilo i brod iz snimke: položaji jednom u sekundi (metri istok/gore/sjever od referentne tačke snimke; lat/lon/alt kao kolone)
- pojavljivanja (spawn), uništenja (death) i odlasci (left), polijetanja i slijetanja kad su snimljena
- objekti, uništeni, polijetanja, slijetanja i dužina po snimci
- svaka linija snimke čuva se cijela u heat.raw.parquet, na satu redova

## Odakle dolazi {#where-it-comes-from}

vlastite Tacview snimke igre &lt;game>\data\Tracks\\\*.acmi (ACMI 2.x tekst, običan ili zipovan)

## Kako ga uključiti {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 u [KEY = track_record])

Upišite komandu u terminal otvoren u folderu watcher-a (vidite [Prije nego počnete](before-you-start.md)). Ako ne uspije, zadnji red kaže zašto; [Instalacija i pokretanje](installing-and-running.md) pokriva uobičajene uzroke.

`python -m heat3d_watch setup il2-tacview` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup il2-tacview --apply` ih mijenja, a original čuva kao `<file>.heat3d-backup` (vidite [Komande](commands.md#setup)). Ispisuje `il2-tacview: changed: ...` za svaku promjenu, ili `il2-tacview: nothing to change` kad je već uključeno.

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

Isti modul služi i za: [IL-2 Sturmovik: Great Battles (podaci uživo)](game-il2.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | metri (istok, visina, sjever od prve tačke) |
| Zrcaljeno za preglednik | `z` |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (snimke i demo-e koje igra sprema), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- T svakog objekta (geografska dužina, širina, visina, roll, pitch, yaw, U, V, heading) kao položaji jednom u sekundi po objektu, s Name, Type, Pilot, Coalition/Color, Country, Group i Parent
- pojavljivanja, uklanjanja (death ako je prvo došao događaj Destroyed, inače left), događaji TakenOff i Landed, događaji Message i Bookmark kao redovi
- globalne vrijednosti ReferenceLongitude/Latitude (ishodište mape), RecordingTime/ReferenceTime (kada), DataSource, DataRecorder i Title u meta.json

**Čuva se sirovo**

- svaka neprazna logička linija cijela kao `text` (linija nastavljena završnom kosom crtom unazad se spaja, kako to ACMI čita), pod svojom vrstom: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` i `event` (objekt 0), `object` (id,Key=Value,...)
- ono što drži samo sirovi sidecar: položaji između redova jednom u sekundi, oružje, granate, flares, chaff i drugi objekti koji se ne crtaju kao putanje, svako drugo svojstvo (telemetrija poput IAS, AOA, gasa, goriva gdje je snimka ima), druge globalne vrijednosti (Comments, Briefing, Author, Category), događaji osim onih koji se čitaju (Timeout, LeftArea, ...)

**Nije dostupno**

- ništa što snimka sadrži; ono što igra ne upisuje u svoje snimke nije u njima

**Veličina**: otprilike tekst same snimke plus oko 70 bajta po liniji, prije zstd: snimka od 100 MB daje oko 150-250 MB sirovo, što zstd svodi blizu veličine zipovane snimke

## Provjereno {#verified}

testirano na sintetičkim ACMI 2.2 datotekama (tekst i zipovane); nije testirano na snimci iz igre

## Izvor {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
