---
title: "Star Citizen (logy)"
nav_order: 42
lang: "sk"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (logy) {#star-citizen-log-files}

Počas hry Star Citizen watcher číta súbory, ktoré hra zapisuje, a ukladá, čo sa stalo, aby ste sa na to neskôr mohli pozrieť ako na štatistiky a časovú os.

*Technické údaje: adaptér `starcitizen`, typ [`log`](sources-and-rules.md); beží, kým beží `StarCitizen.exe`, a hľadá nové dáta každých 0,5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- smrti s obeťou, vrahom, zbraňou, typom poškodenia a zónou (hráči aj NPC)
- vyradené a zničené vozidlá, s vodičom, príčinou a zónou
- ciele kvantovej cesty, zmeny slnečnej sústavy, spawny, respawny, vyradenia
- každý riadok Game.log celý v heat.raw.parquet
- zabitia (hráč a NPC), smrti, samovraždy, zničené a stratené vozidlá, kvantové skoky

## Odkiaľ to berie {#where-it-comes-from}

&lt;inštalácia>\StarCitizen\LIVE\Game.log (priečinok zostavenia spusteného StarCitizen.exe), len súbor logu, ktorý hra zapisuje – hra s Easy Anti-Cheat: nič sa nedotýka jej procesu

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

Star Citizen: vlastný log klienta, `<inštalácia>\StarCitizen\LIVE\Game.log`.

Hra zapisuje Game.log nanovo pri každom spustení (predchádzajúci ide do
`logbackups\`). Číta sa len tento súbor: Star Citizen používa Easy Anti-Cheat a nič tu sa nedotýka procesu hry. Riadky začínajú časovou značkou UTC a úrovňou, potom značkou v lomených zátvorkách:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(tu zalomené; v súbore je každý na jednom riadku). Zóna smrti je obvykle loď, v ktorej obeť sedela, nie miesto. Formát nedokumentuje Cloud Imperium a mení sa medzi patchmi; vzory nasledujú riadky, ktoré čítajú komunitné sledovače zabití (napr. <https://github.com/DimmaDont/all-slain>, MIT – len fakty), a čokoľvek, čo sa nezhoduje, sa preskočí a nič sa nedomýšľa. `pos` vozidla je relatívne k zóne a uchováva sa len ako text: žiadne súradnice sa nekreslia.

Každý riadok sa uchová celý v surovom sprievodnom súbore relácie (pravidlo konvertorov 3DHeat), či sa zhoduje alebo nie: `type` je značka riadku v lomených zátvorkách (`Actor Death`, `Spawn Flow`, ...), inak jeho prvé slovo v zátvorkách (`Notice`, `CSessionManager::OnClientSpawned`), inak `untagged`; riadok bez časovej značky je `untimed`.

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | nie |
| Os nahor | `y` |
| Jednotky | polohy sa nezaznamenávajú |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Typ `log`: číta len to, čo hra alebo platforma vydáva (súbory, ktoré hra zapisuje počas behu), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- `<Actor Death>`: obeť, vrah, zbraň a jej trieda, typ poškodenia, zóna; NPC alebo hráč
- `<Vehicle Destruction>`: vozidlo, zóna, poloha vo vzťahu k zóne ako text, vodič, príčina, spôsob, úroveň zničenia
- `<Quantum Navtarget>` ciele, `<Changing Solar System>`, `OnClientSpawned`, oživenia v nemocnici, vyradenia s ich príčinami, `EndSession`
- handle hráča z `<AccountLoginCharacterStatus_Character>` alebo z riadku prihlásenia

**Uchované surové**

- každý riadok Game.log celý, `type` = jeho značka v lomených zátvorkách (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), inak jeho prvé slovo v zátvorkách (`Notice`, `CSessionManager::OnClientSpawned`, ...), inak `untagged`; riadky bez časovej značky (hlavička logu, zalomený text) ako `untimed`; `used` tam, kde sa riadok stal riadkom

**Nedostupné**

- polohy: log ich v použiteľnom rámci nedáva (`pos` zničeného vozidla je relatívne k zóne, ktorej miesto sa nezapisuje)
- čokoľvek z procesu alebo siete hry: Star Citizen používa Easy Anti-Cheat; číta sa len súbor logu
- skoršie spustenia (`logbackups`): Game.log každého spustenia sa uchová, keď sa hralo
- riadky vo formáte, ktorý patch mení: uchované surové, dekódované znova, keď sa pozná nová podoba

**Veľkosť**: Game.log rastie zhruba 5 až 15 MB za hodinu hry (viac v rušných oblastiach a pri chybách); zstd v heat.raw.parquet ho zmenší zhruba na desatinu

## Overené {#verified}

testované na syntetických riadkoch Game.log vo formáte, ktorý dokumentujú komunitné sledovače; neotestované proti hre

## Zdroj {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
