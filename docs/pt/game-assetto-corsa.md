---
title: "Assetto Corsa (dados ao vivo)"
nav_order: 2
lang: "pt"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (dados ao vivo) {#assetto-corsa-live-data}

Enquanto se joga Assetto Corsa, o watcher guarda os dados que o próprio jogo envia, para que se possam ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `assetto-corsa`, tipo [`telemetry`](sources-and-rules.md); corre enquanto `acs.exe` ou `acs_x86.exe` estiver em execução e procura dados novos a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- posição do próprio carro (XYZ no mundo, m: média dos pontos de contacto dos pneus) a 10 Hz, com velocidade, marcha, acelerador e freio
- início e fim da sessão, com a pista e o carro que o jogo informa
- voltas pelo contador de voltas do jogo, com o tempo da volta
- teleportes (de volta aos boxes, um reinício): `teleport` onde o carro estava, `spawn` onde ele está agora
- voltas, melhor volta, distância, velocidade máxima

## De onde vem {#where-it-comes-from}

memória partilhada Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Como ligar {#how-to-switch-it-on}

Não é preciso ligar nada: o watcher lê a fonte como o jogo ou a plataforma a disponibiliza.

## Como funciona {#how-it-works}

Telemetria própria dos jogos de corrida: Forza, os jogos Assetto Corsa, os jogos de rali e o BeamNG, gravados como trajetos, voltas e etapas.

Todo o jogo aqui publica a telemetria dele de propósito, para painéis e plataformas de movimento; nada é injetado e nada que o jogo não entrega é lido. A decodificação não é escrita duas vezes: são os gravadores de voltas do gamecapture, em `heat3d_capture/telemetry` do 3DHeat GameCapture, copiados para `heat3d_watch/decoders` (testados lá com pacotes montados a partir dos layouts publicados), e este módulo transforma os quadros deles nas linhas do watcher: a posição do carro algumas vezes por segundo com a velocidade, a marcha e os pedais, um evento por volta ou etapa, e os números que o piloto guarda: voltas, melhor volta, distância, velocidade máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, ativado nas configurações de HUD e jogabilidade do jogo, para 127.0.0.1 porta 5300, formato Dash. Um pacote por tick da simulação; o deslocamento do bloco do painel é encontrado a partir dos pacotes (`forza.detect_layout`). Metros no mundo, Y para cima; o mundo é canhoto e é desenhado como enviado, como faz o gravador de voltas (documentação "Data Out" do Forza Motorsport e do Forza Horizon). O jogo envia para uma só porta, e o FH Companion e outras aplicações Data Out escutam na mesma. Dois programas não podem partilhá-la: no Windows, o socket ligado a 127.0.0.1 recebe os pacotes, e o ligado a todos os endereços na mesma porta não recebe nenhum, seja qual for o que chegou primeiro. Por isso o watcher espera um pouco depois que o jogo inicia antes de apanhar a porta, nunca a tira de uma aplicação que a está a usar, e a solta assim que outra aplicação começa a escutar ali. Enquanto está com a porta, ele reencaminha cada pacote sem alteração para 127.0.0.1:5301 - ponha a caixa de porta do FH Companion (separador de telemetria) em 5301 e os dois gravam.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Memória partilhada que o jogo escreve para as aplicações: `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`). Aberta só para leitura e somente depois que o jogo a criou (`simracing_shm`). A posição é a média dos quatro pontos de contacto dos pneus, em metros no mundo, Y para cima. As voltas vêm pelo contador do jogo (AC, ACC) ou ao passar pelo ponto de partida de novo (AC EVO, AC Rally), como faz o `kunos.py` para o gravador de voltas.

#### Tudo guardado {#everything-kept}

As linhas são algumas por segundo; os jogos enviam muito mais. Cada pacote UDP que chega - nos menus, entre voltas, os que nenhum decodificador lê - é guardado inteiro no `heat.raw.parquet` da sessão, sob o formato dele (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), e cada página de memória partilhada (a região inteira do mapeamento, não só os bytes decodificados) a cada mudança, sob o nome do mapeamento (`acpmf_physics`, ...). `used` marca o que também passou a linha; o `selfCheck.completeness` do `meta.json` conta cada tipo (regra do conversor do 3DHeat).

Também servem este módulo: [Assetto Corsa Competizione (dados ao vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dados ao vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dados ao vivo)](game-assetto-corsa-rally.md), [BeamNG.drive (dados ao vivo)](game-beamng.md), [DiRT Rally 2.0 (dados ao vivo)](game-dirt-rally-2.md), [EA SPORTS WRC (dados ao vivo)](game-ea-wrc.md), [Forza Horizon 4 (dados ao vivo)](game-forza-horizon-4.md), [Forza Horizon 5 (dados ao vivo)](game-forza-horizon-5.md), [Forza Horizon 6 (dados ao vivo)](game-forza-horizon-6.md), [Forza Motorsport (dados ao vivo)](game-forza-motorsport.md), [Richard Burns Rally (dados ao vivo)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- linhas a 10 Hz da página de física: posição (média dos pontos de contacto dos pneus), velocidade, marcha, acelerador, freio, yaw/pitch/roll (rad), rpm, esterço (como a página o traz); início da sessão com a pista e o carro da página estática; voltas, posição na corrida

**Guardado bruto**

- cada página inteira - a região completa do mapeamento, não só os bytes decodificados - a cada vez que os bytes mudam, na leitura de 10 Hz do watcher: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; uma releitura idêntica byte a byte à anterior é contada em `unchanged_reads` do meta.json, não guardada de novo
- tudo o que é decodificado só para ficheiros de volta (`decoders/kunos.py`: deslizamento, carga, pressão, temperaturas, cambagem, suspensão, pontos de contacto, temperaturas de freio, razão e ângulo de deslizamento por roda; velocidades no mundo e locais, velocidade angular, auxílios) está nessas páginas

**Não disponível**

- posições de outros carros: as páginas descrevem só o carro do jogador (a página gráfica do ACC tem ids e coordenadas de outros carros em algumas versões - guardados na página bruta, não decodificados)
- os ticks de física entre as leituras do watcher: o jogo reescreve a página na taxa da física (até 333 Hz) e o watcher lê 10 vezes por segundo

**Tamanho**: cerca de 150-300 MB por hora antes da compressão (uma região de 4 KB por página, até 10 mudanças por segundo); as páginas são em grande parte zeros, e o zstd guarda uma pequena fração

## Verificado {#verified}

decodificação do gravador de voltas do gamecapture (testada com páginas sintéticas); o adaptador testado com memória partilhada montada no teste a partir do layout documentado; sem teste contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
