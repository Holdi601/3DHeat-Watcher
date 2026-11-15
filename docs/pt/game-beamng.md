---
title: "BeamNG.drive (dados ao vivo)"
nav_order: 7
lang: "pt"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (dados ao vivo) {#beamngdrive-live-data}

Enquanto se joga BeamNG.drive, o watcher guarda os dados que o próprio jogo envia para fora, para se poderem ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `beamng`, tipo [`telemetry`](sources-and-rules.md); ele corre enquanto `BeamNG.drive.x64.exe` ou `BeamNG.drive.exe` está em execução e procura novos dados a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- posição do próprio carro (no mundo, m, girada para Y para cima) a 10 Hz, com velocidade, marcha, acelerador e freio
- início da direção, reinícios (respawn), voltas além do ponto onde a direção começou
- voltas, melhor volta, distância, velocidade máxima

## De onde vêm os dados {#where-it-comes-from}

UDP 127.0.0.1:4460, do mod de protocolo heat3d (mods/beamng/heat3d deste repositório)

## Como ativar {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` instala o mod; depois, em Options > Other > Protocols > "others"

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz o motivo; [Instalação e execução](installing-and-running.md) cobre as causas mais comuns.

`python -m heat3d_watch setup beamng` lista os ficheiros que ele mudaria; `python -m heat3d_watch setup beamng --apply` os altera e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `beamng: changed: ...` para cada mudança, ou `beamng: nothing to change` quando já está ativo.

## Como funciona {#how-it-works}

Telemetria própria dos jogos de corrida: Forza, os jogos Assetto Corsa, os jogos de rali e o BeamNG, gravados como trajetos, voltas e etapas.

Todo o jogo aqui publica a sua telemetria de propósito, para painéis e equipamentos de movimento; nada é injetado e nada que o jogo não entrega é lido. A decodificação não é escrita duas vezes: são os gravadores de voltas do gamecapture, em `heat3d_capture/telemetry` do 3DHeat GameCapture, copiados para `heat3d_watch/decoders` (testados lá com pacotes montados a partir dos layouts publicados). Este módulo transforma os quadros deles nas linhas do watcher: a posição do carro algumas vezes por segundo, com velocidade, marcha e pedais; um evento por volta ou etapa; e os números que o piloto guarda: voltas, melhor volta, distância e velocidade máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP "Data Out", ativado nas configurações de HUD e Gameplay do jogo, para 127.0.0.1 porta 5300, formato Dash. Um pacote por tick da simulação; o deslocamento do bloco do painel é encontrado a partir dos pacotes (`forza.detect_layout`). Metros no mundo, Y para cima; o mundo é canhoto e é desenhado como foi enviado, como faz o gravador de voltas (documentação "Data Out" do Forza Motorsport e do Forza Horizon).
O jogo envia para uma única porta, e o FH Companion e outras aplicações Data Out escutam na mesma. Dois programas não podem partilhá-la: no Windows, o socket ligado a 127.0.0.1 recebe os pacotes e o ligado a todos os endereços na mesma porta não recebe nenhum, seja qual for o que chegou primeiro. Por isso o watcher espera um pouco depois que o jogo inicia antes de apanhar a porta, nunca a tira de uma aplicação que já a usa, e a solta assim que outra aplicação começa a escutar nela. Enquanto tem a porta, reencaminha todo pacote sem alterações para 127.0.0.1:5301: defina a caixa de porta do FH Companion (o separador de telemetria) como 5301 e os dois gravam.

#### BeamNG.drive {#beamngdrive}

O mod de protocolo `heat3d` que o gamecapture distribui (UDP 4460, Options > Other > Protocols > "others"); o mundo Z para cima do BeamNG é girado para Y para cima, como faz o `beamng.py`.

#### Tudo guardado {#everything-kept}

As linhas são poucas por segundo; os jogos enviam muito mais. Todo pacote UDP que chega (nos menus, entre voltas, os que nenhum decodificador lê) é guardado inteiro no `heat.raw.parquet` da sessão, sob o formato dele (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), e cada página de memória partilhada (o mapeamento inteiro, não só os bytes decodificados) é guardada cada vez que muda, sob o nome do mapeamento dele (`acpmf_physics`, ...). `used` marca o que também passou a linhas; `selfCheck.completeness` no `meta.json` conta cada tipo (regra do conversor do 3DHeat).

O mesmo módulo também serve: [Assetto Corsa (dados ao vivo)](game-assetto-corsa.md), [Assetto Corsa Competizione (dados ao vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dados ao vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dados ao vivo)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (dados ao vivo)](game-dirt-rally-2.md), [EA SPORTS WRC (dados ao vivo)](game-ea-wrc.md), [Forza Horizon 4 (dados ao vivo)](game-forza-horizon-4.md), [Forza Horizon 5 (dados ao vivo)](game-forza-horizon-5.md), [Forza Horizon 6 (dados ao vivo)](game-forza-horizon-6.md), [Forza Motorsport (dados ao vivo)](game-forza-motorsport.md), [Richard Burns Rally (dados ao vivo)](game-richard-burns-rally.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros (o mundo Z para cima do BeamNG girado em torno de X, como faz o gravador de voltas) |
| Espelhado para o visualizador | nenhum |
| Escala da unidade (`scale`: o visualizador multiplica as posições por ele) | 1 |

Estes valores vão para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`. Assim o visualizador do 3DHeat gira e dimensiona as linhas sozinho: veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **não**. `games --markdown` mostra isso como "um jogador".
- Tipo `telemetry`: lê só o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), por isso grava também em jogo online, além do offline; a marcação decide apenas se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online: veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- linhas a 10 Hz: posição, velocidade, marcha, acelerador, freio, yaw, rpm, esterço; início da direção, reinícios, voltas

**Mantido bruto**

- todo pacote que chega à porta, inteiro, na taxa de 100 Hz do mod: `H3D1` (a estrutura de 160 bytes do mod: relógio, posição, velocidade, os eixos do carro, velocidade de yaw, nove entradas, velocidade da superfície de cada roda, rotação, carga e material do solo), `<n>-byte` para qualquer outro

**Não disponível**

- o que o mod não envia: o BeamNG não tem pacote de telemetria fixo, então os canais são os que o mod heat3d escolheu (outros veículos, danos e o nome do mapa não estão nele)

**Tamanho**: cerca de 80 MB por hora antes da compressão (100 pacotes por segundo de 160 bytes mais um cabeçalho de item de 70 bytes)

## Verificado {#verified}

decodificação do gravador de voltas do gamecapture (testada com pacotes montados a partir da estrutura do mod); adaptador testado com esses pacotes; o mod não foi testado dentro do jogo

## Fonte {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
