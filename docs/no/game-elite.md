---
title: "Elite Dangerous (loggfiler)"
nav_order: 18
lang: "no"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (loggfiler) {#elite-dangerous-log-files}

Mens du spiller Elite Dangerous, leser watcheren filene spillet skriver, og lagrer det som skjedde, slik at du kan se på det senere på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `elite`, type [`log`](sources-and-rules.md); den kjører mens `EliteDangerous64.exe` kjører, og ser etter nye data hvert 0,25 s.*

## Hva som lagres {#what-is-recorded}

- hver journalhendelse, under sitt journalnavn, med de enkle feltene
- posisjon i galaksen (StarPos, lysår) ved hopp, lokasjoner, gjenoppstandelser, dødsfall, dokking, landing
- spawn ved LoadGame/Resurrect, død ved Died, dokket/udokket, touchdown/liftoff, hopp, session_end
- overflaterute på planet fra Status.json: breddegrad, lengdegrad, høyde, kurs, og meter i et tangentplan per himmellegeme (økt = navnet på himmellegemet), med Status.json sine andre enkle felt (Flags, Flags2, GuiFocus, LegalState, ...)
- hver journallinje og hver følgefil hel i heat.raw.parquet
- hopp, distanse hoppet, dødsfall, drap, opptjente kreditter, fullførte oppdrag, skannede himmellegemer, besøkte systemer, dokkinger, landinger

## Hvor dataene kommer fra {#where-it-comes-from}

Spillerjournalen %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (nyeste fil, fulgt mens den skrives), Status.json og de andre følgefilene \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) i samme mappe

## Slik slår du det på {#how-to-switch-it-on}

Du må ikke slå noe på: watcheren leser kilden slik spillet eller plattformen leverer den.

## Slik fungerer det {#how-it-works}

Elite Dangerous: spillerjournalen og Status.json som spillet skriver mens det kjører.

Hvor: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - ett JSON-objekt per linje, én fil per start av spillet (en lang økt fortsetter i part .02, .03 ...). Hver linje har `timestamp` (UTC, ISO 8601) og `event`. Galaktiske posisjoner er systemets `StarPos` [x, y, z], i lysår fra Sol, på `FSDJump`,
  `Location` og `CarrierJump`. Elites galaktiske system har y opp (mot galaktisk nord),
  z mot galaksekjernen og x mot galaktisk lengdegrad 270 - et venstrehåndssystem, så vieweren speiler z for å tegne det riktig vei.
* `Status.json` - skrevet om hel hver gang skipets tilstand endrer seg: `Flags`, og nær en planet `Latitude`, `Longitude` (grader), `Altitude` (meter), `Heading`, `BodyName` og `PlanetRadius` (meter).
* De andre følgefilene, hver skrevet om hel når den tilhørende journalhendelsen skrives: `Market.json`, `Outfitting.json`, `Shipyard.json`,
  `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`,
  `Backpack.json`, `FCMaterials.json`. Hver `*.json` i mappen som spillet skriver i denne økten, lagres hel hver gang den endrer seg (3DHeat sin regel for konvertering: det kilden inneholder, leses eller lagres), under sitt filnavn.

Hver journallinje lagres hel i øktens rå sidefil under sin `event`, hver følgefil under sitt filnavn; en linje som ikke er JSON, under `unparsed`.

Overflateposisjoner legges i et lokalt tangentplan per himmellegeme, i meter: den første posisjonen på et himmellegeme er origo, x mot øst, z mot nord, y opp (høyde), samme håndedhet som galaksesystemet, og radene bærer himmellegemets navn som sin `session`, slik at en kjøretur eller gåtur på en planet tegnes som en egen rute. Galaksradene har økt «galaxy». De to skalaene ligger i én tabell; velg økt i vieweren.

Format: Frontiers «Elite Dangerous Player Journal»-manual (publisert med hver oppdatering på de offisielle forumene, <https://forums.frontier.co.uk/> - «Journal Manual», v4.x), hendelser og felt slik den beskriver dem; Status.json-flagg etter manualens kapittel «Status File».

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | ja |
| Opp-akse | `y` |
| Enheter | lysår (galaksrader, økt «galaxy»); meter øst/opp/nord fra første posisjon på et himmellegeme (overflaterader, økt = navnet på himmellegemet) |
| Speilvendt for vieweren | `z` |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `log`: den leser bare det spillet eller plattformen gir ut (filer spillet skriver mens det kjører), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- hver journallinje som en rad under sin `event`, med de enkle feltene (den lokaliserte teksten der spillet gir en; tekster over 300 tegn kuttes i raden)
- galaksrader (StarPos) ved FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; overflaterader fra Status.json og Touchdown/Liftoff
- Status.json sine enkle felt (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) på overflaterader
- statistikken: hopp, distanse, dødsfall, drap, opptjente kreditter, oppdrag, skannede himmellegemer, besøkte systemer, dokkinger, landinger

**Lagres uendret**

- hver journallinje hel, `type` = dens `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` sann: listene og objektene radene utelater (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) finnes bare her
- en journallinje som ikke er JSON, `type` `unparsed`
- hver følgefil hel hver gang spillet skriver den om, `type` = filnavnet: `Status.json` (`used` når den ga en overflaterad), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, og enhver annen `*.json` spillet skriver der

**Ikke tilgjengelig**

- posisjon mellom hoppene (inne i et system, i supercruise eller vanlig rom): spillet skriver bare systemets StarPos og, nær en planet, breddegrad, lengdegrad og høyde
- andre skip og spilleres posisjoner: journalen er sjåførens egen beretning
- fart, gass og annen flytelemetri: spillet skriver ikke dem
- journaler og følgefiler fra tidligere økter: lagres når de ble spilt (følgeren starter ved slutten av en fil som er eldre enn denne kjøringen av spillet)
- Frontiers følge-web-API (cAPI): krever at spilleren logger inn hos Frontier; ikke en fil spillet skriver

**Størrelse**: omtrent 1-5 MB rå tekst per time: journalen 0,2-2 MB, Status.json (under 1 KB, skrevet om opptil hvert sekund) 1-2 MB, et sett med market/outfitting/shipyard 20-150 KB per stasjon besøkt; zstd i heat.raw.parquet gjør det omtrent en tidel

## Verifisert {#verified}

parseren spilt om på ekte journalfiler fra en lokal installasjon (antall hendelser stemmer med statistikken); overflatepunktene i Status.json testet bare på syntetiske øyeblikksbilder

## Kilde {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
