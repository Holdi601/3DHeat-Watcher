---
title: "League of Legends (estado do jogo)"
nav_order: 29
lang: "pt"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (estado do jogo) {#league-of-legends-game-state}

Enquanto se joga League of Legends, o watcher guarda o que o jogo informa a programas no próprio computador, para se poder ver depois como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `lol-live`, tipo [`gsi`](sources-and-rules.md); ele corre enquanto `League of Legends.exe` está em execução e procura novos dados a cada 0,5 s.*

## O que é gravado {#what-is-recorded}

- sem posições: a API não tem nenhuma
- feed de abates: abates, mortes e assistências do jogador, abates de outros campeões com quem matou, vítima, assistentes
- dragões, arautos, barões, torres, inibidores, multiabates, ases, primeiro sangue, início e fim da partida
- próprios abates, mortes, assistências, pontuação de creeps, pontuação de wards, nível, ouro, campeão, tempo de jogo, resultado
- objetivos conquistados pela equipa do jogador

## De onde vêm os dados {#where-it-comes-from}

API de Dados do Cliente Ao Vivo do cliente do jogo, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), durante uma partida

## Como ativar {#how-to-switch-it-on}

Nada precisa ser ligado: o watcher lê a fonte da forma que o jogo ou a plataforma a disponibiliza.

## Como funciona {#how-it-works}

League of Legends: a API de Dados do Cliente Ao Vivo que o cliente do jogo serve durante uma partida.

Enquanto uma partida corre (também no modo de treino e no de espectador), `League of Legends.exe` responde em <https://127.0.0.1:2999> com o que o jogador pode ver na própria interface do jogo:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} a partir do EventID N: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Não há posições: a API não tem nenhuma, então uma sessão de League é feita de eventos e estatísticas, sem tabela de calor. O certificado é autoassinado, da raiz própria da Riot (`riotgames.pem`, publicado em <https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Os termos de uso dele não são declarados, então ele não vem junto: coloque-o em `<dados>\riotgames.pem` e a conexão é verificada com ele; sem ele, a verificação fica desligada, e só para 127.0.0.1, o único endereço com que este adaptador fala.

A política da Riot permite que ferramentas mostrem o que o jogador poderia saber pelo próprio jogo, e nada calculado além disso (sem cronómetros de inimigos): isto grava o feed de abates e a tabela de pontuação que o jogador vê, e os números do próprio jogador.

Toda resposta também é guardada inteira (regra do conversor do 3DHeat, docs/converters.md no repositório do visualizador): `heat.raw.parquet`, `type` é o endpoint ("allgamedata", "eventdata"), `text` é o JSON como o cliente enviou, `status` quando não foi 200. Uma resposta byte a byte igual à anterior do mesmo endpoint (a lista de eventos enquanto nada acontece) é guardada uma vez e contada em `unchanged_replies` no meta.json. O allgamedata traz tudo o que os outros endpoints servem (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), então eles não são pedidos separadamente. Respostas antes de uma partida (o ecrã de carregamento) esperam numa fila de pendências e entram na sessão da partida; depois do GameEnd a sessão fica aberta até o cliente fechar, para que as respostas do ecrã final sejam guardadas com ela.

Fonte: <https://developer.riotgames.com/docs/lol#game-client-api>

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | não |
| Eixo para cima | `z` |
| Unidades | nenhuma (sem posições) |
| Espelhado para o visualizador | nenhum |
| Escala da unidade (`scale`: o visualizador multiplica as posições por ele) | 1 |

Estes valores vão para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`. Assim o visualizador do 3DHeat gira e dimensiona as linhas sozinho: veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `gsi`: lê só o que o jogo ou a plataforma entrega (uma integração de estado de jogo ou uma API local que o jogo serve), por isso grava também em jogo online, além do offline; a marcação decide apenas se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online: veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- o feed de abates a partir do eventdata: cada evento uma vez, com os campos nomeados dele decodificados (quem matou, vítima e assistentes com campeão e equipa, estruturas e o lado delas, tipo de dragão, roubos, multiabates, ases, primeiro sangue, o resultado), e cada outro campo de um evento na linha dele, pelo próprio nome
- do allgamedata: os próprios abates, mortes, assistências, pontuação de creeps, pontuação de wards, nível, ouro, campeão, tempo de jogo, modo de jogo e mapa

**Mantido bruto**

- `allgamedata`: cada resposta inteira (`text`), a cada 2 s — activePlayer (habilidades, cada atributo do campeão, runas completas, ouro, nível), allPlayers (itens com slots e preços, runas, feitiços de invocador, pontuações, nível, morto e tempo de reaparecimento, skin, rota, se é bot), os eventos, gameData (modo, tempo, mapa, terreno); `used` verdadeiro enquanto a partida corre, falso no ecrã final
- `eventdata`: cada resposta inteira, pedida a cada 0,5 s a partir do próximo id de evento; `used` verdadeiro quando trouxe eventos novos
- uma resposta byte a byte igual à anterior do mesmo endpoint é guardada uma vez e contada (`unchanged_replies` no meta.json); respostas de erro (o RESOURCE_NOT_FOUND do ecrã de carregamento) são guardadas com o `status` delas, antes do início da partida

**Não disponível**

- posições: a API não tem nenhuma (sem minimapa, sem coordenadas)
- os outros endpoints (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): cada um serve uma parte do allgamedata, então não são pedidos
- a API de Replay (`/replay/*` na mesma porta): ela reproduz replays e partidas assistidas quando ligada no game.cfg; não faz parte de uma partida jogada
- os endpoints do ficheiro de bloqueio (lockfile) do cliente da League: não é uma API publicada (veja Fontes e regras)
- valores entre duas leituras: a API responde quando é perguntada e não envia sozinha; a tabela de pontuação é pedida a cada 2 s, os eventos a cada 0,5 s

**Tamanho**: o allgamedata tem 15 a 40 KB (ele traz a lista inteira de eventos, que cresce) a cada 2 s: cerca de 30 a 70 MB por hora em `raw.bin`; o eventdata acrescenta pouco, já que respostas iguais são contadas, não guardadas; o zstd reduz o JSON repetido no `heat.parquet` a alguns MB por hora (estimado a partir do formato documentado)

## Verificado {#verified}

testado com um servidor local falso que serve respostas no formato documentado; não testado contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
