---
title: "IL-2 Sturmovik: Great Battles (živá data)"
nav_order: 26
lang: "cs"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (živá data) {#il-2-sturmovik-great-battles-live-data}

Když hrajete IL-2 Sturmovik: Great Battles, Watcher ukládá data, která hra sama posílá ven, abyste se na ně mohli později podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `il2`, druh [`telemetry`](sources-and-rules.md); běží, když je spuštěný `Il-2.exe` nebo `IL2Series.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- lety: letadlo, které si hráč vzal (spawn), a okamžik, kdy výstup přestane (session_end) – bez pozice ve světě, hra žádnou neposílá
- shozené bomby a vypuštěné rakety (hmotnost), zásahy a přijaté poškození, výbuchy, dávky střelby – pozice vztažené k letadlu
- indikovaná vzdušná rychlost, AGL, vertikální rychlost, g, otáčky motoru jednou za sekundu, se všemi dalšími indikátory, které paket nese (tlak v sání, třes motoru, stav a tlak podvozku, AoA, boční skluz, zrychlení x/y/z, třes kabiny, klapky, vzduchové brzdy)
- lety, vystřelená kola, bomby, rakety, přijaté zásahy, nejvyšší rychlost, nejvyšší g, doba letu; název serveru a jméno pilota online
- každý telemetrický paket celý v heat.raw.parquet

## Odkud to pochází {#where-it-comes-from}

telemetrický UDP výstup hry na 127.0.0.1:41995 (`[KEY = telemetrydevice]` v &lt;game>\data\startup.cfg)

## Jak to zapnout {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (přidá addrN = "127.0.0.1:41995", enable = true), pak IL-2 restartujte

Příkaz napište do terminálu otevřeného ve složce Watcheru (viz [Než začnete](before-you-start.md)). Pokud selže, poslední řádek řekne proč; [Instalace a spuštění](installing-and-running.md) popisuje obvyklé příčiny.

`python -m heat3d_watch setup il2` vypíše soubory, které by změnil; `python -m heat3d_watch setup il2 --apply` je opravdu změní a původní soubor uloží jako `<file>.heat3d-backup` (viz [Příkazy](commands.md#setup)). Pro každou změnu vypíše `il2: changed: ...`, nebo `il2: nothing to change`, když je už zapnuto.

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

Stejný modul slouží také: [IL-2 Sturmovik: Great Battles (replaye)](game-il2-tacview.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ne |
| Osa nahoru | `y` |
| Jednotky | žádné: telemetrie nemá pozice ve světě |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- SET_FOCUS (letadlo, které si hráč vzal: let), DROP_BOMB a ROCKET_LAUNCH (hmotnost, pozice vztažená k letadlu), HIT a DAMAGE (pozice vztažená k letadlu, síla), EXPLOSION (pozice vztažená k letadlu, poloměr), GUN_FIRE (počet výstřelů za dotaz) jako řádky
- SETUP_ENG (index, id, pozice vztažená k letadlu, maximální otáčky), SETUP_GUN (index, pozice vztažená k letadlu, hmotnost střely, úsťová rychlost) a SETUP_LGEAR (index, id, pozice vztažená k letadlu) jako řádky: motory, zbraně a podvozek letadla na začátku letu
- SRV_TITLE, SRV_ADDR, SRS_ADDR a CLIENT_DAT (jméno pilota) do meta.json; koalice z CTRL_DAT jako tým letu
- všech patnáct indikátorů specifikace na jednosekundovém řádku `state` (jedna hodnota jako číslo, jedna na každý motor, podvozkovou nohu nebo osu jako seznam); nejvyšší rychlost, g a AGL z každého paketu

**Uchováno surové**

- každý datagram celý jako `payload`, pod svým Packet_ID: `0x54000101` pro telemetrii (použito, když vytvořil řádek nebo položku v meta.json), jakékoli jiné id jako ono samo, datagram příliš krátký na to jako `short`
- jen surový záznam obsahuje: indikátory mezi jednosekundovými řádky (hra je posílá rychlostí 50 Hz / decimation), událost SETUP kratší, než je rozložení ve specifikaci, id událostí, které specifikace neuvádí

**Nedostupné**

- pozice ve světě: telemetrický výstup žádnou nemá (pozice událostí jsou vztaženy k letadlu); adaptér il2-tacview čte pozice z vlastních Tacview záznamů hry
- jiná letadla a hráči: výstup popisuje jen letadlo hráče

**Velikost**: asi 8 MB za hodinu při 10 Hz nastavených příkazem setup (decimation 5; paket má asi 160 bajtů plus rámec), 40 MB při plné rychlosti hry 50 Hz, před zstd; zstd opakující se floaty zmenší na zlomek

## Ověřeno {#verified}

testováno na paketech sestavených podle specifikace Il2_TeleOutput (rev 1.2) od hry; úpravy startup.cfg testovány na kopii souboru; netestováno proti běžící hře

## Zdroj {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
