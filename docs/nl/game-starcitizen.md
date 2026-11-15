---
title: "Star Citizen (logbestanden)"
nav_order: 42
lang: "nl"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (logbestanden) {#star-citizen-log-files}

Terwijl je Star Citizen speelt, leest de watcher de bestanden die het spel schrijft en slaat hij op wat er gebeurde, zodat je het later kunt bekijken als statistieken en tijdlijn.

*Technische details: adapter `starcitizen`, soort [`log`](sources-and-rules.md); hij draait zolang `StarCitizen.exe` actief is en zoekt elke 0,5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- doden met slachtoffer, moordenaar, wapen, schadetype en zone (spelers en NPC's)
- voertuigen uitgeschakeld en vernietigd, met bestuurder, oorzaak en zone
- doelen van quantumreizen, wisselingen van zonnestelsel, spawns, herspawns, buitengevechtstellingen
- elke Game.log-regel ongewijzigd in heat.raw.parquet
- kills (speler en NPC), deaths, zelfmoorden, voertuigen vernietigd en verloren, quantumsprongen

## Waar het vandaan komt {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (de buildmap van het draaiende StarCitizen.exe), alleen het logbestand dat het spel schrijft - een spel met Easy Anti-Cheat: niets raakt het proces aan

## Hoe je het aanzet {#how-to-switch-it-on}

Niets hoeft aangezet te worden: de watcher leest de bron zoals het spel of platform die aanbiedt.

## Hoe het werkt {#how-it-works}

Star Citizen: het eigen logboek van de client, `<install>\StarCitizen\LIVE\Game.log`.

Het spel schrijft Game.log opnieuw bij elke start (het vorige gaat naar `logbackups\`). Alleen dat bestand wordt gelezen: Star Citizen draait Easy Anti-Cheat, en niets hier komt in de buurt van het proces van het spel. Regels beginnen met een UTC-tijdstempel en een niveau, daarna een tag tussen punthaken:

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

(hier over meerdere regels afgebroken; in het bestand is elke regel één regel). De zone van een dode is meestal het schip waarin het slachtoffer zat, niet een plek. Het formaat is niet door Cloud Imperium gedocumenteerd en verandert tussen patches; de patronen volgen de regels die community-kill-trackers lezen (bijv. <https://github.com/DimmaDont/all-slain>, MIT - alleen feiten), en wat niet past wordt overgeslagen, niet geraden. De `pos` van een voertuig is zone-relatief en alleen als tekst bewaard: er worden geen coördinaten getekend.

Elke regel wordt ongewijzigd bewaard in het ruwe bijbestand van de sessie (converterregel van 3DHeat), of hij past of niet: `type` is de tag van de regel tussen punthaken (`Actor Death`, `Spawn Flow`, ...), anders het eerste woord tussen haakjes (`Notice`, `CSessionManager::OnClientSpawned`), anders `untagged`; een regel zonder tijdstempel is `untimed`.

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | nee |
| Omhoog-as | `y` |
| Eenheden | geen posities opgeslagen |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Dit gaat in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. De 3DHeat-viewer draait en schaalt de rijen daardoor zelf - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `log`: hij leest alleen wat het spel of platform uitgeeft (bestanden die het spel schrijft terwijl het draait), dus hij legt ook online spel vast; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (elke `stats` van de sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt, ongewijzigd bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard wordt; `used` markeert wat ook rijen werd). `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- `<Actor Death>`: slachtoffer, moordenaar, wapen en zijn klasse, schadetype, zone; NPC of speler
- `<Vehicle Destruction>`: voertuig, zone, zone-relatieve positie als tekst, bestuurder, oorzaak, hoe, vernietigingsniveau
- `<Quantum Navtarget>`-doelen, `<Changing Solar System>`, `OnClientSpawned`, herspawns in het ziekenhuis, buitengevechtstellingen met hun oorzaken, `EndSession`
- de handle van de speler uit `<AccountLoginCharacterStatus_Character>` of de inlogregel

**Ruw bewaard**

- elke Game.log-regel ongewijzigd, `type` = zijn tag tussen punthaken (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), anders het eerste woord tussen haakjes (`Notice`, `CSessionManager::OnClientSpawned`, ...), anders `untagged`; regels zonder tijdstempel (de kop van het logboek, omgebroken tekst) als `untimed`; `used` waar de regel een rij werd

**Niet beschikbaar**

- posities: het logboek geeft er geen in een vorm die getekend kan worden (de `pos` van een vernietigd voertuig is relatief aan een zone waarvan de plek niet gelogd wordt)
- alles uit het proces of het netwerk van het spel: Star Citizen draait Easy Anti-Cheat; alleen het logbestand wordt gelezen
- logs van eerdere starts (`logbackups`): elke Game.log van een start wordt bewaard wanneer hij gespeeld wordt
- regels in een formaat dat een patch verandert: ruw bewaard, en opnieuw gedecodeerd zodra het nieuwe formaat bekend is

**Grootte**: Game.log groeit ongeveer 5-15 MB per uur spelen (meer in drukke gebieden en bij fouten); zstd in heat.raw.parquet maakt het ongeveer een tiende

## Getest {#verified}

getest op synthetische Game.log-regels in het formaat dat community-trackers documenteren; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
