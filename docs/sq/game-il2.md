---
title: "IL-2 Sturmovik: Great Battles (të dhëna live)"
nav_order: 26
lang: "sq"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (të dhëna live) {#il-2-sturmovik-great-battles-live-data}

Ndërsa luan IL-2 Sturmovik: Great Battles, watcher ruan të dhënat që vetë loja i dërgon, që t'i shohësh më vonë si statistika dhe vijë kohore.

*Detaje teknike: adaptori `il2`, lloji [`telemetry`](sources-and-rules.md); punon sa kohë `Il-2.exe` ose `IL2Series.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- misionet (sorties): avioni i marrë (spawn) dhe kur ndalon dalja (session_end) - pa pozicion në botë: loja nuk dërgon asnjë
- bombat dhe raketat e lëshuara (masa), goditjet dhe dëmi i marrë, shpërthimet, breshëritë e gjuajtjes - pozicione lokale ndaj avionit
- shpejtësia ekuivalente e ajrit, AGL, shpejtësia vertikale, g, RPM e motorit një herë në sekondë, me çdo tregues tjetër që mban paketa (presioni i manifoldit, dridhja e motorit, gjendja dhe presioni i trenit të uljes, AoA, sideslip, nxitimi x/y/z, dridhja e kabinës, flaps, air brakes)
- misionet, plumbat e gjuajtur, bombat, raketat, goditjet e marra, shpejtësia më e lartë, g më i lartë, koha e fluturimit; titulli i serverit dhe emri i pilotit online
- çdo paketë telemetrie e plotë te heat.raw.parquet

## Nga vjen {#where-it-comes-from}

dalja UDP e telemetrisë së lojës te 127.0.0.1:41995 ([KEY = telemetrydevice] te &lt;game>\data\startup.cfg)

## Si ta ndezësh {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (shton addrN = "127.0.0.1:41995", enable = true), rinise IL-2

Shkruaje komandën në një terminal të hapur në dosjen e watcher-it (shih [Para se të fillosh](before-you-start.md)). Nëse dështon, rreshti i fundit tregon pse; [Instalimi dhe nisja](installing-and-running.md) përmban shkaqet më të zakonshme.

`python -m heat3d_watch setup il2` liston skedarët që do t'i ndryshonte; `python -m heat3d_watch setup il2 --apply` i ndryshon, duke e ruajtur origjinalin si `<file>.heat3d-backup` (shih [Komandat](commands.md#setup)). Printon `il2: changed: ...` për çdo ndryshim, ose `il2: nothing to change` kur është tashmë i ndezur.

## Si funksionon {#how-it-works}

IL-2 Sturmovik: Great Battles - dalja UDP e telemetrisë së lojës, dhe regjistrimet e veta Tacview.

1. Telemetria ("Telemetry output of IL2 v4.003", rishikimi 1.2, e shpërndarë si
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Ndizet te
   `<game>\data\startup.cfg`, seksioni `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:port]" (disa objektiva njëkohësisht), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` shton një objektiv, 127.0.0.1:41995 (JoyPro përdor
   41994, e paracaktuara e lojës është 4322), dhe e ndez daljen. Paketat,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Treguesit: 0 ENG_RPM, 1 ENG_MP, 2/3 engine shake, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz përfshirë gravitetin),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Ngjarjet (të paketuara me 2 bajte): 0 SET_FOCUS (STRING: bajt
   gjatësie + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB dhe 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT dhe 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Pozicionet e ngjarjeve janë lokale ndaj avionit të lojtarit; rrjedha
   nuk ka fare pozicion në botë - pra këto janë ngjarje dhe numra, jo një gjurmë.

2. Regjistrimi Tacview: `tacviewrecord = 1` te `[KEY = track_record]` e bën
   lojën të shkruajë `<game>\data\Tracks\*.acmi` (në multiplayer vendos serveri).
   Një skedar i përfunduar konvertohet: çdo avion, mjet dhe anije me
   pozicionet, spawn-in dhe heqjen (shkatërruar ose iku), ngritjet dhe uljet kur
   regjistrimi i ka. Formati tekst ACMI 2.x, i thjeshtë ose i zipuar, sipas
   <https://www.tacview.net/documentation/acmi/en/> - rreshtat "#t" e lëvizin orën,
   rreshtat "id,Key=Value,..." vendosin veti (id-të hex, presjet me ikje "\\,", një
   "\\" në fund e vazhdon rreshtin), "-id" e heq një objekt, objekti 0 mban
   globalet (ReferenceLongitude/Latitude, RecordingTime, ...) dhe ngjarjet
   ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] ose
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], gjatësia dhe gjerësia relative me
   referencën, fushat e zbrazëta pa ndryshim. Pozicionet futen në një hartë të sheshtë rreth
   pikës së referencës: x lindje, y lartësia, z veri, metra. Pika e referencës
   është `geo` i sesionit, e mbajtur te meta.json dhe te fundi i tabelës,
   kështu që shikuesi mund ta vendosë botën e vërtetë poshtë gjurmëve.

Të njëjtin modul e përdor edhe: [IL-2 Sturmovik: Great Battles (riluajtje)](game-il2-tacview.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | jo |
| Boshti lart | `y` |
| Njësitë | asnjë: telemetria nuk ka pozicione në botë |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `telemetry`: lexon vetëm atë që loja ose platforma e jep vetë (një port UDP ose memorie e përbashkët që loja e publikon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- SET_FOCUS (avioni i marrë: një mision), DROP_BOMB dhe ROCKET_LAUNCH (masa, pozicioni lokal), HIT dhe DAMAGE (pozicioni lokal, forca), EXPLOSION (pozicioni lokal, rrezja), GUN_FIRE (plumba për çdo pyetje) si rreshta
- SETUP_ENG (indeksi, id, pozicioni lokal, RPM maksimale), SETUP_GUN (indeksi, pozicioni lokal, masa e predhës, shpejtësia e gojës) dhe SETUP_LGEAR (indeksi, id, pozicioni lokal) si rreshta: motorët, armët dhe këmbët e trenit të uljes të avionit kur fillon misioni
- SRV_TITLE, SRV_ADDR, SRS_ADDR dhe CLIENT_DAT (emri i pilotit) te meta.json; koalicioni i CTRL_DAT si ekipi i misionit
- të pesëmbëdhjetë treguesit e specifikimit te rreshti `state` një herë në sekondë (një vlerë si numër, një për çdo motor, këmbë treni ose bosht si listë); shpejtësia, g dhe AGL më të larta nga çdo paketë

**Ruajtur të papërpunuara**

- çdo datagram i plotë si `payload`, nën Packet_ID të vet: `0x54000101` për telemetrinë (`used` kur bëri një rresht ose një hyrje te meta.json), çdo id tjetër si vetvetja, një datagram shumë i shkurtër për një si `short`
- çfarë mban vetëm skedari anësor i papërpunuar: treguesit mes rreshtave një herë në sekondë (loja i dërgon me 50 Hz / decimation), një ngjarje SETUP më e shkurtër se struktura e specifikimit, id-ë ngjarjesh që specifikimi nuk i liston

**Nuk ofrohet**

- një pozicion në botë: dalja e telemetrisë nuk ka (pozicionet e ngjarjeve janë lokale ndaj avionit); adaptori il2-tacview i lexon pozicionet nga regjistrimet Tacview të vetë lojës
- avionët dhe lojtarët e tjerë: dalja përshkruan vetëm avionin e vetë lojtarit

**Madhësia**: rreth 8 MB në orë me 10 Hz të `setup` (decimation 5; një paketë është rreth 160 bajte plus kuadri i saj), 40 MB me 50 Hz të plotë të lojës, para zstd; zstd i zvogëlon float-et që përsëriten në një pjesë të vogël

## Verifikuar {#verified}

u provua me paketa të ndërtuara sipas specifikimit Il2_TeleOutput të vetë lojës (rev 1.2); ndryshimet e startup.cfg u provuan mbi një kopje të skedarit; i paprovuar me lojën që punon

## Burimi {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
