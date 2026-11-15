---
title: "iRacing (dados ao vivo)"
nav_order: 28
lang: "pt"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (dados ao vivo) {#iracing-live-data}

Enquanto se joga iRacing, o watcher guarda os dados que o próprio jogo envia, para que se possam ver depois como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `iracing`, tipo [`telemetry`](sources-and-rules.md); corre enquanto `iRacingSim64DX11.exe` ou `iRacingSim64.exe` estiver em execução e procura dados novos a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- a condução a 5 Hz, sem posição (o iRacing não dá posição ao vivo): velocidade, marcha, acelerador, freio, volta, parte da volta, posição na corrida e na classe, incidentes
- início da sessão, entrar e sair do carro, entrar e sair do pit lane, voltas com o tempo de volta, incidentes com os respetivos pontos, bandeira quadriculada, chegada
- os ficheiros de telemetria .ibt gravados durante a sessão (latitude, longitude, altitude - o visualizador os lê)
- voltas, melhor volta, incidentes, posição na corrida, paradas nos boxes, distância, velocidade máxima
- toda a memória partilhada em `heat.raw.parquet`: cabeçalho, cabeçalhos de variáveis, informações da sessão, cada linha de telemetria lida

## De onde vem {#where-it-comes-from}

memória partilhada Local\IRSDKMemMapFileName (o SDK do iRacing); ficheiros .ibt em %USERPROFILE%\Documents\iRacing\telemetry

## Como ligar {#how-to-switch-it-on}

Nada para os dados ao vivo. Para posições: grave a telemetria no carro (Alt+L) ou defina irsdkLog=1 no ficheiro app.ini

## Como funciona {#how-it-works}

iRacing, ao vivo: a memória partilhada do SDK do iRacing, lida de forma nativa.

O iRacing publica a telemetria dele para as aplicações num mapeamento de ficheiro nomeado, `Local\IRSDKMemMapFileName`, que o simulador cria enquanto corre (e sinaliza `Local\IRSDKDataValidEvent` a cada atualização, o que não é necessário aqui: o watcher olha dez vezes por segundo). O layout é o `irsdk_defines.h` do SDK, também seguido pelo pyirsdk (MIT) - escrito de novo aqui a partir desses factos:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

O simulador escreve as `numBuf` linhas em rodízio; a mais nova é a de maior tickCount, e uma linha é lida de novo se o seu tickCount mudou enquanto era copiada.

Os dados ao vivo não têm posição no mundo - latitude, longitude e altitude só existem nos ficheiros `.ibt` que o iRacing grava em `Documents\iRacing\telemetry` (Alt+L no carro, ou `irsdkLog=1`), que o próprio visualizador 3DHeat lê. Então isto grava a condução como eventos sem coordenadas - velocidade, volta, a parte da volta feita, posição na corrida, incidentes - mais voltas, incidentes, paradas nos boxes e a bandeira quadriculada, e no fim os ficheiros `.ibt` gravados durante a sessão como eventos `telemetry_file`, para o visualizador abri-los.

Ao lado das linhas, o mapa de memória inteiro é guardado no ficheiro auxiliar bruto da sessão (`heat.raw.parquet`): a parte fixa do cabeçalho (`header`, cada vez que muda), os cabeçalhos de variáveis (`var_headers`, inteiros, e em `text` como JSON, cada vez que o layout muda), o YAML das informações da sessão (`session_info`, o texto dele cada vez que `sessionInfoUpdate` muda) e a linha de telemetria mais nova (`telemetry`, cada variável dela, em cada leitura que encontra um novo tick). Os cabeçalhos de variáveis e uma linha são tudo o que um decodificador posterior precisa para ler qualquer variável.

Fonte: o SDK do iRacing (irsdk_defines.h, documentação do fórum "iRacing SDK"); kutu/pyirsdk (MIT) para confirmar os deslocamentos.

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | não |
| Eixo para cima | `y` |
| Unidades | sem posições ao vivo; os ficheiros .ibt trazem latitude/longitude/altitude |
| Espelhado para o visualizador | nenhum |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `telemetry`: lê só o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- da linha de telemetria mais nova: tempo da sessão, número, estado e id, na pista, replay, volta, voltas completas, parte e metros da volta, última e melhor volta, velocidade, marcha, acelerador, freio, RPM, pit road, superfície da pista, posição na corrida e na classe, contagem de incidentes próprios (as linhas `driving` a 5 Hz e os eventos)
- agora também nas linhas `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (graus, a partir dos radianos do simulador - só quando o cabeçalho da variável dá a unidade como rad), `fuel_l` (unidade l), `lat_accel` e `lon_accel` (unidade m/s^2)
- do YAML das informações da sessão: o índice do carro do jogador, pista e configuração, tipos de sessão, nome, carro, equipa e número de cada piloto (linhas session_start, meta.json)
- verificado nos testes com um bloco montado a partir do irsdk_defines.h; ainda não verificado com o simulador

**Guardado bruto**

- `telemetry`: a linha mais nova inteira, cada variável que o simulador publica (os vetores CarIdx de cada carro, pneus, suspensão, os vetores `_ST` de alta taxa onde o simulador os tem ...), em cada leitura que encontra um novo tick; `tick` a contagem de ticks do simulador; `used` é falso enquanto um replay toca
- `var_headers`: os cabeçalhos de variáveis inteiros (144 bytes cada) e, em `text`, como JSON (nome, tipo, deslocamento, contagem, unidade, descrição), cada vez que o layout muda - o bastante para ler toda variável de toda linha guardada
- `session_info`: o texto YAML inteiro cada vez que o contador de atualização dele muda (fim de semana, sessões e resultados, pilotos, afinação do carro, rádio, listas de câmaras), `update` o contador
- `header`: o cabeçalho irsdk de 112 bytes inteiro cada vez que muda (versão, status, taxa de ticks, deslocamentos, os ticks das linhas)

**Não disponível**

- uma posição no mundo ao vivo: a memória partilhada não tem nenhuma; latitude, longitude e altitude só estão nos ficheiros .ibt (com a gravação ligada), que o visualizador lê - o watcher nomeia os gravados durante a sessão
- os ticks entre duas leituras: o simulador escreve 60 linhas por segundo em 3 ou 4 posições e o watcher lê 10 vezes por segundo, então a maioria dos ticks é sobrescrita antes de poder ser lida; o ficheiro .ibt tem todos os ticks quando a gravação está ligada

**Tamanho**: uma linha de telemetria tem alguns KB (cerca de 5 a 10 KB com os vetores de todos os carros), guardada até 10 vezes por segundo, mais o cabeçalho (112 bytes) com a mesma frequência e o YAML das informações da sessão (dezenas de KB) quando muda: cerca de 0,2 a 0,4 GB por hora na pista antes da compressão; o zstd reduz a uma fração (ainda não medido numa sessão real)

## Verificado {#verified}

testado com um bloco de memória partilhada montado no teste a partir do layout do irsdk; sem teste contra o simulador

## Fonte {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
