---
title: "Statistikat e Steam (platformë)"
nav_order: 42
lang: "sq"
source: game-steam-stats.md
source_hash: "09ecf3611c02"
nav_exclude: true
search_exclude: true
---
# Statistikat e Steam (platformë) {#steam-statistics-platform}

Watcher-i ruan atë që mbajnë statistikat e Steam për lojërat e tua, që më vonë ta shohësh historikun tënd si statistika dhe si vijë kohore.

*Detaje teknike: adapteri `steam-stats`, lloji [`platform`](sources-and-rules.md); punon gjithë kohën (nuk pret të nisë një lojë) dhe kërkon të dhëna të reja çdo 30 s.*

## Çfarë regjistrohet {#what-is-recorded}

- çdo statistikë që një lojë ruan në Steam (emrat dhe vlerat e saj), për çdo lojë, kur ndryshon
- arritjet e zhbllokuara me emrin e shfaqur, përshkrimin dhe kohën e zhbllokimit
- ndryshimet e statistikave me vlerën e vjetër, vlerën e re dhe ndryshimin
- koha e luajtur (minuta, dy javët e fundit) dhe koha e luajtjes së fundit

## Nga vjen {#where-it-comes-from}

Cache-i lokal i statistikave të Steam %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin me UserGameStatsSchema_&lt;appid>.bin; koha e luajtur nga %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% nga HKCU\Software\Valve\Steam SteamPath)

## Si ta ndezësh {#how-to-switch-it-on}

Nuk ka nevojë të ndezësh asgjë: watcher-i e lexon burimin ashtu siç e jep loja ose platforma.

## Si funksionon {#how-it-works}

Ajo që mbajnë nisësi dhe drejtuesi i grafikës për lojën: statistikat, arritjet,
koha e luajtur dhe vijat kohore të Steam, si dhe momentet kryesore dhe klipet e NVIDIA.

Asnjë nga këto burime nuk ka nevojë që loja të bashkëpunojë ose të jetë duke punuar, ndaj tre
adapterët këtu janë gjithmonë të ndezur dhe shikojnë disa skedarë çdo disa sekonda.

#### Statistikat e Steam (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, i rishkruar nga
klienti Steam sa herë që një lojë ruan statistikat e saj, i dekoduar me skemën
`UserGameStatsSchema_<appid>.bin` pranë tij (KeyValues binare, shih `_steam.py`).
Statistikat janë numra të plotë ose dhjetorë siç i përcakton loja; arritjet janë bite
me kohë zhbllokimi në sekonda Unix. Koha e luajtur është te
`<Steam>\userdata\<account>\config\localconfig.vdf` nën apps/&lt;appid>:
Playtime dhe Playtime2wks në minuta, LastPlayed në sekonda Unix.
Steam gjendet përmes HKCU\Software\Valve\Steam SteamPath.
API e statistikave: <https://partner.steamgames.com/doc/features/achievements>

I njëjti modul shërben edhe: [Momentet kryesore të NVIDIA (platformë)](game-nvidia-highlights.md), [Steam Timeline (platformë)](game-steam-timeline.md).

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

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Një çelës në kllapa gjarpërore plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher-i ndjek [rregullin e konverterëve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: ajo që mban burimi lexohet ose ruhet, nuk hidhet kurrë. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që merr adapteri ruhet e plotë në `heat.raw.parquet` të sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rresht), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexohet**

- çdo statistikë e skedarit të statistikave me emrin e saj në API (int, float, avgrate), çdo bit arritjeje me kohën e zhbllokimit, e emërtuar dhe e përshkruar nga skema
- ndryshimet ndaj leximit të fundit (e vjetra, e reja, diferenca), zhbllokimet e reja; koha e luajtur, koha e luajtur në dy javë dhe koha e luajtjes së fundit nga localconfig.vdf

**Ruhet e papërpunuar**

- `UserGameStats`: bajtet e skedarit të statistikave, të plota, sa herë që regjistrohet (`crc`, `PendingChanges`, bitet e arritjeve që skema nuk i përcakton më dhe çdo çelës që dekoduesi e kapërcen janë aty)
- `UserGameStatsSchema`: bajtet e skedarit të skemës pranë tij, që statistikat të dekodohen nga sesioni vetëm (emrat e çdo statistike dhe arritjeje në çdo gjuhë, ikonat, flamujt)
- `localconfig_app`: blloku i plotë i lojës në localconfig.vdf si JSON (gjendja e sinkronizimit në re, opsionet e nisjes, distinktivet dhe çdo çelës tjetër që Steam mban për çdo lojë) kur regjistrohet koha e luajtur
- një skedar statistikash që dekoduesi nuk e lexon (i prerë gjatë shkrimit, ose me strukturë të re): bajtet e tij dhe skema në një sesion pa rreshta (`used` false; `unreadable` në meta.json)

**Nuk ka**

- pjesa tjetër e localconfig.vdf (miqtë, biseda, cilësimet e Steam): nuk janë të lojës dhe janë private
- vlerat e statistikave midis dy shkrimeve: Steam e rishkruan skedarin kur loja ruan statistikat, zakonisht kur mbyllet
- përqindjet globale të arritjeve dhe statistikat e lojtarëve të tjerë: janë në serverët e Steam, jo këtu

**Madhësia**: disa KB për çdo ulje të regjistruar, plus skema (deri në disa qindra KB për një lojë me shumë arritje) - shumë poshtë 1 MB për orë loje; zstd e zvogëlon tekstin e skemës përgjysmë ose më shumë

## Verifikuar {#verified}

testuar me skedarë dhe skema reale statistikash nga një instalim lokal; zbulimi i ndryshimeve testuar me skedarë të ndërtuar në formatin binar KeyValues

## Burimi {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
