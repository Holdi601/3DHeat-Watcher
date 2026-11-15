---
title: "World of Tanks (repriser)"
nav_order: 47
lang: "no"
source: game-wot-replays.md
source_hash: "c3fbbeebfee0"
nav_exclude: true
search_exclude: true
---
# World of Tanks (repriser) {#world-of-tanks-replays}

Etter en kamp i World of Tanks gjør watcheren repriseen spillet lagret om til filer du kan se på et kart i 3DHeat-visningen.

*Tekniske detaljer: adapter `wot-replays`, type [`replay`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill starter) og ser etter nye data hvert 5. s.*

## Hva som tas opp {#what-is-recorded}

- hvert kjøretøys posisjon og retning omtrent 10 ganger i sekundet, så lenge opptaksklienten kjente til det: sitt eget lag hele tiden, en fiende mens den er oppdaget
- spiller, lag og kjøretøy (nasjon:tank) for hver; dødsfall der offeret falt og drap der dreperen sto, med omtrent ett sekunds nøyaktighet, fra resultatene
- kartet; opptakerens drap, skade, overlevelse og resultat som statistikk

## Hvor det kommer fra {#where-it-comes-from}

repriser World of Tanks lagrer: &lt;World of Tanks>/replays/\*.wotreplay (med slagopptak på), konvertert av den eksterne konverteren `heat3d-wot-replay` (exporters/ext/wot-replay)

## Slik slår du det på {#how-to-switch-it-on}

slå på slagopptak i World of Tanks' innstillinger (Generelt > Ta opp slag) og installer konverteren: pip install -e &lt;3DHeat>/exporters/ext/wot-replay

Innstillinger fra miljøvariabler:

- `HEAT3D_WOT_REPLAY`: konverterens mappe (en klone eller utpakket utgivelse), når den ikke er installert eller ligger ved siden av watcheren

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

#### World of Tanks og World of Warships {#world-of-tanks-and-world-of-warships}

Begge lagrer en reprise av hvert slag til `<spill>/replays/` når opptak er på
(`*.wotreplay`, `*.wowsreplay`); installasjonene finnes via Wargamings Game Center-liste,
`C:/Games/World_of_Tanks*` / `World_of_Warships*`, og Steam. Som for War Thunder leser
watcheren ikke filene selv: en ekstern konverterer for hvert gjør det (`exporters/ext/wot-replay`,
kommandoen `heat3d-wot-replay`; `exporters/ext/wows-replay`, kommandoen
`heat3d-wows-replay`), holdt for seg selv slik at et problem med Wargamings vilkår bare
berører den konverteren. Funnet på PATH, installert, eller ved siden av watcheren gjør den
hver ny reprise om til `<map>/<match>.parquet` og `<match>.match.json` i sesjonsmappen; mangler
den, sier watcheren én gang hvordan den installeres. Opptakerens linje - kjøretøy eller skip,
drap, skade (World of Tanks), om vedkommende overlevde, og resultatet (World of Tanks) - blir
sesjonens statistikk. Hva hver konverterer leser, og hva den ikke leser, står i README-en
dens.

Den samme modulen betjener også: [Counter-Strike 2 (repriser)](game-cs2-demos.md), [Dota 2 (repriser)](game-dota-replays.md), [Squad (repriser)](game-squad-demos.md), [War Thunder (repriser)](game-warthunder-replays.md), [World of Warships (repriser)](game-wows-replays.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | ja |
| Opp-akse | `y` |
| Enheter | meter (x øst, y opp, z nord) |
| Speilvendt for visningen | `z` |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse går inn i hver sesjons `meta.json` (`axes`) og, når sesjonen har posisjoner, i `heat.parquet`s fotnote, så 3DHeat-visningen snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `replay`: den leser bare det spillet eller plattformen gir ut (repriser og demoer spillet lagrer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som tas opp {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver sesjons `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

En nøkkel i klammer fylles ut ved kjøring (`score.{team}` er én nøkkel per lag). Nøkler koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; «Hva som tas opp» ovenfor nevner dem.

## Fullstendighet {#completeness}

Konverteren adapteren kjører følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det repriseren inneholder, leses eller beholdes, og det blir aldri kastet - leses inn i tabellen og kampdokumentet, alt annet beholdes helt i sidefiler ved siden av dem, og telles i kampdokumentets `selfCheck.completeness`. Konverterens egen dokumentasjon lister hva den leser, beholder rått og ikke kan lese.

## Verifisert {#verified}

konverteren er kontrollert på offentlige repriser fra flere spillversjoner og med tester på bygde repriser; denne koblingen med tester med en erstatningskommando

## Kilde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
