---
title: "iRacing (date în direct)"
nav_order: 28
lang: "ro"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (date în direct) {#iracing-live-data}

Cât timp jucați iRacing, watcher-ul salvează datele pe care jocul însuși le trimite, ca să le puteți vedea mai târziu sub formă de statistici și cronologie.

*Detalii tehnice: adaptorul `iracing`, tipul [`telemetry`](sources-and-rules.md); rulează cât timp `iRacingSim64DX11.exe` sau `iRacingSim64.exe` este pornit și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- conducerea, la 5 Hz, fără poziție (iRacing nu oferă una în direct): viteza, treapta, accelerația, frâna, tura, partea din tură, poziția în cursă și în clasă, incidentele
- începutul sesiunii, urcatul și coborâtul din mașină, intrarea și ieșirea de pe banda boxelor, ture cu timpul de tură, incidente cu punctele lor, steagul în carouri, sosirea
- fișierele de telemetrie .ibt scrise în timpul sesiunii (latitudine, longitudine, altitudine - le citește vizualizatorul)
- ture, cea mai bună tură, incidente, poziția în cursă, opriri la boxe, distanța, viteza maximă
- toată memoria partajată, în `heat.raw.parquet`: antetul, antetele variabilelor, informațiile sesiunii, fiecare linie de telemetrie citită

## De unde vine {#where-it-comes-from}

memoria partajată Local\IRSDKMemMapFileName (SDK-ul iRacing); fișiere .ibt în %USERPROFILE%\Documents\iRacing\telemetry

## Cum se activează {#how-to-switch-it-on}

Nimic pentru datele în direct. Pentru poziții: înregistrați telemetria în mașină (Alt+L) sau setați irsdkLog=1 în app.ini

## Cum funcționează {#how-it-works}

iRacing, în direct: SDK-ul iRacing prin memoria partajată, citită nativ.

iRacing își publică telemetria pentru aplicații într-un mapping de fișier numit, `Local\IRSDKMemMapFileName`, pe care simulatorul îl creează cât timp rulează (și semnalizează `Local\IRSDKDataValidEvent` la fiecare actualizare, ceea ce nu este necesar aici: watcher-ul citește de zece ori pe secundă). Layoutul este cel din `irsdk_defines.h` al SDK-ului, urmat și de pyirsdk (MIT) - scris din nou aici după aceste fapte:

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

Simulatorul scrie `numBuf` linii în ordine circulară; cea mai nouă este cea cu tickCount-ul cel mai mare, iar o linie se citește din nou dacă tickCount-ul ei s-a mișcat cât timp era copiată.

Datele în direct nu au poziție în lume - latitudinea, longitudinea și altitudinea există doar în fișierele `.ibt` pe care iRacing le înregistrează în `Documents\iRacing\telemetry` (Alt+L în mașină sau `irsdkLog=1`), pe care vizualizatorul 3DHeat le citește singur. Deci aceasta înregistrează conducerea ca evenimente fără coordonate - viteza, tura, partea din tură parcursă, poziția în cursă, incidentele - plus ture, incidente, opriri la boxe și steagul în carouri, iar la final fișierele `.ibt` scrise în timpul sesiunii ca evenimente `telemetry_file`, pe care vizualizatorul să le deschidă.

Alături de rânduri se păstrează harta completă a memoriei, în sidecarul brut al sesiunii (`heat.raw.parquet`): partea fixă a antetului (`header`, de fiecare dată când se schimbă), antetele variabilelor (`var_headers`, întregi, și ca JSON în `text`, de fiecare dată când se schimbă layoutul), textul YAML al informațiilor sesiunii (`session_info`, textul de fiecare dată când se mișcă `sessionInfoUpdate`) și cea mai nouă linie de telemetrie (`telemetry`, fiecare variabilă a ei, la fiecare citire care găsește un tick nou). Antetele variabilelor și o linie sunt tot ce are nevoie un decodor ulterior ca să citească orice variabilă.

Sursă: SDK-ul iRacing (irsdk_defines.h, documentația SDK din forumul iRacing); kutu/pyirsdk (MIT) pentru confirmarea decalajelor.

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | nu |
| Axa verticală | `y` |
| Unități | fără poziții în direct; fișierele .ibt au latitudinea/longitudinea/altitudinea |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)".
- Tipul `telemetry`: citește doar ce oferă jocul sau platforma (un port UDP sau memoria partajată pe care o publică jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- din cea mai nouă linie de telemetrie: timpul sesiunii, numărul, starea și id-ul, pe pistă, în reluare, tura, turele parcurse, partea și metrii din tură, ultima și cea mai bună tură, viteza, treapta, accelerația, frâna, turația, banda boxelor, suprafața pistei, poziția în cursă și în clasă, numărul propriu de incidente (rândurile `driving` la 5 Hz și evenimentele)
- acum și pe rândurile `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (grade, din radianii simulatorului - doar când antetul variabilei dă unitatea rad), `fuel_l` (unitatea l), `lat_accel` și `lon_accel` (unitatea m/s^2)
- din YAML-ul informațiilor sesiunii: indexul mașinii jucătorului, pista și configurația, tipurile de sesiune, numele fiecărui pilot, mașina, echipa și numărul (rânduri session_start, meta.json)
- verificat cu un bloc construit după irsdk_defines.h în teste; încă nu cu simulatorul

**Păstrat brut**

- `telemetry`: cea mai nouă linie întreagă, fiecare variabilă pe care o publică simulatorul (matricile CarIdx ale fiecărei mașini, roțile, suspensia, matricile `_ST` de mare frecvență acolo unde simulatorul le are ...), la fiecare citire care găsește un tick nou; `tick` numărul de ticuri al simulatorului; `used` este fals cât timp rulează o reluare
- `var_headers`: antetele variabilelor întregi (144 de octeți fiecare) și, în `text`, ca JSON (nume, tip, offset, număr, unitate, descriere), de fiecare dată când se schimbă layoutul - suficient ca să citească orice variabilă din fiecare linie păstrată
- `session_info`: textul YAML întreg de fiecare dată când se mișcă contorul de actualizare (weekend, sesiuni și rezultate, piloți, setările mașinii, radio, liste de camere), `update` contorul
- `header`: antetul irsdk de 112 octeți întreg de fiecare dată când se schimbă (versiunea, starea, rata ticurilor, decalajele, ticurile liniilor)

**Nu este disponibil**

- o poziție în lume în direct: memoria partajată nu are niciuna; latitudinea, longitudinea și altitudinea există doar în fișierele .ibt (cu înregistrarea pornită), pe care le citește vizualizatorul - watcher-ul numește pe cele scrise în timpul sesiunii
- ticurile dintre două citiri: simulatorul scrie 60 de linii pe secundă în 3 sau 4 sloturi, iar watcher-ul citește de 10 ori pe secundă, deci majoritatea ticurilor sunt suprascrise înainte să poată fi citite; fișierul .ibt are fiecare tick când înregistrarea este pornită

**Dimensiune**: o linie de telemetrie are câțiva KB (cam 5 până la 10 KB cu toate matricile fiecărei mașini), păstrată de până la 10 ori pe secundă, plus antetul (112 octeți) la fel de des și YAML-ul informațiilor sesiunii (zeci de KB) când se schimbă: aproximativ 0,2 până la 0,4 GB pe oră pe pistă înainte de compresie; zstd o aduce la o fracțiune (încă nemăsurată pe o sesiune reală)

## Verificat {#verified}

testat pe un bloc de memorie partajată construit în test după layoutul irsdk; netestat cu simulatorul

## Sursă {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
