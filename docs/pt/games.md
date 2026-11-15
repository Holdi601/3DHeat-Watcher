---
title: Jogos
nav_order: 4
lang: "pt"
source: games.md
source_hash: "dcee7fc45a5b"
nav_exclude: true
search_exclude: true
---
# Jogos {#games}

O watcher conhece 50 fontes em 45 jogos e plataformas. Cada uma tem uma página própria, gerada a partir do adaptador: o que regista, de onde vem, como ligar, como funciona, os eixos e o que foi verificado.

Tipos: `telemetry`, `gsi`, `log`, `replay` e `platform` - veja [Fontes e regras](sources-and-rules.md). Posições: *sim* quando o adaptador escreve linhas com um lugar, *emprestada* quando vem de outra gravação do mesmo jogo (veja [NVIDIA Highlights](nvidia-highlights.md)), *não* quando a fonte não tem nenhuma. Os perfis de memória não aparecem nesta lista: nenhum vem junto, e cada um escreve o próprio (veja [Ler a memória](memory-reading.md)).

| Jogo | Tipo | Posições | Fonte |
|---|---|---|---|
| [American Truck Simulator (dados ao vivo)](game-ats.md) | telemetry | sim | memória partilhada `Local\SCSTelemetry`, escrita pelo plugin scs-sdk da RenCloud (revisão 12) em `<jogo>\bin\win_x64\plugins` |
| [Assetto Corsa (dados ao vivo)](game-assetto-corsa.md) | telemetry | sim | memória partilhada `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (dados ao vivo)](game-assetto-corsa-competizione.md) | telemetry | sim | memória partilhada `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (dados ao vivo)](game-assetto-corsa-evo.md) | telemetry | sim | memória partilhada `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (dados ao vivo)](game-assetto-corsa-rally.md) | telemetry | sim | memória partilhada `Local\acpmf_physics`, `Local\acpmf_static` (as mesmas páginas do AC e do ACC) |
| [Automobilista 2 (dados ao vivo)](game-automobilista-2.md) | telemetry | sim | memória partilhada $pcars2$ (layout SMS SharedMemory.h) |
| [BeamNG.drive (dados ao vivo)](game-beamng.md) | telemetry | sim | UDP 127.0.0.1:4460 a partir do mod de protocolo heat3d (mods/beamng/heat3d neste repositório) |
| [Counter-Strike 2 (replays)](game-cs2-demos.md) | replay | sim | demos que o CS2 guarda: `<CS2>/game/csgo/replays/*.dem` (transferidas do histórico de partidas) e `<CS2>/game/csgo/*.dem` (gravadas) |
| [Counter-Strike 2 (estado do jogo)](game-cs2-gsi.md) | gsi | sim | Game State Integration: envios HTTP para 127.0.0.1:3311, configurados por `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (dados ao vivo)](game-dcs.md) | telemetry | sim | o hook do watcher `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, linhas UDP para 127.0.0.1:41993 |
| [DiRT Rally 2.0 (dados ao vivo)](game-dirt-rally-2.md) | telemetry | sim | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); enquanto outra aplicação usa a 20777, o watcher deixa-lhe a porta |
| [Dota 2 (replays)](game-dota-replays.md) | replay | sim | replays que o Dota 2 guarda: `<Dota>/game/dota/replays/<id da partida>.dem` (transferidos no cliente, ou com `dota-replay <id da partida>`) |
| [Dota 2 (estado do jogo)](game-dota2-gsi.md) | gsi | sim | Game State Integration: envios HTTP para 127.0.0.1:3312, configurados por `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (dados ao vivo)](game-f1-23.md) | telemetry | sim | telemetria UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (dados ao vivo)](game-f1-24.md) | telemetry | sim | telemetria UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (dados ao vivo)](game-f1-25.md) | telemetry | sim | telemetria UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (dados ao vivo)](game-ea-wrc.md) | telemetry | sim | UDP 127.0.0.1:20777, o pacote session_update da estrutura `wrc` predefinida `(Documents\My` `Games\WRC\telemetry\config.json`); enquanto outra aplicação usa a 20777, o watcher deixa-lhe a porta |
| [Elite Dangerous (ficheiros de log)](game-elite.md) | log | sim | Diário do jogador `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (o ficheiro mais recente, acompanhado enquanto é escrito), Status.json e os outros ficheiros `*.json` do companheiro (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) na mesma pasta |
| [Euro Truck Simulator 2 (dados ao vivo)](game-ets2.md) | telemetry | sim | memória partilhada `Local\SCSTelemetry`, escrita pelo plugin scs-sdk da RenCloud (revisão 12) em `<jogo>\bin\win_x64\plugins` |
| [EVE Online (ficheiros de log)](game-eve.md) | log | não | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` e os `Chatlogs\*.txt` ao lado (cada ficheiro escrito desde que o cliente foi iniciado) |
| [Forza Horizon 4 (dados ao vivo)](game-forza-horizon-4.md) | telemetry | sim | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada pacote é reencaminhado sem alterações para 127.0.0.1:5301 |
| [Forza Horizon 5 (dados ao vivo)](game-forza-horizon-5.md) | telemetry | sim | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada pacote é reencaminhado sem alterações para 127.0.0.1:5301 |
| [Forza Horizon 6 (dados ao vivo)](game-forza-horizon-6.md) | telemetry | sim | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada pacote é reencaminhado sem alterações para 127.0.0.1:5301 |
| [Forza Motorsport (dados ao vivo)](game-forza-motorsport.md) | telemetry | sim | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada pacote é reencaminhado sem alterações para 127.0.0.1:5301 |
| [Hearthstone (ficheiros de log)](game-hearthstone.md) | log | não | `<instalação>\Logs\Power.log` (ou `Logs\Hearthstone_*\Power.log`), escrito quando `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` tem uma secção [Power], e cada outro `*.log` que o jogo escreve ali |
| [IL-2 Sturmovik: Great Battles (dados ao vivo)](game-il2.md) | telemetry | não | a saída de telemetria UDP do jogo para 127.0.0.1:41995 ([KEY = telemetrydevice] em `<jogo>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md) | replay | sim | as gravações Tacview do próprio jogo `<jogo>\data\Tracks\*.acmi` (texto ACMI 2.x, puro ou comprimido) |
| [iRacing (dados ao vivo)](game-iracing.md) | telemetry | não | memória partilhada `Local\IRSDKMemMapFileName` (o SDK do iRacing); ficheiros .ibt em `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (estado do jogo)](game-lol-live.md) | gsi | não | Live Client Data API do cliente do jogo, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), durante uma partida |
| [League of Legends (replays)](game-lol-replays.md) | replay | sim | replays que o cliente do League guarda: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (apenas os metadados simples do fim de partida); com a própria chave de API da Riot, a linha do tempo oficial da partida pela Match-V5 API da Riot |
| [Microsoft Flight Simulator 2020 (dados ao vivo)](game-msfs2020.md) | telemetry | sim | SimConnect pelo SimConnect.dll da própria instalação (a pasta do simulador, ou `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (dados ao vivo)](game-msfs2024.md) | telemetry | sim | SimConnect pelo SimConnect.dll da própria instalação (a pasta do simulador, ou `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (ficheiros de log)](game-minecraft.md) | log | sim | `%APPDATA%\.minecraft\logs\latest.log` (acompanhado), `saves\<mundo>\stats\<uuid>.json` e `saves\<mundo>\playerdata\<uuid>.dat` / level.dat (NBT comprimido em gzip), lidos quando o jogo os guarda |
| [NVIDIA highlights (plataforma)](game-nvidia-highlights.md) | platform | emprestada | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<jogo>\config.json`; os clipes na pasta de captura `(%USERPROFILE%\Videos\NVIDIA\<Jogo>\*.mp4`) e `<temp>\Highlights\<jogo>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (replays)](game-osu-replays.md) | replay | sim | replays que o osu! (versão estável) guarda: `%LOCALAPPDATA%/osu!/Data/r/*.osr` (cada partida jogada) e `osu!/Replays/*.osr` (exportados) |
| [Path of Exile (ficheiros de log)](game-poe.md) | log | não | `<instalação>\logs\Client.txt` do Path of Exile ou do Path of Exile 2 (acompanhado; a pasta de instalação é a do executável em execução) |
| [Project CARS 2 (dados ao vivo)](game-project-cars-2.md) | telemetry | sim | memória partilhada $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (dados ao vivo)](game-raceroom.md) | telemetry | sim | memória partilhada $R3E (r3e.h da Sector3, versão 3) |
| [Richard Burns Rally (dados ao vivo)](game-richard-burns-rally.md) | telemetry | sim | telemetria UDP do plugin NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (estado do jogo)](game-rocketleague-stats.md) | gsi | sim | Stats API: fluxo JSON TCP de 127.0.0.1:49123 (a porta em `<RL>\TAGame\Config\TAStatsAPI.ini` ou DefaultStatsAPI.ini) |
| [Squad (replays)](game-squad-demos.md) | replay | sim | demos de servidor que o Squad grava com o comando de administrador AdminDemoRec: `<servidor>/SquadGame/Saved/Demos/*.replay`, lidos pelo leitor externo `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (ficheiros de log)](game-starcitizen.md) | log | não | `<instalação>\StarCitizen\LIVE\Game.log` (a pasta de build do StarCitizen.exe em execução), só o ficheiro de log que o jogo escreve - um jogo com Easy Anti-Cheat: nada toca no processo do jogo |
| [Estatísticas da Steam (plataforma)](game-steam-stats.md) | platform | não | a cache local de estatísticas da Steam `%STEAM%\appcache\stats\UserGameStats_<conta>_<appid>.bin` com `UserGameStatsSchema_<appid>.bin`; tempo de jogo de `%STEAM%\userdata\<conta>\config\localconfig.vdf` (%STEAM% de `HKCU\Software\Valve\Steam` SteamPath) |
| [Linha do tempo da Steam (plataforma)](game-steam-timeline.md) | platform | não | `%STEAM%\userdata\<conta>\gamerecordings\timelines\timeline_<appid><data>_<hora>.json` |
| [VALORANT (replays)](game-valorant-replays.md) | replay | não | replays que o VALORANT guarda: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (apenas as partes que não estão ofuscadas) |
| [War Thunder (replays)](game-warthunder-replays.md) | replay | sim | replays que o War Thunder guarda: `<War` `Thunder>/Replays/*.wrpl` (com a gravação de replays ligada), convertidos pelo conversor externo `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (estado do jogo)](game-warthunder-webmap.md) | gsi | sim | o mapa web local do jogo, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replays)](game-wot-replays.md) | replay | sim | replays que o World of Tanks guarda: `<World` of `Tanks>/replays/*.wotreplay` (com a gravação de batalhas ligada), convertidos pelo conversor externo `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replays)](game-wows-replays.md) | replay | sim | replays que o World of Warships guarda: `<World` of `Warships>/replays/*.wowsreplay` (com replays ligados), convertidos pelo conversor externo `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (dados ao vivo)](game-xplane.md) | telemetry | sim | a interface UDP do X-Plane em 127.0.0.1:49000 (datarefs RREF e RPOS de posição, respondidos ao watcher) |

Jogos que não são gravados, e porquê: [Fontes e regras](sources-and-rules.md#what-is-declined-and-why). Tudo numa só tabela, como `python -m heat3d_watch games --markdown` a imprime: [Todos os jogos numa tabela](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
