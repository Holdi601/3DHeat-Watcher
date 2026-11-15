---
title: "Steam-statistik (platform)"
nav_order: 42
lang: "da"
source: game-steam-stats.md
source_hash: "09ecf3611c02"
nav_exclude: true
search_exclude: true
---
# Steam-statistik (platform) {#steam-statistics-platform}

Watcheren gemmer det, Steam-statistik holder om dine spil, så du senere kan se din historik som statistik og en tidslinje.

*Teknisk info: adapter `steam-stats`, type [`platform`](sources-and-rules.md); den kører hele tiden (den venter ikke på, at et spil starter) og kigger efter nye data hvert 30. sekund.*

## Hvad der optages {#what-is-recorded}

- hver stat et spil gemmer i Steam (dets egne navne og værdier), pr. spil, når den ændres
- oplåste achievements med visningsnavn, beskrivelse og oplåsningstidspunkt
- statistikændringer med gammel værdi, ny værdi og forskel
- spilletid (minutter, sidste to uger) og tidspunkt for sidste spil

## Hvor det kommer fra {#where-it-comes-from}

Steams lokale statistik-cache %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin med UserGameStatsSchema_&lt;appid>.bin; spilletid fra %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% fra HKCU\Software\Valve\Steam SteamPath)

## Sådan slår du det til {#how-to-switch-it-on}

Intet skal slås til: watcheren læser kilden, som spillet eller platformen leverer den.

## Sådan virker det {#how-it-works}

Det, launcheren og grafikdriveren gemmer om spil: Steams statistik, achievements, spilletid og tidslinjer, og NVIDIAs highlights og klip.

Ingen af disse kilder kræver, at et spil samarbejder eller kører, så de tre adaptere her er altid slået til og kigger på nogle få filer hvert par sekund.

#### Steam-statistik (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, skrevet om af Steam-klienten, hver gang et spil gemmer sine stats, afkodet med skemaet `UserGameStatsSchema_<appid>.bin` ved siden af (binære KeyValues, se `_steam.py`). Stats er heltal eller flydende tal, som spillet definerer dem; achievements er bits med et oplåsningstidspunkt i Unix-sekunder. Spilletid står i `<Steam>\userdata\<account>\config\localconfig.vdf` under apps/&lt;appid>: Playtime og Playtime2wks i minutter, LastPlayed i Unix-sekunder. Steam findes via HKCU\Software\Valve\Steam SteamPath.
Stats-API: <https://partner.steamgames.com/doc/features/achievements>

Det samme modul betjener også: [NVIDIA highlights (platform)](game-nvidia-highlights.md), [Steam Timeline (platform)](game-steam-timeline.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | nej |
| Op-akse | `y` |
| Enheder | meter |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse gemmes i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **nej**. `games --markdown` viser dette som "enkeltspiller".
- Type `platform`: den læser kun det, spillet eller platformen udleverer (det Steam eller grafikdriveren gemmer), så den optager i online-spil lige så vel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøgler, denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

En nøgle i klammer udfyldes under kørsel (`score.{team}` er én nøgle pr. hold). Nøgler, koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne, står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeat's [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det, kilden indeholder, bliver læst eller gemt, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, helt i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, samt alle felter gemt ved navn; `used` markerer det, der også blev til rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- hver stat i stats-filen under sit API-navn (int, float, avgrate), hver achievement-bit med sit oplåsningstidspunkt, navngivet og beskrevet af skemaet
- ændringer i forhold til sidste læsning (gammel, ny, forskel), nye oplåsninger; spilletid, to-ugers spilletid og sidst spillet fra localconfig.vdf

**Gemt rå**

- `UserGameStats`: stats-filens bytes, hele, hver gang den optages (`crc`, `PendingChanges`, achievement-bits, skemaet ikke længere definerer, og enhver nøgle afkoderen springer over, ligger i den)
- `UserGameStatsSchema`: skemafilens bytes ved siden af, så stats kan afkodes ud fra sessionen alene (hver stats og achievements navne på alle sprog, ikoner, flag)
- `localconfig_app`: spillets hele blok fra localconfig.vdf som JSON (synkroniseringstilstand i skyen, startindstillinger, badges og alle andre nøgler Steam gemmer pr. spil), når spilletiden optages
- en stats-fil, afkoderen ikke kan læse (skåret over midt i skrivningen, eller et nyt layout): dens bytes og skemaet i en session uden rækker (`used` falsk; `unreadable` i meta.json)

**Ikke tilgængeligt**

- resten af localconfig.vdf (venner, chat, Steam-indstillinger): ikke spillets, og privat
- stat-værdier mellem to skrivninger: Steam omskriver filen, når spillet gemmer sine stats, typisk når det lukkes
- globale achievement-procenter og andre spilleres stats: de ligger på Steams servere, ikke her

**Størrelse**: få KB pr. optaget session, plus skemaet (op til nogle hundrede KB for et spil med mange achievements) - langt under 1 MB pr. spilletime; zstd halverer eller mere skemaets tekst

## Verificeret {#verified}

testet på rigtige stats-filer og skemaer fra en lokal installation; ændringsregistrering testet på filer bygget i det binære KeyValues-format

## Kilde {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
