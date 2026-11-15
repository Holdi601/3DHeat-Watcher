---
title: "Star Citizen (log soubory)"
nav_order: 42
lang: "cs"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (log soubory) {#star-citizen-log-files}

Když hrajete Star Citizen, Watcher čte soubory, které hra zapisuje, a uloží, co se stalo, abyste se na to mohli později podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `starcitizen`, druh [`log`](sources-and-rules.md); běží, dokud běží `StarCitizen.exe`, a hledá nová data každých 0,5 s.*

## Co se zaznamenává {#what-is-recorded}

- smrti s obětí, vrahem, zbraní, druhem poškození a zónou (hráči i NPC)
- vyřazená a zničená vozidla, s řidičem, příčinou a zónou
- cíle kvantového cestování, změny sluneční soustavy, objevení se, oživení, vyřazení
- každý řádek Game.log celý v heat.raw.parquet
- zabití (hráč i NPC), smrti, sebevraždy, zničená a ztracená vozidla, kvantové skoky

## Odkud to pochází {#where-it-comes-from}

&lt;instalace>\StarCitizen\LIVE\Game.log (složka buildu spuštěného StarCitizen.exe), jen soubor logu, který hra zapisuje - hra s Easy Anti-Cheat: nic se nedotkne jejího procesu

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

Star Citizen: vlastní log klienta, `<instalace>\StarCitizen\LIVE\Game.log`.

Hra zapisuje Game.log znovu při každém spuštění (předchozí se přesune do
`logbackups\`). Čte se jen tento soubor: Star Citizen používá Easy Anti-Cheat
a nic zde se nedotýká procesu hry. Řádky začínají časovým razítkem UTC a
úrovní, pak značkou v lomených závorkách:

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

(zalomeno zde; v souboru je každý řádek celý). Zóna smrti je obvykle
loď, ve které oběť seděla, ne místo. Formát nedokumentuje Cloud
Imperium a mění se mezi patchi; vzory následují řádky, které čtou komunitní
nástroje na sledování zabití (např. <https://github.com/DimmaDont/all-slain>, MIT - jen
fakta), a cokoli, co neodpovídá, se přeskočí, neodhaduje se. Pole `pos` vozidla je
vztažené k zóně a ukládá se jen jako text: nic se nekreslí.

Každý řádek se ukládá celý do surového doprovodného souboru relace (pravidlo
převodníků 3DHeat), ať odpovídá, nebo ne: `type` je značka řádku v lomených závorkách (`Actor
Death`, `Spawn Flow`, ...), jinak jeho první slovo v závorkách (`Notice`,
`CSessionManager::OnClientSpawned`), jinak `untagged`; řádek bez časového razítka je `untimed`.

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ne |
| Osa nahoru | `y` |
| Jednotky | žádné pozice se nezaznamenávají |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapíší do `meta.json` (`axes`) každé relace a, pokud relace obsahuje pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků upravuje sám - viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `log`: čte jen to, co hra nebo platforma vydává (soubory, které hra zapisuje za běhu), takže zaznamenává i v online hře i offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory`, a nikdy u hry označené jako hraná online - viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- `<Actor Death>`: oběť, vrah, zbraň a její třída, druh poškození, zóna; NPC nebo hráč
- `<Vehicle Destruction>`: vozidlo, zóna, pozice vzhledem k zóně jako text, řidič, příčina, způsob, úroveň zničení
- cíle `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, oživení v nemocnici, vyřazení s jejich příčinami, `EndSession`
- jméno hráče z `<AccountLoginCharacterStatus_Character>` nebo z řádku přihlášení

**Uchováno surové**

- každý řádek Game.log celý, `type` = jeho značka v lomených závorkách (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), jinak jeho první slovo v závorkách (`Notice`, `CSessionManager::OnClientSpawned`, ...), jinak `untagged`; řádky bez časového razítka (hlavička logu, zalomený text) jako `untimed`; `used` tam, kde se řádek stal řádkem

**Nedostupné**

- pozice: log žádnou v rámci, který lze nakreslit, nedává (pole `pos` zničeného vozidla je vztažené k zóně, jejíž místo se neloguje)
- cokoli z procesu nebo sítě hry: Star Citizen používá Easy Anti-Cheat; čte se jen soubor logu
- logy předchozích spuštění (`logbackups`): Game.log každého spuštění se uloží, když se hraje
- řádky ve formátu, který patch změní: uloží se surově a dekódují se znovu, až bude znám nový tvar

**Velikost**: Game.log roste asi 5-15 MB za hodinu hraní (více v rušných oblastech a při chybách); zstd v heat.raw.parquet ho zmenší asi na desetinu

## Ověřeno {#verified}

testováno na syntetických řádcích Game.log ve formátu, který dokumentují komunitní trackery; zatím neotestováno ve hře

## Zdroj {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
