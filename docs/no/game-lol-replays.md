---
title: "League of Legends (repriser)"
nav_order: 30
lang: "no"
source: game-lol-replays.md
source_hash: "ed26619fa904"
nav_exclude: true
search_exclude: true
---
# League of Legends (repriser) {#league-of-legends-replays}

Etter en kamp i League of Legends gjør watcheren om repriseen spillet lagret, til filer du kan se på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `lol-replays`, type [`replay`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill starter) og ser etter nye data hvert 5. s.*

## Hva som lagres {#what-is-recorded}

- hver spillers champion, rolle, lag, drap, dødsfall, assists, gull, skade på champions og resultat, og alle andre tall i poengtabellen på slutten av kampen
- din egen linje som statistikk, og radene dine merket som dine (meta.json `player`), med din Riot-ID i innstillingene
- med din egen Riot API-nøkkel: hver spillers posisjon hvert minutt med minuttets statistikk, og hver hendelse i tidslinjen (drap der de skjedde, bygninger, monstre, vakter, gjenstander, ferdigheter), på klokkeslettet tidslinjen gir
- hver del av repriosefilen lagret hel i heat.raw.parquet; ikke dekodet: spillet fra øyeblikk til øyeblikk, som er kryptert og forvirret mot juks

## Hvor dataene kommer fra {#where-it-comes-from}

repriser klienten til League lagrer: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (bare de vanlige metadataene fra slutten av kampen); med din egen Riot API-nøkkel, kampens offisielle tidslinje fra Riots Match-V5 API

## Slik slår du det på {#how-to-switch-it-on}

lagre en reprise i League-klienten (kamphistorikk > last ned) og installer leseren: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`); for posisjoner, sett riot_api_key og riot_platform med `config --set`

Innstillinger fra miljøvariabler:

- `HEAT3D_RIOT_REPLAYS`: leserens mappe (et klon eller en utpakket utgave), når den ikke er installert eller ved siden av watcheren

## Slik fungerer det {#how-it-works}

League of Legends og Valorant-repriser: det som kan leses av dem slik de er.

Begge spillene lagrer repriser på spillerens disk, og begge beskytter det som ligger inni:
dataene om spillet fra øyeblikk til øyeblikk er forvirret, og på ulike måter med hver oppdatering,
for å hindre at de brukes til juks. Å komme forbi det betyr å demontere spillets egen kode,
noe Riots vilkår forbyr (Terms of Service 3.1 og 7.1) - så det gjøres ikke noe sted i 3DHeat. Det
som hver fil bærer åpent, leses, og resten lagres slik det er: hver del av filen, hel, i øktens
`heat.raw.parquet` (3DHeat sin regel for konvertering, docs/converters.md i vieweren sitt depot),
og telles i `selfCheck.completeness` i meta.json.

Watcheren leser ikke filene selv: en ekstern leser gjør det (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
kommandoen `heat3d-riot-replays`), holdt adskilt slik at et problem med Riots
vilkår bare berører den leseren. Finnes den på PATH, er installert, eller ligger ved siden av watcheren,
leser den hver ny reprise; mangler den, sier watcheren én gang hvordan den installeres. Det
leseren får ut, skriver watcheren inn i økten; tidslinjen fra Match-V5 under hentes av watcheren selv,
siden den ikke finnes i filen.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Begge beholderversjonene bærer
poengtabellen fra slutten av kampen som vanlig JSON (`statsJson`): for hver av de ti spillerne
champion, drap, dødsfall, assists, gull, skade på champions, gjenstander, lag, rolle, seier, deres Riot-ID, og hvert
annet tall spillet summerer (over hundre per spiller); alle blir spillerens
`player_result`-rad. ROFL1 (patch 14.9 og tidligere) har den etter et fast hode
(`RIOT\0\0`, en 256-byte signatur, så lengdene); ROFL2 (14.11 og senere,
`RIOT\2\0`) helt til slutt i filen, med lengden i de siste fire bytene (oppgitt
av en ingeniør hos Riot, ReplayBook-sak 299). ROFL1s nyttelastshode (spill-id,
lengde, antall deler og nøkkelbilder, lengden på delnøkkelen) og tabellen over
delene (id, type, lengde, neste del, forskyvning) ligger åpent og leses; selve
delene er kryptert, og lagres hele uleste.

Posisjonene kommer ikke fra filen. Med en utviklernøkkel fra Riot for spilleren selv (`riot_api_key` i innstillingene; en personlig nøkkel er ment nettopp for dette,
«showing (self) player stats») hentes kampens offisielle tidslinje fra
Riots Match-V5 API: hver spillers posisjon én gang i minuttet med alt minuttets bilde sier om dem
(gull, erfaring, nivå, minions, champion- og skadestatistikk), og hver hendelse i tidslinjen - drap, bygninger, elitemonstre, vakter, gjenstander, ferdigheter, nivåer - hver en rad, der den skjedde når den har et sted.
Uten nøkkel hentes ingenting, og ingenting sendes.

Den samme modulen dekker også: [VALORANT (repriser)](game-valorant-replays.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | ja |
| Opp-akse | `y` |
| Enheter | Summoner's Rift-kartets enheter (omtrent 15000 på tvers) |
| Speilvendt for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `replay`: den leser bare det spillet eller plattformen gir ut (repriser og demoer spillet lagrer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`champion`, `game_seconds`, `won`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- metadata-JSON: kampens lengde, versjon, id-er for siste del og nøkkelbilde, og `statsJson` - hvert felt i hver spillers poengtabell på deres `player_result`-rad (tall gitt som tekst leses som tall)
- ROFL1: lengdeblokken, nyttelastshodet (spill-id, kampens lengde, antall nøkkelbilder og deler, id-er for oppstarts- og kampstartsdelen, nøkkelbildeintervall, delnøkkelen slik den er lagret) og tabellen over delene (id, type, lengde, neste del, forskyvning) - i meta.json `rofl` og radenes `text`
- ROFL2: versjonsstrengen
- Match-V5-tidslinjen (bare med egen API-nøkkel): hvert deltakerbilde på en `position`-rad (eller `participant_frame` uten sted) med alle felt flatet ut (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); hver hendelse som en rad navngitt etter sin type, plassert der den har en `position`, CHAMPION_KILL som et drap og et dødsfall

**Lagres uendret**

- hver del av .rofl-filen, hel, i filrekkefølge (`offset`), slik at delene er filen: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); ethvert stykke som ingen del dekker, som `unknown`
- tidslinjen hel: `timeline <type>` for hver hendelse, `timeline participantFrame` for hvert spillerbilde (`participant` er dens id), `timeline` for resten

**Ikke tilgjengelig**

- selve spillet (posisjoner, evner, hver enhet, fra øyeblikk til øyeblikk): ROFL1s deler og ROFL2s body er kryptert, og pakkene inni er forvirret med hver oppdatering; å komme forbi det betyr å demontere klienten, noe Riots vilkår forbyr (3.1, 7.1). Lagret hel, ikke lest
- posisjoner uten din egen Riot API-nøkkel: filen har ingen åpent

**Størrelse**: rå sidefil er omtrent repriseens egen størrelse: de krypterte delene komprimeres ikke

## Verifisert {#verified}

leseren (heat3d-riot-replays) testet på filer bygd etter oppsettene i roflxd.cs (MIT); tidslinjen etter Match-V5s dokumenterte JSON; ingen ekte reprise var tilgjengelig for å sjekke mot

## Kilde {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
