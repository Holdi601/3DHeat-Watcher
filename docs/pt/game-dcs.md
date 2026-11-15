---
title: "DCS World (dados ao vivo)"
nav_order: 10
lang: "pt"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (dados ao vivo) {#dcs-world-live-data}

Enquanto se joga DCS World, o watcher guarda os dados que o próprio jogo envia para fora, para que se possa ver depois, num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `dcs`, tipo [`telemetry`](sources-and-rules.md); ele corre enquanto `DCS.exe` está aberto e procura dados novos a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- a própria posição a 10 Hz, em metros a leste/altura/norte da origem do teatro (a partir de latitude/longitude/altitude); lat/lon/alt e os metros do mundo do próprio DCS (dcs_x norte, dcs_y para cima, dcs_z leste) como colunas
- atitude, velocidade indicada e verdadeira, Mach, velocidade vertical, ângulo de ataque e derrapagem, rumo magnético, AGL e altitude radar, g nos três eixos, velocidade e taxas de rotação, no ar, a posição da câmara e seu vetor de direção, tipo de aeronave
- decolagens e pousos com o aeródromo; quedas, ejeções, mortes de pilotos
- abates e ser abatido, com os dois tipos de unidade e a arma; outros eventos do jogo como vierem
- vidas por missão (spawn ... session_end), abates, mortes, distância, maior altitude, maior g
- cada linha que o hook envia, guardada por inteiro em heat.raw.parquet, com um despejo a cada segundo das tabelas de exportação da aeronave (motores, trem de pouso e flaps, carga, contramedidas, rota, navegação) e cada outro callback (pausa, chat, jogadores a entrar, carregamento da missão)

## De onde vem {#where-it-comes-from}

o hook do watcher %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, linhas UDP para 127.0.0.1:41993

## Como ligar {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (adiciona Scripts\Hooks\heat3d-watch.lua), depois reinicie o DCS

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz o motivo; [Instalação e execução](installing-and-running.md) explica as causas mais comuns.

`python -m heat3d_watch setup dcs` lista os ficheiros que seriam alterados; `python -m heat3d_watch setup dcs --apply` faz as alterações e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `dcs: changed: ...` para cada alteração, ou `dcs: nothing to change` quando já estiver ligado.

## Como funciona {#how-it-works}

DCS World: um pequeno script de hook do próprio watcher, que envia linhas UDP para 127.0.0.1:41993.

O DCS executa os ficheiros Lua de `Saved Games\DCS*\Scripts\Hooks\` ao arrancar; um hook pode usar as funções de exportação (`Export.Lo*`) e receber os callbacks da simulação (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - veja `<DCS>\API\DCS_ControlAPI.html` e <https://wiki.hoggitworld.com/view/DCS_Export_Script>. O `setup` grava `heat3d-watch.lua` ali (um ficheiro próprio: o Export.lua e os hooks de outras ferramentas não são tocados), que envia dez linhas por segundo, mais uma por segundo, e uma para cada evento do jogo ou callback, sem nunca esperar resposta. A porta é 41993 para que o hook do JoyPro (41992) e o Tacview (42674) continuem a funcionar ao lado dela. As linhas (campos separados por ';'):

```text
hello;v=2                                       o hook foi carregado
start;mission=..;map=..;me=<id do jogador>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   a data, a hora de início e o clima da missão, achatados
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   uma vez por segundo
ev;t=..;name=<nome do onGameEvent>;args=a|b|c      cada onGameEvent
cb;t=..;name=<callback>;args=a|b                   cada outro callback (pausa, chat, jogadores, carregamento)
noexport;t=..                                      o servidor proíbe a exportação da própria aeronave
stop;t=..                                          a missão terminou
```

`p` é LoGetSelfData: Position x/y/z - metros do mundo do próprio DCS, x norte, y para cima, z leste - mais LatLongAlt (graus, m), Heading/Pitch/Bank (radianos), com LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) e LoGetAccelerationUnits() x/y/z (g); e, como o `Scripts\Export.lua` as documenta, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack e LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (m/s no mundo), LoGetAngularVelocity (rad/s), LoGetInAir, e o ponto e o vetor de direção de LoGetCameraPosition (metros do mundo). `d` é um despejo, a cada segundo, de tabelas inteiras, achatadas em chaves com pontos: LoGetSelfData (país, coalizão, nomes de unidade e de grupo, níveis de tipo, sinalizadores), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus e alguns números (pausa, aceleração do tempo, assento, pressão, desvios). O watcher guarda cada linha por inteiro no ficheiro auxiliar bruto; `p` também passa a linhas.

As posições vão para o mesmo mapa plano que o dos outros simuladores de voo (`Tangent`: x leste, y altitude acima do nível do mar, z norte, metros), a partir de LatLongAlt, em torno da origem fixa do teatro (`THEATRES`, a partir do `map` da linha de início), de modo que cada missão num mesmo teatro partilha um mapa, e um mapa no qual o visualizador pode colocar o mundo real. Um teatro que não está na tabela usa a latitude e a longitude do primeiro ponto, arredondadas para graus inteiros. Os x/y/z do próprio DCS são guardados como `dcs_x`, `dcs_y`, `dcs_z`; um ponto sem LatLongAlt não pode ser posicionado e apenas é contado (`fixes_without_latlon`). A origem é o `geo` da sessão, no meta.json e no rodapé da tabela.

Os argumentos de onGameEvent, como o DCS_ControlAPI os entrega: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Um servidor multijogador pode proibir a exportação da própria aeronave (LoIsOwnshipExportAllowed é false); nesse caso não há posições, só eventos, e a sessão informa isso.

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros (leste, altitude, norte a partir da origem do teatro) |
| Espelhado para o visualizador | `z` |
| Escala das unidades (`scale`: o visualizador multiplica as posições por ele) | 1 |

Isso vai para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`, de modo que o visualizador do 3DHeat gira e ajusta as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `telemetry`: ele lê apenas o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), por isso grava também em partidas online, e não só offline; a marcação só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem a memória, e nunca num jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado por inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- `p` (10 Hz): posição, LatLongAlt, atitude, IAS, AGL, g (x/y/z), tipo de aeronave, e de TAS, Mach, velocidade vertical, AoA, derrapagem, rumo magnético, altitude radar, velocidade do mundo, taxas de rotação, no ar e ponto/vetor de direção da câmara do hook 2 - tudo como colunas de linha (unidades como o Export.lua as entrega)
- `start`: missão, teatro, id e nome do próprio jogador, multijogador, ficheiro da missão, servidor; `mis`: a data e a hora de início da missão no meta.json
- `ev`: cada onGameEvent como uma linha (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, qualquer outro nome como vier)
- `noexport` e `stop` como linhas e no meta.json

**Guardado bruto**

- cada linha que o hook envia, por inteiro, como `text`, sob o tipo dela: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; uma linha de qualquer outro tipo sob `unknown`
- `d` (1 Hz, só bruto): LoGetSelfData inteiro (país, coalizão, nome de unidade e de grupo, níveis de tipo, sinalizadores), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vetor de vento, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, balizas de rádio, pausa, aceleração do tempo, assento, pressão, desvios - achatados em chaves com pontos
- `mis`: a tabela de clima da missão, achatada; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage com os argumentos deles

**Não disponível**

- outras unidades (LoGetWorldObjects, LoGetObjectById) e dados de sensores (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): não pedidos - todo objeto de uma missão a 10 Hz custa caro dentro do próprio quadro do DCS, e um servidor os controla (allow_object_export, allow_sensor_export); o Tacview os grava
- a tabela inteira da missão (DCS.getCurrentMission tem cada unidade e gatilho, megabytes): só a data, a hora de início, o clima, a surtida, o teatro e a versão são enviados
- os callbacks onPlayerTry\*: eles respondem ao DCS (permitir ou recusar), por isso o hook não mexe neles
- endereços e UCIDs de outros jogadores: net.get_player_info os entrega só a um servidor, e não são do jogador para guardar
- entradas de tabela além de 800 chaves ou de 6 níveis de profundidade numa linha `d` são cortadas, para que uma linha continue a ser um único datagrama

**Tamanho**: cerca de 20 MB por hora de linhas `p` (10 por segundo, cerca de 500 bytes cada com o quadro) e 15 a 40 MB de despejos `d` (um por segundo, 4 a 10 KB conforme a carga e a rota da aeronave), antes do zstd; as chaves repetidas comprimem cerca de dez vezes

## Verificado {#verified}

formato de linha testado com datagramas sintéticos; o hook em Lua não foi testado dentro do DCS (escrito a partir da API de hooks/exportação do DCS e da lista de funções Lo\* do Scripts\Export.lua, não executado)

## Fonte {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
