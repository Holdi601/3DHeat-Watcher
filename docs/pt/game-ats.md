---
title: "American Truck Simulator (dados ao vivo)"
nav_order: 1
lang: "pt"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (dados ao vivo) {#american-truck-simulator-live-data}

Enquanto se joga American Truck Simulator, o watcher guarda os dados que o próprio jogo envia para fora, para se poderem ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `ats`, tipo [`telemetry`](sources-and-rules.md); ele corre enquanto `amtrucks.exe` está em execução e procura novos dados a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- a posição mundial do caminhão (x leste, y para cima, z sul, m) a 10 Hz enquanto ele se move, e a cada 5 s enquanto está parado; rumo, velocidade, odômetro
- fretes iniciados (carga, de onde, para onde), entregues (receita, XP, km), cancelados; multas, pedágios, balsas, trens, reabastecimentos
- balsas, trens e gravações de jogo carregadas cortam a rota (teleport, spawn)
- distância, velocidade máxima, entregas, receita, XP, multas
- toda a memória partilhada do plugin em `heat.raw.parquet`, cada vez que muda

## De onde vêm os dados {#where-it-comes-from}

memória partilhada Local\SCSTelemetry, escrita pelo plugin scs-sdk-plugin da RenCloud (revisão 12) em &lt;jogo>\bin\win_x64\plugins

## Como ativar {#how-to-switch-it-on}

instale o scs-telemetry.dll (revisão 12) de github.com/RenCloud/scs-sdk-plugin em &lt;jogo>\bin\win_x64\plugins; o jogo pede, uma vez a cada arranque, permissão para o SDK

## Como funciona {#how-it-works}

Euro Truck Simulator 2 e American Truck Simulator: o SDK de telemetria da SCS, pelo plugin da RenCloud.

A SCS publica um SDK de telemetria (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) para plugins que o jogador põe em `<jogo>\bin\win_x64\plugins\`. O próprio jogo não publica nada; o plugin muito usado de <https://github.com/RenCloud/scs-sdk-plugin> (MIT) copia os canais do SDK para a memória partilhada `Local\SCSTelemetry` (32 KiB), no layout descrito em `scs-telemetry/inc/scs-telemetry-common.hpp`. Este código lê a revisão 12 desse layout (PLUGIN_REVID 12) e nada além dela: o plugin escreve a revisão dele no deslocamento 40, e qualquer outra revisão fica sem leitura, em vez de ser lida errado. Deslocamentos usados (zonas como o cabeçalho as marca; alinhamento natural):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

A posição mundial do caminhão é o quadro mundial da SCS: x leste, y para cima, z sul, em metros (dextrógiro, y para cima; o visualizador a desenha como vem). Balsas, trens e carregar uma gravação de jogo movem o caminhão sem dirigir: a rota é cortada ali.

O mapeamento inteiro (os 32 KiB do plugin: todas as zonas acima e as que não são lidas, como a configuração do caminhão, rodas, desgaste, os demais canais do caminhão e o que a revisão organiza depois do byte 4400, os reboques) é guardado no ficheiro bruto anexo da sessão cada vez que muda, com `type` `SCSTelemetry` e a `revision` ao lado. Uma página de outra revisão também é guardada inteira, em vez de lida errado.

O mesmo módulo também serve: [Euro Truck Simulator 2 (dados ao vivo)](game-ets2.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros (mundo da SCS: x leste, y para cima, z sul) |
| Espelhado para o visualizador | nenhum |
| Escala da unidade (`scale`: o visualizador multiplica as posições por ele) | 1 |

Estes valores vão para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`. Assim o visualizador do 3DHeat gira e dimensiona as linhas sozinho: veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `telemetry`: lê só o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), por isso grava também em jogo online, além do offline; a marcação decide apenas se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online: veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- estado de SDK e de pausa, revisão do plugin, jogo e versão, tempo no jogo, posição mundial e rumo do caminhão, velocidade, odômetro, marca e nome do caminhão, carga, cidade e empresa de origem e de destino, receita do frete, XP e distância, penalidade de cancelamento, multas e o motivo delas, pedágios, balsas, trens, as marcações de evento especiais (linhas, eventos e estatísticas)
- agora também nas linhas de posição: `pitch` e `roll` (graus, a partir das voltas do SDK), `gear` e `rpm`
- deslocamentos verificados com uma transcrição campo a campo do cabeçalho da revisão 12 do plugin, cujos inícios de zona são verificados nos testes; ainda não verificados contra o jogo

**Mantido bruto**

- `SCSTelemetry`: os 32 KiB inteiros do mapeamento do plugin, cada leitura cujos bytes diferem da cópia guardada por último (`unchanged_reads` no meta.json conta as outras), com a `revision` ao lado: cada zona (configuração do caminhão e do reboque, os canais do caminhão: pedais, direção, combustível, AdBlue, pressões, temperaturas, desgaste, luzes, rodas), vetores de posição e aceleração, textos de frete e de jogo, e tudo o que a revisão organiza depois do byte 4400 (os reboques); `used` fica verdadeiro enquanto o SDK está ativo e a revisão é 12
- uma página de outra revisão do plugin é guardada inteira, com `used` falso, em vez de ser lida errado

**Não disponível**

- tudo o que o plugin não copia do SDK, e tudo enquanto o plugin não está instalado: o jogo não publica telemetria própria
- caminhões de outros jogadores no TruckersMP ou em comboios: o SDK dá só o caminhão do próprio jogador

**Tamanho**: 32 KiB até 10 vezes por segundo enquanto se dirige (cada leitura difere nesse caso): cerca de 1,2 GB por hora antes da compressão, uma cópia só enquanto pausado; a maior parte da página são zeros e configurações que não mudam, então o zstd a reduz muitas vezes (ainda não medido numa sessão real)

## Verificado {#verified}

testado com memória partilhada montada a partir do layout do cabeçalho da revisão 12 do plugin; não testado contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
