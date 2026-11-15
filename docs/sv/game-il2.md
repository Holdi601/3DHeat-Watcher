---
title: "IL-2 Sturmovik: Great Battles (livedata)"
nav_order: 26
lang: "sv"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (livedata) {#il-2-sturmovik-great-battles-live-data}

När du spelar IL-2 Sturmovik: Great Battles sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den som statistik och en tidslinje.

*Tekniska detaljer: adapter `il2`, slag [`telemetry`](sources-and-rules.md); den körs medan `Il-2.exe` eller `IL2Series.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- sorteringar: flygplanet som tas (spawn) och när utgången upphör (session_end) - ingen världsposition, spelet skickar ingen
- bomber och raketer som släpps (massa), träffar och skador som tas, explosioner, eldskurar - positioner lokala för flygplanet
- ekvivalent lufthastighet, AGL, vertikal hastighet, g, motorvarvtal en gång per sekund, med alla andra indikatorer paketet bär (laddtryck, motorvibration, växelläge och tryck, anfallsvinkel, sidglidning, acceleration x/y/z, kabinvibration, klaffar, luftbromsar)
- sorteringar, avfyrade skott, bomber, raketer, träffar tagna, högsta fart, högsta g, flygtid; serverns titel och pilotnamn online
- varje telemetripaket sparat helt i heat.raw.parquet

## Var datan kommer ifrån {#where-it-comes-from}

spelets telemetri-UDP-utgång till 127.0.0.1:41995 ([KEY = telemetrydevice] i &lt;spel>\data\startup.cfg)

## Så slår du på det {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (lägger till addrN = "127.0.0.1:41995", enable = true), starta om IL-2

Skriv kommandot i en terminal som öppnats i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger sista raden varför; [Installera och köra](installing-and-running.md) går igenom de vanliga orsakerna.

`python -m heat3d_watch setup il2` listar vilka filer den skulle ändra; `python -m heat3d_watch setup il2 --apply` ändrar dem och sparar originalet som `<fil>.heat3d-backup` (se [Kommandon](commands.md#setup)). Den skriver `il2: changed: ...` för varje ändring, eller `il2: nothing to change` när den redan är påslagen.

## Så fungerar det {#how-it-works}

IL-2 Sturmovik: Great Battles - spelets telemetri-UDP-utgång, och dess egna Tacview-inspelningar.

1. Telemetri ("Telemetry output of IL2 v4.003", revision 1.2, levererad som
   `<spel>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Påslagen i
   `<spel>\data\startup.cfg`, avsnittet `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:port]" (flera mål samtidigt), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` lägger till ett mål, 127.0.0.1:41995 (JoyPro använder
   41994, spelets standard är 4322), och slår på utgången. Paketen, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indikatorer: 0 ENG_RPM, 1 ENG_MP, 2/3 motorvibration, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz inklusive gravitation),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Händelser (2-byte packade): 0 SET_FOCUS (STRING: längdbyte + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB och 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT och 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Händelsernas positioner är lokala för spelarens flygplan; strömmen
   har ingen världsposition alls - så det här är händelser och siffror, inte en bana.

2. Tacview-inspelning: `tacviewrecord = 1` i `[KEY = track_record]` gör att
   spelet skriver `<spel>\data\Tracks\*.acmi` (i flerspelarläge bestämmer servern).
   En färdig fil konverteras: varje flygplan, fordon och fartyg med sina
   positioner, uppträdande och borttagning (förstörd eller borta), start och landningar när
   inspelningen har dem. ACMI 2.x-textformat, vanlig eller zippad, enligt
   <https://www.tacview.net/documentation/acmi/en/> - rader "#t" flyttar klockan, rader
   "id,Key=Value,..." sätter egenskaper (hexadecimala id, kommatecken escapade "\\,", ett
   avslutande "\\" fortsätter raden), "-id" tar bort ett objekt, objekt 0 bär
   globala värden (ReferenceLongitude/Latitude, RecordingTime, ...) och händelserna
   ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] eller
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], longitud och latitud relativt
   referensen, tomma fält oförändrade. Positionerna läggs i en platt karta kring
   referenspunkten: x österut, y höjd, z norrut, meter. Referenspunkten är sessionens `geo`,
   bärs i meta.json och tabellens fotnot, så att visaren kan lägga den verkliga världen under banorna.

Samma modul används också av: [IL-2 Sturmovik: Great Battles (repriser)](game-il2-tacview.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | nej |
| Upp-axel | `y` |
| Enheter | inga: telemetrin har inga världspositioner |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- SET_FOCUS (flygplanet som tas: en sortering), DROP_BOMB och ROCKET_LAUNCH (massa, lokal position), HIT och DAMAGE (lokal position, kraft), EXPLOSION (lokal position, radie), GUN_FIRE (skott per avfrågning) som rader
- SETUP_ENG (index, id, lokal position, högsta varvtal), SETUP_GUN (index, lokal position, projektilens massa, mynningshastighet) och SETUP_LGEAR (index, id, lokal position) som rader: flygplanets motorer, kanoner och hjulben när sorteringen börjar
- SRV_TITLE, SRV_ADDR, SRS_ADDR och CLIENT_DAT (pilotnamn) i meta.json; CTRL_DAT:s koalition som sorteringens lag
- alla femton indikatorerna i specen på den en-gång-per-sekund-raden `state` (ett värde som ett tal, ett per motor, hjulben eller axel som en lista); högsta fart, g och AGL från varje paket

**Sparas råa**

- varje datagram helt som `payload`, under sitt Packet_ID: `0x54000101` för telemetri (använd när det gav en rad eller en meta.json-post), annat id som det är, ett datagram för kort för ett sådant som `short`
- det som bara den råa sidofilen har: indikatorerna mellan de en-gång-per-sekund-raderna (spelet skickar dem med 50 Hz / decimation), en SETUP-händelse kortare än specens layout, händelse-id som specen inte listar

**Finns inte**

- en världsposition: telemetriutgången har ingen (händelsernas positioner är lokala för flygplanet); il2-tacview-adaptern läser positioner från spelets egna Tacview-inspelningar
- andra flygplan och spelare: utgången beskriver bara spelarens eget flygplan

**Storlek**: ungefär 8 MB per timme vid setups 10 Hz (decimation 5; ett paket är ungefär 160 byte plus sin ram), 40 MB vid spelets fulla 50 Hz, före zstd; zstd krymper de repetitiva flyttalen till en bråkdel

## Verifierat {#verified}

testad på paket byggda från spelets egen Il2_TeleOutput-specifikation (rev 1.2); startup.cfg-ändringar testade på en kopia av filen; ännu inte testad mot det körande spelet

## Källa {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
