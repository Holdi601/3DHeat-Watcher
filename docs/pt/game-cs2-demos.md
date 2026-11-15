---
title: "Counter-Strike 2 (replays)"
nav_order: 8
lang: "pt"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replays) {#counter-strike-2-replays}

Depois de uma partida de Counter-Strike 2, o watcher transforma o replay que o jogo guardou em ficheiros que se podem ver num mapa no visualizador do 3DHeat.

*Detalhes técnicos: adaptador `cs2-demos`, tipo [`replay`](sources-and-rules.md); ele corre o tempo todo (não espera um jogo começar) e procura dados novos a cada 5 s.*

## O que é gravado {#what-is-recorded}

- a posição, a direção do olhar, a vida e o dinheiro de cada jogador (a cada 8º tick)
- abates, mortes, dano, granadas, plantios e desarmes onde aconteceram
- rondas, placar, economia; a linha de placar do jogador conectado, como estatísticas

## De onde vem {#where-it-comes-from}

demos que o CS2 guarda: &lt;CS2>/game/csgo/replays/\*.dem (transferidas do histórico de partidas) e &lt;CS2>/game/csgo/\*.dem (gravadas)

## Como ativar {#how-to-switch-it-on}

transfira a demo de uma partida no CS2 (Watch > Your Matches), ou grave uma com o comando de console `record`

Configurações por variáveis de ambiente:

- `HEAT3D_CS2`: a pasta do 3DHeat CS2, quando ela não estiver ao lado do watcher nem instalada

## Como funciona {#how-it-works}

Replays e demos: o que um jogo guarda de uma partida, convertido quando a partida termina.

Um replay guarda tudo o que uma interface ao vivo esconde em jogos multijogador -
a posição de cada jogador, cada abate onde aconteceu - e é um ficheiro que o jogo grava
para os jogadores, então lê-lo não toca em nada do jogo. O watcher observa as pastas
em que os jogos os guardam, espera até que um ficheiro novo pare de crescer (senão o jogo
ainda estaria a escrever), e o converte numa thread de trabalho, de modo que uma conversão
longa nunca bloqueia o resto do watcher.

A primeira vez que uma pasta é vista, os replays que já estão nela são apenas registados, não
convertidos: quem tem anos de demos encontraria o watcher ocupado por um dia inteiro.
`python -m heat3d_watch replays <adapter> [folder]` converte os existentes quando se pedir.

#### Counter-Strike 2 {#counter-strike-2}

O CS2 guarda as demos que um jogador transfere do histórico de partidas (separador Watch) em
`<CS2>/game/csgo/replays/` e as que são gravadas com o comando de console `record` em
`<CS2>/game/csgo/`. Cada uma é convertida pelo conversor de CS2 deste próprio repositório
(3DHeat CS2, github.com/Holdi601/3DHeat-CS2: a posição, a direção do olhar, a vida e o
dinheiro de cada jogador a cada oitavo tick; abates, mortes, dano, granadas, plantios e
desarmes onde aconteceram; rondas, placar, economia) para a pasta da sessão, como a tabela
`<mapa>/<partida>.parquet` e o resumo `<partida>.match.json` que os separadores Mapa de calor e
Partida do visualizador leem. O placar da partida passa a ser as estatísticas da sessão: para o
jogador cuja conta Steam está conectada neste computador (do `loginusers.vdf` da Steam), sob
os nomes simples - abates, mortes, assistências, ADR, KAST, percentagem de headshots,
primeiros abates, clutches - e o placar e as rondas.

A mesma parte também serve: [Dota 2 (replays)](game-dota-replays.md), [osu! (replays)](game-osu-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `z` |
| Unidades | polegadas (unidades Source) |
| Espelhado para o visualizador | `y` |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Isso vai para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o
rodapé de `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho -
veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `replay`: ele lê apenas o que o jogo ou a plataforma entrega (replays e demos que o jogo guarda), por isso grava também em partidas online, e não só offline; a marcação só decide se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem a memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (`stats` de cada sessão em `meta.json` e a tabela `stats` de `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Uma chave entre chaves é completada na execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela dos campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O conversor que este adaptador executa segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que o replay contém é lido ou guardado, nunca descartado - lido na tabela e no documento da partida, e todo o resto guardado inteiro em ficheiros auxiliares ao lado deles, contado em `selfCheck.completeness` do documento da partida. A documentação do próprio conversor lista o que ele lê, o que guarda em bruto e o que não consegue ler.

## Verificado {#verified}

o conversor é testado em demos reais de torneios; a observação de pastas e as estatísticas por testes

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
