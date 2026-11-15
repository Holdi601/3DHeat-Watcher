---
title: "Counter-Strike 2 (repriser)"
nav_order: 8
lang: "no"
source: game-cs2-demos.md
source_hash: "82fe00f0f2f0"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (repriser) {#counter-strike-2-replays}

Etter en kamp i Counter-Strike 2 gjør watcheren repriseen spillet lagret om til filer du kan se på et kart i 3DHeat-visningen.

*Tekniske detaljer: adapter `cs2-demos`, type [`replay`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill starter) og ser etter nye data hvert 5. s.*

## Hva som tas opp {#what-is-recorded}

- hver spillers posisjon, siktretning, helse og penger (hvert 8. tick)
- drap, dødsfall, skade, granater, plantinger og desarmeringer der de skjedde
- runder, stilling og økonomi; den innloggede spillerens linje på resultattavlen som statistikk

## Hvor det kommer fra {#where-it-comes-from}

demoene CS2 lagrer: &lt;CS2>/game/csgo/replays/\*.dem (lastet ned fra kamphistorikken) og &lt;CS2>/game/csgo/\*.dem (tatt opp)

## Slik slår du det på {#how-to-switch-it-on}

last ned en kamps demo i CS2 (Watch > Your Matches), eller ta opp en med konsollkommandoen `record`

Innstillinger fra miljøvariabler:

- `HEAT3D_CS2`: mappen til 3DHeat CS2, når den ikke ligger ved siden av watcheren eller er installert

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

#### Counter-Strike 2 {#counter-strike-2}

CS2 lagrer demoene en spiller laster ned fra kamphistorikken (fanen watch) til
`<CS2>/game/csgo/replays/`, og de som er tatt opp med konsollkommandoen `record`, til
`<CS2>/game/csgo/`. Hver konverteres med dette repoets egen CS2-konverterer (3DHeat CS2,
github.com/Holdi601/3DHeat-CS2: hver spillers posisjon, siktretning, helse og penger hvert
åttende tick; drap, dødsfall, skade, granater, plantinger og desarmeringer der de skjedde;
runder, stilling, økonomi) inn i sesjonsmappen, som tabellen `<map>/<match>.parquet` og
sammendraget `<match>.match.json` som visningens fane for varme og kamp leser. Kampens
resultattavle blir sesjonens statistikk: for spilleren hvis Steam-konto er innlogget på
denne maskinen (fra Steams `loginusers.vdf`), under de vanlige navnene - drap, dødsfall,
assists, ADR, KAST, hodeskuddprosent, åpningsdrap, clutcher - og stillingen og rundene.

Den samme modulen betjener også: [Dota 2 (repriser)](game-dota-replays.md), [Squad (repriser)](game-squad-demos.md), [War Thunder (repriser)](game-warthunder-replays.md), [World of Tanks (repriser)](game-wot-replays.md), [World of Warships (repriser)](game-wows-replays.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | ja |
| Opp-akse | `z` |
| Enheter | tommer (Source-enheter) |
| Speilvendt for visningen | `y` |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse går inn i hver sesjons `meta.json` (`axes`) og, når sesjonen har posisjoner, i `heat.parquet`s fotnote, så 3DHeat-visningen snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `replay`: den leser bare det spillet eller plattformen gir ut (repriser og demoer spillet lagrer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som tas opp {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver sesjons `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

En nøkkel i klammer fylles ut ved kjøring (`score.{team}` er én nøkkel per lag). Nøkler koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; «Hva som tas opp» ovenfor nevner dem.

## Fullstendighet {#completeness}

Konverteren adapteren kjører følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det repriseren inneholder, leses eller beholdes, og det blir aldri kastet - leses inn i tabellen og kampdokumentet, alt annet beholdes helt i sidefiler ved siden av dem, og telles i kampdokumentets `selfCheck.completeness`. Konverterens egen dokumentasjon lister hva den leser, beholder rått og ikke kan lese.

## Verifisert {#verified}

konverteren er testet på ekte turneringsdemoer; mappeovervåkingen og statistikken med tester

## Kilde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
