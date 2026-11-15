---
title: "Star Citizen (loggfiler)"
nav_order: 41
lang: "no"
source: game-starcitizen.md
source_hash: "7b1ce51dc50a"
nav_exclude: true
search_exclude: true
---
# Star Citizen (loggfiler) {#star-citizen-log-files}

Mens du spiller Star Citizen, leser watcheren filene spillet skriver, og lagrer det som skjedde, slik at du senere kan se på det som statistikk og en tidslinje.

*Tekniske detaljer: adapter `starcitizen`, type [`log`](sources-and-rules.md); den kjører mens `StarCitizen.exe` går og ser etter nye data hvert 0,5 s.*

## Hva som tas opp {#what-is-recorded}

- dødsfall med offer, drapsmann, våpen og dets klasse, skadetype og sone (spillere og NPC-er)
- kjøretøy satt ut av spill og ødelagt, med fører, årsak og sone
- kvantumreise-mål, endringer av solsystem, innspawninger, respawn og utslåinger
- hver Game.log-linje hel i `heat.raw.parquet`
- drap (spiller og NPC), dødsfall, selvmord, kjøretøy ødelagt og tapt, kvantumhopp

## Hvor det kommer fra {#where-it-comes-from}

&lt;installasjon>\StarCitizen\LIVE\Game.log (byggmappen til den kjørende StarCitizen.exe), bare loggfilen spillet skriver - et Easy Anti-Cheat-spill: ingenting rører prosessen

## Slik slår du det på {#how-to-switch-it-on}

Ingenting må slås på: watcheren leser kilden slik spillet eller plattformen gir den.

## Slik fungerer det {#how-it-works}

Star Citizen: klientens egen logg, `<installasjon>\StarCitizen\LIVE\Game.log`.

Spillet skriver Game.log på nytt ved hver start (den forrige flyttes til `logbackups\`). Bare den filen leses: Star Citizen kjører Easy Anti-Cheat, og ingenting her kommer nær spillets prosess. Linjene starter med et UTC-tidsstempel og et nivå, deretter en tag i vinkelparenteser:

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

(brutt over her; én linje hver i filen). Sonen til et dødsfall er vanligvis skipet offeret satt i, ikke et sted. Formatet er ikke dokumentert av Cloud Imperium og endrer seg mellom patcher; mønstrene følger linjene fellesskapets drapssporere leser (f.eks. <https://github.com/DimmaDont/all-slain>, MIT - bare fakta), og det som ikke passer, hoppes over og gjettes ikke. Et kjøretøys `pos` er sonerelativ og tas bare vare på som tekst: ingen koordinater tegnes.

Hver linje tas vare på hel i øktens rå sidefil (3DHeats konverteringsregel), enten den passer eller ikke: `type` er linjens tag i vinkelparenteser (`Actor Death`, `Spawn Flow`, ...), ellers dens første ord i klammer (`Notice`, `CSessionManager::OnClientSpawned`), ellers `untagged`; en linje uten tidsstempel er `untimed`.

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | nei |
| Opp-akse | `y` |
| Enheter | ingen posisjoner tatt opp |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `log`: den leser bare det spillet eller plattformen gir ut (filer spillet skriver mens det kjører), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- `<Actor Death>`: offer, drapsmann, våpen og dets klasse, skadetype, sone; NPC eller spiller
- `<Vehicle Destruction>`: kjøretøy, sone, sonerelativ posisjon som tekst, fører, årsak, hvordan, ødeleggelsesnivå
- `<Quantum Navtarget>`-mål, `<Changing Solar System>`, `OnClientSpawned`, sykehus-respawn, utslåinger med årsaker, `EndSession`
- spillerens handle fra `<AccountLoginCharacterStatus_Character>` eller innloggingslinjen

**Tatt vare på rått**

- hver Game.log-linje hel, `type` = dens tag i vinkelparenteser (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), ellers dens første ord i klammer (`Notice`, `CSessionManager::OnClientSpawned`, ...), ellers `untagged`; linjer uten tidsstempel (loggens topptekst, brutt tekst) som `untimed`; `used` der linjen ble en rad

**Ikke tilgjengelig**

- posisjoner: loggen gir ingen i en ramme som kan tegnes (et ødelagt kjøretøys `pos` er relativ til en sone hvis sted ikke er logget)
- alt fra spillets prosess eller nettverk: Star Citizen kjører Easy Anti-Cheat; bare loggfilen leses
- tidligere starters logger (`logbackups`): hver starts Game.log tas vare på når den spilles
- linjer i et format en patch endrer: tatt vare på rått, dekodet på nytt når den nye formen er kjent

**Størrelse**: Game.log vokser omtrent 5-15 MB i timen med spilling (mer i travle områder og med feil); zstd i `heat.raw.parquet` gjør det omtrent en tiendedel

## Verifisert {#verified}

testet på syntetiske Game.log-linjer i formatet fellesskapets sporere dokumenterer; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
