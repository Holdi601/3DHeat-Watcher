---
title: "IL-2 Sturmovik: Great Battles (reluări)"
nav_order: 27
lang: "ro"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (reluări) {#il-2-sturmovik-great-battles-replays}

După un meci din IL-2 Sturmovik: Great Battles, watcher-ul transformă reluarea salvată de joc în fișiere pe care le puteți privi pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `il2-tacview`, tipul [`replay`](sources-and-rules.md); rulează tot timpul (nu așteaptă pornirea unui joc) și caută date noi la fiecare 5 s.*

## Ce se înregistrează {#what-is-recorded}

- fiecare avion, vehicul și navă din înregistrare: poziții o dată pe secundă (metri est/sus/nord față de punctul de referință al înregistrării; lat/lon/alt ca coloane)
- apariții, distrugeri (moarte) și plecări (left), decolări și aterizări când sunt înregistrate
- obiecte, distruse, decolări, aterizări și lungimea pentru fiecare înregistrare
- fiecare linie a înregistrării, păstrată întreagă în heat.raw.parquet, pe ceasul rândurilor

## De unde vine {#where-it-comes-from}

înregistrările Tacview ale jocului însuși &lt;joc>\data\Tracks\\\*.acmi (text ACMI 2.x, simplu sau zip)

## Cum se activează {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 în [KEY = track_record])

Scrieți comanda într-un terminal deschis în folderul watcher-ului (vedeți [Înainte de a începe](before-you-start.md)). Dacă eșuează, ultima linie spune de ce; [Instalarea și rularea](installing-and-running.md) acoperă cauzele obișnuite.

`python -m heat3d_watch setup il2-tacview` arată ce fișiere ar schimba; `python -m heat3d_watch setup il2-tacview --apply` le schimbă, păstrând originalul ca `<file>.heat3d-backup` (vedeți [Comenzile](commands.md#setup)). Afișează `il2-tacview: changed: ...` pentru fiecare schimbare sau `il2-tacview: nothing to change` când este deja activat.

## Cum funcționează {#how-it-works}

IL-2 Sturmovik: Great Battles - ieșirea UDP de telemetrie a jocului și înregistrările Tacview proprii ale acestuia.

1. Telemetria („Telemetry output of IL2 v4.003", revizia 1.2, livrată ca `<joc>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Se activează în `<joc>\data\startup.cfg`, secțiunea `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = „IP[:port]" (mai multe destinații deodată), `decimation` (50 Hz / n), `enable`, `port`. `setup` adaugă o destinație, 127.0.0.1:41995 (JoyPro folosește 41994, portul implicit al jocului este 4322), și activează ieșirea. Pachete, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indicatori: 0 ENG_RPM, 1 ENG_MP, 2/3 vibrația motorului, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz inclusiv gravitația), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Evenimente (împachetate pe 2 octeți): 0 SET_FOCUS (STRING: un octet de lungime + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB și 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT și 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Pozițiile evenimentelor sunt locale față de avionul jucătorului; fluxul nu are deloc poziție în lume - deci sunt evenimente și cifre, nu o traiectorie.

2. Înregistrarea Tacview: `tacviewrecord = 1` în `[KEY = track_record]` face ca jocul să scrie `<joc>\data\Tracks\*.acmi` (în multiplayer decide serverul). Un fișier terminat este convertit: fiecare avion, vehicul și navă cu pozițiile sale, apariția și scoaterea (distrus sau dispărut), decolările și aterizările când înregistrarea le are. Format text ACMI 2.x, simplu sau zip, conform <https://www.tacview.net/documentation/acmi/en/> - liniile „#t" mută ceasul, liniile „id,Key=Value,..." setează proprietăți (id-uri hexadecimale, virgulele scăpate „\\,", o „\\" de la sfârșit continuă linia), „-id" scoate un obiect, obiectul 0 poartă globalele (ReferenceLongitude/Latitude, RecordingTime, ...) și evenimentele („Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] sau Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], longitudinea și latitudinea față de referință, câmpurile goale rămân neschimbate. Pozițiile intră într-o hartă plată în jurul punctului de referință: x est, y altitudine, z nord, metri. Punctul de referință este `geo` al sesiunii, purtat în meta.json și în subsolul tabelului, ca vizualizatorul să poată așeza lumea reală sub trasee.

Același modul servește și: [IL-2 Sturmovik: Great Battles (date în direct)](game-il2.md).

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

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)".
- Tipul `replay`: citește doar ce oferă jocul sau platforma (reluările și demo-urile pe care le salvează jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- T-ul fiecărui obiect (longitudinea, latitudinea, altitudinea, roll, pitch, yaw, U, V, direcția) ca poziții o dată pe secundă pentru fiecare obiect, cu Name, Type, Pilot, Coalition/Color, Country, Group și Parent
- apariții, scoateri (moartea când un eveniment Destroyed a venit primul, altfel left), evenimente TakenOff și Landed, evenimente Message și Bookmark ca rânduri
- globalele ReferenceLongitude/Latitude (originea hărții), RecordingTime/ReferenceTime (când), DataSource, DataRecorder și Title în meta.json

**Păstrat brut**

- fiecare linie logică nevidă, întreagă, ca `text` (o linie continuată cu o „\\" de la sfârșit este unită, cum o citește ACMI), sub tipul ei: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` și `event` (obiectul 0), `object` (id,Key=Value,...)
- ce are doar sidecarul brut: pozițiile dintre rândurile de o dată pe secundă, armele, proiectilele, flarele, chaff-ul și alte obiecte care nu sunt desenate ca trasee, orice altă proprietate (telemetria precum IAS, AOA, accelerația, combustibilul, acolo unde înregistrarea le are), alte globale (Comments, Briefing, Author, Category), evenimente diferite de cele citite (Timeout, LeftArea, ...)

**Nu este disponibil**

- nimic din ce conține înregistrarea; ce nu scrie jocul în înregistrările sale nu se află în ele

**Dimensiune**: aproximativ textul înregistrării plus cam 70 de octeți pe linie, înainte de zstd: o înregistrare de 100 MB face cam 150-250 MB brut, pe care zstd îl aduce aproape de dimensiunea înregistrării zip

## Verificat {#verified}

testat pe fișiere ACMI 2.2 sintetice (text și zip); netestat pe o înregistrare din joc

## Sursă {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
