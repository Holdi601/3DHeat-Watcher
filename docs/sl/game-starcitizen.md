---
title: "Star Citizen (dnevniške datoteke)"
nav_order: 42
lang: "sl"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (dnevniške datoteke) {#star-citizen-log-files}

Medtem ko igrate Star Citizen, watcher bere datoteke, ki jih igra zapisuje, in shrani, kaj se je zgodilo, da si to pozneje lahko ogledate kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `starcitizen`, vrsta [`log`](sources-and-rules.md); teče, medtem ko se izvaja `StarCitizen.exe`, in vsakih 0,5 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- smrti z žrtvijo, ubijalcem, orožjem, vrsto poškodbe in območjem (igralci in NPC)
- onemogočena in uničena vozila z voznikom, vzrokom in območjem
- cilji kvantnega potovanja, spremembe sončnega sistema, pojavitve, ponovni zagoni, onesposobitve
- vsaka vrstica Game.log cela v heat.raw.parquet
- ubijanja (igralci in NPC), smrti, samomori, uničena in izgubljena vozila, kvantni skoki

## Od kod prihajajo {#where-it-comes-from}

&lt;namestitev&gt;\StarCitizen\LIVE\Game.log (mapa zgradbe zagnanega StarCitizen.exe), samo datoteka dnevnika, ki jo zapisuje igra - igra z Easy Anti-Cheat: nič se ne dotakne njenega procesa

## Kako vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklopiti: watcher bere vir tako, kot ga igra ali platforma ponuja.

## Kako deluje {#how-it-works}

Star Citizen: lastni dnevnik odjemalca, `<namestitev>\StarCitizen\LIVE\Game.log`.

Igra piše Game.log znova ob vsakem zagonu (prejšnjega premakne v
`logbackups\`). Bere se samo ta datoteka: Star Citizen teče z Easy Anti-Cheat, zato se tu
nič ne dotakne procesa igre. Vrstice se začnejo s časovno oznako UTC in ravnjo, nato oznako v
kotnih oklepajih:

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

(tu prelomljeno; v datoteki je vsaka vrstica ena.) Območje smrti je ponavadi
ladja, v kateri je sedela žrtev, ne kraj. Format ne dokumentira Cloud
Imperium in se med popravki spreminja; vzorci sledijo vrsticam, ki jih berejo skupnostni
sledilniki ubojev (npr. <https://github.com/DimmaDont/all-slain>, MIT - samo dejstva), vse, kar se ne
ujema, se preskoči in ne ugiba. `pos` vozila je glede na območje in se shrani samo kot
besedilo: nič se ne riše na koordinatah.

Vsaka vrstica se shrani cela v surovo spremljevalno datoteko seje (pravilo pretvornikov 3DHeat),
ujemajoča ali ne: `type` je oznaka vrstice v kotnih oklepajih (`Actor
Death`, `Spawn Flow`, ...), sicer njena prva beseda v oklepajih (`Notice`,
`CSessionManager::OnClientSpawned`), sicer `untagged`; vrstica brez časovne oznake je `untimed`.

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | ne |
| Navpična os | `y` |
| Enote | položaji niso zabeleženi |
| Zrcaljenje za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `log`: bere samo, kar igra ali platforma ponudi (datoteke, ki jih igra zapisuje med delovanjem), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- `<Actor Death>`: žrtev, ubijalec, orožje in njegov razred, vrsta poškodbe, območje; igralec ali NPC
- `<Vehicle Destruction>`: vozilo, območje, položaj glede na območje kot besedilo, voznik, vzrok, način, stopnja uničenja
- cilji `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, ponovni zagoni v bolnišnici, onesposobitve z vzroki, `EndSession`
- ročaj igralca iz `<AccountLoginCharacterStatus_Character>` ali vrstice prijave

**Shranjeno surovo**

- vsaka vrstica Game.log cela, `type` = njena oznaka v kotnih oklepajih (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), sicer njena prva beseda v oklepajih (`Notice`, `CSessionManager::OnClientSpawned`, ...), sicer `untagged`; vrstice brez časovne oznake (glava dnevnika, prelomljeno besedilo) kot `untimed`; `used` tam, kjer je vrstica postala vrstica

**Ni na voljo**

- položaji: dnevnik jih ne daje v okvirju, ki se da narisati (`pos` uničenega vozila je glede na območje, katerega lega ni zabeležena)
- vse iz procesa igre ali omrežja: Star Citizen teče z Easy Anti-Cheat; bere se samo datoteka dnevnika
- dnevniki prejšnjih zagonov (`logbackups`): Game.log vsakega zagona se shrani, ko se igra
- vrstice v obliki, ki jo popravek spremeni: shranjene surovo, dekodirane znova, ko je nova oblika znana

**Velikost**: Game.log na uro igre raste za približno 5-15 MB (več v živahnih območjih in pri napakah); zstd v heat.raw.parquet ga skrči na približno desetino

## Preverjeno {#verified}

preizkušeno na sintetičnih vrsticah Game.log v obliki, ki jo dokumentirajo skupnostni sledilniki; nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
