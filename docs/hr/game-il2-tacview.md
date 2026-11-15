---
title: "IL-2 Sturmovik: Great Battles (replay-i)"
nav_order: 27
lang: "hr"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (replay-i) {#il-2-sturmovik-great-battles-replays}

Nakon meča u IL-2 Sturmovik: Great Battles, watcher pretvara snimku koju je igra spremila u datoteke koje možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `il2-tacview`, vrsta [`replay`](sources-and-rules.md); radi cijelo vrijeme (ne čeka da se igra pokrene) i traži nove podatke svakih 5 s.*

## Što se bilježi {#what-is-recorded}

- svaki zrakoplov, vozilo i brod iz snimke: položaji jednom u sekundi (metri istok/gore/sjever od referentne točke snimke; geografska širina, dužina i visina kao stupci)
- pojave, uništenja (smrt) i odlasci (lijevo), polijetanja i slijetanja kad su snimljeni
- objekti, uništeni, polijetanja, slijetanja i duljina po snimci
- svaki redak snimke cijel u heat.raw.parquet, prema satu redaka

## Odakle dolaze {#where-it-comes-from}

vlastite Tacview snimke igre &lt;game>\data\Tracks\\\*.acmi (ACMI 2.x tekst, običan ili zipan)

## Kako ga uključiti {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 u [KEY = track_record])

Naredbu upišite u terminal otvoren u mapi watchera (pogledajte [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) pokriva uobičajene uzroke.

`python -m heat3d_watch setup il2-tacview` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup il2-tacview --apply` ih mijenja, a izvornik čuva kao `<file>.heat3d-backup` (pogledajte [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `il2-tacview: changed: ...`, ili `il2-tacview: nothing to change` kad je već uključeno.

## Kako radi {#how-it-works}

IL-2 Sturmovik: Great Battles - telemetrijski UDP izlaz igre i njezine vlastite Tacview snimke.

1. Telemetrija ("Telemetry output of IL2 v4.003", revizija 1.2, isporučena kao
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Uključuje se u
   `<game>\data\startup.cfg`, odjeljak `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:port]" (više odredišta odjednom), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` dodaje jedno odredište, 127.0.0.1:41995 (JoyPro
   koristi 41994, zadani port igre je 4322), i uključuje izlaz. Paketi,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indikatori: 0 ENG_RPM, 1 ENG_MP, 2/3 tresenje motora, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz uključujući
   gravitaciju), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS
   (rad), 14 VERTICAL_SPEED (m/s). Događaji (2-bajtno pakiranje): 0 SET_FOCUS
   (STRING: bajt duljine + ASCII), 1 SETUP_ENG {short index, short id, float
   pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float
   projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short
   id, float pos[3]}, 4 DROP_BOMB i 5 ROCKET_LAUNCH {float pos[3], float mass,
   WORD flags}, 6 HIT i 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION
   {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11
   SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server
   client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Položaji
   događaja su lokalni za zrakoplov igrača; tok nema nikakav svjetski položaj -
   zato su ovo događaji i brojke, a ne putanja.

2. Tacview snimka: `tacviewrecord = 1` u `[KEY = track_record]` tjera igru da
   piše `<game>\data\Tracks\*.acmi` (u višeigračkoj igri odlučuje server). Gotova
   datoteka se pretvara: svaki zrakoplov, vozilo i brod s položajima, pojavom i
   uklanjanjem (uništen ili nestao), polijetanjima i slijetanjima kad ih snimka
   ima. ACMI 2.x tekstualni format, običan ili zipan, prema
   <https://www.tacview.net/documentation/acmi/en/> - redci "#t" pomiču sat,
   redci "id,Key=Value,..." postavljaju svojstva (heksadecimalni ID-evi, zarezi
   escapani kao "\\,", završni "\\" nastavlja redak), "-id" uklanja objekt,
   objekt 0 nosi globalne vrijednosti (ReferenceLongitude/Latitude,
   RecordingTime, ...) i događaje ("Event=Destroyed\|id\|text"). T =
   Lon\|Lat\|Alt[\|U\|V] ili Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading],
   dužina i širina relativno prema referenci, prazna polja ostaju nepromijenjena.
   Položaji idu u ravnu kartu oko referentne točke: x istok, y visina, z sjever,
   metri. Referentna točka je `geo` sesije, nosi se u meta.json i u podnožju
   tablice, pa preglednik može položiti stvarni svijet ispod putanja.

Isti modul služi i: [IL-2 Sturmovik: Great Battles (živi podaci)](game-il2.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os gore | `y` |
| Jedinice | metri (istok, visina, sjever od prve točke) |
| Zrcaljenje za preglednik | `z` |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma predaje (snimke i demo zapise koje igra sprema), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- T svakog objekta (dužina, širina, visina, roll, pitch, yaw, U, V, heading) kao položaji jednom u sekundi po objektu, s Name, Type, Pilot, Coalition/Color, Country, Group i Parent
- pojave, uklanjanja (smrt ako je prije došao događaj Destroyed, inače odlazak), događaji TakenOff i Landed, događaji Message i Bookmark kao retci
- globalne vrijednosti ReferenceLongitude/Latitude (ishodište karte), RecordingTime/ReferenceTime (kad), DataSource, DataRecorder i Title u meta.json

**Čuva se sirovo**

- svaki neprazan logički redak cijel kao `text` (redak nastavljen završnim "\" spaja se, kako ga ACMI čita), pod svojom vrstom: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` i `event` (objekt 0), `object` (id,Key=Value,...)
- što samo sirova pomoćna datoteka sadrži: položaje između retka po sekundi, oružje, granate, baklje, pljevu i ostale objekte koji se ne crtaju kao putanje, svako ostalo svojstvo (telemetriju poput IAS-a, AOA-a, gasa, goriva ako je snimka ima), ostale globalne vrijednosti (Comments, Briefing, Author, Category), događaje osim pročitanih (Timeout, LeftArea, ...)

**Nije dostupno**

- ništa što snimka ne sadrži; ono što igra ne piše u svoje snimke nije u njima

**Veličina**: otprilike sam tekst snimke plus oko 70 bajta po retku, prije zstd-a: snimka od 100 MB čini oko 150-250 MB sirovih podataka, koje zstd svodi blizu veličine zipane snimke

## Provjereno {#verified}

testirano na sintetičkim ACMI 2.2 datotekama (tekstualnim i zipanim); nije testirano na snimci iz igre

## Izvor {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
