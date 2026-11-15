---
title: "IL-2 Sturmovik: Great Battles (live-data)"
nav_order: 26
lang: "da"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (live-data) {#il-2-sturmovik-great-battles-live-data}

Mens du spiller IL-2 Sturmovik: Great Battles, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem som statistik og en tidslinje.

*Tekniske detaljer: adapter `il2`, type [`telemetry`](sources-and-rules.md); den kører, mens `Il-2.exe` eller `IL2Series.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- togter: det fly, der tages (spawn), og hvornår udgangen stopper (session_end) - ingen verdensposition: spillet sender ingen
- bomber og raketter sluppet (masse), træf og skader modtaget, eksplosioner, skudsalver - positioner lokale for flyet
- ækvivalent lufthastighed, AGL, lodret hastighed, g, motoromdrejninger én gang i sekundet, med alle andre indikatorer pakken bærer (manifoldtryk, motorrystelse, gearstatus og -tryk, AoA, sideglidning, acceleration x/y/z, cockpitrystelse, klapper, luftbremser)
- togter, skud affyret, bomber, raketter, modtagne træf, højeste hastighed, højeste g, flyvetid; serverens titel og pilotnavn online
- hver telemetripakke gemt hel i heat.raw.parquet

## Hvor data kommer fra {#where-it-comes-from}

spillets telemetri-UDP-udgang til 127.0.0.1:41995 ([KEY = telemetrydevice] i &lt;game>\data\startup.cfg)

## Sådan slår du det til {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (tilføjer addrN = "127.0.0.1:41995", enable = true), genstart IL-2

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du går i gang](before-you-start.md)). Hvis den fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

`python -m heat3d_watch setup il2` viser de filer, den ville ændre; `python -m heat3d_watch setup il2 --apply` ændrer dem og gemmer originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `il2: changed: ...` for hver ændring, eller `il2: nothing to change`, når den allerede er slået til.

## Sådan virker det {#how-it-works}

IL-2 Sturmovik: Great Battles - spillets telemetri-UDP-udgang og dets egne Tacview-optagelser.

1. Telemetri ("Telemetry output of IL2 v4.003", revision 1.2, leveret som
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Slået til i
   `<game>\data\startup.cfg`, sektion `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:port]" (flere mål samtidig), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` tilføjer ét mål, 127.0.0.1:41995 (JoyPro bruger
   41994, spillets standard er 4322), og slår udgangen til. Pakker,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indikatorer: 0 ENG_RPM, 1 ENG_MP, 2/3 motorrystelse, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz inkl. tyngdekraft),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Hændelser (2-byte pakket): 0 SET_FOCUS (STRING: længdebyte +
   ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB og 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT og 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Hændelsespositioner er lokale for spillerens fly; strømmen
   har slet ingen verdensposition - så det er hændelser og tal, ikke en rute.

2. Tacview-optagelse: `tacviewrecord = 1` i `[KEY = track_record]` får spillet til at skrive
   `<game>\data\Tracks\*.acmi` (i multiplayer bestemmer serveren). En færdig fil
   konverteres: hvert fly, køretøj og skib med sine positioner, spawn og fjernelse (ødelagt eller
   væk), start og landinger når optagelsen har dem. ACMI 2.x-tekstformat, almindelig eller
   zippet, efter <https://www.tacview.net/documentation/acmi/en/> - "#t"-linjer flytter uret,
   "id,Key=Value,..."-linjer sætter egenskaber (hex-id'er, kommaer escaped "\\,", en
   afsluttende "\\" fortsætter linjen), "-id" fjerner et objekt, objekt 0 bærer
   de globale værdier (ReferenceLongitude/Latitude, RecordingTime, ...) og hændelserne
   ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] eller
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], længde- og breddegrad i forhold til
   referencen, tomme felter uændrede. Positionerne lægges i et fladt kort omkring
   referencepunktet: x øst, y højde, z nord, meter. Referencepunktet er sessionens `geo`, som bæres i meta.json og tabellens
   footer, så vieweren kan lægge den rigtige verden under banerne.

Modulet dækker også: [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | nej |
| Op-akse | `y` |
| Enheder | ingen: telemetrien har ingen verdensposition |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det spillet udleverer)".
- Type `telemetry`: den læser kun det, spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- SET_FOCUS (det fly, der tages: et tog), DROP_BOMB og ROCKET_LAUNCH (masse, lokal position), HIT og DAMAGE (lokal position, kraft), EXPLOSION (lokal position, radius), GUN_FIRE (runder pr. aflæsning) som rækker
- SETUP_ENG (indeks, id, lokal position, maksimal omdrejningstal), SETUP_GUN (indeks, lokal position, projektilmasse, mundingshastighed) og SETUP_LGEAR (indeks, id, lokal position) som rækker: flyets motorer, våben og understel, når toget begynder
- SRV_TITLE, SRV_ADDR, SRS_ADDR og CLIENT_DAT (pilotnavn) i meta.json; CTRL_DATs coalition som togets hold
- alle femten indikatorer i specifikationen på den én-gang-i-sekundet `state`-række (én værdi som et tal, én pr. motor, gearben eller akse som en liste); højeste hastighed, g og AGL fra hver pakke

**Gemt råt**

- hver datagram hel som `payload`, under sit Packet_ID: `0x54000101` for telemetri (brugt, når den lavede en række eller en meta.json-post), ethvert andet id som det selv, en datagram der er for kort til en, som `short`
- det kun råsidefilen holder: indikatorerne mellem de én-gang-i-sekundet-rækker (spillet sender dem med 50 Hz / decimation), en SETUP-hændelse kortere end specifikationens layout, hændelsesid'er specifikationen ikke nævner

**Ikke tilgængeligt**

- en verdensposition: telemetriudgangen har ingen (hændelsespositioner er lokale for flyet); il2-tacview-adapteren læser positioner fra spillets egne Tacview-optagelser
- andre fly og spillere: udgangen beskriver kun spillerens eget fly

**Størrelse**: cirka 8 MB i timen ved setups 10 Hz (decimation 5; en pakke er cirka 160 bytes plus sin ramme), 40 MB ved spillets fulde 50 Hz, før zstd; zstd krymper de gentagne floats til en brøkdel

## Verificeret {#verified}

testet på pakker bygget ud fra spillets egen Il2_TeleOutput-specifikation (rev 1.2); ændringer i startup.cfg testet på en kopi af filen; ikke testet mod det kørende spil

## Kilde {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
