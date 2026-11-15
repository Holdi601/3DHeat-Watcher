---
title: "X-Plane (date în direct)"
nav_order: 50
lang: "ro"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (date în direct) {#x-plane-live-data}

Cât timp jucați X-Plane, watcher-ul salvează datele pe care jocul însuși le trimite, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `xplane`, tipul [`telemetry`](sources-and-rules.md); rulează cât timp `X-Plane.exe` este pornit și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- propria poziție, la 10 Hz (latitudine/longitudine/altitudine ca metri est/sus/nord de prima fixare; lat/lon/alt păstrate ca coloane)
- atitudinea, viteza indicată și reală, viteza față de sol, Mach, viteza verticală, AoA, alunecarea laterală, direcția magnetică, AGL, forțele g (normală, axială, laterală), vitezele și ratele de rotație, flapsurile, frânele aerodinamice, manetele, pe sol
- greutățile (totală, combustibil, încărcătură), maneta de tren, pilotul automat, turația și N1 ale motorului, timpul și data din simulator, pauza, viteza simulării, reluarea, temperatura exterioară și presiunea la nivelul mării (X-Plane 12) o dată pe secundă
- decolări, aterizări, prăbușiri, resetări de zbor (session_start/session_end pe fiecare zbor)
- timpul de zbor, timpul în aer, distanța, altitudinea maximă, forța g maximă, aterizări
- fiecare răspuns trimis de X-Plane, întreg, în heat.raw.parquet

## De unde vine {#where-it-comes-from}

interfața UDP a X-Plane pe 127.0.0.1:49000 (RREF datarefs și RPOS poziția, răspunse watcher-ului)

## Cum se activează {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 răspunde implicit)

## Cum funcționează {#how-it-works}

X-Plane 11 și 12: interfața UDP proprie a simulatorului, pe portul 49000.

X-Plane răspunde oricui cere pe 127.0.0.1:49000, la rata cerută, către adresa și portul de unde a venit cererea (documentul „Exchanging Data with X-Plane" al X-Plane, livrat în `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS dă latitudinea și longitudinea ca double, RREF doar ca float, la jumătate de metru distanță una de alta, deci RPOS conduce poziția; RREF aduce restul și ține locul când RPOS nu vine. Datarefs (numele ca în `Resources\plugins\DataRefs.txt` din X-Plane 12, <https://developer.x-plane.com/datarefs/>):

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

Restul zborului, la aceeași rată (viteza reală, viteza verticală, AoA, alunecarea laterală, direcția magnetică, Mach, forțele g axială și laterală, ratele de rotație, flapsurile, frânele aerodinamice, manetele: `DATAREFS`), cu starea mai lentă a aeronavei o dată pe secundă (greutăți, maneta de tren, pilotul automat, motoarele, timpul simulatorului, pauza și viteza, vremea: `SLOW_DATAREFS`). Fiecare datagramă se păstrează și ea întreagă în sidecarul brut al sesiunii, iar meta.json numește dataref-ul din spatele fiecărui index RREF.

X-Plane 12 acceptă aceste cereri doar cu Settings > Network > „Accept incoming connections" activat. Pozițiile intră într-o hartă plată în jurul primei fixări a sesiunii (`Tangent`): x est, z nord în metri, y altitudinea deasupra nivelului mării - astfel încât un zbor orizontal rămâne orizontal oricât de departe ajunge, lucru pe care un plan tangent adevărat l-ar încovoia odată cu Pământul. Originea hărții este `geo` al sesiunii: meta.json și subsolul tabelului o poartă, ca vizualizatorul să poată așeza lumea reală sub zbor.

Acest modul adăpostește și ce au în comun celelalte simulatoare de zbor: harta plată, contabilitatea zborului (decolările, aterizările, prăbușirile, distanța), socketul UDP și lista de biblioteci Steam.

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | metri (est, altitudine, nord de la prima fixare) |
| Oglindit pentru vizualizator | `z` |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **nu**. `games --markdown` arată asta ca „un singur jucător".
- Tipul `telemetry`: citește doar ce oferă jocul sau platforma (un port UDP sau memoria partajată pe care o publică jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- RPOS (10 Hz): longitudinea, latitudinea, altitudinea, AGL, pitch, direcția reală, roll, viteza (est, sus, sud) și ratele de rotație P/Q/R - toate pe rânduri
- RREF (10 Hz): cele 27 de datarefs ale `DATAREFS` - poziția, atitudinea, IAS, viteza față de sol, TAS, viteza verticală, AoA, alunecarea laterală, direcția magnetică, Mach, forțele g normală/axială/laterală, ratele de rotație, flapsurile, frânele aerodinamice, manetele, AGL, prăbușit, pe sol, timpul de zbor - pe rânduri
- RREF (1 Hz): cele 20 de datarefs ale `SLOW_DATAREFS` - greutățile, maneta de tren, servomotoarele pilotului automat, timpul și data din simulator, pauza, viteza simulării, reluarea, numărul de motoare, turația motoarelor 1-4, N1 al motoarelor 1-2, temperatura aerului exterior, presiunea la nivelul mării - pe rânduri, ca ultima valoare primită

**Păstrat brut**

- fiecare datagramă întreagă ca `payload`, sub cele patru litere ale antetului: `RREF` și `RPOS` (folosite când interogarea a făcut un rând; în meniuri, fără fixare, nu fac niciunul), orice altceva trimite X-Plane către portul watcher-ului sub antetul său sau `unknown`; `requests` din meta.json spune ce dataref este fiecare index RREF, deci payload-urile se citesc fără acest modul

**Nu este disponibil**

- fiecare alt dataref (X-Plane are mii): RREF trimite doar ce i se cere, câte o abonare pentru fiecare; lista cere zborul, starea aeronavei și timpul simulatorului - mai mult detaliu de cabină (radiouri, lumini, fiecare indicator al motorului, defecțiuni) ar înmulți cererile
- numele aeronavei și tipul ICAO: datarefs de tip tablou de octeți, pe care RREF le trimite câte un float pe caracter
- alte aeronave (AI și multiplayer): datarefs sim/multiplayer/position nu sunt cerute
- ieșirea DATA (Settings > Data Output): trimite către o adresă fixă aleasă în simulator, nu către cine cere; RREF și RPOS acoperă ce citește watcher-ul

**Dimensiune**: aproximativ 17 MB pe oră înainte de zstd (RREF și RPOS la 10 Hz, cu cam 220 și 70 de octeți plus un cadru fiecare, RREF-ul lent o dată pe secundă), dacă X-Plane trimite valorile fiecărei interogări într-un singur pachet, cum face; zstd reduce floaturile de câteva ori

## Verificat {#verified}

testat pe un X-Plane fals care răspunde RREF/RPOS după „Exchanging Data with X-Plane" din X-Plane 12; numele datarefs verificate după DataRefs.txt din X-Plane 12; netestat cu simulatorul pornit

## Sursă {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
