---
title: "IL-2 Sturmovik: Great Battles (date în direct)"
nav_order: 26
lang: "ro"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (date în direct) {#il-2-sturmovik-great-battles-live-data}

Cât timp jucați IL-2 Sturmovik: Great Battles, watcher-ul salvează datele pe care jocul însuși le trimite, ca să le puteți vedea mai târziu sub formă de statistici și cronologie.

*Detalii tehnice: adaptorul `il2`, tipul [`telemetry`](sources-and-rules.md); rulează cât timp `Il-2.exe` sau `IL2Series.exe` este pornit și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- misiunile de zbor: avionul preluat (spawn) și momentul când se oprește ieșirea (session_end) - fără poziție în lume: jocul nu trimite una
- bombe și rachete lansate (masa), lovituri și daune primite, explozii, rafale de tragere - poziții locale față de avion
- viteza indicată echivalentă, AGL, viteza verticală, forța g, turația motorului o dată pe secundă, cu fiecare alt indicator din pachet (presiunea în galerie, vibrația motorului, starea și presiunea treptelor, AoA, alunecarea laterală, accelerațiile x/y/z, vibrația cabinei, flapsurile, frânele aerodinamice)
- misiuni de zbor, cartușe trase, bombe, rachete, lovituri primite, cea mai mare viteză, cea mai mare forță g, timpul de zbor; titlul serverului și numele pilotului online
- fiecare pachet de telemetrie, întreg, în heat.raw.parquet

## De unde vine {#where-it-comes-from}

ieșirea UDP de telemetrie a jocului către 127.0.0.1:41995 ([KEY = telemetrydevice] în &lt;joc>\data\startup.cfg)

## Cum se activează {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (adaugă addrN = "127.0.0.1:41995", enable = true), apoi reporniți IL-2

Scrieți comanda într-un terminal deschis în folderul watcher-ului (vedeți [Înainte de a începe](before-you-start.md)). Dacă eșuează, ultima linie spune de ce; [Instalarea și rularea](installing-and-running.md) acoperă cauzele obișnuite.

`python -m heat3d_watch setup il2` arată ce fișiere ar schimba; `python -m heat3d_watch setup il2 --apply` le schimbă, păstrând originalul ca `<file>.heat3d-backup` (vedeți [Comenzile](commands.md#setup)). Afișează `il2: changed: ...` pentru fiecare schimbare sau `il2: nothing to change` când este deja activat.

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

Același modul servește și: [IL-2 Sturmovik: Great Battles (reluări)](game-il2-tacview.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | nu |
| Axa verticală | `y` |
| Unități | niciuna: telemetria nu are poziții în lume |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)".
- Tipul `telemetry`: citește doar ce oferă jocul sau platforma (un port UDP sau memoria partajată pe care o publică jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- SET_FOCUS (avionul preluat: o misiune de zbor), DROP_BOMB și ROCKET_LAUNCH (masa, poziția locală), HIT și DAMAGE (poziția locală, forța), EXPLOSION (poziția locală, raza), GUN_FIRE (runde pe interogare) ca rânduri
- SETUP_ENG (index, id, poziția locală, turația maximă), SETUP_GUN (index, poziția locală, masa proiectilului, viteza gurii țevii) și SETUP_LGEAR (index, id, poziția locală) ca rânduri: motoarele, armele și picioarele trenului avionului la începutul misiunii
- SRV_TITLE, SRV_ADDR, SRS_ADDR și CLIENT_DAT (numele pilotului) în meta.json; coaliția din CTRL_DAT ca echipa misiunii
- toți cei cincisprezece indicatori ai specificației pe rândul `state` o dată pe secundă (o valoare ca număr, câte una pentru fiecare motor, picior de tren sau axă ca listă); cea mai mare viteză, forța g și AGL din fiecare pachet

**Păstrat brut**

- fiecare datagramă întreagă ca `payload`, sub Packet_ID-ul ei: `0x54000101` pentru telemetrie (folosit când a făcut un rând sau o intrare în meta.json), orice alt id ca atare, o datagramă prea scurtă pentru unul ca `short`
- ce are doar sidecarul brut: indicatorii dintre rândurile de o dată pe secundă (jocul îi trimite la 50 Hz / decimation), un eveniment SETUP mai scurt decât layoutul specificației, id-uri de evenimente pe care specificația nu le listează

**Nu este disponibil**

- o poziție în lume: ieșirea de telemetrie nu are niciuna (pozițiile evenimentelor sunt locale față de avion); adaptorul il2-tacview citește pozițiile din înregistrările Tacview ale jocului
- alte avioane și alți jucători: ieșirea descrie doar avionul propriu al jucătorului

**Dimensiune**: aproximativ 8 MB pe oră la 10 Hz, rata implicită a setup-ului (decimation 5; un pachet are cam 160 de octeți plus cadrul său), 40 MB la 50 Hz, rata completă a jocului, înainte de zstd; zstd micșorează floaturile repetitive la o fracțiune

## Verificat {#verified}

testat pe pachete construite după specificația Il2_TeleOutput a jocului (rev 1.2); modificările din startup.cfg testate pe o copie a fișierului; netestat cu jocul pornit

## Sursă {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
