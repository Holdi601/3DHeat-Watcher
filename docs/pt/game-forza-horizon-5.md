---
title: "Forza Horizon 5 (dados ao vivo)"
nav_order: 22
lang: "pt"
source: game-forza-horizon-5.md
source_hash: "0083724478e7"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 5 (dados ao vivo) {#forza-horizon-5-live-data}

Enquanto se joga Forza Horizon 5, o watcher guarda os dados que o próprio jogo envia, para que se possam ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `forza-horizon-5`, tipo [`telemetry`](sources-and-rules.md); corre enquanto `ForzaHorizon5.exe` estiver em execução e procura dados novos a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- posição do próprio carro (XYZ no mundo, m) a 10 Hz, com velocidade, marcha, acelerador, freio e volta
- início e fim da direção (session_start/session_end), voltas com o tempo de volta do jogo
- início e chegada da corrida, com a posição na corrida
- teleportes (retorno, viagem rápida): `teleport` onde o carro estava, `spawn` onde ele está agora
- voltas, melhor volta, distância, velocidade máxima, corridas

## De onde vem {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada pacote reencaminhado sem alteração para 127.0.0.1:5301

## Como ligar {#how-to-switch-it-on}

No jogo: Configurações > HUD e jogabilidade > Data Out ativado, IP 127.0.0.1, porta 5300 (Motorsport: formato Dash). FH Companion ou outra aplicação Data Out: ponha a porta dele em 5301 - o watcher reencaminha cada pacote; enquanto outra aplicação escuta na 5300, o watcher deixa a porta para ele e não grava nada

## Como funciona {#how-it-works}

Telemetria própria dos jogos de corrida: Forza, os jogos Assetto Corsa, os jogos de rali e o BeamNG, gravados como trajetos, voltas e etapas.

Todo o jogo aqui publica a telemetria dele de propósito, para painéis e plataformas de movimento; nada é injetado e nada que o jogo não entrega é lido. A decodificação não é escrita duas vezes: são os gravadores de voltas do gamecapture, em `heat3d_capture/telemetry` do 3DHeat GameCapture, copiados para `heat3d_watch/decoders` (testados lá com pacotes montados a partir dos layouts publicados), e este módulo transforma os quadros deles nas linhas do watcher: a posição do carro algumas vezes por segundo com a velocidade, a marcha e os pedais, um evento por volta ou etapa, e os números que o piloto guarda: voltas, melhor volta, distância, velocidade máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, ativado nas configurações de HUD e jogabilidade do jogo, para 127.0.0.1 porta 5300, formato Dash. Um pacote por tick da simulação; o deslocamento do bloco do painel é encontrado a partir dos pacotes (`forza.detect_layout`). Metros no mundo, Y para cima; o mundo é canhoto e é desenhado como enviado, como faz o gravador de voltas (documentação "Data Out" do Forza Motorsport e do Forza Horizon). O jogo envia para uma só porta, e o FH Companion e outras aplicações Data Out escutam na mesma. Dois programas não podem partilhá-la: no Windows, o socket ligado a 127.0.0.1 recebe os pacotes, e o ligado a todos os endereços na mesma porta não recebe nenhum, seja qual for o que chegou primeiro. Por isso o watcher espera um pouco depois que o jogo inicia antes de apanhar a porta, nunca a tira de uma aplicação que a está a usar, e a solta assim que outra aplicação começa a escutar ali. Enquanto está com a porta, ele reencaminha cada pacote sem alteração para 127.0.0.1:5301 - ponha a caixa de porta do FH Companion (separador de telemetria) em 5301 e os dois gravam.

#### Tudo guardado {#everything-kept}

As linhas são algumas por segundo; os jogos enviam muito mais. Cada pacote UDP que chega - nos menus, entre voltas, os que nenhum decodificador lê - é guardado inteiro no `heat.raw.parquet` da sessão, sob o formato dele (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), e cada página de memória partilhada (a região inteira do mapeamento, não só os bytes decodificados) a cada mudança, sob o nome do mapeamento (`acpmf_physics`, ...). `used` marca o que também passou a linha; o `selfCheck.completeness` do `meta.json` conta cada tipo (regra do conversor do 3DHeat).

Também servem este módulo: [Assetto Corsa (dados ao vivo)](game-assetto-corsa.md), [Assetto Corsa Competizione (dados ao vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dados ao vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dados ao vivo)](game-assetto-corsa-rally.md), [BeamNG.drive (dados ao vivo)](game-beamng.md), [DiRT Rally 2.0 (dados ao vivo)](game-dirt-rally-2.md), [EA SPORTS WRC (dados ao vivo)](game-ea-wrc.md), [Forza Horizon 4 (dados ao vivo)](game-forza-horizon-4.md), [Forza Horizon 6 (dados ao vivo)](game-forza-horizon-6.md), [Forza Motorsport (dados ao vivo)](game-forza-motorsport.md), [Richard Burns Rally (dados ao vivo)](game-richard-burns-rally.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros; o mundo do Forza é canhoto, desenhado como enviado, como faz o gravador de voltas |
| Espelhado para o visualizador | nenhum |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `telemetry`: lê só o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- linhas a 10 Hz: posição, velocidade, marcha, acelerador, freio, volta, yaw/pitch/roll (rad), rpm, esterço (-1..1); session_start com a ordem do carro, a classe, o PI e a tração; voltas com o tempo de volta do jogo; posição na corrida

**Guardado bruto**

- cada pacote que chega à porta, inteiro, na taxa do jogo (um por tick da simulação), sob o formato dele: `dash-horizon` (324 bytes, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: desgaste dos pneus e id da pista), `sled` (232, sem posição), `<n>-byte` para o resto - inclusive os pacotes de menu (isRaceOn 0), os pacotes retidos até o layout do painel ser comprovado, e os ~13 bytes do pacote do Horizon que nenhum layout publicado nomeia
- todos os canais de cada roda do bloco Sled (razão de deslizamento, ângulo de deslizamento, deslizamento combinado, suspensão, velocidade da roda, rumble, poça), acelerações, velocidade angular, potência, torque, boost, combustível, temperaturas dos pneus, embreagem, freio de mão, linha de pilotagem, diferença de freio da IA: tudo nos pacotes, decodificado a partir deles por `decoders/fulllap.decode_full`

**Não disponível**

- outros carros: o Data Out descreve só o carro do jogador
- o nome da pista ou do trajeto: o Forza Horizon nunca envia um; o Motorsport 2023 envia só um número de pista
- os pacotes enquanto outra aplicação (FH Companion) ocupa a UDP 5300: o watcher deixa a porta para ele

**Tamanho**: cerca de 85 MB por hora antes da compressão (60 pacotes por segundo de 324 bytes mais um cabeçalho de item de 70 bytes); pacotes seguidos mudam pouco, então o zstd guarda uma fração deles

## Verificado {#verified}

decodificação do gravador de voltas do gamecapture (testada com pacotes montados a partir do layout do Data Out); o adaptador testado com pacotes sintéticos e com trajetórias de volta gravadas, reproduzidas como pacotes; sem teste contra o próprio jogo

## Fonte {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
