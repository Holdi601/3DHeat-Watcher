---
title: "Elite Dangerous (logfiler)"
nav_order: 18
lang: "da"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (logfiler) {#elite-dangerous-log-files}

Mens du spiller Elite Dangerous, læser watcheren de filer, spillet skriver, og gemmer hvad der skete, så du senere kan se det på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `elite`, type [`log`](sources-and-rules.md); den kører, mens `EliteDangerous64.exe` kører, og leder efter nye data hver 0.25 s.*

## Hvad der registreres {#what-is-recorded}

- hver journalhændelse under sit journalnavn, med sine almindelige felter
- position i galaksen (StarPos, lysår) ved hop, lokationer, spawn, død, docking, landing
- spawn ved LoadGame/Resurrect, død ved Died, docked/undocked, touchdown/liftoff, hop, session_end
- rute på planetoverfladen fra Status.json: breddegrad, længdegrad, højde, kurs og meter i et tangentplan pr. legeme (session = legemets navn), med Status.jsons øvrige almindelige felter (Flags, Flags2, GuiFocus, LegalState, ...)
- hver journallinje og hver companion-fil hel i heat.raw.parquet
- hop, distance hoppet, dødsfald, drab, kreditter tjent, gennemførte missioner, scannede legemer, besøgte systemer, dockinger, landinger

## Hvor data kommer fra {#where-it-comes-from}

Spillerjournalen %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (nyeste fil, fulgt mens den skrives), Status.json og de andre companion-\*.json-filer (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) i samme mappe

## Sådan slår du det til {#how-to-switch-it-on}

Der er intet at slå til: watcheren læser kilden, som spillet eller platformen stiller den til rådighed.

## Sådan virker det {#how-it-works}

Elite Dangerous: spillerjournalen og Status.json, som spillet skriver, mens det kører.

Hvor: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - én JSON-objekt pr. linje, én
  fil pr. start (en lang session fortsætter i part .02, .03 ...). Hver linje
  har `timestamp` (UTC, ISO 8601) og `event`. Galaktiske positioner er
  systemets `StarPos` [x, y, z], i lysår fra Sol, på `FSDJump`,
  `Location` og `CarrierJump`. Elites galaktiske koordinatsystem har y op (mod
  galaktisk nord), z mod galaksens kerne og x mod galaktisk længdegrad
  270 - et venstrehåndet system, så vieweren spejler z for at tegne det den rigtige vej rundt.
* `Status.json` - omskrevet hel, hver gang skibets tilstand ændrer sig: `Flags`,
  og nær en planet `Latitude`, `Longitude` (grader), `Altitude` (meter),
  `Heading`, `BodyName` og `PlanetRadius` (meter).
* De andre companion-filer, hver omskrevet hel, når den tilsvarende journalhændelse
  skrives: `Market.json`, `Outfitting.json`, `Shipyard.json`,
  `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`,
  `Backpack.json`, `FCMaterials.json`. Hver `*.json` i mappen, som spillet
  skriver i denne session, gemmes hel, hver gang den ændrer sig (3DHeats
  konverterregel: det kilden indeholder, læses eller gemmes), under sit filnavn.

Hver journallinje gemmes hel i sessionens råsidefil under sin `event`, hver companion-fil under sit filnavn; en linje der ikke er JSON, under `unparsed`.

Overfladepositioner lægges i et lokalt tangentplan pr. legeme, i meter: det første fix på et legeme er dets udgangspunkt, x mod øst, z mod nord, y op (højde), samme håndedhed som galaksens koordinatsystem, og rækkerne bærer legemets navn som deres `session`, så en kørsel eller gang på en planet tegnes som en rute for sig selv. Galaksens rækker har session "galaxy". De to skalaer ligger i én tabel; vælg session i vieweren.

Format: Frontiers "Elite Dangerous Player Journal"-manual (udgivet med hver opdatering på de officielle fora, <https://forums.frontier.co.uk/> - "Journal Manual", v4.x), hændelser og felter som beskrevet der; Status.jsons flag efter samme manuals kapitel "Status File".

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | lysår (galaksens rækker, session 'galaxy'); meter øst/op/nord fra det første fix på et legeme (overfladerækker, session = legemets navn) |
| Spejlet for vieweren | `z` |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det spillet udleverer)".
- Type `log`: den læser kun det, spillet eller platformen udleverer (filer spillet skriver, mens det kører), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- hver journallinje som en række under sin `event`, med sine almindelige felter (den lokaliserede tekst, hvor spillet giver en; tekster længere end 300 tegn afkortes i rækken)
- galaksens rækker (StarPos) ved FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; overfladerækker fra Status.json og Touchdown/Liftoff
- Status.jsons almindelige felter (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) på overfladerækkerne
- statistikkerne: hop, distance, dødsfald, drab, tjente kreditter, missioner, scannede legemer, besøgte systemer, dockinger, landinger

**Gemt råt**

- hver journallinje hel, `type` = dens `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` sand: listerne og objekterne rækkerne udelader (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) findes kun her
- en journallinje der ikke er JSON, `type` `unparsed`
- hver companion-fil hel, hver gang spillet omskriver den, `type` = dens filnavn: `Status.json` (`used`, når den lavede en overfladerække), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, og enhver anden `*.json` spillet skriver ddér

**Ikke tilgængeligt**

- position mellem hop (inde i et system, i supercruise eller normalrum): spillet skriver kun systemets StarPos og, nær en planet, breddegrad, længdegrad og højde
- andre skibes og spilleres positioner: journalen er kommandørens egen beretning
- hastighed, gas og anden flyvetelemetri: spillet skriver dem ikke
- journaler og companion-filer fra tidligere sessioner: gemmes, når de blev spillet (følgeren starter ved slutningen af en fil, der er ældre end denne kørsel af spillet)
- Frontiers companion-webAPI (cAPI): kræver spillerens Frontier-login; ikke en fil spillet skriver

**Størrelse**: cirka 1-5 MB rå tekst i timen: journalen 0.2-2 MB, Status.json (under 1 KB, omskrevet op til hvert sekund) 1-2 MB, et marked/outfitting/shipyard-sæt 20-150 KB pr. station besøgt; zstd i heat.raw.parquet gør det cirka en tiendedel

## Verificeret {#verified}

parseren afspillet over rigtige journalfiler fra en lokal installation (antal hændelser stemmer med statistikken); overfladefix i Status.json testet kun på syntetiske øjebliksbilleder

## Kilde {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
