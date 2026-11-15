---
title: "RaceRoom Racing Experience (dados ao vivo)"
nav_order: 38
lang: "pt"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (dados ao vivo) {#raceroom-racing-experience-live-data}

Enquanto se joga RaceRoom Racing Experience, o watcher guarda os dados que o próprio jogo envia para fora, para se poderem ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `raceroom`, tipo [`telemetry`](sources-and-rules.md); ele corre enquanto `RRRE64.exe` ou `RRRE.exe` está em execução e procura novos dados a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- a posição (XYZ no mundo, m) de cada carro a 10 Hz, por nome do piloto, com o próprio carro marcado, com velocidade e posição na corrida; marcha, acelerador e freio do próprio carro
- início da sessão com a pista que o jogo informa; voltas por carro com o tempo da volta; chegadas; as próprias paradas nos boxes
- teleportes (de volta aos boxes, um reinício): `teleport` onde o carro estava, `spawn` onde ele está agora
- as próprias voltas, melhor volta, posição na corrida, distância, velocidade máxima
- toda a página de memória partilhada do jogo em `heat.raw.parquet`, cada vez que muda
- os próprios pontos de incidente

## De onde vêm os dados {#where-it-comes-from}

memória partilhada $R3E (r3e.h versão 3 da Sector3)

## Como ativar {#how-to-switch-it-on}

Nada precisa ser ligado: o watcher lê a fonte da forma que o jogo ou a plataforma a disponibiliza.

## Como funciona {#how-it-works}

Memória partilhada que os jogos de corrida publicam para painéis, aberta só para leitura, e nunca criada.

Vários simuladores entregam a sua telemetria como um mapeamento de ficheiro nomeado do Windows, que o jogo cria e que qualquer um pode ler: as páginas `Local\acpmf_*` da Kunos (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` do AC EVO), `Local\IRSDKMemMapFileName` do iRacing, `$R3E` do RaceRoom, `$pcars2$` do Automobilista 2 / Project CARS 2.

Porque não `mmap.mmap(-1, size, tagname=...)`, que é a forma comum em Python: quando o mapeamento ainda não existe, ele o *cria*, e aqui isso seria só leitura. Um jogo iniciado depois abre o mapeamento do watcher em vez de criar o seu, e aí não consegue escrever nele, então a telemetria dele fica morta até o watcher soltar. O watcher inicia um adaptador assim que o processo do jogo aparece, exatamente no momento em que o jogo ainda não criou o seu mapeamento. Por isso isto abre com `OpenFileMappingW`, que só encontra um mapeamento existente, mapeia com `FILE_MAP_READ` e informa "ainda não existe" no caso contrário; os adaptadores tentam de novo logo depois.

Nada aqui consegue escrever: a visão é mapeada só para leitura e só é copiada com `ctypes.string_at`.

Dois jogos são lidos aqui também; cada carro na pista está nas páginas próprias.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

`r3e.h` da Sector3 (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, versão 3.6), `#pragma pack(1)`. O cabeçalho diz onde começam os pilotos e qual é o tamanho de cada um (`all_drivers_offset`, `driver_data_size`), então a parte de cada piloto — nome, slot, posição, posição no mundo (float x y z, m), voltas completadas, tempo da volta atual, estado de chegada, faixa dos boxes, velocidade — é lida por esses valores. Os campos do próprio jogador (melhor e volta anterior, posição na corrida, pontos de incidente, marcha, pedais, nomes da pista e do traçado) são lidos nos deslocamentos da versão 3.6 só quando `all_drivers_offset` é o 2008 que esse layout lhe dá. O Y é tomado como para cima; o cabeçalho não diz.

O mesmo módulo também serve: [Automobilista 2 (dados ao vivo)](game-automobilista-2.md), [Project CARS 2 (dados ao vivo)](game-project-cars-2.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros; Y para cima presumido (o r3e.h não diz) |
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

- por slot de piloto (pelo deslocamento e tamanho do próprio cabeçalho): nome, slot, estado de chegada, posição, posição no mundo, voltas completadas, tempo da volta atual, faixa dos boxes, velocidade
- os campos do próprio jogador, só quando a página é do layout r3e.h 3.6: nomes da pista e do traçado, tipo de sessão, posição na corrida, melhor e volta anterior, pontos de incidente, marcha, acelerador, freio, o slot do jogador
- deslocamentos obtidos do r3e.h 3.6 da Sector3 e verificados numa página montada a partir dele nos testes; ainda não verificados contra o jogo

**Mantido bruto**

- `r3e`: o mapeamento $R3E inteiro, cada leitura cujos bytes diferem da cópia guardada por último — cada campo do r3e.h: a física do jogador (orientação, velocidades, acelerações, forças g), motor, combustível, pneus, freios, danos, flags, menu de boxes, tempos de setor, e os dados inteiros de cada slot de piloto (classe, modelo, equipa, tempos de setor, diferenças, penalidades, pneus)
- `used` fica verdadeiro para uma página lida em linhas; falso para uma página nos menus, pausada, em replay, de outro layout, ou apanhada a meio de uma escrita (`torn` 1); `unchanged_reads` no meta.json conta as leituras byte a byte iguais à cópia guardada antes

**Não disponível**

- entradas e física dos outros pilotos: a página dá só a do próprio jogador
- tempos de volta exatos dos outros carros: um slot tem só o tempo da volta em andamento, então uma volta é o último tempo em andamento visto (a cerca de 0,1 s)
- os campos do próprio jogador num layout diferente do 3.6: guardados brutos, não lidos, até serem verificados

**Tamanho**: a página tem 44 KB (r3e.h 3.6; o mapeamento é arredondado para páginas inteiras de 4 KB), até 10 vezes por segundo enquanto se dirige: cerca de 1,6 GB por hora antes da compressão; slots de piloto vazios e campos que não mudam se comprimem muito bem com o zstd (ainda não medido numa sessão real)

## Verificado {#verified}

testado com uma página montada no teste a partir do r3e.h 3.6 (deslocamentos obtidos do cabeçalho oficial); não testado contra o jogo; os tempos de volta dos outros carros são o último tempo de volta em andamento visto (a cerca de 0,1 s)

## Fonte {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
