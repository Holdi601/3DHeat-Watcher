---
title: "IL-2 Sturmovik: Great Battles (replaye)"
nav_order: 27
lang: "cs"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (replaye) {#il-2-sturmovik-great-battles-replays}

Po bitvě v IL-2 Sturmovik: Great Battles Watcher promění replay, který hra uložila, na soubory, na které se můžete podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `il2-tacview`, druh [`replay`](sources-and-rules.md); běží pořád (nečeká, až se hra spustí) a hledá nová data každých 5 s.*

## Co se zaznamenává {#what-is-recorded}

- každé letadlo, vozidlo a loď ze záznamu: pozice jednou za sekundu (metry na východ/nahoru/na sever od referenčního bodu záznamu; zeměpisná šířka, délka a výška jako sloupce)
- objevení (spawn), zničení (death) a odlety (left), vzlety a přistání, pokud jsou v záznamu
- objekty, zničené, vzlety, přistání a délka na každý záznam
- každý řádek záznamu celý v heat.raw.parquet, s časem řádku

## Odkud to pochází {#where-it-comes-from}

vlastní Tacview záznamy hry &lt;game>\data\Tracks\\\*.acmi (text ACMI 2.x, prostý nebo zabalený do zipu)

## Jak to zapnout {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 v [KEY = track_record])

Příkaz napište do terminálu otevřeného ve složce Watcheru (viz [Než začnete](before-you-start.md)). Pokud selže, poslední řádek řekne proč; [Instalace a spuštění](installing-and-running.md) popisuje obvyklé příčiny.

`python -m heat3d_watch setup il2-tacview` vypíše soubory, které by změnil; `python -m heat3d_watch setup il2-tacview --apply` je opravdu změní a původní soubor uloží jako `<file>.heat3d-backup` (viz [Příkazy](commands.md#setup)). Pro každou změnu vypíše `il2-tacview: changed: ...`, nebo `il2-tacview: nothing to change`, když je už zapnuto.

## Jak to funguje {#how-it-works}

IL-2 Sturmovik: Great Battles – telemetrický UDP výstup hry a její vlastní Tacview záznamy.

1. Telemetrie („Telemetry output of IL2 v4.003“, revize 1.2, dodávaná jako
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Zapíná se v
   `<game>\data\startup.cfg`, v sekci `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = „IP[:port]“ (několik cílů najednou), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` přidá jeden cíl, 127.0.0.1:41995 (JoyPro používá
   41994, výchozí port hry je 4322), a výstup zapne. Pakety,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indikátory: 0 ENG_RPM, 1 ENG_MP, 2/3 třes motoru, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz včetně gravitace),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Události (2bajtově zabalené): 0 SET_FOCUS (STRING: bajt
   délky + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB a 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT a 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Pozice událostí jsou vztaženy k letadlu hráče; proud nemá vůbec
   žádnou pozici ve světě – jde tedy o události a čísla, ne o trasu.

2. Tacview záznam: `tacviewrecord = 1` v `[KEY = track_record]` nechá hru zapsat
   `<game>\data\Tracks\*.acmi` (ve hře pro více hráčů rozhoduje server).
   Dokončený soubor se převede: každé letadlo, vozidlo a loď se svými
   pozicemi, objevením a odstraněním (zničení nebo odlet), vzlety a přistání,
   pokud je v záznamu mají. Formát ACMI 2.x v textu, prostý nebo zabalený do zipu,
   podle <https://www.tacview.net/documentation/acmi/en/> – řádky „#t“ posouvají hodiny,
   řádky „id,Key=Value,...“ nastavují vlastnosti (hexadecimální id, čárky
   escapované „\\,“, koncová „\\“ pokračuje na dalším řádku), „-id“ objekt odstraní,
   objekt 0 nese globální údaje (ReferenceLongitude/Latitude, RecordingTime, ...)
   a události („Event=Destroyed\|id\|text“). T = Lon\|Lat\|Alt[\|U\|V] nebo
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], délka a šířka vztažené k
   referenci, prázdná pole se nemění. Pozice se ukládají do ploché mapy kolem
   referenčního bodu: x na východ, y výška, z na sever, v metrech. Referenční
   bod je `geo` relace, uložený v meta.json a v zápatí tabulky, takže prohlížeč
   může skutečný svět položit pod trasy.

Stejný modul slouží také: [IL-2 Sturmovik: Great Battles (živá data)](game-il2.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry (na východ, výška, na sever od prvního určení polohy) |
| Zrcadleno pro prohlížeč | `z` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `replay`: čte jen to, co hra nebo platforma vydává (replaye a dema, která hra uloží), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- T každého objektu (délka, šířka, výška, náklon, sklon, natočení, U, V, kurz) jako pozice jednou za sekundu u každého objektu, se jménem, typem, pilotem, koalicí/barvou, zemí, skupinou a rodičem
- objevení, odstranění (smrt, pokud dřív přišla událost Destroyed, jinak odlet), události TakenOff a Landed, události Message a Bookmark jako řádky
- globální údaje ReferenceLongitude/Latitude (počátek mapy), RecordingTime/ReferenceTime (kdy), DataSource, DataRecorder a Title do meta.json

**Uchováno surové**

- každý neprázdný logický řádek záznamu celý jako `text` (řádek pokračující koncovou zpětnou lomítkou se spojí, jak ho čte ACMI), pod svým druhem: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` a `event` (objekt 0), `object` (id,Key=Value,...)
- jen surový záznam obsahuje: pozice mezi jednosekundovými řádky, zbraně, granáty, světlice, plevy a další objekty, které se nekreslí jako trasy, každou jinou vlastnost (telemetrii jako IAS, AOA, plyn, palivo, pokud ji záznam má), jiné globální údaje (Comments, Briefing, Author, Category), události jiné než ty přečtené (Timeout, LeftArea, ...)

**Nedostupné**

- nic, co záznam neobsahuje; co hra do svých záznamů nezapíše, v nich není

**Velikost**: zhruba text samotného záznamu plus asi 70 bajtů na řádek před zstd: 100MB záznam dá asi 150–250 MB surových dat, které zstd srazí přibližně na velikost zabaleného záznamu

## Ověřeno {#verified}

testováno na syntetických souborech ACMI 2.2 (prostých i zabalených do zipu); netestováno na záznamu z hry

## Zdroj {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
