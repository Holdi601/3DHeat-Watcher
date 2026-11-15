---
title: "Automobilista 2 (dados ao vivo)"
nav_order: 6
lang: "pt"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (dados ao vivo) {#automobilista-2-live-data}

Enquanto se joga Automobilista 2, o watcher guarda os dados que o próprio jogo envia para fora, para se poderem ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `automobilista-2`, tipo [`telemetry`](sources-and-rules.md); ele corre enquanto `AMS2AVX.exe` ou `AMS2.exe` está em execução e procura novos dados a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- a posição (XYZ no mundo, m) de cada carro a 10 Hz, por nome do piloto, com o próprio carro marcado, com velocidade e posição na corrida; marcha, acelerador e freio do próprio carro
- início da sessão com a pista que o jogo informa; voltas por carro com o tempo da volta; chegadas; as próprias paradas nos boxes
- teleportes (de volta aos boxes, um reinício): `teleport` onde o carro estava, `spawn` onde ele está agora
- as próprias voltas, melhor volta, posição na corrida, distância, velocidade máxima
- toda a página de memória partilhada do jogo em `heat.raw.parquet`, cada vez que muda

## De onde vêm os dados {#where-it-comes-from}

memória partilhada $pcars2$ (layout SharedMemory.h da SMS)

## Como ativar {#how-to-switch-it-on}

No jogo: Opções > Sistema > Memória partilhada: "Project CARS 2"

## Como funciona {#how-it-works}

Memória partilhada que os jogos de corrida publicam para painéis, aberta só para leitura, e nunca criada.

Vários simuladores entregam a sua telemetria como um mapeamento de ficheiro nomeado do Windows, que o jogo cria e que qualquer um pode ler: as páginas `Local\acpmf_*` da Kunos (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` do AC EVO), `Local\IRSDKMemMapFileName` do iRacing, `$R3E` do RaceRoom, `$pcars2$` do Automobilista 2 / Project CARS 2.

Porque não `mmap.mmap(-1, size, tagname=...)`, que é a forma comum em Python: quando o mapeamento ainda não existe, ele o *cria*, e aqui isso seria só leitura. Um jogo iniciado depois abre o mapeamento do watcher em vez de criar o seu, e aí não consegue escrever nele, então a telemetria dele fica morta até o watcher soltar. O watcher inicia um adaptador assim que o processo do jogo aparece, exatamente no momento em que o jogo ainda não criou o seu mapeamento. Por isso isto abre com `OpenFileMappingW`, que só encontra um mapeamento existente, mapeia com `FILE_MAP_READ` e informa "ainda não existe" no caso contrário; os adaptadores tentam de novo logo depois.

Nada aqui consegue escrever: a visão é mapeada só para leitura e só é copiada com `ctypes.string_at`.

Dois jogos são lidos aqui também; cada carro na pista está nas páginas próprias.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

`SharedMemory.h` da SMS (distribuído na pasta Support\SharedMemory do jogo; AMS2: Opções > Sistema > Memória partilhada "Project CARS 2"), `#pragma pack(4)`. `mParticipantInfo[64]` a partir do byte 28, 100 bytes cada: mIsActive, mName[64], mWorldPosition[3] (m, Y para cima), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) é o carro do jogador; por participante, mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); o mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear do jogador; mSequenceNumber (7320) fica ímpar enquanto o jogo escreve. Os deslocamentos foram obtidos a partir de duas cópias independentes do cabeçalho (a cópia do próprio jogo não está instalada aqui), que concordam entre si.

As duas páginas são guardadas inteiras além disso (docs/converters.md, "Live sources"): o mapeamento inteiro, cada leitura cujos bytes diferem da cópia guardada por último, no ficheiro bruto anexo da sessão sob o `type` `r3e` ou `pcars2` — cada slot de piloto e cada campo da estrutura, também os que não são lidos aqui, para que um decodificador futuro precise só do ficheiro bruto.

O mesmo módulo também serve: [Project CARS 2 (dados ao vivo)](game-project-cars-2.md), [RaceRoom Racing Experience (dados ao vivo)](game-raceroom.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros |
| Espelhado para o visualizador | nenhum |
| Escala da unidade (`scale`: o visualizador multiplica as posições por ele) | 1 |

Estes valores vão para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`. Assim o visualizador do 3DHeat gira e dimensiona as linhas sozinho: veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `telemetry`: lê só o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), por isso grava também em jogo online, além do offline; a marcação decide apenas se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online: veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- por participante (até 64): ativo, nome, posição no mundo, posição na corrida, voltas completadas; a última volta, o estado de corrida e a velocidade dele
- o carro do jogador (mViewedParticipantIndex), estado do jogo e da sessão, local e variante da pista, melhor e última volta, velocidade, freio, acelerador, marcha; mSequenceNumber para descartar uma cópia apanhada a meio de uma escrita
- deslocamentos de duas cópias independentes do SharedMemory.h da SMS que concordam, verificados numa página montada a partir delas nos testes; ainda não verificados contra o jogo

**Mantido bruto**

- `pcars2`: o mapeamento $pcars2$ inteiro (a estrutura vai bem além dos 11.312 bytes lidos aqui), cada leitura cujos bytes diferem da cópia guardada por último: a orientação de cada participante, os tempos de setor, nomes de carro e de classe, modos e flags de box, a física, pneus, suspensão, danos e clima do jogador, e tudo o que versões posteriores do Automobilista 2 acrescentaram
- `used` fica verdadeiro para uma página lida em linhas; falso para uma página nos menus, pausada, em replay, de outro layout, ou apanhada a meio de uma escrita (`torn` 1); `unchanged_reads` no meta.json conta as leituras byte a byte iguais à cópia guardada antes

**Não disponível**

- entradas e física dos outros participantes: a página dá só o carro visto
- tudo enquanto a opção de memória partilhada do jogo está desligada (o Automobilista 2 não escreve nada nesse caso)

**Tamanho**: o mapeamento tem cerca de 20 a 30 KB (conforme a versão do jogo), até 10 vezes por segundo enquanto se dirige: aproximadamente 0,7 a 1,1 GB por hora antes da compressão; o zstd reduz os slots de participante vazios e os nomes que não mudam a uma fração (ainda não medido numa sessão real)

## Verificado {#verified}

testado com uma página montada no teste; deslocamentos de duas cópias independentes do SharedMemory.h que concordam, não da cópia que o jogo distribui; não testado contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
