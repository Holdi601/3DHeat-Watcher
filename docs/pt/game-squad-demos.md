---
title: "Squad (replays)"
nav_order: 41
lang: "pt"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (replays) {#squad-replays}

Depois de uma partida de Squad, o watcher transforma o replay que o jogo guardou em ficheiros que se podem ver num mapa no visualizador do 3DHeat.

*Detalhes técnicos: adaptador `squad-demos`, tipo [`replay`](sources-and-rules.md); ele corre o tempo todo (não espera um jogo começar) e procura dados novos a cada 5 s.*

## O que é gravado {#what-is-recorded}

- a posição, o giro do corpo e a velocidade de cada jogador cada vez que o servidor a replica (até 8 vezes por segundo), a pé e em veículos terrestres
- o nome, a equipa, a facção e o pelotão de cada jogador, a acompanhar as mudanças de equipa
- não: o movimento dos helicópteros, abates e itens implantáveis - veja o README do leitor

## De onde vem {#where-it-comes-from}

demos de servidor que o Squad grava com o comando de admin AdminDemoRec: &lt;servidor>/SquadGame/Saved/Demos/\*.replay, lidas pelo leitor externo `heat3d-squad-demo` (exporters/ext/squad-demo)

## Como ativar {#how-to-switch-it-on}

grave no servidor: dê ao admin a permissão `demos` no Admins.cfg, depois AdminDemoRec &lt;nome> e AdminDemoStop no console do jogo; copie a demo para cá e instale o leitor: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Configurações por variáveis de ambiente:

- `HEAT3D_SQUAD_DEMO`: a pasta do conversor (um clone ou um pacote extraído), quando ele não estiver instalado nem ao lado do watcher

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

#### Squad {#squad}

Os servidores dedicados do Squad gravam uma demo de uma partida quando um admin com a
permissão `demos` executa AdminDemoRec &lt;nome> (e AdminDemoStop), em
`<servidor>/SquadGame/Saved/Demos/<nome>.replay` - um replay de rede da Unreal Engine que
guarda o que o servidor replicou, inclusive o movimento de cada jogador. O watcher não lê
essas demos sozinho: um leitor externo lê (leitor de demos do 3DHeat Squad,
`exporters/ext/squad-demo`, comando `heat3d-squad-demo`), separado para que um problema nele
não afete nada mais. Ele corre em cada demo nova nas pastas em que um servidor local grava, ou
numa pasta que as configurações acrescentam para demos copiadas de um servidor alugado, e gera
na pasta da sessão `<mapa>/<partida>.parquet` e `<partida>.match.json`. A camada, o mapa, o
número de jogadores e a duração da partida passam a ser as estatísticas da sessão.

A mesma parte também serve: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [osu! (replays)](game-osu-replays.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `z` |
| Unidades | unidades Unreal (centímetros) |
| Espelhado para o visualizador | nenhum |
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

`layer`, `map`, `match_seconds`, `players`

Uma chave entre chaves é completada na execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela dos campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O conversor que este adaptador executa segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que o replay contém é lido ou guardado, nunca descartado - lido na tabela e no documento da partida, e todo o resto guardado inteiro em ficheiros auxiliares ao lado deles, contado em `selfCheck.completeness` do documento da partida. A documentação do próprio conversor lista o que ele lê, o que guarda em bruto e o que não consegue ler.

## Verificado {#verified}

o leitor é verificado em demos públicas de servidores (o movimento coincide com a velocidade que ele carrega; a equipa de cada linha coincide com a facção do soldado dele) e por testes em demos montadas; este gancho por testes com um comando substituto

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
