---
title: "Microsoft Flight Simulator 2020 (dados ao vivo)"
nav_order: 31
lang: "pt"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (dados ao vivo) {#microsoft-flight-simulator-2020-live-data}

Enquanto se joga Microsoft Flight Simulator 2020, o watcher guarda os dados que o próprio jogo envia para fora, para que se possa ver depois, num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `msfs2020`, tipo [`telemetry`](sources-and-rules.md); ele corre enquanto `FlightSimulator.exe` está aberto e procura dados novos a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- a posição da própria aeronave a cada quadro da simulação, amostrada a 10 Hz (latitude/longitude/altitude como metros a leste/acima/norte do primeiro ponto; lat/lon/alt guardados como colunas)
- atitude, velocidade indicada, velocidade em relação ao solo, AGL, g, no solo; velocidade verdadeira, Mach, velocidade vertical, AoA, derrapagem, rumo magnético, velocidades do corpo, acelerações e taxas de rotação a cerca de 10 Hz
- peso, combustível, flaps, trem de pouso, spoilers, freio de estacionamento, piloto automático, acelerador, RPM, clima, velocidade da simulação, hora e estado da câmara a cada segundo; o título da aeronave e o tipo ATC, modelo e id
- decolagens, pousos, quedas, voos iniciados e encerrados (session_start/session_end)
- tempo de voo, tempo no ar, distância, maior altitude, maior g, pousos
- cada mensagem do SimConnect guardada por inteiro em heat.raw.parquet

## De onde vem {#where-it-comes-from}

SimConnect pelo SimConnect.dll do próprio jogador (a pasta do simulador, ou %MSFS_SDK%\SimConnect SDK\lib)

## Como ligar {#how-to-switch-it-on}

nada; o SimConnect.dll vem com o MSFS 2020 (ou com o SDK do MSFS)

## Como funciona {#how-it-works}

Microsoft Flight Simulator 2020 e 2024: SimConnect, pelo SimConnect.dll do próprio jogador.

SimConnect é a API cliente publicada do simulador (documentação do SDK: <https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>, <https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>). O watcher não traz a DLL: ele carrega a que veio com o simulador ou com o seu SDK - o MSFS 2020 coloca `SimConnect.dll` na pasta de instalação; o MSFS 2024 na Steam traz apenas a interna, então os jogadores de 2024 instalam o SDK do MSFS 2024 (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; o simulador de 2024 também aceita clientes de 2020).

As chamadas, do SimConnect.h, todas a devolver um HRESULT (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL quando nada espera
SimConnect_Close(HANDLE)
```

Cada mensagem começa com SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} (#pragma pack 1). As lidas aqui:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], depois os DWORDs de versão
3  QUIT            o simulador está a fechar
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, depois os valores (FLOAT64 cada aqui)
```

Variáveis de simulação (unidades pedidas para que não haja conversão): PLANE LATITUDE/LONGITUDE (graus), PLANE ALTITUDE (metros, acima do nível do mar), PLANE ALT ABOVE GROUND (metros), PLANE PITCH/BANK DEGREES e PLANE HEADING DEGREES TRUE (graus; os sinais do próprio SimConnect - nariz para cima é arfagem negativa), AIRSPEED INDICATED e GROUND VELOCITY (nós), G FORCE (gforce), SIM ON GROUND (booleano). Eventos de sistema: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Mais três definições de dados pedem o resto do voo (`MOTION_VARS`, a cada sexto quadro da simulação), o estado mais lento da aeronave (`STATE_VARS`, uma vez por segundo) e os nomes dela (`NAME_VARS`, strings de 256 bytes, quando mudam); cada uma é uma definição própria, então uma variável que uma versão do simulador não conhece custa apenas aquele bloco. Cada mensagem é guardada por inteiro no ficheiro auxiliar bruto da sessão.

As posições vão para o mesmo mapa plano que o do X-Plane (x leste, y altitude, z norte, em metros a partir do primeiro ponto da sessão); esse ponto é o `geo` da sessão, no meta.json e no rodapé da tabela.

O mesmo módulo também serve: [Microsoft Flight Simulator 2024 (dados ao vivo)](game-msfs2024.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros (leste, altitude, norte a partir do primeiro ponto) |
| Espelhado para o visualizador | `z` |
| Escala das unidades (`scale`: o visualizador multiplica as posições por ele) | 1 |

Isso vai para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`, de modo que o visualizador do 3DHeat gira e ajusta as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `telemetry`: ele lê apenas o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), por isso grava também em partidas online, e não só offline; a marcação só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem a memória, e nunca num jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado por inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- SIMOBJECT_DATA da definição de posição (a cada quadro da simulação): latitude, longitude, altitude, AGL, arfagem, inclinação, rumo verdadeiro, IAS, velocidade em relação ao solo, g, no solo - o último quadro da consulta como linha; cada quadro para toques e decolagens
- SIMOBJECT_DATA da definição de movimento (cerca de 10 Hz: TAS, Mach, velocidade vertical, AoA, derrapagem, rumo magnético, velocidade do corpo, aceleração e taxa de rotação nos três eixos) e da definição de estado (1 Hz: pesos, combustível, flaps, trem de pouso, spoilers, freio de estacionamento, piloto automático, motores, acelerador e RPM, temperatura externa, vento, pressão ao nível do mar, velocidade da simulação, hora zulu e local, estado da câmara) nas linhas, como foram recebidos por último
- SIMOBJECT_DATA da definição de nomes (título, tipo ATC, modelo e id) no meta.json e na coluna `aircraft` das linhas; OPEN (aplicação e versão) no meta.json
- EVENT e EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (o ficheiro de voo) e AircraftLoaded (o ficheiro da aeronave) como voos, quedas e meta.json
- QUIT encerra a sessão

**Guardado bruto**

- cada mensagem que o SimConnect entrega ao watcher, por inteiro como `payload`, sob o nome do SIMCONNECT_RECV_ID dele: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (uma variável ou evento que o simulador não aceitou, com o id de envio e o índice), qualquer outro id pelo nome ou `RECV_<id>`
- o que só o ficheiro auxiliar bruto guarda: a posição de cada quadro da simulação entre as linhas, os eventos Pause, Sim, CrashReset, PositionChanged e FlightSaved, uma definição que o simulador recusou (uma variável que ele não conhecia: o bloco então não é lido pelo nome); `requests` no meta.json lista as variáveis e unidades de cada definição, em ordem, para que os payloads sejam lidos sem este módulo

**Não disponível**

- outras aeronaves (tráfego de IA, outros jogadores online): SimConnect_RequestDataOnSimObjectType consultaria todas as aeronaves num raio - mais carga no simulador, e voos de outros jogadores
- o bloco de movimento a cada quadro da simulação: ele é pedido a cada sexto quadro (cerca de 10 Hz, a taxa das linhas), o que mantém o feed bruto perto de um quinto do tamanho; o bloco de posição continua a cada quadro
- as milhares de outras variáveis de simulação (rádios, luzes, todos os instrumentos de cada motor, falhas): uma definição guarda o que pede; as listas pedem o voo, o estado da aeronave e a hora da simulação
- dados meteorológicos observados, instalações (aeroportos, VORs), dados de cliente de complementos: pedidos separados, não feitos

**Tamanho**: cerca de 30 a 55 MB por hora antes do zstd: o bloco de posição a cada quadro da simulação (cerca de 200 bytes com o quadro, 30 a 60 por segundo), o bloco de movimento a cerca de 10 Hz (cerca de 240 bytes), o bloco de estado uma vez por segundo; o zstd reduz os doubles várias vezes

## Verificado {#verified}

decodificação de mensagens testada com buffers montados a partir dos layouts do SimConnect.h; a conexão SimConnect ao vivo não foi testada

## Fonte {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
