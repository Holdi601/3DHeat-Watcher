---
title: "X-Plane (të dhëna live)"
nav_order: 49
lang: "sq"
source: game-xplane.md
source_hash: "be1c5b21d2ef"
nav_exclude: true
search_exclude: true
---
# X-Plane (të dhëna live) {#x-plane-live-data}

Ndërsa luan X-Plane, watcher ruan të dhënat që vetë loja i dërgon, që t'i shohësh më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `xplane`, lloji [`telemetry`](sources-and-rules.md); punon sa kohë `X-Plane.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni yt me 10 Hz (gjerësia/gjatësia/lartësia si metra lindje/lart/veri nga pika e parë e fiksuar; lat/lon/alt të ruajtura si kolona)
- qëndrimi (attitude), shpejtësia e treguar dhe e vërtetë e ajrit, shpejtësia mbi tokë, Mach, shpejtësia vertikale, AoA, sideslip, drejtimi magnetik, AGL, g (normal, aksial, anësor), shpejtësitë dhe ritmet e rrotullimit, flaps, speedbrake, gazi, në tokë
- peshat (totale, karburanti, ngarkesa), doreza e trenit të uljes, autopiloti, RPM dhe N1 e motorit, ora dhe data e simulatorit, pauza, shpejtësia e simulatorit, riluajtja, temperatura jashtë dhe presioni në nivelin e detit (X-Plane 12) një herë në sekondë
- ngritjet, uljet, përplasjet (crash), rivendosjet e fluturimit (session_start/session_end për çdo fluturim)
- koha e fluturimit, koha në ajër, distanca, lartësia më e lartë, g më i lartë, uljet
- çdo përgjigje që dërgon X-Plane e plotë te heat.raw.parquet

## Nga vjen {#where-it-comes-from}

ndërfaqja UDP e X-Plane te 127.0.0.1:49000 (datarefs RREF dhe pozicioni RPOS, përgjigjur watcher-it)

## Si ta ndezësh {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 përgjigjet si parazgjedhje)

## Si funksionon {#how-it-works}

X-Plane 11 dhe 12: ndërfaqja UDP e vetë simulatorit në portën 49000.

X-Plane i përgjigjet kujtdo që pyet te 127.0.0.1:49000, me ritmin e kërkuar,
te adresa dhe porta nga erdhi kërkesa (dokumenti i X-Plane "Exchanging Data with
X-Plane", i shpërndarë te `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS jep gjerësinë dhe gjatësinë si double (RREF vetëm si float, gjysmë metri
largësi), prandaj ai drejton pozicionin; RREF sjell pjesën tjetër dhe zëvendëson kur
RPOS nuk vjen. Datarefs (emrat si te `Resources\plugins\DataRefs.txt` i X-Plane 12,
<https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

dhe pjesa tjetër e fluturimit me të njëjtin ritëm (shpejtësia e vërtetë e ajrit, shpejtësia vertikale, AoA,
sideslip, drejtimi magnetik, Mach, g aksial dhe anësor, ritmet e rrotullimit, flaps,
speedbrake, gazi: `DATAREFS`), me gjendjen më të ngadaltë të avionit një herë në
sekondë (peshat, doreza e trenit të uljes, autopiloti, motorët, ora e simulatorit, pauza dhe
shpejtësia, moti: `SLOW_DATAREFS`). Çdo datagram ruhet edhe i plotë te
skedari anësor i papërpunuar i sesionit, dhe meta.json emërton dataref-in pas çdo indeksi RREF.

X-Plane 12 i pranon këto vetëm me Settings > Network > "Accept incoming
connections" të ndezur. Pozicionet futen në një hartë të sheshtë rreth pikës së parë
të fiksuar të seancës (`Tangent`): x lindje, z veri në metra, y lartësia mbi nivelin e detit - kështu një
fluturim i drejtë mbetet i drejtë sa larg të shkojë, ndërsa një plan i vërtetë
tangjent do ta përkulte poshtë me tokën. Origjina e hartës është `geo` i sesionit: meta.json
dhe fundi i tabelës e mbajnë, kështu që shikuesi mund ta vendosë botën e vërtetë poshtë
fluturimit.

Ky modul mban edhe çfarë ndajnë simulatorët e tjerë të fluturimit: hartën e sheshtë, llogaritjen
e fluturimit (ngritjet, uljet, përplasjet, distanca), soketin UDP dhe
listën e bibliotekës Steam.

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

- Shënuar si lojë që luhet online (`multiplayer`): **jo**. `games --markdown` e shfaq këtë si "single-player".
- Lloji `telemetry`: lexon vetëm atë që loja ose platforma e jep vetë (një port UDP ose memorie e përbashkët që loja e publikon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- RPOS (10 Hz): gjatësia, gjerësia, lartësia mbi nivelin e detit, AGL, pitch, drejtimi i vërtetë, roll, shpejtësia (lindje, lart, jug) dhe ritmet e rrotullimit P/Q/R - të gjitha te rreshtat
- RREF (10 Hz): 27 datarefs të `DATAREFS` - pozicioni, qëndrimi, IAS, shpejtësia mbi tokë, TAS, shpejtësia vertikale, AoA, sideslip, drejtimi magnetik, Mach, g normal/aksial/anësor, ritmet e rrotullimit, flaps, speedbrake, gazi, AGL, përplasja, në tokë, koha e fluturimit - te rreshtat
- RREF (1 Hz): 20 datarefs të `SLOW_DATAREFS` - peshat, doreza e trenit të uljes, servot e autopilotit, ora dhe data e simulatorit, pauza, shpejtësia e simulatorit, riluajtja, numri i motorëve, RPM e motorëve 1-4, N1 e motorëve 1-2, temperatura e ajrit jashtë, presioni në nivelin e detit - te rreshtat siç u morën së fundi

**Ruajtur të papërpunuara**

- çdo datagram i plotë si `payload`, nën kokën e vet me katër shkronja: `RREF` dhe `RPOS` (`used` kur pyetja bëri një rresht; në meny, pa pikë të fiksuar, nuk bëjnë asnjë), çdo gjë tjetër që X-Plane dërgon te porta e watcher-it nën kokën e vet ose `unknown`; `requests` i meta.json tregon cili dataref është çdo indeks RREF, kështu që payload-et lexohen pa këtë modul

**Nuk ofrohet**

- çdo dataref tjetër (X-Plane ka mijëra): RREF dërgon vetëm çfarë kërkohet, një abonim për secilin; lista kërkon fluturimin, gjendjen e avionit dhe kohën e simulatorit - më shumë detaje të kabinës (radiot, dritat, treguesit e çdo motori, defektet) do t'i shumëfishonin kërkesat
- emri i avionit dhe lloji ICAO: datarefs me varg bajtesh, që RREF i dërgon një float për çdo shkronjë
- avionët e tjerë (AI dhe multiplayer): datarefs sim/multiplayer/position nuk kërkohen
- dalja DATA (Settings > Data Output): dërgon te një adresë fikse e zgjedhur në simulator, jo te ai që pyet; RREF dhe RPOS mbulojnë çfarë lexon watcher

**Madhësia**: rreth 17 MB në orë para zstd (RREF dhe RPOS me 10 Hz, rreth 220 dhe 70 bajte plus një kuadër secili, RREF i ngadaltë një herë në sekondë), nëse X-Plane i dërgon vlerat e çdo pyetjeje në një paketë siç e bën; zstd i zvogëlon float-et disa herë

## Verifikuar {#verified}

u provua me një X-Plane të rremë që i përgjigjet RREF/RPOS sipas 'Exchanging Data with X-Plane' të X-Plane 12; emrat e dataref-eve u kontrolluan me DataRefs.txt të X-Plane 12; i paprovuar me simulatorin që punon

## Burimi {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
