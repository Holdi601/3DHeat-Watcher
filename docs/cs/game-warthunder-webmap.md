---
title: "War Thunder (stav hry)"
nav_order: 47
lang: "cs"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (stav hry) {#war-thunder-game-state}

Když hrajete War Thunder, Watcher ukládá to, co hra hlásí programům na vašem počítači, abyste se na to mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `warthunder-webmap`, druh [`gsi`](sources-and-rules.md); běží, dokud běží `aces.exe`, a hledá nová data každých 0,5 s.*

## Co se zaznamenává {#what-is-recorded}

- vlastní pozice (východ/sever na mapě v metrech; výška z /state v letadle, jinak 0) dvakrát za sekundu, kurz, rychlost
- oživení a odchod vlastní techniky z mapy (zničena, přistála, zpět do hangáru), jeden výlet na každé
- ostatní letadla a pozemní jednotky na minimapě jako pozice se sledovanými id a stranou (bez výšky)
- letiště, zóny dobytí a základny jednou, a zóny měnící stranu
- řádky zpravodajství o zabitích a zásahu (kdo, technika, sloveso); zabití a smrti hráče, když je nastavené vaše jméno (`config --set player_names.warthunder-webmap=<name>`)
- oživení, vzdálenost, nejvyšší výška, nejvyšší pravá vzdušná rychlost, technika; zabití a smrti, když je nastavené vaše jméno
- každá odpověď webové mapy uchovaná celá v heat.raw.parquet – včetně celého /state a /indicators, chatu, cílů bitvy a obrázku mapy; mezi bitvami v relaci vlastní

## Odkud to pochází {#where-it-comes-from}

místní webová mapa hry, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

War Thunder: vlastní místní webová mapa hry na <http://127.0.0.1:8111>.

Hra nabízí stránku, kterou může ukázat druhá obrazovka nebo telefon („webová mapa“), a JSON za ní, zatímco běží – ve všech režimech, i ve hře pro více hráčů:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: the map's extent in metres; valid false in the hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: what the minimap shows, the player's own
                  vehicle with icon "Player"; no ids, no heights
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: flight values,
                  valid only in an aircraft
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} newer than the ids given, each
                  {"id", "msg", "sender", "enemy", "mode", "time"}; damage lines read like
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  the chat newer than the id given, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    the battle's objectives and their status
/map.img         the map's picture the page draws the objects on
```

Každá odpověď se uchová celá ve vedlejším surovém souboru relace pod svým koncovým bodem
(map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img);
mezi bitvami odpovědi jdou do vlastní relaci.

Pozice na mapě se převede na metry podle rozsahu: u = min_x + x \* (max_x - min_x)
na východ, v = max_y - y \* (max_y - min_y) na sever (y obrázku jde dolů). Řádky jsou
x = u, y = výška (vlastní letadlo „H, m“; 0 pro všechno ostatní), z = v, takže
Y je nahoře; z je zrcadleno pro prohlížeč, aby sever nebyl vykreslen na jih.

Barvy říkají strany tak, jak je hráč vidí: vlastní žlutá (#faC81E výchozí), squadron
zelená, spojenci modrá (#174DFF), nepřátelé červená (#f40C00); palety pro barvoslepé barvy
mění, takže rozhoduje odstín, ne přesná hodnota. Hra nikoho na mapě nejmenuje a objektům nedává
id: ostatní objekty tu id dostávají tak, že se sledují od dotazu k dotazu (nejbližší stejného
typu a ikony), což může u dvou letadel stejného typu, která proletí blízko sebe, prohodit.
Vlastní jméno hráče není ani v API: zadejte ho v nastavení (`config --set
player_names.warthunder-webmap=<your name>`) a řádky zpravodajství o hráči se
změní na zabití a smrti; bez něj se zaznamenají jako zpravodajství.

Zdroje: vlastní stránka hry na <http://127.0.0.1:8111> a její JSON; fakta o polích
podle projektu JoyPro 2 (docs/telemetry-recording.md; GPL, použito jen pro fakta).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry (východ/sever na mapě; výška jen pro vlastní letadlo) |
| Zrcadleno pro prohlížeč | `z` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, když relace má pozice, do patičky `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítkuje řádky sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukáže jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `gsi`: čte jen to, co hra nebo platforma vydává (game-state integration nebo místní API, které hra poskytuje), takže nahrává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda se smí číst paměť.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle jména (každé relace `stats` v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč na každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedené jménem.

## Úplnost {#completeness}

Watcher dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se načte nebo uchová, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér dostane, uchovává celý v `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uchovaná podle jména; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- /map_info.json: rozsah mapy a mřížka (metry, id mapy) do meta.json; neplatná ukončí bitvu
- /map_obj.json (dvakrát za sekundu): vlastní technika, ostatní letadla a pozemní jednotky (sledovaná id, strana podle barvy, ikona, kurz, barva) a letiště, zóny a základny jako řádky
- /state (dvakrát za sekundu, v letadle): výška, TAS, IAS, Mach a Vy na vlastních řádcích
- /indicators (každé 2 s): armáda a typ techniky
- /hudmsg (jednou za sekundu): řádky zpravodajství o zabitích a zásazích jako zabití, smrti, zásahy a řádky zpravodajství; ostatní události HUD jako řádky

**Uchováno surové**

- každá odpověď celá, `text` je JSON tak, jak ho hra poslala, pod svým koncovým bodem: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` bajty obrázku mapy jako `payload`, jednou za bitvu
- co drží jen surový vedlejší soubor: každé pole /state nad těch pět načtených (AoA, AoS, Ny, Wx, plyn, otáčky, palivo, ...; sada se u každého letadla liší), každé pole /indicators (palubní přístroje letadel, rychlost, podvozek, osádka a stabilizátor tanků), ostatní klíče objektů mapy (color[], blink, icon_bg, konce letišť), `sender`, `enemy` a `mode` z hudmsg, chat (/gamechat, jednou za sekundu), cíle bitvy a jejich stav (/mission.json, každých 10 s v bitvě), řádky řečené před spuštěním Watcheru
- mezi bitvami (hangár, načítání) odpovědi jdou do vlastní relaci označené v meta.json jako `between_battles`, která nemá řádky

**Nedostupné**

- jména, id a výšky vozidel ostatních hráčů: webová mapa je nemá (id se tu dávají sledováním objektů od dotazu k dotazu); řádky zpravodajství jmenují hráče bez pozic
- vše mimo webovou mapu: replaye hry čte převodník replayů War Thunder a paměť hry se nikdy nečte (hra online)
- /map_obj.json rychleji než dvakrát za sekundu: rychlost dotazů zůstává nízká, aby se vlastní webový server hry nezatěžoval

**Velikost**: asi 50–120 MB za hodinu JSONu před zstd v bitvě (map_obj 5–15 KB dvakrát za sekundu, state asi 1,5 KB dvakrát za sekundu, indicators každé 2 s, chat a řádky HUD malé) plus obrázek mapy jednou za bitvu (pod 2 MB); 1–2 MB za hodinu mezi bitvami (vzhled mapy dvakrát za sekundu, HUD a chat jednou, každá odpověď krátká); zstd opakovaný JSON zmenší více než desetkrát

## Ověřeno {#verified}

testováno proti falešnému místnímu serveru, který posílá odpovědi ve formátu webové mapy hry; neotestováno proti běžící hře

## Zdroj {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
