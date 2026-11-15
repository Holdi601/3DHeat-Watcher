---
title: "Linha do tempo do Steam (plataforma)"
nav_order: 44
lang: "pt"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Linha do tempo do Steam (plataforma) {#steam-timeline-platform}

O watcher guarda o que a Linha do tempo do Steam guarda sobre os jogos, para que se possa ver o histórico depois como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `steam-timeline`, tipo [`platform`](sources-and-rules.md); ele corre o tempo todo (não espera um jogo começar) e procura dados novos a cada 10 s.*

## O que é gravado {#what-is-recorded}

- uma sessão por ficheiro de linha do tempo: o início e o fim (session_start, session_end)
- conquistas desbloqueadas durante o jogo, com a hora
- mudanças de modo de jogo (a jogar, preparação, menus, ecrã de carregamento)
- eventos que os jogos adicionam pelo ISteamTimeline, com título e descrição, sob o nome do ícone deles
- fases do jogo (uma partida, uma missão) com as etiquetas dela; eventos dentro de uma fase carregam o id dela como `session`
- descrições de estado que o jogo mostra na linha do tempo ("Round 3")
- os próprios erros de gravação do Steam

## De onde vem {#where-it-comes-from}

%STEAM%\userdata\\&lt;conta>\gamerecordings\timelines\timeline_&lt;appid>&lt;data>_&lt;hora>.json

## Como ativar {#how-to-switch-it-on}

Steam > Configurações > Gravação de jogos: grave em segundo plano ou sob demanda (o Steam grava as linhas do tempo então)

## Como funciona {#how-it-works}

O que o lançador e o driver de vídeo guardam sobre o jogo: as estatísticas do Steam, conquistas,
tempo de jogo e linhas do tempo, e os destaques e clipes da NVIDIA.

Nenhuma dessas fontes precisa que um jogo coopere ou esteja a correr, então os três adaptadores
daqui estão sempre ligados e olham alguns ficheiros a cada poucos segundos.

#### Linha do tempo do Steam (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<conta>\gamerecordings\timelines\timeline_<appid><aaaammdd>_<hhmmss>.json`,
escrito enquanto a Gravação de jogos do Steam está ligada. O ficheiro é JSON com números em
texto: "daterecorded" (segundos Unix), "starttime"/"endtime" (ms) e "entries", cada um
{"id", "time" (ms desde daterecorded), "type", ...}. Tipos vistos em ficheiros reais:
```text
achievement        achievement_name - Steam adds these for every game
gamemode           mode, an ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - Steam's own ("#GameRecording_RecordingFailed")
event              a game's AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              a StartGamePhase..EndGamePhase span: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
A estrutura do ficheiro é do Steam e não é documentada; os campos são os parâmetros da API.
Qualquer outro tipo é gravado sob o próprio nome, com os seus campos.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

A mesma parte também serve: [NVIDIA highlights (plataforma)](game-nvidia-highlights.md), [Estatísticas do Steam (plataforma)](game-steam-stats.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | não |
| Eixo para cima | `y` |
| Unidades | metros |
| Espelhado para o visualizador | nenhum |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Isso vai para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o
rodapé de `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho -
veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **não**. `games --markdown` mostra isso como "single-player".
- Tipo `platform`: ele lê apenas o que o jogo ou a plataforma entrega (o que o Steam ou o driver de vídeo guarda), por isso grava também em partidas online, e não só offline; a marcação só decide se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem a memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (`stats` de cada sessão em `meta.json` e a tabela `stats` de `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Uma chave entre chaves é completada na execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela dos campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte contém é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e os campos guardados por nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- cada entrada uma vez, como uma linha na sua hora: o tipo, cada campo simples (title, description, icon, priority, duration, possible_clip, o nome da conquista, o modo, ...), as etiquetas de uma fase por grupo, o nome de apresentação da conquista a partir do esquema de estatísticas; o início e o fim do ficheiro

**Guardado em bruto**

- cada entrada inteira, como JSON, sob o `type` do próprio Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, qualquer outro): os campos aninhados - o ícone e a prioridade de uma etiqueta, tudo o que um Steam posterior acrescentar - só estão aqui
- `timeline`: os campos do próprio ficheiro (daterecorded, starttime, endtime, quaisquer outros), quando a sessão abre e de novo quando eles mudam

**Não disponível**

- a gravação em si (vídeo): o Steam a guarda nas pastas dele; a sessão se refere ao ficheiro de linha do tempo pelo nome
- uma leitura de um ficheiro que o Steam está a escrever e que não pode ser analisado nem com o fim fechado: contado (`bad` no estado do adaptador) e lido de novo na próxima mudança, quando as entradas dele são aproveitadas

**Tamanho**: algumas centenas de entradas de 100 a 300 bytes por hora de jogo: bem abaixo de 1 MB por hora

## Verificado {#verified}

testado em ficheiros reais de linha do tempo de uma instalação local: conquista, gamemode, error e os próprios eventos, state_description e phase dos jogos; o formato do ficheiro em si não é documentado

## Fonte {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
