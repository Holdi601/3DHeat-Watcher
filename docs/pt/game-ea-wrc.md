---
title: "EA SPORTS WRC (dados ao vivo)"
nav_order: 17
lang: "pt"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (dados ao vivo) {#ea-sports-wrc-live-data}

Enquanto se joga EA SPORTS WRC, o watcher guarda os dados que o próprio jogo envia, para que se possam ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `ea-wrc`, tipo [`telemetry`](sources-and-rules.md); corre enquanto `WRC.exe` estiver em execução e procura dados novos a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- posição do próprio carro (XYZ no mundo, m) a 10 Hz, com velocidade, marcha, acelerador, freio e distância na etapa
- início da etapa (o cronómetro da etapa a começar), chegada com o tempo da etapa, reinícios
- teleportes (um reset para a estrada): `teleport` onde o carro estava, `spawn` onde ele está agora
- etapas, melhor tempo de etapa, distância, velocidade máxima

## De onde vem {#where-it-comes-from}

UDP 127.0.0.1:20777, o pacote `session_update` da estrutura `wrc` padrão (Documents\My Games\WRC\telemetry\config.json); enquanto outra aplicação ocupa a 20777, o watcher deixa a porta para ele

## Como ligar {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` liga o pacote `session_update` no config.json (com uma cópia de segurança antes)

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz porquê; [Instalar e executar](installing-and-running.md) cobre as causas mais comuns.

`python -m heat3d_watch setup ea-wrc` lista os ficheiros que ele mudaria; `python -m heat3d_watch setup ea-wrc --apply` os altera e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `ea-wrc: changed: ...` para cada mudança, ou `ea-wrc: nothing to change` quando já está ligado.

## Como funciona {#how-it-works}

Telemetria própria dos jogos de corrida: Forza, os jogos Assetto Corsa, os jogos de rali e o BeamNG, gravados como trajetos, voltas e etapas.

Todo o jogo aqui publica a telemetria dele de propósito, para painéis e plataformas de movimento; nada é injetado e nada que o jogo não entrega é lido. A decodificação não é escrita duas vezes: são os gravadores de voltas do gamecapture, em `heat3d_capture/telemetry` do 3DHeat GameCapture, copiados para `heat3d_watch/decoders` (testados lá com pacotes montados a partir dos layouts publicados), e este módulo transforma os quadros deles nas linhas do watcher: a posição do carro algumas vezes por segundo com a velocidade, a marcha e os pedais, um evento por volta ou etapa, e os números que o piloto guarda: voltas, melhor volta, distância, velocidade máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, ativado nas configurações de HUD e jogabilidade do jogo, para 127.0.0.1 porta 5300, formato Dash. Um pacote por tick da simulação; o deslocamento do bloco do painel é encontrado a partir dos pacotes (`forza.detect_layout`). Metros no mundo, Y para cima; o mundo é canhoto e é desenhado como enviado, como faz o gravador de voltas (documentação "Data Out" do Forza Motorsport e do Forza Horizon). O jogo envia para uma só porta, e o FH Companion e outras aplicações Data Out escutam na mesma. Dois programas não podem partilhá-la: no Windows, o socket ligado a 127.0.0.1 recebe os pacotes, e o ligado a todos os endereços na mesma porta não recebe nenhum, seja qual for o que chegou primeiro. Por isso o watcher espera um pouco depois que o jogo inicia antes de apanhar a porta, nunca a tira de uma aplicação que a está a usar, e a solta assim que outra aplicação começa a escutar ali. Enquanto está com a porta, ele reencaminha cada pacote sem alteração para 127.0.0.1:5301 - ponha a caixa de porta do FH Companion (separador de telemetria) em 5301 e os dois gravam.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: o `Documents/My Games/WRC/telemetry/config.json` do WRC (o pacote `session_update` da estrutura `wrc`), o `hardware_settings_config.xml` do DiRT (`<udp enabled="true" extradata="3" port="20777">`), o plugin NGP do RBR (`udpTelemetry=1`, porta 6776). Etapas pelo cronómetro de etapa do jogo (`rally.StageSplitter`). O RBR não documenta os eixos dele: o eixo para cima é aquele em que a etapa varia menos, decidido quando a sessão fecha.

#### Tudo guardado {#everything-kept}

As linhas são algumas por segundo; os jogos enviam muito mais. Cada pacote UDP que chega - nos menus, entre voltas, os que nenhum decodificador lê - é guardado inteiro no `heat.raw.parquet` da sessão, sob o formato dele (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), e cada página de memória partilhada (a região inteira do mapeamento, não só os bytes decodificados) a cada mudança, sob o nome do mapeamento (`acpmf_physics`, ...). `used` marca o que também passou a linha; o `selfCheck.completeness` do `meta.json` conta cada tipo (regra do conversor do 3DHeat).

Também servem este módulo: [Assetto Corsa (dados ao vivo)](game-assetto-corsa.md), [Assetto Corsa Competizione (dados ao vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dados ao vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dados ao vivo)](game-assetto-corsa-rally.md), [BeamNG.drive (dados ao vivo)](game-beamng.md), [DiRT Rally 2.0 (dados ao vivo)](game-dirt-rally-2.md), [Forza Horizon 4 (dados ao vivo)](game-forza-horizon-4.md), [Forza Horizon 5 (dados ao vivo)](game-forza-horizon-5.md), [Forza Horizon 6 (dados ao vivo)](game-forza-horizon-6.md), [Forza Motorsport (dados ao vivo)](game-forza-motorsport.md), [Richard Burns Rally (dados ao vivo)](game-richard-burns-rally.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros |
| Espelhado para o visualizador | nenhum |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `telemetry`: lê só o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- linhas a 10 Hz: posição, velocidade, marcha, acelerador, freio, distância na etapa, yaw, rpm, esterço; início da etapa, chegada com o tempo da etapa, reinícios

**Guardado bruto**

- cada pacote que chega à porta, inteiro, na taxa do jogo, sob o formato dele: `session_update` (a estrutura `wrc` padrão, 237 bytes), `wrc <n>-byte` para qualquer outro pacote que a configuração envie
- no pacote, além das linhas: velocidade e aceleração no mundo, os eixos do carro, posição e velocidade do cubo de cada roda, velocidade do ponto de contacto, temperatura do freio, embreagem, freio de mão, o relógio do jogo; 22 bytes (deslocamentos 16-36 e 40) que nenhuma lista de canais publicada nomeia

**Não disponível**

- outros carros: os jogos enviam só o carro do jogador
- as outras estruturas e pacotes que a configuração de telemetria pode definir (session_start, session_end, pause): só o `session_update` é ligado pelo `setup`; qualquer outro pacote enviado à porta é guardado

**Tamanho**: cerca de 65 MB por hora a 60 pacotes por segundo (237 bytes mais um cabeçalho de item de 70 bytes; a taxa -1 da configuração envia um por quadro, então mais com uma taxa de quadros maior); o zstd guarda uma fração

## Verificado {#verified}

decodificação do gravador de voltas do gamecapture (testada com pacotes montados a partir dos layouts documentados); o adaptador testado com pacotes montados no teste e enviados por UDP; sem teste contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
