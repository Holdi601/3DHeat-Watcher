---
title: "Steam Timeline (platformë)"
nav_order: 43
lang: "sq"
source: game-steam-timeline.md
source_hash: "3a502e4ad09e"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (platformë) {#steam-timeline-platform}

Watcher-i ruan atë që mban Steam Timeline për lojërat e tua, që më vonë ta shohësh historikun tënd si statistika dhe si vijë kohore.

*Detaje teknike: adapteri `steam-timeline`, lloji [`platform`](sources-and-rules.md); punon gjithë kohën (nuk pret të nisë një lojë) dhe kërkon të dhëna të reja çdo 10 s.*

## Çfarë regjistrohet {#what-is-recorded}

- një sesion për çdo skedar vijë kohore: fillimi dhe fundi i tij (session_start, session_end)
- arritjet e zhbllokuara gjatë lojës, me kohë
- ndryshimet e mënyrës së lojës (duke luajtur, përgatitje, menu, ekran ngarkimi)
- ngjarjet që lojërat shtojnë përmes ISteamTimeline, me titull dhe përshkrim, nën emrin e ikonës së tyre
- fazat e lojës (një ndeshje, një mision) me etiketat e tyre; ngjarjet brenda një faze mbartin id-në e saj si sesion
- përshkrimet e gjendjes që loja shfaq në vijën kohore ("Round 3")
- gabimet e regjistrimit të vetë Steam

## Nga vjen {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Si ta ndezësh {#how-to-switch-it-on}

Steam > Settings > Game Recording: regjistro në sfond ose sipas kërkesës (atëherë Steam shkruan vijat kohore)

## Si funksionon {#how-it-works}

Ajo që mbajnë nisësi dhe drejtuesi i grafikës për lojën: statistikat, arritjet,
koha e luajtur dhe vijat kohore të Steam, si dhe momentet kryesore dhe klipet e NVIDIA.

Asnjë nga këto burime nuk ka nevojë që loja të bashkëpunojë ose të jetë duke punuar, ndaj tre
adapterët këtu janë gjithmonë të ndezur dhe shikojnë disa skedarë çdo disa sekonda.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
shkruar kur Steam Game Recording është i ndezur. Skedari është JSON me numra si
tekst: "daterecorded" (sekonda Unix), "starttime"/"endtime" (ms) dhe
"entries", secila {"id", "time" (ms nga daterecorded), "type", ...}. Llojet
e parë në skedarë realë:
```text
achievement        achievement_name - Steam i shton këto për çdo lojë
gamemode           mode, një ETimelineGameMode: 1 duke luajtur, 2 përgatitje, 3 menu,
                   4 ekran ngarkimi
error              description - e vetë Steam ("#GameRecording_RecordingFailed")
event              AddInstantaneousTimelineEvent/AddRangeTimelineEvent i një loje:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              një interval StartGamePhase..EndGamePhase: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
Struktura e skedarit është e Steam dhe e padokumentuar; fushat janë
parametrat e API-t. Çdo lloj tjetër regjistrohet nën emrin e vet me fushat e tij.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

I njëjti modul shërben edhe: [Momentet kryesore të NVIDIA (platformë)](game-nvidia-highlights.md), [Statistikat e Steam (platformë)](game-steam-stats.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | jo |
| Boshti lart | `y` |
| Njësitë | metra |
| E pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë në `meta.json` të çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Shumë lojtarë {#multiplayer}

- Shënuar si e luajtur në internet (`multiplayer`): **jo**. `games --markdown` e shfaq si "single-player".
- Lloji `platform`: lexon vetëm atë që loja ose platforma jep (ajo që mbajnë Steam ose drejtuesi i grafikës), ndaj regjistron si në lojë në internet ashtu edhe jashtë saj; flamuri vendos vetëm nëse memoria mund të lexohet ndonjëherë.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur në internet - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri vendos me emër (`stats` e çdo sesioni në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Një çelës në kllapa gjarpërore plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher-i ndjek [rregullin e konverterëve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: ajo që mban burimi lexohet ose ruhet, nuk hidhet kurrë. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që merr adapteri ruhet e plotë në `heat.raw.parquet` të sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rresht), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexohet**

- çdo hyrje një herë, si rresht në kohën e saj: lloji i saj, çdo fushë e thjeshtë (title, description, icon, priority, duration, possible_clip, emri i arritjes, mode, ...), etiketat e një faze sipas grupit, emri i shfaqur i arritjes nga skema e statistikave; fillimi dhe fundi i skedarit

**Ruhet e papërpunuar**

- çdo hyrje e plotë si JSON nën `type` e vetë Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, çdo tjetër): fushat e ndërthurura - ikona dhe prioriteti i një etikete, çdo gjë që Steam shton më vonë - janë vetëm këtu
- `timeline`: fushat e vetë skedarit (daterecorded, starttime, endtime, çdo tjetër), kur hapet sesioni dhe sërish kur ndryshojnë

**Nuk ka**

- vetë regjistrimi (video): Steam e mban në dosjet e veta; sesioni i referohet skedarit të vijës kohore me emër
- një lexim i një skedari që Steam po e shkruan dhe që nuk analizohet as me fundin e mbyllur: numërohet (`bad` në gjendjen e adapterit) dhe lexohet sërish në ndryshimin tjetër, ku merren hyrjet e tij

**Madhësia**: disa qindra hyrje me 100-300 bajte për orë loje: shumë poshtë 1 MB për orë

## Verifikuar {#verified}

testuar me skedarë realë vijash kohore nga një instalim lokal: hyrje achievement, gamemode, error, si dhe event, state_description dhe phase të vetë lojërave; vetë formati i skedarit është i padokumentuar

## Burimi {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
