---
title: "IL-2 Sturmovik: Great Battles (replaye)"
nav_order: 27
lang: "sk"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (replaye) {#il-2-sturmovik-great-battles-replays}

Po zápase IL-2 Sturmovik: Great Battles watcher prevedie replay, ktorý hra uložila, do súborov, ktoré si môžete pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `il2-tacview`, typ [`replay`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- každé lietadlo, vozidlo a loď zo záznamu: polohy raz za sekundu (metre na východ/nahor/na sever od referenčného bodu záznamu; zemepisná šírka, dĺžka a výška ako stĺpce)
- zrodenia, zničenia (smrť) a odlety (odišiel), vzlety a pristátia, ak sú zaznamenané
- objekty, zničené, vzlety, pristátia a dĺžka na jeden záznam
- každý riadok záznamu celý v heat.raw.parquet, v riadkoch času (#t)

## Odkiaľ to berie {#where-it-comes-from}

vlastné záznamy Tacview hry &lt;game>\data\Tracks\\\*.acmi (text ACMI 2.x, prostý alebo zazipovaný)

## Ako to zapnúť {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 v [KEY = track_record])

Príkaz napíšte do terminálu otvoreného v priečinku watchera (pozrite [Pred začiatkom](before-you-start.md)). Ak zlyhá, posledný riadok povie prečo; [Inštalácia a spustenie](installing-and-running.md) popisuje obvyklé príčiny.

`python -m heat3d_watch setup il2-tacview` vypíše súbory, ktoré by zmenil; `python -m heat3d_watch setup il2-tacview --apply` ich zmení a pôvodný súbor nechá ako `<file>.heat3d-backup` (pozrite [Príkazy](commands.md#setup)). Pri každej zmene vypíše `il2-tacview: changed: ...`, alebo `il2-tacview: nothing to change`, ak je už zapnuté.

## Ako to funguje {#how-it-works}

IL-2 Sturmovik: Great Battles - výstupné telemetrické UDP hry a jej vlastné záznamy Tacview.

1. Telemetria („Telemetry output of IL2 v4.003", revízia 1.2, dodávaná ako `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Zapína sa v `<game>\data\startup.cfg`, sekcia `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = „IP[:port]" (viac cieľov naraz), `decimation` (50 Hz / n), `enable`, `port`. `setup` pridá jeden cieľ, 127.0.0.1:41995 (JoyPro používa 41994, predvolený port hry je 4322), a výstup zapne. Pakety, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indikátory: 0 ENG_RPM, 1 ENG_MP, 2/3 otrasy motora, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz vrátane gravitácie), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Udalosti (2-bajtovo zabalené): 0 SET_FOCUS (STRING: bajt dĺžky + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB a 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT a 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Polohy udalostí sú lokálne voči lietadlu hráča; prúd nemá vôbec svetovú polohu - sú to teda udalosti a čísla, nie stopa.

2. Záznam Tacview: `tacviewrecord = 1` v `[KEY = track_record]` nechá hru zapisovať `<game>\data\Tracks\*.acmi` (v multiplayeri rozhoduje server). Hotový súbor sa prevedie: každé lietadlo, vozidlo a loď s polohami, zrodením a odstránením (zničený alebo odišiel), vzlety a pristátia, ak ich záznam má. Formát ACMI 2.x ako text, prostý alebo zazipovaný, podľa <https://www.tacview.net/documentation/acmi/en/> - riadky „#t" posúvajú hodiny, riadky „id,Key=Value,..." nastavujú vlastnosti (hexadecimálne ID, čiarky escapované „\\,", koncová „\\" pokračuje v riadku), „-id" odstráni objekt, objekt 0 nesie globálne hodnoty (ReferenceLongitude/Latitude, RecordingTime, ...) a udalosti („Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] alebo Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], dĺžka a šírka vzhľadom na referenciu, prázdne polia sa nemenia. Polohy idú do plochej mapy okolo referenčného bodu: x na východ, y výška, z na sever, v metroch. Referenčný bod je `geo` relácie, uložený v meta.json a v päte tabuľky, takže prehliadač vie položiť skutočný svet pod trate.

Ten istý modul slúži aj: [IL-2 Sturmovik: Great Battles (živé dáta)](game-il2.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Osa nahor | `y` |
| Jednotky | metre (na východ, výška, na sever od prvého zamerania) |
| Zrkadlenie pre prehliadač | `z` |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)".
- Druh `replay`: číta len to, čo hra alebo platforma sprístupňuje (replaye a dema, ktoré hra uloží), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- T každého objektu (dĺžka, šírka, výška, roll, pitch, yaw, U, V, heading) ako polohy raz za sekundu na objekt, s Name, Type, Pilot, Coalition/Color, Country, Group a Parent
- zrodenia, odstránenia (smrť, ak udalosť Destroyed prišla skôr, inak odišiel), udalosti TakenOff a Landed, udalosti Message a Bookmark ako riadky
- globálne hodnoty ReferenceLongitude/Latitude (počiatok mapy), RecordingTime/ReferenceTime (kedy), DataSource, DataRecorder a Title do meta.json

**Uchované surové**

- každý neprázdny logický riadok celý ako `text` (riadok pokračujúci koncovou „\\" sa spojí, ako ho číta ACMI), pod svojím druhom: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` a `event` (objekt 0), `object` (id,Key=Value,...)
- to, čo drží len surový záznam: polohy medzi jednosekundovými riadkami, zbrane, granáty, svetlice, plevy a ďalšie objekty, ktoré sa nekreslia ako stopy, každá iná vlastnosť (telemetria ako IAS, AOA, plyn, palivo, ak ju záznam má), iné globálne hodnoty (Comments, Briefing, Author, Category), udalosti iné ako tie čítané (Timeout, LeftArea, ...)

**Nie je k dispozícii**

- nič, čo záznam neobsahuje; čo hra do svojich záznamov nezapíše, v nich nie je

**Veľkosť**: približne text samotného záznamu plus okolo 70 bajtov na riadok pred zstd: 100 MB záznam dá približne 150-250 MB surových dát, ktoré zstd zmenší takmer na veľkosť zazipovaného záznamu

## Overené {#verified}

overené na syntetických súboroch ACMI 2.2 (text aj zazipované); nevyskúšané na zázname z hry

## Zdroj {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
