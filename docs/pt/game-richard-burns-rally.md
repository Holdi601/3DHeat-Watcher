---
title: "Richard Burns Rally (dados ao vivo)"
nav_order: 39
lang: "pt"
source: game-richard-burns-rally.md
source_hash: "1b9866f5a1f6"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (dados ao vivo) {#richard-burns-rally-live-data}

Enquanto se joga Richard Burns Rally, o watcher guarda os dados que o próprio jogo envia para fora, para se poderem ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `richard-burns-rally`, tipo [`telemetry`](sources-and-rules.md); ele corre enquanto `RichardBurnsRally_SSE.exe` ou `RichardBurnsRally.exe` está em execução e procura novos dados a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- posição do próprio carro (XYZ no mundo, m) a 10 Hz, com velocidade, marcha, acelerador, freio e distância na etapa
- início da etapa (quando o cronómetro da etapa começa), chegada com o tempo da etapa, reinícios
- teleportes (um retorno à estrada): `teleport` onde o carro estava, `spawn` onde ele está agora
- etapas, melhor tempo de etapa, distância, velocidade máxima

## De onde vêm os dados {#where-it-comes-from}

Telemetria UDP do plugin NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Como ativar {#how-to-switch-it-on}

RSF/NGP: no RichardBurnsRally.ini, na seção [NGP], defina udpTelemetry=1 e o endereço como 127.0.0.1:6776

## Como funciona {#how-it-works}

Telemetria própria dos jogos de corrida: Forza, os jogos Assetto Corsa, os jogos de rali e o BeamNG, gravados como trajetos, voltas e etapas.

Todo o jogo aqui publica a sua telemetria de propósito, para painéis e equipamentos de movimento; nada é injetado e nada que o jogo não entrega é lido. A decodificação não é escrita duas vezes: são os gravadores de voltas do gamecapture, em `heat3d_capture/telemetry` do 3DHeat GameCapture, copiados para `heat3d_watch/decoders` (testados lá com pacotes montados a partir dos layouts publicados). Este módulo transforma os quadros deles nas linhas do watcher: a posição do carro algumas vezes por segundo, com velocidade, marcha e pedais; um evento por volta ou etapa; e os números que o piloto guarda: voltas, melhor volta, distância e velocidade máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP "Data Out", ativado nas configurações de HUD e Gameplay do jogo, para 127.0.0.1 porta 5300, formato Dash. Um pacote por tick da simulação; o deslocamento do bloco do painel é encontrado a partir dos pacotes (`forza.detect_layout`). Metros no mundo, Y para cima; o mundo é canhoto e é desenhado como foi enviado, como faz o gravador de voltas (documentação "Data Out" do Forza Motorsport e do Forza Horizon).
O jogo envia para uma única porta, e o FH Companion e outras aplicações Data Out escutam na mesma. Dois programas não podem partilhá-la: no Windows, o socket ligado a 127.0.0.1 recebe os pacotes e o ligado a todos os endereços na mesma porta não recebe nenhum, seja qual for o que chegou primeiro. Por isso o watcher espera um pouco depois que o jogo inicia antes de apanhar a porta, nunca a tira de uma aplicação que já a usa, e a solta assim que outra aplicação começa a escutar nela. Enquanto tem a porta, reencaminha todo pacote sem alterações para 127.0.0.1:5301: defina a caixa de porta do FH Companion (o separador de telemetria) como 5301 e os dois gravam.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: o `Documents/My Games/WRC/telemetry/config.json` do WRC (o pacote `session_update` da estrutura `wrc`), o `hardware_settings_config.xml` do DiRT (`<udp enabled="true" extradata="3" port="20777">`), o plugin NGP do RBR (`udpTelemetry=1`, porta 6776). Etapas pelo cronómetro de etapa do jogo (`rally.StageSplitter`). O RBR não documenta os seus eixos: o eixo para cima é aquele ao longo do qual a etapa varia menos, decidido quando a sessão fecha.

#### Tudo guardado {#everything-kept}

As linhas são poucas por segundo; os jogos enviam muito mais. Todo pacote UDP que chega (nos menus, entre voltas, os que nenhum decodificador lê) é guardado inteiro no `heat.raw.parquet` da sessão, sob o formato dele (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), e cada página de memória partilhada (o mapeamento inteiro, não só os bytes decodificados) é guardada cada vez que muda, sob o nome do mapeamento dele (`acpmf_physics`, ...). `used` marca o que também passou a linhas; `selfCheck.completeness` no `meta.json` conta cada tipo (regra do conversor do 3DHeat).

O mesmo módulo também serve: [Assetto Corsa (dados ao vivo)](game-assetto-corsa.md), [Assetto Corsa Competizione (dados ao vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dados ao vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dados ao vivo)](game-assetto-corsa-rally.md), [BeamNG.drive (dados ao vivo)](game-beamng.md), [DiRT Rally 2.0 (dados ao vivo)](game-dirt-rally-2.md), [EA SPORTS WRC (dados ao vivo)](game-ea-wrc.md), [Forza Horizon 4 (dados ao vivo)](game-forza-horizon-4.md), [Forza Horizon 5 (dados ao vivo)](game-forza-horizon-5.md), [Forza Horizon 6 (dados ao vivo)](game-forza-horizon-6.md), [Forza Motorsport (dados ao vivo)](game-forza-motorsport.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros; eixo para cima decidido pela condução (o RBR não documenta os seus eixos) |
| Espelhado para o visualizador | nenhum |
| Escala da unidade (`scale`: o visualizador multiplica as posições por ele) | 1 |

Estes valores vão para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`. Assim o visualizador do 3DHeat gira e dimensiona as linhas sozinho: veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **não**. `games --markdown` mostra isso como "um jogador".
- Tipo `telemetry`: lê só o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), por isso grava também em jogo online, além do offline; a marcação decide apenas se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online: veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- linhas a 10 Hz: posição, velocidade, marcha, acelerador, freio, distância na etapa, yaw, rpm, esterço; início da etapa, chegada com o tempo da etapa, reinícios

**Mantido bruto**

- todo pacote que chega à porta, inteiro, na taxa do jogo, sob o formato dele: `telemetry` (a TelemetryData de 664 bytes do NGP), `rbr <n>-byte` para os demais
- além das linhas: a atitude, as velocidades e acelerações do próprio carro, a deflexão e a força da mola de cada roda, o progresso da etapa e a distância até o fim; o resto dos 664 bytes (blocos de motor, pneus e freios por roda) ainda não é decodificado em lugar nenhum

**Não disponível**

- outros carros: os jogos enviam só o carro do jogador
- a unidade de velocidade e os eixos: não documentados — a velocidade é tirada das posições, e o eixo para cima, da condução

**Tamanho**: cerca de 160 MB por hora a 60 pacotes por segundo (664 bytes mais um cabeçalho de item de 70 bytes); o zstd guarda uma fração

## Verificado {#verified}

decodificação do gravador de voltas do gamecapture (testada com pacotes montados a partir dos layouts documentados); o adaptador testado com pacotes montados no teste, enviados por UDP; não testado contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
