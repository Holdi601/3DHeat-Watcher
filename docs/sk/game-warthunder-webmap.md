---
title: "War Thunder (herný stav)"
nav_order: 47
lang: "sk"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (herný stav) {#war-thunder-game-state}

Keď hráte War Thunder, watcher ukladá to, čo hra hlási programom vo vašom počítači, aby ste si to neskôr mohli pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `warthunder-webmap`, druh [`gsi`](sources-and-rules.md); beží, kým beží `aces.exe`, a hľadá nové dáta každých 0,5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- vlastná pozícia (východ/sever na mape v metroch; výška z /state v lietadle, inak 0) dvakrát za sekundu, smer, rýchlosť
- oživenia a odchod vlastného vozidla z mapy (zničené, pristálo, späť do hangára), jeden výlet na každé
- ostatné lietadlá a pozemné jednotky na minimape ako pozície so sledovanými id a stranou (bez výšky)
- letiská, zóny dobytia a základne raz, a zmeny strany zón
- riadky hlásení o zabitiach a poškodeniach (kto, vozidlo, sloveso); zabitia a smrti hráča, keď je nastavené vaše meno (`config --set player_names.warthunder-webmap=<name>`)
- oživenia, vzdialenosť, najvyššia výška, najvyššia pravá vzdušná rýchlosť (TAS), vozidlo; zabitia a smrti, keď je meno nastavené
- každá odpoveď webovej mapy uchovaná celá v `heat.raw.parquet` – vrátane plného /state a /indicators, chatu, cieľov bitky a obrázka mapy; medzi bitkami v samostatnej relácii

## Odkiaľ to pochádza {#where-it-comes-from}

lokálna webová mapa hry, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

War Thunder: lokálna webová mapa hry na <http://127.0.0.1:8111>.

Hra podáva stránku, ktorú môže ukázať druhá obrazovka alebo telefón („webová mapa“), aj JSON za ňou, kým beží – vo všetkých režimoch, aj vo viachráčovom:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: rozsah mapy v metroch; valid false v hangári
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 obrázka mapy, y smeruje dole), "dx", "dy" (smer),
                  airfields "sx", "sy", "ex", "ey"}]: čo minimapa ukazuje; vlastné vozidlo s ikonou "Player"; žiadne id, žiadne výšky
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: hodnoty letu, platné len v lietadle
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} novšie než dané id, každé
                  {"id", "msg", "sender", "enemy", "mode", "time"}; riadky poškodení vyzerajú takto
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  chat novší než dané id, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    ciele bitky a ich stav
/map.img         obrázok mapy, na ktorý stránka kreslí objekty
```

Každá odpoveď sa uchová celá v surovom sprievodnom súbore relácie pod svojím koncovým bodom (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); medzi bitkami idú odpovede do vlastnej relácie, ktorá nemá riadky.

Pozícia na mape sa mení na metre podľa rozsahu: u = min_x + x \* (max_x - min_x) na východ, v = max_y - y \* (max_y - min_y) na sever (y obrázka ide nadol). Riadky sú x = u, y = výška („H, m“ vlastného lietadla; 0 pre všetko ostatné), z = v, takže Y smeruje nahor; z je pre viewer zrkadlené, aby sever nebol kreslený na juh.

Farby hovoria o stranách tak, ako ich hráč vidí: vlastná žltá (predvolene #faC81E), squad zelená, spojenci modrá (#174DFF), nepriatelia červená (#f40C00); palety pre ľudí s farbosleposťou ich menia, takže rozhoduje odtieň, nie presná hodnota. Hra nikoho na mape nepomenúva a objektom nedáva id: ostatným objektom ich watcher dáva sledovaním z dopytu na dopyt (najbližší rovnakého typu a ikony), čo môže zameniť dve lietadlá rovnakého typu, ktoré prelietajú blízko seba. Vlastné meno hráča nie je ani v API: zadajte ho v nastaveniach (`config --set player_names.warthunder-webmap=<your name>`) a riadky hlásení o zabitiach hráča sa stanú zabitiami a smrťami; bez neho sa zaznamenajú ako hlásenia o zabitiach.

Zdroje: vlastná stránka hry na <http://127.0.0.1:8111> a jej JSON; fakty o poliach podľa projektu JoyPro 2 (docs/telemetry-recording.md; GPL, použité len kvôli faktom).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `y` |
| Jednotky | metre (východ/sever na mape; výška len pre vlastné lietadlo) |
| Zrkadlené pre viewer | `z` |
| Mierka (`scale`: viewer pozície násobí týmto číslom) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat riadky otáča a mení mierku sám – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hraná online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Druh `gsi`: číta len to, čo hra alebo platforma vydáva (game-state integration alebo lokálne API, ktoré hra poskytuje), takže zaznamenáva aj online hru, aj offline; príznak rozhoduje len o tom, či sa smie čítať pamäť.
- Pamäť: tento adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online – pozrite [Pravidlá a zdroje](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Štatistické kľúče, ktoré kód tohto adaptéra nastavuje podľa názvu (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Kľúč v zložených zátvorkách sa doplní až za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z vlastných názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich uvádza.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: čo zdroj obsahuje, sa prečíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celý v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a potom každé pole, ktoré sa podľa názvu ponechalo; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Prečítané**

- /map_info.json: rozsah mapy a mriežka (metre, id mapy) do meta.json; neplatná ukončí bitku
- /map_obj.json (dvakrát za sekundu): vlastné vozidlo, ostatné lietadlá a pozemné jednotky (sledované id, strana z farby, ikona, kurz, farba) a letiská, zóny a základne ako riadky
- /state (dvakrát za sekundu, v lietadle): výška, TAS, IAS, Mach a Vy na vlastných riadkoch
- /indicators (každé 2 s): armáda a typ vozidla
- /hudmsg (raz za sekundu): riadky hlásení o zabitiach a poškodeniach ako zabitia, smrti, zásahy a riadky hlásení; ostatné udalosti HUD ako riadky

**Uchované surové**

- každá odpoveď celá, `text` je JSON tak, ako ju hra poslala, pod svojím koncovým bodom: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` bajty obrázka mapy ako `payload`, raz za bitku
- čo drží len surový sprievodný súbor: každé pole /state nad päť čítaných (AoA, AoS, Ny, Wx, plyn, otáčky, palivo, ... – sada jedného lietadla sa líši od druhého), každé pole /indicators (kokpitné prístroje lietadiel, rýchlosť, rýchlostný stupeň, posádka a stabilizátor tankov), ďalšie kľúče objektov mapy (color[], blink, icon_bg, konce letísk), sender, enemy a mode z hudmsg, chat (/gamechat, raz za sekundu), ciele bitky a ich stav (/mission.json, každých 10 s v bitke), riadky povedané pred spustením watchera
- medzi bitkami (hangár, načítavanie) idú odpovede do vlastnej relácie označenej `between_battles` v meta.json, ktorá nemá riadky

**Nie je k dispozícii**

- mená, id a výšky vozidiel iných hráčov: webová mapa ich nemá (id sa tu dávajú sledovaním objektov z dopytu na dopyt); hlásenia o zabitiach pomenúvajú hráčov bez pozícií
- všetko mimo webovej mapy: replaye hry číta konvertor replayov War Thunder a pamäť hry sa nikdy nečíta (online hra)
- /map_obj.json rýchlejšie ako dvakrát za sekundu: tempo dopytov je nízke, aby sa webový server samotnej hry nepreťažil

**Veľkosť**: asi 50–120 MB za hodinu JSON pred zstd v bitke (map_obj 5–15 KB dvakrát za sekundu, state asi 1,5 KB dvakrát za sekundu, indicators každé 2 s, chat a riadky HUD malé) plus obrázok mapy raz za bitku (pod 2 MB); 1–2 MB za hodinu medzi bitkami (pohľad na mapu dvakrát za sekundu, HUD a chat raz, každá krátka odpoveď); zstd zmenší opakujúci sa JSON viac ako desaťnásobne

## Overené {#verified}

testované voči falošnému lokálnemu serveru, ktorý podáva odpovede vo formáte webovej mapy hry; netestované voči bežiacej hre

## Zdroj {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
