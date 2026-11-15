---
title: "IL-2 Sturmovik: Great Battles (živé dáta)"
nav_order: 26
lang: "sk"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (živé dáta) {#il-2-sturmovik-great-battles-live-data}

Počas hry IL-2 Sturmovik: Great Battles watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť ako štatistiky a časovú os.

*Technické údaje: adaptér `il2`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `Il-2.exe` alebo `IL2Series.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- lety: lietadlo, ktoré bolo prevzaté (spawn), a kedy výstup prestane (session_end) - bez svetovej polohy: hra žiadnu neposiela
- zhodené bomby a vypustené rakety (hmotnosť), zásahy a prijaté poškodenie, výbuchy, dávky streľby - polohy lokálne voči lietadlu
- ekvivalentná vzdušná rýchlosť, AGL, vertikálna rýchlosť, g, otáčky motora raz za sekundu, so všetkými ostatnými indikátormi, ktoré paket nesie (pretlak sania, otrasy motora, stav a tlak podvozku, AoA, bočný sklz, zrýchlenie x/y/z, otrasy kabíny, klapky, brzdové klapky)
- lety, vystrelené náboje, bomby, rakety, zasiahnutia, najvyššia rýchlosť, najvyššie g, čas letu; názov servera a meno pilota online
- každý telemetrický paket celý v heat.raw.parquet

## Odkiaľ to berie {#where-it-comes-from}

telemetrický UDP výstup hry na 127.0.0.1:41995 ([KEY = telemetrydevice] v &lt;game>\data\startup.cfg)

## Ako to zapnúť {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (pridá addrN = "127.0.0.1:41995", enable = true), potom reštartujte IL-2

Príkaz napíšte do terminálu otvoreného v priečinku watchera (pozrite [Pred začiatkom](before-you-start.md)). Ak zlyhá, posledný riadok povie prečo; [Inštalácia a spustenie](installing-and-running.md) popisuje obvyklé príčiny.

`python -m heat3d_watch setup il2` vypíše súbory, ktoré by zmenil; `python -m heat3d_watch setup il2 --apply` ich zmení a pôvodný súbor nechá ako `<file>.heat3d-backup` (pozrite [Príkazy](commands.md#setup)). Pri každej zmene vypíše `il2: changed: ...`, alebo `il2: nothing to change`, ak je už zapnuté.

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

2. Záznam Tacview: `tacviewrecord = 1` v `[KEY = track_record]` nechá hru zapisovať `<game>\data\Tracks\*.acmi` (v multiplayeri rozhoduje server). Hotový súbor sa prevedie: každé lietadlo, vozidlo a loď s polohami, zrodením a odstránením (zničený alebo odišiel), vzlety a pristátia, ak ich záznam má. Formát ACMI 2.x ako text, prostý alebo zazipovaný, podľa <https://www.tacview.net/documentation/acmi/en/> - riadky „#t" posúvajú hodiny, riadky „id,Key=Value,..." nastavujú vlastnosti (hexadecimálne ID, čiarky escapované „\\,", koncová „\\" pokračuje v riadku), „-id" odstráni objekt, objekt 0 nesie globálne hodnoty (ReferenceLongitude/Latitude, RecordingTime, ...) a udalosti („Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] alebo Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], dĺžka a šírka vzhľadom na referenciu, prázdne polia sa nemenia. Polohy idú do plochej mapy okolo referenčného bodu: x na východ, y výška, z na sever, v metroch. Referenčný bod je `geo` relácie, uložený v meta.json a v päte tabuľky, takže prehliadač vie položiť skutočný svet pod lety.

Ten istý modul slúži aj: [IL-2 Sturmovik: Great Battles (replaye)](game-il2-tacview.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | nie |
| Osa nahor | `y` |
| Jednotky | žiadne: telemetria nemá svetové polohy |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)".
- Druh `telemetry`: číta len to, čo hra alebo platforma sprístupňuje (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- SET_FOCUS (prevzaté lietadlo: let), DROP_BOMB a ROCKET_LAUNCH (hmotnosť, lokálna poloha), HIT a DAMAGE (lokálna poloha, sila), EXPLOSION (lokálna poloha, polomer), GUN_FIRE (výstrely za dopyt) ako riadky
- SETUP_ENG (index, id, lokálna poloha, maximálne otáčky), SETUP_GUN (index, lokálna poloha, hmotnosť strely, úsťová rýchlosť) a SETUP_LGEAR (index, id, lokálna poloha) ako riadky: motory, zbrane a podvozkové nohy lietadla, keď let začína
- SRV_TITLE, SRV_ADDR, SRS_ADDR a CLIENT_DAT (meno pilota) do meta.json; tím letu z koalície v CTRL_DAT
- všetkých pätnásť indikátorov špecifikácie na riadku `state` raz za sekundu (jedna hodnota ako číslo, jedna na motor, podvozkovú nohu alebo os ako zoznam); najvyššia rýchlosť, g a AGL zo všetkých paketov

**Uchované surové**

- každý datagram celý ako `payload`, pod svojím Packet_ID: `0x54000101` pre telemetriu (použité, keď vytvoril riadok alebo položku meta.json), iné ID ako ono samo, datagram príliš krátky na to ako `short`
- to, čo drží len surový záznam: indikátory medzi jednosekundovými riadkami (hra ich posiela pri 50 Hz / decimation), udalosť SETUP kratšia ako rozloženie špecifikácie, ID udalostí, ktoré špecifikácia neuvádza

**Nie je k dispozícii**

- svetová poloha: telemetrický výstup ju nemá (polohy udalostí sú lokálne voči lietadlu); adaptér il2-tacview číta polohy z vlastných záznamov Tacview hry
- iné lietadlá a hráči: výstup opisuje len vlastné lietadlo hráča

**Veľkosť**: približne 8 MB za hodinu pri 10 Hz z nastavenia `setup` (decimation 5; paket má okolo 160 bajtov plus rámec), 40 MB pri plných 50 Hz hry, pred zstd; zstd zmenší opakujúce sa floaty na zlomok

## Overené {#verified}

overené na paketoch zostavených podľa vlastnej špecifikácie hry Il2_TeleOutput (rev 1.2); úpravy startup.cfg overené na kópii súboru; nevyskúšané na bežiacej hre

## Zdroj {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
