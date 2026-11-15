---
title: "Counter-Strike 2 (estado do jogo)"
nav_order: 9
lang: "pt"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (estado do jogo) {#counter-strike-2-game-state}

Enquanto se joga Counter-Strike 2, o watcher guarda o que o jogo informa a programas no próprio computador, para que se possa ver depois, num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `cs2-gsi`, tipo [`gsi`](sources-and-rules.md); ele corre enquanto `cs2.exe` está aberto e procura dados novos a cada 0,05 s.*

## O que é gravado {#what-is-recorded}

- a própria posição (XYZ no mundo, em polegadas) e a direção do olhar até 10 vezes por segundo, enquanto o jogador está vivo
- nascimentos (a primeira vez que cada ronda aparece, e renascimentos) e mortes (vida a chegar a 0, ou a contagem de mortes)
- abates com a arma ativa, a partir das estatísticas da partida
- rondas (início, fim, vencedor), bomba plantada, desarmada ou explodida, fases da partida e o resultado
- abates, assistências, mortes, MVPs, placar, dinheiro, dano, abates de headshot, rondas ganhas e perdidas

## De onde vem {#where-it-comes-from}

Game State Integration: envios HTTP (POST) para 127.0.0.1:3311, configurados em &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Como ligar {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, depois inicie o CS2 (ele lê o ficheiro ao arrancar)

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz o motivo; [Instalação e execução](installing-and-running.md) explica as causas mais comuns.

`python -m heat3d_watch setup cs2-gsi` lista os ficheiros que seriam alterados; `python -m heat3d_watch setup cs2-gsi --apply` faz as alterações e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `cs2-gsi: changed: ...` para cada alteração, ou `cs2-gsi: nothing to change` quando já estiver ligado.

Configurações por variáveis de ambiente:

- `HEAT3D_CS2_GSI_PORT`: a porta para a qual o jogo envia (predefinição 3311); o ficheiro cfg do jogo precisa indicar a mesma porta

## Como funciona {#how-it-works}

Valve Game State Integration: Counter-Strike 2 e Dota 2 informam a um servidor web local o que acontece.

Os dois jogos leem todos os `gamestate_integration_*.cfg` da pasta cfg deles ao arrancar, e a partir daí enviam um documento JSON (POST) para o `uri` de cada ficheiro sempre que o estado muda (no máximo a cada `throttle` segundos, e a cada `heartbeat` segundos quando nada muda). O watcher é esse servidor web: ele escuta somente em 127.0.0.1, responde a cada envio com 200 na hora e faz o trabalho na própria thread de leitura.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      porta 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   porta 3312
```

O que um jogador recebe - e, portanto, o que pode ser gravado - é o que o jogo decide que o jogador pode ver:

- CS2: `provider` (o steamid próprio), `map` (nome, modo, fase warmup/live/intermission/gameover, ronda, placar de team_ct/team_t), `round` (fase freezetime/live/over, bomba plantada/explodida/desarmada, win_team), `player` (o jogador que está a ser *observado*: o próprio jogador enquanto vivo, um colega depois da morte) com `state` (vida, colete, dinheiro, round_kills, round_killhs, round_totaldmg), `match_stats` (kills, assists, deaths, mvps, score), `position` e `forward` como textos "x, y, z" em unidades do mundo (polegadas, Z para cima), `weapons`; `bomb` só para espectadores. As posições dos outros jogadores (`allplayers_*`) são enviadas só para espectadores e GOTV, por isso não são pedidas.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos em unidades do mundo, level, alive, respawn_seconds), `buildings` (vida de cada torre, quartel e ancient), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Não há altura: z é 0. Também são pedidos, e guardados por inteiro: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (o jogo envia o que o cliente do próprio jogador tem; quais deles trazem algo durante a partida, e não como espectador, ainda não foi testado).

Cada documento também é guardado por inteiro (regra de conversores do 3DHeat, docs/converters.md no repositório do visualizador): `heat.raw.parquet`, `type` "gsi", `text` é o JSON como foi enviado - apenas o token do ficheiro cfg fica em branco, porque é o segredo do próprio watcher, não dado do jogo. Documentos enviados enquanto nenhuma partida está aberta (menus, carregamento, entre partidas) ficam numa `Backlog` e vão para a sessão da próxima partida, antes do início dela; o que sobra quando o jogo fecha ganha uma sessão própria, que contém só eles. Envios ilegíveis e envios com token errado também são guardados ("gsi-unreadable", "gsi-bad-auth").

Fontes: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (o formato que o CS2 manteve), <https://github.com/antonpup/CounterStrike2GSI> e <https://github.com/antonpup/Dota2GSI> (listas de campos; MIT, lidos apenas para os factos).

O mesmo módulo também serve: [Dota 2 (estado do jogo)](game-dota2-gsi.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `z` |
| Unidades | polegadas (unidades do Hammer) |
| Espelhado para o visualizador | `y` |
| Escala das unidades (`scale`: o visualizador multiplica as posições por ele) | 1 |

Isso vai para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`, de modo que o visualizador do 3DHeat gira e ajusta as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `gsi`: ele lê apenas o que o jogo ou a plataforma entrega (uma integração de estado ou uma API local que o jogo oferece), por isso grava também em partidas online, e não só offline; a marcação só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem a memória, e nunca num jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado por inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- a posição, a direção do olhar, a vida, o colete, o dinheiro, a arma ativa, o capacete, o kit de desarme, a quantidade de flash/fumaça/fogo e o valor do equipamento do jogador observado, em cada linha de posição enquanto for o próprio jogador (steamid do provider = steamid do jogador)
- nascimentos, mortes (vida a chegar a 0, ou a contagem de mortes das estatísticas), abates (quando a contagem sobe)
- fases da partida, rondas (tempo de congelamento, ao vivo, fim, vencedor), bomba plantada/desarmada/explodida, o resultado
- abates, assistências, mortes, MVPs, placar, dinheiro, dano, abates de headshot, rondas ganhas e perdidas, como estatísticas

**Guardado bruto**

- `gsi`: cada documento que o jogo envia, por inteiro, como foi enviado (`text`), com `used` verdadeiro quando foi lido numa partida - provider (versão, data e hora), map (modo, nomes dos equipas, derrotas seguidas, tempos limite, vitórias na série, `round_wins` com a condição de vitória de cada ronda), round, o jogador observado (clã, slot de watcher, atividade, cada arma com skin, munição e reserva), bomb, contagens de fase, e o diff `previously`/`added` que o próprio jogo envia em relação ao envio anterior
- documentos de menus, carregamentos e entre partidas: guardados do mesmo modo, no próprio horário, antes do início da próxima partida; depois da última partida, numa sessão própria (`raw_only` no meta.json)
- `gsi-unreadable`: um envio que não é um objeto JSON, com os bytes dele como `payload` e `length`
- `gsi-bad-auth`: um envio com outro token que não o do ficheiro cfg

**Não disponível**

- outros jogadores (`allplayers_*`) e granadas (`allgrenades`): o jogo os envia só a espectadores e GOTV, e o watcher não os pede (Fontes e regras); uma demo tem todos os jogadores - veja [Counter-Strike 2 (replays)](game-cs2-demos.md)
- estados entre envios: o jogo envia no máximo a cada 0,1 s (`throttle`) e só quando algo muda, a cada 10 s (`heartbeat`) caso contrário
- o token do ficheiro cfg, em branco em cada documento guardado: é o segredo do próprio watcher, não dado do jogo
- envios além de 10.000 em espera (o watcher bloqueou) são contados como `dropped_packets`, não guardados; um envio acima de 4 MB é guardado como `gsi-unreadable` com o tamanho, mas sem os bytes

**Tamanho**: o documento de um jogador tem 2 a 4 KB, enviado até 10 vezes por segundo enquanto algo muda: cerca de 30 a 150 MB por hora em `raw.bin` durante a partida, e um décimo disso ou menos no `heat.raw.parquet` com zstd (estimado pelo formato publicado, não medido no jogo)

## Verificado {#verified}

testado com documentos no formato GSI publicado, enviados ao adaptador em execução; a instalação e a busca da pasta cfg testadas numa instalação local; não testado com o jogo em execução

## Fonte {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
