---
title: "IL-2 Sturmovik: Great Battles (živi podaci)"
nav_order: 26
lang: "hr"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (živi podaci) {#il-2-sturmovik-great-battles-live-data}

Dok igrate IL-2 Sturmovik: Great Battles, watcher sprema podatke koje sama igra šalje van, pa ih kasnije možete pogledati kao statistiku i vremensku crtu.

*Tehnički podaci: adapter `il2`, vrsta [`telemetry`](sources-and-rules.md); radi dok su `Il-2.exe` ili `IL2Series.exe` pokrenuti i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- letovi: zrakoplov koji je uzet (spawn) i trenutak kad izlaz stane (session_end) - bez svjetskog položaja: igra ga ne šalje
- bombe i rakete koje su ispuštene (masa), pogoci i oštećenja, eksplozije, rafali iz oružja - položaji lokalni za zrakoplov
- ekvivalentna zračna brzina, AGL, vertikalna brzina, g, broj okretaja motora jednom u sekundi, uz sve ostale indikatore koje paket nosi (tlak u usisnoj grani, tresenje motora, stanje i tlak stajnog trapa, AoA, klizanje, ubrzanje x/y/z, tresenje kabine, zakrilci, aerokočnice)
- letovi, ispaljeni meci, bombe, rakete, primljeni pogoci, najveća brzina, najveći g, vrijeme leta; naziv servera i ime pilota na mreži
- svaki telemetrijski paket cijel u heat.raw.parquet

## Odakle dolaze {#where-it-comes-from}

telemetrijski UDP izlaz igre na 127.0.0.1:41995 ([KEY = telemetrydevice] u &lt;game>\data\startup.cfg)

## Kako ga uključiti {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (dodaje addrN = "127.0.0.1:41995", enable = true), zatim ponovno pokrenite IL-2

Naredbu upišite u terminal otvoren u mapi watchera (pogledajte [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) pokriva uobičajene uzroke.

`python -m heat3d_watch setup il2` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup il2 --apply` ih mijenja, a izvornik čuva kao `<file>.heat3d-backup` (pogledajte [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `il2: changed: ...`, ili `il2: nothing to change` kad je već uključeno.

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

Isti modul služi i: [IL-2 Sturmovik: Great Battles (replay-i)](game-il2-tacview.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Os gore | `y` |
| Jedinice | nema: telemetrija nema svjetske položaje |
| Zrcaljenje za preglednik | nema |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma predaje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- SET_FOCUS (zrakoplov uzet: let), DROP_BOMB i ROCKET_LAUNCH (masa, lokalni položaj), HIT i DAMAGE (lokalni položaj, sila), EXPLOSION (lokalni položaj, polumjer), GUN_FIRE (rafali po očitavanju) kao retci
- SETUP_ENG (indeks, ID, lokalni položaj, najveći broj okretaja), SETUP_GUN (indeks, lokalni položaj, masa projektila, početna brzina) i SETUP_LGEAR (indeks, ID, lokalni položaj) kao retci: motori, topovi i nosači kotača zrakoplova kad let počne
- SRV_TITLE, SRV_ADDR, SRS_ADDR i CLIENT_DAT (ime pilota) u meta.json; CTRL_DAT-ova koalicija kao tim sesije
- svih petnaest indikatora iz specifikacije na retku `state` jednom u sekundi (jedna vrijednost kao broj, po motoru, nogu stajnog trapa ili osi kao popis); najveća brzina, g i AGL iz svakog paketa

**Čuva se sirovo**

- svaki datagram cijel kao `payload`, pod svojim Packet_ID: `0x54000101` za telemetriju (korišten kad je napravio redak ili unos u meta.json), svaki ostali ID kao on sam, datagram prekratak za jedan kao `short`
- što samo sirova pomoćna datoteka sadrži: indikatori između redaka po sekundi (igra ih šalje pri 50 Hz / decimation), događaj SETUP kraći od rasporeda iz specifikacije, ID-evi događaja koje specifikacija ne navodi

**Nije dostupno**

- svjetski položaj: telemetrijski izlaz ga nema (položaji događaja su lokalni za zrakoplov); adapter il2-tacview čita položaje iz vlastitih Tacview snimki igre
- drugi zrakoplovi i igrači: izlaz opisuje samo zrakoplov igrača

**Veličina**: oko 8 MB po satu pri postavci setup od 10 Hz (decimation 5; paket je oko 160 bajta plus okvir), 40 MB pri punih 50 Hz igre, prije zstd-a; zstd svodi ponavljajuće floatove na djelić

## Provjereno {#verified}

testirano na paketima izgrađenima prema specifikaciji Il2_TeleOutput igre (rev 1.2); izmjene startup.cfg testirane na kopiji datoteke; nije testirano na pokrenutoj igri

## Izvor {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
