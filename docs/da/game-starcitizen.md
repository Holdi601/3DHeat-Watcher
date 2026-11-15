---
title: "Star Citizen (logfiler)"
nav_order: 41
lang: "da"
source: game-starcitizen.md
source_hash: "7b1ce51dc50a"
nav_exclude: true
search_exclude: true
---
# Star Citizen (logfiler) {#star-citizen-log-files}

Mens du spiller Star Citizen, læser watcheren de filer, spillet skriver, og gemmer det, der skete, så du senere kan se det som statistik og en tidslinje.

*Tekniske detaljer: adapter `starcitizen`, type [`log`](sources-and-rules.md); den kører, mens `StarCitizen.exe` kører, og leder efter nye data hver 0.5 s.*

## Hvad der registreres {#what-is-recorded}

- dødsfald med offer, dræber, våben, skadestype og zone (spillere og NPC'er)
- køretøjer slået ud og ødelagt, med fører, årsag og zone
- kvantum-rejsemål, skift af solsystem, spawns, genopstandelser, invaliditeter
- hver Game.log-linje hel i heat.raw.parquet
- drab (spiller og NPC), dødsfald, selvmord, ødelagte og tabte køretøjer, kvantumspring

## Hvor data kommer fra {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (build-mappen for den kørende StarCitizen.exe), kun den logfil spillet skriver - et Easy Anti-Cheat-spil: intet rører dets proces

## Sådan slår du det til {#how-to-switch-it-on}

Der skal ikke slås noget til: watcheren læser kilden, som spillet eller platformen udleverer den.

## Sådan virker det {#how-it-works}

Star Citizen: klientens eget log, `<install>\StarCitizen\LIVE\Game.log`.

Spillet skriver Game.log forfra ved hver start (den forrige flyttes til `logbackups\`). Kun
den fil læses: Star Citizen kører Easy Anti-Cheat, og intet her rører ved spillets
proces. Linjerne starter med et UTC-tidsstempel og et niveau, derefter et tag i vinkelparenteser:

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

(her brudt over flere linjer; i filen én linje hver). En dødsfalds zone er som regel
skibet, offeret sad i, ikke et sted. Formatet er ikke dokumenteret af Cloud
Imperium og ændrer sig mellem patches; mønstrene følger de linjer, community-
drabstællere læser (f.eks. <https://github.com/DimmaDont/all-slain>, MIT - kun fakta),
og det, der ikke passer, springes over i stedet for at gættes. Et køretøjs
`pos` er zonerelativ og gemmes kun som tekst: der tegnes ingen koordinater.

Hver linje gemmes hel i kørslens rå sidefil (3DHeats konverterregel), uanset om den
matcher: `type` er linjens tag i vinkelparenteser (`Actor
Death`, `Spawn Flow`, ...), ellers dens første ord i klammer (`Notice`,
`CSessionManager::OnClientSpawned`), ellers `untagged`; en linje uden tidsstempel er `untimed`.

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | nej |
| Op-akse | `y` |
| Enheder | ingen positioner registreret |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser det som "tilladt (læser kun det spillet udgiver)".
- Type `log`: den læser kun det spillet eller platformen udleverer (filer spillet skriver, mens det kører), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- `<Actor Death>`: offer, dræber, våben og dets klasse, skadestype, zone; NPC eller spiller
- `<Vehicle Destruction>`: køretøj, zone, zonerelativ position som tekst, fører, årsag, hvordan, ødelæggelsesniveau
- `<Quantum Navtarget>`-mål, `<Changing Solar System>`, `OnClientSpawned`, hospitalsgenopstandelser, invaliditeter med deres årsager, `EndSession`
- spillerens handle fra `<AccountLoginCharacterStatus_Character>` eller login-linjen

**Gemt råt**

- hver Game.log-linje hel, `type` = dens tag i vinkelparenteser (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), ellers dens første ord i klammer (`Notice`, `CSessionManager::OnClientSpawned`, ...), ellers `untagged`; linjer uden tidsstempel (logets header, brudt tekst) som `untimed`; `used` hvor linjen blev til en række

**Ikke tilgængeligt**

- positioner: loggen giver ingen i en ramme, der kan tegnes (et ødelagt køretøjs `pos` er i forhold til en zone, hvis sted ikke logges)
- noget fra spillets proces eller netværk: Star Citizen kører Easy Anti-Cheat; kun logfilen læses
- tidligere starters logs (`logbackups`): hver starts Game.log gemmes, når den spilles
- linjer i et format, en patch ændrer: gemt råt, afkodet igen, når det nye format er kendt

**Størrelse**: Game.log vokser cirka 5-15 MB i timen spil (mere i travle områder og ved fejl); zstd i heat.raw.parquet gør det cirka til en tiendedel

## Verificeret {#verified}

testet på syntetiske Game.log-linjer i det format, community-drabstællere dokumenterer; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
