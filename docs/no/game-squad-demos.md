---
title: "Squad (repriser)"
nav_order: 40
lang: "no"
source: game-squad-demos.md
source_hash: "a908f7e6d9c3"
nav_exclude: true
search_exclude: true
---
# Squad (repriser) {#squad-replays}

Etter en kamp i Squad gjør watcheren repriseen spillet lagret om til filer du kan se på et kart i 3DHeat-visningen.

*Tekniske detaljer: adapter `squad-demos`, type [`replay`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill starter) og ser etter nye data hvert 5. s.*

## Hva som tas opp {#what-is-recorded}

- hver spillers posisjon, kroppens retning og fart hver gang serveren replikerer den (opptil 8 ganger i sekundet), til fots og i kjøretøy på bakken
- hver spillers navn, lag, fraksjon og tropp, og lagbytter følges
- ikke: helikopterbevegelse, drap og utplasserbare ting - se leserens README

## Hvor det kommer fra {#where-it-comes-from}

serverdemoer Squad tar opp med admin-kommandoen AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, lest av den eksterne leseren `heat3d-squad-demo` (exporters/ext/squad-demo)

## Slik slår du det på {#how-to-switch-it-on}

ta opp på serveren: gi admin tillatelsen `demos` i Admins.cfg, og deretter AdminDemoRec &lt;navn> og AdminDemoStop i spillets konsoll; kopier demoen hit og installer leseren: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Innstillinger fra miljøvariabler:

- `HEAT3D_SQUAD_DEMO`: konverterens mappe (en klone eller utpakket utgivelse), når den ikke er installert eller ligger ved siden av watcheren

## Slik fungerer det {#how-it-works}

Repriser og demoer: det spillet lagrer av en kamp, gjort om når kampen er over.

En reprise inneholder alt et live-grensesnitt holder tilbake i flerspillerspill -
hver spillers posisjon, hvert drap der det skjedde - og den er en fil spillet skriver til
sine spillere, så lesing berører ingenting i spillet. Watcheren ser i mappene spillene
lagrer dem i, venter til en ny fil slutter å vokse (spillet skriver ellers fortsatt til
den), og konverterer den i en arbeidstråd, så en lang konvertering aldri holder opp resten
av watcheren.

Første gang en mappe ses, bare noteres repriser som allerede ligger der, de konverteres
ikke: en spiller med år med demoer ville ellers fått watcheren opptatt i en dag.
`python -m heat3d_watch replays <adapter> [mappe]` konverterer de eksisterende på forespørsel.

#### Squad {#squad}

Squads dedikerte servere tar opp en demo av en kamp når en admin med tillatelsen `demos`
kjører AdminDemoRec &lt;navn> (og AdminDemoStop), inn i
`<server>/SquadGame/Saved/Demos/<navn>.replay` - en nettverksreprise fra Unreal Engine som
inneholder det serveren replikerte, hver spillers bevegelse inkludert. Watcheren leser dem
ikke selv: en ekstern leser gjør det (3DHeat Squad demo reader, `exporters/ext/squad-demo`,
kommandoen `heat3d-squad-demo`), holdt for seg selv slik at et problem med den ikke berører
noe annet. Den kjøres på hver ny demo i mappene en lokal server skriver til, eller i en mappe
innstillingene legger til for demoer kopiert fra en leid server, inn i sesjonsmappen som
`<map>/<match>.parquet` og `<match>.match.json`. Laget, kartet, antallet spillere og
kampens lengde blir sesjonens statistikk.

Den samme modulen betjener også: [Counter-Strike 2 (repriser)](game-cs2-demos.md), [Dota 2 (repriser)](game-dota-replays.md), [War Thunder (repriser)](game-warthunder-replays.md), [World of Tanks (repriser)](game-wot-replays.md), [World of Warships (repriser)](game-wows-replays.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | ja |
| Opp-akse | `z` |
| Enheter | Unreal-enheter (centimeter) |
| Speilvendt for visningen | ingen |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse går inn i hver sesjons `meta.json` (`axes`) og, når sesjonen har posisjoner, i `heat.parquet`s fotnote, så 3DHeat-visningen snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `replay`: den leser bare det spillet eller plattformen gir ut (repriser og demoer spillet lagrer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som tas opp {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver sesjons `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

En nøkkel i klammer fylles ut ved kjøring (`score.{team}` er én nøkkel per lag). Nøkler koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; «Hva som tas opp» ovenfor nevner dem.

## Fullstendighet {#completeness}

Konverteren adapteren kjører følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det repriseren inneholder, leses eller beholdes, og det blir aldri kastet - leses inn i tabellen og kampdokumentet, alt annet beholdes helt i sidefiler ved siden av dem, og telles i kampdokumentets `selfCheck.completeness`. Konverterens egen dokumentasjon lister hva den leser, beholder rått og ikke kan lese.

## Verifisert {#verified}

leseren er kontrollert på offentlige serverdemoer (bevegelsen stemmer med farten den bærer; hver rads lag stemmer med soldatens fraksjon) og med tester på bygde demoer; denne koblingen med tester med en erstatningskommando

## Kilde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
