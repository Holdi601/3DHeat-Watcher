---
title: "osu! (replays)"
nav_order: 35
lang: "pt"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (replays) {#osu-replays}

Depois de uma partida de osu!, o watcher transforma o replay que o jogo guardou em ficheiros que se podem ver num mapa no visualizador do 3DHeat.

*Detalhes técnicos: adaptador `osu-replays`, tipo [`replay`](sources-and-rules.md); ele corre o tempo todo (não espera um jogo começar) e procura novos dados a cada 5 s.*

## O que é gravado {#what-is-recorded}

- o caminho do cursor sobre a área de jogo (x 0..512, y 0..384) e as teclas premidas, a cada quadro
- pontuação, combo, 300s/100s/50s/gekis/katus/erros, precisão, mods, combo completo
- a barra de vida ao longo da jogada, os hashes do mapa e do replay, a semente aleatória, o id da pontuação online

## De onde vêm os dados {#where-it-comes-from}

replays que o osu! (versão estável) guarda: %LOCALAPPDATA%/osu!/Data/r/\*.osr (cada jogada) e osu!/Replays/\*.osr (exportados)

## Como ativar {#how-to-switch-it-on}

Nada precisa ser ligado: o watcher lê a fonte da forma que o jogo ou a plataforma a disponibiliza.

## Como funciona {#how-it-works}

Replays e demos: o que um jogo guarda de uma partida, convertido quando a partida termina.

Um replay guarda tudo o que uma interface ao vivo esconde em jogos multijogador — a posição de cada jogador, cada abate onde aconteceu — e é um ficheiro que o jogo escreve para os jogadores, então lê-lo não toca em nada do jogo. O watcher observa as pastas em que os jogos os guardam, espera até que um ficheiro novo pare de crescer (senão o jogo ainda o está a escrever), e o converte numa thread de trabalho, para que uma conversão longa nunca bloqueie o resto do watcher.

Na primeira vez que uma pasta é vista, os replays que já estão nela são apenas registados, não convertidos: um jogador com anos de demos veria o watcher ocupado por um dia inteiro. `python -m heat3d_watch replays <adaptador> [pasta]` converte os existentes sob pedido.

#### osu! {#osu}

O osu! (versão estável) guarda cada jogada em `osu!/Data/r/*.osr` e os exportados em `osu!/Replays/`. O watcher os lê por conta própria, no formato que a wiki do osu! publica: o caminho do cursor e as teclas a cada quadro, a linha de pontuação, a barra de vida, a semente e o id da pontuação; o ficheiro é guardado inteiro ao lado, em partes, no `heat.raw.parquet` da sessão.

O mesmo módulo também serve: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | pixels do osu! (área de jogo 512 x 384) |
| Espelhado para o visualizador | `z` |
| Escala da unidade (`scale`: o visualizador multiplica as posições por ele) | 1 |

Estes valores vão para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`. Assim o visualizador do 3DHeat gira e dimensiona as linhas sozinho: veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `replay`: lê só o que o jogo ou a plataforma entrega (replays e demos que o jogo guarda), por isso grava também em jogo online, além do offline; a marcação decide apenas se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online: veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`accuracy`, `full_combo`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- cada quadro: uma linha no seu tempo (milissegundos somados), x e y na área de jogo, `keys` os bits das teclas (rato 1 e 2, teclas 1 e 2, fumaça); no mania, x guarda as teclas premidas em vez de um lugar
- o cabeçalho, cada campo: modo, versão, o MD5 do mapa (o ficheiro nomeia o mapa só por ele), o jogador, o MD5 do replay, 300s, 100s, 50s, gekis, katus, erros, pontuação, combo máximo, combo completo, mods (pelo nome em `osu.modNames` do meta.json), a hora da jogada — como estatísticas e em `osu` no meta.json
- o gráfico da barra de vida: uma linha `life` por ponto (tempo, vida 0..1)
- o quadro `-12345`: a semente aleatória (`osu.seed`); o id da pontuação online (`osu.scoreId`); com o Target Practice, a precisão (`osu.targetPracticeAccuracy`)

**Mantido bruto**

- o ficheiro inteiro, em partes, no heat.raw.parquet (`offset` onde cada uma começa, então as partes formam o ficheiro): `header`, `replay_data` (os quadros comprimidos com LZMA como estão guardados), `score_id`, `mod_info`, e `trailing` para o que vem depois das partes que o formato descreve (as exportações do osu!lazer acrescentam dados ali) — guardado, não lido

**Não disponível**

- o mapa em si (objetos de acerto, cronometragem): não está no replay; ele é nomeado só pelo seu MD5
- os replays do próprio osu!lazer: ficam no banco de dados dele, não como ficheiros

**Tamanho**: o ficheiro bruto anexo tem aproximadamente o tamanho do replay (dezenas a centenas de quilobytes)

## Verificado {#verified}

testado com replays montados no formato .osr publicado; o osu!lazer guarda os replays no próprio armazenamento e não é lido

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
