---
title: "Dota 2 (estado do jogo)"
nav_order: 13
lang: "pt"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (estado do jogo) {#dota-2-game-state}

Enquanto se joga Dota 2, o watcher guarda o que o jogo informa a programas no próprio computador, para que se possa ver depois, num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `dota2-gsi`, tipo [`gsi`](sources-and-rules.md); ele corre enquanto `dota2.exe` está aberto e procura dados novos a cada 0,05 s.*

## O que é gravado {#what-is-recorded}

- a posição do próprio herói (X/Y do mundo, unidades do Dota; sem altura) enquanto vivo
- nascimento, mortes (com o tempo de renascimento) e renascimentos do próprio herói
- abates, a partir do aumento da contagem de abates
- construções destruídas, Roshan, eventos do jogo (roshan_killed, aegis_picked_up, ...), estados da partida, resultado
- abates, mortes, assistências, last hits, denies, ouro, GPM, XPM, nível, herói

## De onde vem {#where-it-comes-from}

Game State Integration: envios HTTP (POST) para 127.0.0.1:3312, configurados em &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## Como ligar {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, depois inicie o Dota 2 (ele lê o ficheiro ao arrancar)

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz o motivo; [Instalação e execução](installing-and-running.md) explica as causas mais comuns.

`python -m heat3d_watch setup dota2-gsi` lista os ficheiros que seriam alterados; `python -m heat3d_watch setup dota2-gsi --apply` faz as alterações e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `dota2-gsi: changed: ...` para cada alteração, ou `dota2-gsi: nothing to change` quando já estiver ligado.

Configurações por variáveis de ambiente:

- `HEAT3D_DOTA_GSI_PORT`: a porta para a qual o jogo envia (predefinição 3312); o ficheiro cfg do jogo precisa indicar a mesma porta

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

O mesmo módulo também serve: [Counter-Strike 2 (estado do jogo)](game-cs2-gsi.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `z` |
| Unidades | unidades do mundo do Dota (z sempre 0) |
| Espelhado para o visualizador | `y` |
| Escala das unidades (`scale`: o visualizador multiplica as posições por ele) | 1 |

Isso vai para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`, de modo que o visualizador do 3DHeat gira e ajusta as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `gsi`: ele lê apenas o que o jogo ou a plataforma entrega (uma integração de estado ou uma API local que o jogo oferece), por isso grava também em partidas online, e não só offline; a marcação só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem a memória, e nunca num jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado por inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- a posição (x/y) do próprio herói, vivo, nível, vida, vida máxima, mana, mana máxima; nascimento, mortes com o tempo de renascimento, renascimentos
- abates (quando a contagem de abates sobe); abates, mortes, assistências, last hits, denies, ouro, GPM, XPM, património líquido, nível e herói, como estatísticas
- construções destruídas, Roshan abatido e de volta, cada entrada de `events` uma vez, estados da partida, o vencedor

**Guardado bruto**

- `gsi`: cada documento que o jogo envia, por inteiro, como foi enviado (`text`), com `used` verdadeiro quando foi lido numa partida - todos os quinze componentes que o ficheiro cfg pede: provider, map (dia/noite, pausado, tempos de recarga de wards, placares), player (ouro confiável e não confiável, sequências, lista de abates, comandos emitidos, ...), hero (buffs, talentos, Aghanim's, atributos), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league, e o diff `previously`/`added` do jogo
- documentos de menus, carregamentos e entre partidas: guardados do mesmo modo, no momento em que chegaram, antes do início da próxima partida; depois da última partida, numa sessão própria (`raw_only` no meta.json)
- `gsi-unreadable`: um envio que não é um objeto JSON, com os bytes dele como `payload` e `length`
- `gsi-bad-auth`: um envio com outro token que não o do ficheiro cfg

**Não disponível**

- altura: o jogo envia só x e y
- os outros heróis durante a partida: o jogo envia o próprio herói, e os de todos os jogadores só para espectadores (guardados em bruto nesse caso, não desenhados); vários componentes (draft, minimap, couriers) trazem só o que o cliente do próprio jogador tem - o que, durante a partida, ainda não foi testado
- estados entre envios: no máximo um a cada 0,1 s (`throttle`), a cada 10 s quando nada muda
- o token do ficheiro cfg, em branco em cada documento guardado: o segredo do próprio watcher, não dado do jogo
- envios além de 10.000 em espera (o watcher bloqueou) são contados como `dropped_packets`, não guardados; um envio acima de 4 MB é guardado como `gsi-unreadable` com o tamanho, mas sem os bytes

**Tamanho**: com todos os componentes, o documento de um jogador tem cerca de 5 a 15 KB, enviado até 10 vezes por segundo (o relógio muda a cada envio): cerca de 100 a 500 MB por hora em `raw.bin` durante a partida, cerca de um décimo disso no `heat.raw.parquet` com zstd; o de um espectador, com todos os jogadores e o minimapa, várias vezes isso (estimado pelo formato publicado, não medido no jogo)

## Verificado {#verified}

testado com documentos no formato GSI publicado, enviados ao adaptador em execução; não testado com o jogo em execução

## Fonte {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
