---
title: "iRacing (të dhëna live)"
nav_order: 28
lang: "sq"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (të dhëna live) {#iracing-live-data}

Ndërsa luan iRacing, watcher ruan të dhënat që vetë loja i dërgon, që t'i shohësh më vonë si statistika dhe vijë kohore.

*Detaje teknike: adaptori `iracing`, lloji [`telemetry`](sources-and-rules.md); punon sa kohë `iRacingSim64DX11.exe` ose `iRacingSim64.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- vozitja me 5 Hz pa pozicion (iRacing nuk jep asnjë live): shpejtësia, marshi, gazi, frena, xhiroja, pjesa e xhiros, pozicioni në garë dhe në klasë, incidentet
- fillimi i sesionit, hyrja dhe dalja nga makina, hyrja dhe dalja nga pit lane, xhirot me kohën e xhiros, incidentet me pikët e tyre, flamuri me kuadrate, mbarimi
- skedarët e telemetrisë .ibt të shkruar gjatë seancës (gjerësia, gjatësia, lartësia - shikuesi i lexon)
- xhirot, xhiroja më e mirë, incidentet, pozicioni në garë, ndalesat në pit, distanca, shpejtësia maksimale
- i gjithë memoria e përbashkët te `heat.raw.parquet`: koka, kokat e ndryshoreve, informacioni i sesionit, çdo rresht telemetrie i lexuar

## Nga vjen {#where-it-comes-from}

memoria e përbashkët Local\IRSDKMemMapFileName (iRacing SDK); skedarët .ibt te %USERPROFILE%\Documents\iRacing\telemetry

## Si ta ndezësh {#how-to-switch-it-on}

Asgjë për të dhënat live. Për pozicionet: regjistro telemetrinë në makinë (Alt+L) ose vendos irsdkLog=1 te app.ini

## Si funksionon {#how-it-works}

iRacing, live: memoria e përbashkët e iRacing SDK, e lexuar natyrshëm.

iRacing e publikon telemetrinë për aplikacionet në një mapim skedari me emër,
`Local\IRSDKMemMapFileName`, që simulatori e krijon sa kohë punon (dhe sinjalizon
`Local\IRSDKDataValidEvent` në çdo përditësim, gjë që këtu nuk nevojitet: watcher
shikon dhjetë herë në sekondë). Struktura është ajo e `irsdk_defines.h` të SDK,
e ndjekur edhe nga pyirsdk (MIT) - e shkruar sërish këtu nga ato fakte:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Simulatori shkruan `numBuf` rreshta në rrotullim; më i riu është ai me
tickCount më të lartë, dhe një rresht merret sërish nëse tickCount i tij lëvizi ndërsa
po kopjohej.

Të dhënat live nuk kanë pozicion në botë - gjerësia, gjatësia dhe lartësia janë vetëm te
skedarët `.ibt` që iRacing i regjistron te `Documents\iRacing\telemetry` (Alt+L në
makinë, ose `irsdkLog=1`), që shikuesi 3DHeat i lexon vetë. Pra kjo regjistron
vozitjen si ngjarje pa koordinata - shpejtësia, xhiroja, pjesa e xhiros e
bërë, pozicioni në garë, incidentet - plus xhirot, incidentet, ndalesat në pit dhe
flamurin me kuadrate, dhe në fund skedarët `.ibt` të shkruar gjatë seancës si
ngjarje `telemetry_file`, që shikuesi t'i hapë.

Përveç rreshtave ruhet i gjithë harta e memories, te skedari anësor i papërpunuar i sesionit
(`heat.raw.parquet`): pjesa fikse e kokës (`header`, sa herë
ndryshon), kokat e ndryshoreve (`var_headers`, të plota, dhe si JSON te `text`,
sa herë ndryshon struktura), YAML i informacionit të sesionit (`session_info`, teksti i tij
sa herë lëviz `sessionInfoUpdate`) dhe rreshti më i ri i telemetrisë
(`telemetry`, çdo ndryshore e tij, çdo lexim që gjen një tick të ri). Kokat e
ndryshoreve dhe një rresht janë gjithçka që një dekoder i mëvonshëm duhet për të lexuar çdo ndryshore.

Burimi: iRacing SDK (irsdk_defines.h, dokumentimi në forumin "iRacing SDK");
kutu/pyirsdk (MIT) për konfirmimin e offset-eve.

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | jo |
| Boshti lart | `y` |
| Njësitë | pa pozicione live; skedarët .ibt mbajnë gjerësinë/gjatësinë/lartësinë |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `telemetry`: lexon vetëm atë që loja ose platforma e jep vetë (një port UDP ose memorie e përbashkët që loja e publikon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- nga rreshti më i ri i telemetrisë: ora e sesionit, numri, gjendja dhe id, në pistë, riluajtje, xhiroja, xhirot e përfunduara, pjesa dhe metrat e xhiros, xhiroja e fundit dhe më e mira, shpejtësia, marshi, gazi, frena, RPM, pit road, sipërfaqja e pistës, pozicioni në garë dhe në klasë, numri i incidenteve të veta (rreshtat `driving` me 5 Hz dhe ngjarjet)
- tani edhe te rreshtat `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (gradë, nga radianët e simulatorit - vetëm kur koka e ndryshores e jep njësinë si rad), `fuel_l` (njësia l), `lat_accel` dhe `lon_accel` (njësia m/s^2)
- nga YAML i informacionit të sesionit: indeksi i makinës së lojtarit, pista dhe konfigurimi, llojet e sesioneve, emri, makina, ekipi dhe numri i çdo shoferi (rreshtat session_start, meta.json)
- kontrolluar me një bllok të ndërtuar nga irsdk_defines.h në teste; ende jo me simulatorin

**Ruajtur të papërpunuara**

- `telemetry`: rreshti më i ri i plotë, çdo ndryshore që publikon simulatori (vargjet CarIdx të çdo makine, gomat, pezullimi, vargjet `_ST` me ritëm të lartë ku simulatori i ka ...), çdo lexim që gjen një tick të ri; `tick` numri i tick-eve i simulatorit; `used` është false sa kohë luhet një riluajtje
- `var_headers`: kokat e ndryshoreve të plota (144 bajte secila) dhe, te `text`, si JSON (emri, lloji, offset, count, njësia, përshkrimi), sa herë ndryshon struktura - sa për të lexuar çdo ndryshore të çdo rreshti të ruajtur
- `session_info`: teksti YAML i plotë sa herë lëviz numëruesi i përditësimit (weekend, sesionet dhe rezultatet, shoferët, setup-i i makinës, radio, listat e kamerave), `update` numëruesi
- `header`: koka irsdk 112 bajte e plotë sa herë ndryshon (versioni, statusi, tick rate, offset-et, tick-et e rreshtave)

**Nuk ofrohet**

- një pozicion në botë live: memoria e përbashkët nuk ka; gjerësia, gjatësia dhe lartësia janë vetëm te skedarët .ibt (me regjistrimin ndezur), që shikuesi i lexon - watcher emërton ata të shkruar gjatë seancës
- tick-et mes dy leximeve: simulatori shkruan 60 rreshta në sekondë në 3 ose 4 vende dhe watcher lexon 10 herë në sekondë, kështu që shumica e tick-eve mbishkruhen para se të lexohen; skedari .ibt ka çdo tick kur regjistrimi është ndezur

**Madhësia**: një rresht telemetrie është disa KB (rreth 5 deri 10 KB me vargjet e çdo makine), i ruajtur deri në 10 herë në sekondë, plus koka (112 bajte) po aq shpesh dhe YAML i informacionit të sesionit (dhjetëra KB) kur ndryshon: rreth 0.2 deri 0.4 GB në orë në pistë para kompresimit; zstd e çon në një pjesë të vogël (ende nuk është matur në një sesion të vërtetë)

## Verifikuar {#verified}

u provua me një bllok memorie të përbashkët të ndërtuar në test sipas strukturës irsdk; i paprovuar me simulatorin

## Burimi {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
