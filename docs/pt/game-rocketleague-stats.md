---
title: "Rocket League (estado do jogo)"
nav_order: 40
lang: "pt"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (estado do jogo) {#rocket-league-game-state}

Enquanto se joga Rocket League, o watcher guarda o que o jogo informa aos programas do próprio computador, para que se possa ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `rocketleague-stats`, tipo [`gsi`](sources-and-rules.md); corre enquanto `RocketLeague.exe` estiver em execução e procura dados novos a cada 0,05 s.*

## O que é gravado {#what-is-recorded}

- toques na bola com o lugar da bola (XYZ, unidades Unreal), quem tocou e as velocidades
- golos com o lugar do impacto, quem marcou, quem assistiu e a velocidade; toques na trave com o lugar
- feed de estatísticas (demolições, defesas, remates, defesas épicas, ...), saídas de bola, repetições, início e fim da partida, vencedor
- golos contra, assistências, defesas, remates, demolições, toques, placar e placar das equipas, a partir do UpdateState
- a linha final de cada jogador ao fim da partida
- as próprias linhas como `me`: o jogador nomeado nas configurações (`config --set player_names.rocketleague-stats=<nome>`), senão aquele que a câmara do jogo segue fora das repetições
- nenhuma posição de carros: a API não as tem

## De onde vem {#where-it-comes-from}

API de estatísticas: fluxo TCP de JSON de 127.0.0.1:49123 (porta em &lt;RL>\TAGame\Config\TAStatsAPI.ini ou DefaultStatsAPI.ini)

## Como ligar {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (define PacketSendRate=30), depois abra o Rocket League

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz porquê; [Instalar e executar](installing-and-running.md) cobre as causas mais comuns.

`python -m heat3d_watch setup rocketleague-stats` lista os ficheiros que ele mudaria; `python -m heat3d_watch setup rocketleague-stats --apply` os altera e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `rocketleague-stats: changed: ...` para cada mudança, ou `rocketleague-stats: nothing to change` quando já está ligado.

## Como funciona {#how-it-works}

Rocket League: a API oficial de estatísticas, um socket local para o qual o jogo envia os dados da partida.

Ligada em `<RL>\TAGame\Config\TAStatsAPI.ini` - ou `DefaultStatsAPI.ini` quando o primeiro não existe, o que o jogo só lê nesse caso - na seção `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   mensagens UpdateState por segundo; 0 (a predefinição) desliga a API, no máximo 120
Port             a porta TCP em que o jogo escuta, predefinição 49123 (WebPort 49124 é uma cópia WebSocket)
```

O jogo é o servidor: um cliente se conecta a 127.0.0.1:49123 e lê um fluxo de objetos JSON `{"Event": nome, "Data": {...}}` (algumas versões enviam Data como string JSON), um após o outro, sem separadores. Os eventos são enviados no tick em que acontecem, independentemente da taxa:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 azul / 1 laranja,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; estado do carro
              só para espectadores), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

As localizações são unidades Unreal (centímetros), Z para cima; o campo tem cerca de 8200 x 10240, com os golos em Y = ±5120. As posições dos carros não fazem parte da API: o que tem um lugar é a bola onde foi tocada, marcada ou acertou a trave.

Cada mensagem também é guardada inteira (regra do conversor do 3DHeat, docs/converters.md no repositório do visualizador): `heat.raw.parquet`, com `type` o nome do Event da mensagem e `text` o objeto como chegou do fluxo. Um UpdateState igual byte a byte ao anterior (uma partida pausada, um menu) é guardado uma vez e contado em `unchanged_replies` do meta.json. As mensagens entre partidas esperam num acúmulo pela sessão da próxima partida; o que sobra quando o jogo fecha ganha uma sessão própria. Caracteres entre objetos que não são JSON são guardados como "junk".

Fontes: <https://www.rocketleague.com/en/developer/stats-api> (a página oficial); a grafia dos campos e o enquadramento TCP verificados com o cliente rlstatsapi (<https://docs.rs/crate/rlstatsapi>, MIT; lido só pelos factos).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `z` |
| Unidades | unidades Unreal (centímetros) |
| Espelhado para o visualizador | nenhum |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `gsi`: lê só o que o jogo ou a plataforma entrega (uma integração de estado de jogo ou uma API local que o jogo serve), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- BallHit (lugar, quem, equipa, velocidades antes e depois), GoalScored (lugar do impacto, quem marcou, quem assistiu, velocidade, tempo do golo), CrossbarHit (lugar, último toque, velocidade, força), StatfeedEvent (evento, tipo, alvo principal e secundário), MatchEnded (vencedor, resultado); o nome de cada outro evento como uma linha
- do UpdateState: a arena, o alvo da câmara fora das repetições (quem é `me`), os placares das equipas, os golos, assistências, defesas, remates, demolições, toques, toques em carros e placar de cada jogador (os do próprio como estatísticas, os de todos como `player_result` ao fim da partida); a prorrogação a partir do ClockUpdatedSeconds

**Guardado bruto**

- cada mensagem inteira como chegou do fluxo (`text`), sob o próprio nome de Event: `UpdateState` (o PrimaryId e o Shortcut de cada jogador, o relógio, a velocidade e a equipa da bola, nomes e cores das equipas, as flags de repetição e de vencedor, e o estado do carro onde o jogo o envia), `BallHit`, `GoalScored` (com o último toque da bola), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` e qualquer evento que uma versão posterior acrescente
- um UpdateState igual byte a byte ao anterior (pausado, menus) é guardado uma vez e contado (`unchanged_replies` no meta.json)
- mensagens entre partidas: no próprio tempo, antes do início da próxima partida; depois da última partida, numa sessão própria (`raw_only` no meta.json)
- `unreadable`: um objeto que não é uma mensagem da API de estatísticas; `junk`: caracteres entre objetos

**Não disponível**

- posições e estado dos carros durante o jogo: o jogo só os envia para espectadores
- o UpdateState entre dois envios: o jogo envia PacketSendRate por segundo (`setup` define 30; o jogo permite até 120); os eventos são enviados no tick em que acontecem
- a cópia WebSocket na WebPort (49124): as mesmas mensagens da porta TCP, não lidas duas vezes

**Tamanho**: um UpdateState tem 1-3 KB para seis jogadores, 30 por segundo: cerca de 100-300 MB por hora em `raw.bin` enquanto uma partida corre, um décimo ou menos no `heat.raw.parquet` com zstd (estimado a partir do formato documentado, não medido no jogo)

## Verificado {#verified}

testado com mensagens no formato documentado, enviadas por um servidor local falso; sem teste contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
