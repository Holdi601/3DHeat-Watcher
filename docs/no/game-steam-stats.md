---
title: "Steam-statistikk (plattform)"
nav_order: 42
lang: "no"
source: game-steam-stats.md
source_hash: "09ecf3611c02"
nav_exclude: true
search_exclude: true
---
# Steam-statistikk (plattform) {#steam-statistics-platform}

Watcheren lagrer det Steam-statistikk holder om spillene dine, slik at du senere kan se på historikken din som statistikk og tidslinje.

*Tekniske detaljer: adapter `steam-stats`, type [`platform`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill starter) og ser etter nye data hvert 30. s.*

## Hva som tas opp {#what-is-recorded}

- hver statistikk et spill lagrer i Steam (dets egne navn og verdier), per spill, når den endres
- oppnåelser låst opp, med visningsnavn, beskrivelse og tidspunkt for opplåsing
- endringer i statistikk med gammel verdi, ny verdi og differanse
- spilletid (minutter, siste to uker) og sist spilt

## Hvor det kommer fra {#where-it-comes-from}

Steams lokale statistikkbuffer %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin med UserGameStatsSchema_&lt;appid>.bin; spilletid fra %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% fra HKCU\Software\Valve\Steam SteamPath)

## Slik slår du det på {#how-to-switch-it-on}

Ingenting må slås på: watcheren leser kilden slik spillet eller plattformen gir den.

## Slik fungerer det {#how-it-works}

Det launcheren og grafikkdriveren holder om spilling: Steams statistikk,
oppnåelser, spilletid og tidslinjer, og NVIDIAs høydepunkter og klipp.

Ingen av disse kildene krever at et spill samarbeider eller kjører, så de tre adapterne
her er alltid på og ser på noen få filer hvert par sekund.

#### Steam-statistikk (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, skrevet på nytt av
Steam-klienten hver gang et spill lagrer statistikken sin, dekodet med skjemaet
`UserGameStatsSchema_<appid>.bin` ved siden av (binære KeyValues, se `_steam.py`).
Statistikk er heltall eller desimaltall slik spillet definerer dem; oppnåelser er bit med
et opplåsingstidspunkt i Unix-sekunder. Spilletid står i
`<Steam>\userdata\<account>\config\localconfig.vdf` under apps/&lt;appid>:
Playtime og Playtime2wks i minutter, LastPlayed i Unix-sekunder.
Steam finnes via HKCU\Software\Valve\Steam SteamPath.
Statistikk-API: <https://partner.steamgames.com/doc/features/achievements>

Den samme modulen betjener også: [NVIDIA-høydepunkter (plattform)](game-nvidia-highlights.md), [Steam-tidslinje (plattform)](game-steam-timeline.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | nei |
| Opp-akse | `y` |
| Enheter | meter |
| Speilvendt for visningen | ingen |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse går inn i hver sesjons `meta.json` (`axes`) og, når sesjonen har posisjoner, i `heat.parquet`s fotnote, så 3DHeat-visningen snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **nei**. `games --markdown` viser dette som "enkeltspiller".
- Type `platform`: den leser bare det spillet eller plattformen gir ut (det Steam eller grafikkdriveren beholder), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som tas opp {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver sesjons `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

En nøkkel i klammer fylles ut ved kjøring (`score.{team}` er én nøkkel per lag). Nøkler koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; «Hva som tas opp» ovenfor nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller beholdes, og det blir aldri kastet. Ved siden av radene beholdes hver pakke, side, linje eller svar adapteren mottar, helt i sesjonens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, pluss hvert felt som beholdes med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Lest**

- hver statistikk i statistikkfilen med sitt API-navn (heltall, desimaltall, avgrate), hver oppnåelsesbit med opplåsingstidspunkt, navngitt og beskrevet av skjemaet
- endringer mot forrige lesing (gammel, ny, differanse), nye opplåsinger; spilletid, to-ukers spilletid og sist spilt fra localconfig.vdf

**Beholdt rått**

- `UserGameStats`: statistikkfilens bytes, hele, hver gang den tas opp (`crc`, `PendingChanges`, oppnåelsesbit skjemaet ikke lenger definerer, og alle nøkler dekoderen hopper over, står i den)
- `UserGameStatsSchema`: skjemafilens bytes ved siden av, så statistikken kan dekodes fra sesjonen alene (hver statistikks og oppnåelses navn på alle språk, ikoner, flagg)
- `localconfig_app`: spillets hele blokk fra localconfig.vdf som JSON (synkroniseringstilstand i skyen, startvalg, merker og hver annen nøkkel Steam holder per spill) når spilletiden tas opp
- en statistikkfil dekoderen ikke kan lese (klippet midt i skriving, eller et nytt oppsett): bytene og skjemaet i en sesjon uten rader (`used` false; `unreadable` i meta.json)

**Ikke tilgjengelig**

- resten av localconfig.vdf (venner, chat, Steam-innstillinger): ikke spillets, og privat
- statistikkverdier mellom to skrivinger: Steam skriver filen på nytt når spillet lagrer statistikken, vanligvis når det lukkes
- globale oppnåelsesprosenter og andre spilleres statistikk: de ligger på Steams servere, ikke her

**Størrelse**: noen KB per tatt opp økt, pluss skjemaet (opptil noen hundre KB for et spill med mange oppnåelser) - godt under 1 MB per time spilt; zstd krymper skjemaets tekst med halvparten eller mer

## Verifisert {#verified}

testet på ekte statistikkfiler og skjemaer fra en lokal installasjon; endringsdeteksjon testet på filer bygd i det binære KeyValues-formatet

## Kilde {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
