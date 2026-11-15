---
title: "Hearthstone (ficheiros de log)"
nav_order: 25
lang: "pt"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (ficheiros de log) {#hearthstone-log-files}

Enquanto se joga Hearthstone, o watcher lê os ficheiros que o jogo escreve e guarda o que aconteceu, para se poder ver depois como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `hearthstone`, tipo [`log`](sources-and-rules.md); ele corre enquanto `Hearthstone.exe` está em execução e procura novos dados a cada 0,5 s.*

## O que é gravado {#what-is-recorded}

- início e fim de cada partida, com o resultado (vitória, derrota, empate), turnos e o nome do oponente
- cada turno
- cada linha do Power.log e dos outros logs, inteira, no heat.raw.parquet
- partidas, vitórias, derrotas, empates, turnos, partida mais longa

## De onde vêm os dados {#where-it-comes-from}

&lt;instalação>\Logs\Power.log (ou Logs\Hearthstone_\*\Power.log), escrito depois que %LOCALAPPDATA%\Blizzard\Hearthstone\log.config tem uma seção [Power], e todos os outros \*.log que o jogo escreve ali

## Como ativar {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` acrescenta o registo [Power] ao %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (cópia de segurança guardada); reinicie o jogo

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz o motivo; [Instalação e execução](installing-and-running.md) cobre as causas mais comuns.

`python -m heat3d_watch setup hearthstone` lista os ficheiros que ele mudaria; `python -m heat3d_watch setup hearthstone --apply` os altera e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `hearthstone: changed: ...` para cada mudança, ou `hearthstone: nothing to change` quando já está ativo.

## Como funciona {#how-it-works}

Hearthstone: o Power.log do jogo, que ele escreve assim que o `log.config` pede.

O Hearthstone lê `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` ao arrancar; uma seção `[Power]` com `LogLevel=1` e `FilePrinting=true` faz com que ele escreva cada mudança de estado de cada partida em `<instalação>\Logs\Power.log` (clientes mais novos põem os logs de cada início numa pasta própria, `Logs\Hearthstone_<data>\`). Este é o registo de depuração documentado que os rastreadores de baralho usam desde 2014 (o setup do Hearthstone Deck Tracker escreve a mesma seção). `setup()` acrescenta a seção, com uma cópia de segurança do ficheiro como estava; o jogo precisa ser reiniciado para lê-la.

As linhas usadas, todas de `GameState.DebugPrintPower()` (as linhas `PowerTaskList` repetem essas e são ignoradas):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

O lado do próprio jogador é aquele cuja mão inicial tem as cartas nomeadas (as do oponente ficam ocultas); senão, o lado que não é a IA (conta 0) ou "UNKNOWN HUMAN PLAYER". As linhas trazem só a hora do dia; a data é a de hoje. Sem posições.

Cada linha do Power.log é guardada inteira no ficheiro bruto anexo da sessão (regra do conversor do 3DHeat), incluindo as repetições de `PowerTaskList`, opções, escolhas e atualizações de entidade: `type` é o método que a escreveu (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Qualquer outro log que o jogo escreve ao lado — `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., cada um presente quando o log.config o pede (rastreadores de baralho costumam pedir) — é acompanhado do mesmo jeito e guardado com o seu nome em `log`.

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | não |
| Eixo para cima | `y` |
| Unidades | sem posições gravadas |
| Espelhado para o visualizador | nenhum |
| Escala da unidade (`scale`: o visualizador multiplica as posições por ele) | 1 |

Estes valores vão para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`. Assim o visualizador do 3DHeat gira e dimensiona as linhas sozinho: veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `log`: lê só o que o jogo ou a plataforma entrega (ficheiros que o jogo escreve enquanto corre), por isso grava também em jogo online, além do offline; a marcação decide apenas se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online: veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- `CREATE_GAME`, os jogadores (entidade, id de jogador, conta; a conta 0 é a IA) e os nomes deles (`DebugPrintGame`)
- de que lado está o jogador, pelas cartas nomeadas da mão inicial
- `TAG_CHANGE` de TURN, PLAYSTATE (won, lost, tied) e STATE COMPLETE: turnos, resultado, oponente

**Mantido bruto**

- cada linha do Power.log inteira, `type` = o método que a escreveu (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` onde passou a linha: cada carta jogada, comprada e revelada, cada mudança de tag, ataque, opção e escolha estão aqui, ainda não em linhas
- cada linha dos outros logs da mesma pasta (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... — o que o log.config ligar), com os mesmos `type`, com o nome do log em `log`
- uma linha sem o nível e a hora do dia como `untimed`, uma sem método como `untagged`

**Não disponível**

- posições: um jogo de cartas não tem nenhuma
- as cartas ocultas do oponente: o log nomeia uma carta só quando ela é revelada
- logs que o log.config não liga: o `setup` pede só o [Power]; os outros logs vêm quando outra ferramenta (um rastreador de baralho) os liga
- logs de inícios anteriores: cada início escreve uma pasta nova; as mais antigas que esta execução do jogo não são lidas de novo

**Tamanho**: o Power.log com Verbose tem cerca de 1 a 5 MB por partida, 10 a 40 MB por hora de jogo; os outros logs acrescentam pouco; o zstd no heat.raw.parquet deixa cerca de um décimo ou menos (as linhas se repetem muito)

## Verificado {#verified}

testado com linhas de Power.log sintéticas no formato do jogo; não testado contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
