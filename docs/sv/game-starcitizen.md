---
title: "Star Citizen (loggfiler)"
nav_order: 41
lang: "sv"
source: game-starcitizen.md
source_hash: "7b1ce51dc50a"
nav_exclude: true
search_exclude: true
---
# Star Citizen (loggfiler) {#star-citizen-log-files}

När du spelar Star Citizen läser watchern de filer spelet skriver och sparar vad som hände, så att du senare kan titta på det som statistik och en tidslinje.

*Tekniska detaljer: adapter `starcitizen`, slag [`log`](sources-and-rules.md); den körs medan `StarCitizen.exe` är igång och letar efter ny data var 0,5 s.*

## Vad som spelas in {#what-is-recorded}

- dödsfall med offer, mördare, vapen, skadetyp och zon (spelare och NPC:er)
- fordon som gjorts obrukbara och förstörts, med förare, orsak och zon
- quantum-resmål, byten av solsystem, uppenbaranden, återuppståndelser, utslagningar
- varje rad i Game.log helt i `heat.raw.parquet`
- dödanden (spelare och NPC), dödsfall, självmord, fordon förstörda och förlorade, quantum-hopp

## Var datan kommer ifrån {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (byggmappen för den körande StarCitizen.exe), bara loggfilen som spelet skriver - ett Easy Anti-Cheat-spel: ingenting rör dess process

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

Star Citizen: klientens egen logg, `<install>\StarCitizen\LIVE\Game.log`.

Spelet skriver Game.log på nytt vid varje start (den föregående går till `logbackups\`). Bara den filen läses: Star Citizen kör Easy Anti-Cheat, och ingenting här kommer nära spelets process. Raderna börjar med en UTC-tidsstämpel och en nivå, sedan en tagg inom vinkelparenteser:

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

(radbruten här; en rad vardera i filen). Zonen vid ett dödsfall är oftast skeppet offret satt i, inte en plats. Formatet är inte dokumenterat av Cloud Imperium och ändras mellan patchar; mönstren följer de rader som communityns dödsspårare läser (t.ex. <https://github.com/DimmaDont/all-slain>, MIT - endast fakta), och allt som inte stämmer hoppas över, inte gissas. Ett fordons `pos` är zonrelativ och sparas bara som text: inga koordinater ritas.

Varje rad sparas helt i sessionens råa sidfil (3DHeats konverterarregel), matchad eller inte: `type` är radens tagg i vinkelparenteser (`Actor Death`, `Spawn Flow`, ...), annars dess första ord i parenteser (`Notice`, `CSessionManager::OnClientSpawned`), annars `untagged`; en rad utan tidsstämpel är `untimed`.

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | nej |
| Upp-axel | `y` |
| Enheter | inga positioner registreras |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Slag `log`: den läser bara det spelet eller plattformen lämnar ut (filer som spelet skriver medan det körs), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- `<Actor Death>`: offer, mördare, vapen och dess klass, skadetyp, zon; NPC eller spelare
- `<Vehicle Destruction>`: fordon, zon, zonrelativ position som text, förare, orsak, hur, förstörelsenivå
- `<Quantum Navtarget>`-mål, `<Changing Solar System>`, `OnClientSpawned`, sjukhusåteruppståndelser, utslagningar med deras orsaker, `EndSession`
- spelarens handle från `<AccountLoginCharacterStatus_Character>` eller inloggningsraden

**Sparas råa**

- varje Game.log-rad helt, `type` = dess tagg i vinkelparenteser (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), annars dess första ord i parenteser (`Notice`, `CSessionManager::OnClientSpawned`, ...), annars `untagged`; rader utan tidsstämpel (loggens huvud, radbruten text) som `untimed`; `used` där raden blev en rad

**Finns inte**

- positioner: loggen ger ingen i en ram som kan ritas (ett förstört fordons `pos` är relativ till en zon vars plats inte loggas)
- allt från spelets process eller nätverk: Star Citizen kör Easy Anti-Cheat; bara loggfilen läses
- loggar från tidigare starter (`logbackups`): varje starts Game.log sparas när den spelas
- rader i ett format som en patch ändrar: sparas råa, avkodas igen när den nya formen är känd

**Storlek**: Game.log växer ungefär 5-15 MB per timme spelande (mer i livliga områden och vid fel); zstd i `heat.parquet` gör det ungefär en tiondel

## Verifierat {#verified}

testad på syntetiska Game.log-rader i det format som communityspårare dokumenterar; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
