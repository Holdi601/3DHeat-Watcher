---
title: "IL-2 Sturmovik: Great Battles (repriser)"
nav_order: 27
lang: "sv"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (repriser) {#il-2-sturmovik-great-battles-replays}

Efter en match i IL-2 Sturmovik: Great Battles gör watchern om den repris spelet sparade till filer som du kan titta på på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `il2-tacview`, slag [`replay`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel startar) och letar efter ny data var 5 s.*

## Vad som spelas in {#what-is-recorded}

- varje flygplan, fordon och fartyg i inspelningen: positioner en gång per sekund (meter öster/upp/norr från inspelningens referenspunkt; latitud/longitud/höjd som kolumner)
- uppträdanden, förstörelser (död) och avfärder (lämnat), start och landningar när de finns i inspelningen
- objekt, förstörda, start, landningar och längd per inspelning
- varje rad i inspelningen sparad helt i heat.raw.parquet, på raddernas klocka

## Var datan kommer ifrån {#where-it-comes-from}

spelets egna Tacview-inspelningar &lt;spel>\data\Tracks\\\*.acmi (ACMI 2.x-text, vanlig eller zippad)

## Så slår du på det {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 i [KEY = track_record])

Skriv kommandot i en terminal som öppnats i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger sista raden varför; [Installera och köra](installing-and-running.md) går igenom de vanliga orsakerna.

`python -m heat3d_watch setup il2-tacview` listar vilka filer den skulle ändra; `python -m heat3d_watch setup il2-tacview --apply` ändrar dem och sparar originalet som `<fil>.heat3d-backup` (se [Kommandon](commands.md#setup)). Den skriver `il2-tacview: changed: ...` för varje ändring, eller `il2-tacview: nothing to change` när den redan är påslagen.

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

Samma modul används också av: [IL-2 Sturmovik: Great Battles (livedata)](game-il2.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | meter (öster, höjd, norr från första positionen) |
| Speglad för visaren | `z` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `replay`: den läser bara det spelet eller plattformen lämnar ut (repriser och demon som spelet sparar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- varje objekts T (longitud, latitud, höjd, roll, pitch, yaw, U, V, kurs) som positioner en gång per sekund per objekt, med Name, Type, Pilot, Coalition/Color, Country, Group och Parent
- uppträdanden, borttagningar (död när en Destroyed-händelse kom först, annars lämnat), TakenOff- och Landed-händelser, Message- och Bookmark-händelser som rader
- de globala värdena ReferenceLongitude/Latitude (kartans origo), RecordingTime/ReferenceTime (när), DataSource, DataRecorder och Title i meta.json

**Sparas råa**

- varje icke-tom logisk rad helt som `text` (en rad som fortsätts med ett avslutande snedstreck sammanfogas, så som ACMI läser den), under sitt slag: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` och `event` (objekt 0), `object` (id,Key=Value,...)
- det som bara den råa sidofilen har: positionerna mellan de en-gång-per-sekund-raderna, vapen, granater, bloss, chaff och andra objekt som inte ritas som banor, varje annan egenskap (telemetri som IAS, AOA, gas, bränsle där inspelningen har den), andra globala värden (Comments, Briefing, Author, Category), händelser utöver de lästa (Timeout, LeftArea, ...)

**Finns inte**

- ingenting som inspelningen inte innehåller; det spelet inte skriver i sina inspelningar finns inte i dem

**Storlek**: ungefär inspelningens egen text plus ungefär 70 byte per rad, före zstd: en 100 MB-inspelning blir ungefär 150-250 MB rått, som zstd för nära storleken på den zippade inspelningen

## Verifierat {#verified}

testad på syntetiska ACMI 2.2-filer (text och zippade); ännu inte testad på en inspelning från spelet

## Källa {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
