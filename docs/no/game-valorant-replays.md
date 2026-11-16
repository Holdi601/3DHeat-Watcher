---
title: "VALORANT (repriser)"
nav_order: 44
lang: "no"
source: game-valorant-replays.md
source_hash: "a2c4144797e9"
nav_exclude: true
search_exclude: true
---
# VALORANT (repriser) {#valorant-replays}

Etter en kamp i VALORANT gjør watcheren om repriseen spillet lagret, til filer du kan se på som statistikk og en tidslinje.

*Tekniske detaljer: adapter `valorant-replays`, type [`replay`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill starter) og ser etter nye data hvert 5. s.*

## Hva som lagres {#what-is-recorded}

- kartet, kampens id og agentene som ble valgt; reprisens infoblokk (lengde, versjoner, navn, opptakstid, flagg for komprimering og kryptering)
- serverens hendelsestidslinje: drap (drapsmann og offer som nettverks-id-er), runder som starter, spikes plantet, desarmert og eksplodert, ultimater brukt, sidebytte - hver med sin id og metadata
- hver del av filen lagret hel i heat.raw.parquet; ikke dekodet: posisjoner, navn eller poeng - de ligger i den forvirrede strømmen

## Hvor dataene kommer fra {#where-it-comes-from}

repriser VALORANT lagrer: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (bare de delene som ikke er forvirret)

## Slik slår du det på {#how-to-switch-it-on}

lagre en reprise i VALORANT (karriere > kamp > last ned reprise) og installer leseren: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Innstillinger fra miljøvariabler:

- `HEAT3D_RIOT_REPLAYS`: leserens mappe (et klon eller en utpakket utgave), når den ikke er installert eller ved siden av watcheren

## Slik fungerer det {#how-it-works}

League of Legends og Valorant-repriser: det som kan leses av dem slik de er.

Begge spillene lagrer repriser på spillerens disk, og begge beskytter det som ligger inni:
dataene om spillet fra øyeblikk til øyeblikk er forvirret, og på ulike måter med hver oppdatering,
for å hindre at de brukes til juks. Den delen dekodes ikke noe sted
i 3DHeat. Det
som hver fil bærer åpent, leses, og resten lagres slik det er: hver del av filen, hel, i øktens
`heat.raw.parquet` (3DHeat sin regel for konvertering, docs/converters.md i vieweren sitt depot),
og telles i `selfCheck.completeness` i meta.json.

Watcheren leser ikke filene selv: en ekstern leser gjør det (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
kommandoen `heat3d-riot-replays`), et eget prosjekt. Finnes den på PATH, er installert, eller ligger ved siden av watcheren,
leser den hver ny reprise; mangler den, sier watcheren én gang hvordan den installeres. Det
leseren får ut, skriver watcheren inn i økten; Match-V5-tidslinjen under hentes av watcheren selv,
siden den ikke finnes i filen.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, en lokal reprise fra Unreal Engine. Åpent:
reprisens infoblokk (lengde, nettverksversjon, changelist, navn, når den ble tatt opp, om den er komprimert eller kryptert), kartet, kampens id og
agentene som ble valgt (i hodet), og serverens egen hendelsestidslinje - drap
(drapsmann og offer som nettverks-id-er, ikke navn), runder som starter, spikes plantet,
desarmert og eksplodert, ultimater brukt, sidebytte - hver med sitt tidspunkt,
id og metadata. Posisjoner, navn, poeng og alt annet ligger i den forvirrede strømmen
(reprisedataene og sjekkpunktdelene), som lagres hel og ikke leses.

Den samme modulen dekker også: [League of Legends (repriser)](game-lol-replays.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | nei |
| Opp-akse | `z` |
| Enheter | VALORANT-verdenens enheter |
| Speilvendt for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `replay`: den leser bare det spillet eller plattformen gir ut (repriser og demoer spillet lagrer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- infoblokken, hvert felt (meta.json `vrf`): filversjon, egne versjoner, lengde, nettverksversjon, changelist, navn, live-flagg, opptakstid, flagg for komprimert og kryptert, nøkkelen slik den er lagret
- hodedelen: kartet, kampens id og agentene som ble valgt (funnet ved deres form)
- hver hendelsesdel: id, gruppe, metadata, start- og sluttid, og av dataene hendelsens navn, tidspunkt i sekunder og tallene før det (drapsmanns og offers nettverks-id-er) - en rad hver

**Lagres uendret**

- hver del hel, i filrekkefølge (`offset`), slik at delene er filen: `info`, `header`, `event <gruppe>`, `replay_data`, `checkpoint`, `chunk <n>` for en type oppsettet ikke navngir, `trailing` for bytes etter den siste hele delen

**Ikke tilgjengelig**

- posisjoner, navn, poeng, evner, hver ramme i spillet: reprisedata- og sjekkpunktdelene er forvirret. Lagret hel, ikke lest
- innholdet i en kryptert reprise: gjennomgått og lagret hel, ingenting leses inni

**Størrelse**: rå sidefil er omtrent reprisens egen størrelse: den forvirrede strømmen komprimeres ikke

## Verifisert {#verified}

leseren (heat3d-riot-replays) er bygd etter beholderoppsettet dokumentert av vrfkit (Apache-2.0); ikke testet på en ekte reprise, ingen var tilgjengelig - sjekker før lesing og hopper over det som ikke stemmer

## Kilde {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
