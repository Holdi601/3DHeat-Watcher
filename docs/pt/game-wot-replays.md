---
title: "World of Tanks (replays)"
nav_order: 48
lang: "pt"
source: game-wot-replays.md
source_hash: "4cff18c29936"
nav_exclude: true
search_exclude: true
---
# World of Tanks (replays) {#world-of-tanks-replays}

Depois de uma partida de World of Tanks, o watcher transforma o replay que o jogo guardou em ficheiros que se podem ver num mapa no visualizador do 3DHeat.

*Detalhes técnicos: adaptador `wot-replays`, tipo [`replay`](sources-and-rules.md); ele corre o tempo todo (não espera um jogo começar) e procura dados novos a cada 5 s.*

## O que é gravado {#what-is-recorded}

- a posição e o rumo de cada veículo cerca de 10 vezes por segundo, enquanto o cliente que gravou o conhecia: a própria equipa o tempo todo, um inimigo enquanto estiver avistado
- jogador, equipa e veículo (nação:tanque) de cada um; mortes onde a vítima caiu e abates onde o assassino estava, com cerca de um segundo de precisão, a partir dos resultados
- o mapa; abates, dano, sobrevivência e o resultado do jogador que gravou, como estatísticas

## De onde vem {#where-it-comes-from}

replays que o World of Tanks guarda: &lt;World of Tanks>/replays/\*.wotreplay (com a gravação de batalhas ligada), convertidos pelo conversor externo `heat3d-wot-replay` (exporters/ext/wot-replay)

## Como ativar {#how-to-switch-it-on}

ligue a gravação de batalhas nas configurações do World of Tanks (Geral > Gravar batalhas) e instale o conversor: pip install -e &lt;3DHeat>/exporters/ext/wot-replay

Configurações por variáveis de ambiente:

- `HEAT3D_WOT_REPLAY`: a pasta do conversor (um clone ou um pacote extraído), quando ele não estiver instalado nem ao lado do watcher

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

#### World of Tanks e World of Warships {#world-of-tanks-and-world-of-warships}

Os dois guardam um replay de cada batalha em `<jogo>/replays/` quando a gravação está ligada
(`*.wotreplay`, `*.wowsreplay`); as instalações são encontradas pela lista do Wargaming Game
Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, e pelo Steam. Como no War Thunder, o
watcher não lê os ficheiros sozinho: um conversor externo de cada um lê (`exporters/ext/wot-replay`,
comando `heat3d-wot-replay`; `exporters/ext/wows-replay`, comando `heat3d-wows-replay`), separados
para que um problema com os termos de uso da Wargaming afete só aquele conversor. Encontrado no
PATH, instalado ou ao lado do watcher, ele transforma cada replay novo em `<mapa>/<partida>.parquet`
e `<partida>.match.json` na pasta da sessão; quando falta, o watcher avisa uma vez como instalar.
A linha do jogador que gravou - veículo ou navio, abates, dano (World of Tanks), se sobreviveu e o
resultado (World of Tanks) - passa a ser as estatísticas da sessão. O que cada conversor lê, e o que não
lê, está no README dele.

A mesma parte também serve: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [osu! (replays)](game-osu-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros (x leste, y para cima, z norte) |
| Espelhado para o visualizador | `z` |
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

`map`, `survived`, `vehicle`, `won`

Uma chave entre chaves é completada na execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela dos campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O conversor que este adaptador executa segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que o replay contém é lido ou guardado, nunca descartado - lido na tabela e no documento da partida, e todo o resto guardado inteiro em ficheiros auxiliares ao lado deles, contado em `selfCheck.completeness` do documento da partida. A documentação do próprio conversor lista o que ele lê, o que guarda em bruto e o que não consegue ler.

## Verificado {#verified}

o conversor é verificado em replays públicos de várias versões do jogo e por testes em replays montados; este gancho, por testes com um comando substituto

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
