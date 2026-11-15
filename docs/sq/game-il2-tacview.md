---
title: "IL-2 Sturmovik: Great Battles (riluajtje)"
nav_order: 27
lang: "sq"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (riluajtje) {#il-2-sturmovik-great-battles-replays}

Pas një ndeshjeje IL-2 Sturmovik: Great Battles, watcher e kthen riluajtjen që ruajti loja në skedarë që mund t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `il2-tacview`, lloji [`replay`](sources-and-rules.md); punon gjithë kohën (nuk pret që të nisë një lojë) dhe kërkon të dhëna të reja çdo 5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- çdo avion, mjet dhe anije i regjistrimit: pozicionet një herë në sekondë (metra lindje/lart/veri nga pika e referencës së regjistrimit; lat/lon/alt si kolona)
- spawn-et, shkatërrimet (death) dhe largimet (left), ngritjet dhe uljet kur regjistrohen
- objektet, të shkatërruarat, ngritjet, uljet dhe gjatësia për çdo regjistrim
- çdo rresht i regjistrimit i plotë te heat.raw.parquet, në orën e rreshtave

## Nga vjen {#where-it-comes-from}

regjistrimet Tacview të vetë lojës &lt;game>\data\Tracks\\\*.acmi (tekst ACMI 2.x, i thjeshtë ose i zipuar)

## Si ta ndezësh {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 te [KEY = track_record])

Shkruaje komandën në një terminal të hapur në dosjen e watcher-it (shih [Para se të fillosh](before-you-start.md)). Nëse dështon, rreshti i fundit tregon pse; [Instalimi dhe nisja](installing-and-running.md) përmban shkaqet më të zakonshme.

`python -m heat3d_watch setup il2-tacview` liston skedarët që do t'i ndryshonte; `python -m heat3d_watch setup il2-tacview --apply` i ndryshon, duke e ruajtur origjinalin si `<file>.heat3d-backup` (shih [Komandat](commands.md#setup)). Printon `il2-tacview: changed: ...` për çdo ndryshim, ose `il2-tacview: nothing to change` kur është tashmë i ndezur.

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

Të njëjtin modul e përdor edhe: [IL-2 Sturmovik: Great Battles (të dhëna live)](game-il2.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | metra (lindje, lartësi, veri nga pika e parë e fiksuar) |
| Pasqyruar për shikuesin | `z` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `replay`: lexon vetëm atë që loja ose platforma e jep vetë (riluajtje dhe demo që loja i ruan), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- T i çdo objekti (gjatësia, gjerësia, lartësia, roll, pitch, yaw, U, V, heading) si pozicione një herë në sekondë për objekt, me Name, Type, Pilot, Coalition/Color, Country, Group dhe Parent
- spawn-et, heqjet (death kur një ngjarje Destroyed erdhi e para, përndryshe left), ngjarjet TakenOff dhe Landed, ngjarjet Message dhe Bookmark si rreshta
- globalet ReferenceLongitude/Latitude (origjina e hartës), RecordingTime/ReferenceTime (kur), DataSource, DataRecorder dhe Title te meta.json

**Ruajtur të papërpunuara**

- çdo rresht logjik jo i zbrazët i plotë si `text` (një rresht i vazhduar me backslash në fund bashkohet, siç e lexon ACMI), nën llojin e vet: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` dhe `event` (objekti 0), `object` (id,Key=Value,...)
- çfarë mban vetëm skedari anësor i papërpunuar: pozicionet mes rreshtave një herë në sekondë, armët, predhat, flares, chaff dhe objektet e tjera që nuk vizatohen si gjurmë, çdo veti tjetër (telemetri si IAS, AOA, gazi, karburanti ku regjistrimi i ka), globale të tjera (Comments, Briefing, Author, Category), ngjarje përveç atyre që lexohen (Timeout, LeftArea, ...)

**Nuk ofrohet**

- asgjë nga ç'ka regjistrimi; çfarë loja nuk e shkruan në regjistrimet e veta nuk është aty

**Madhësia**: rreth tekstit të vetë regjistrimit plus rreth 70 bajte për rresht, para zstd: një regjistrim 100 MB jep rreth 150-250 MB të papërpunuara, që zstd i sjell afër madhësisë së regjistrimit të zipuar

## Verifikuar {#verified}

u provua me skedarë sintetikë ACMI 2.2 (tekst dhe zip); i paprovuar me një regjistrim nga loja

## Burimi {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
