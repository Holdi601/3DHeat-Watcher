---
title: "Estatísticas do Steam (plataforma)"
nav_order: 43
lang: "pt"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Estatísticas do Steam (plataforma) {#steam-statistics-platform}

O watcher guarda o que as estatísticas do Steam guardam sobre os jogos, para que se possa ver o histórico depois como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `steam-stats`, tipo [`platform`](sources-and-rules.md); ele corre o tempo todo (não espera um jogo começar) e procura dados novos a cada 30 s.*

## O que é gravado {#what-is-recorded}

- toda estatística que um jogo guarda no Steam (os nomes e valores próprios dele), por jogo, quando muda
- desbloqueios de conquistas com nome de apresentação, descrição e hora do desbloqueio
- mudanças de estatística com valor antigo, valor novo e diferença
- tempo de jogo (minutos, últimas duas semanas) e hora em que foi jogado pela última vez

## De onde vem {#where-it-comes-from}

cache local de estatísticas do Steam %STEAM%\appcache\stats\UserGameStats_&lt;conta>_&lt;appid>.bin, com UserGameStatsSchema_&lt;appid>.bin; tempo de jogo de %STEAM%\userdata\\&lt;conta>\config\localconfig.vdf (%STEAM% a partir de HKCU\Software\Valve\Steam SteamPath)

## Como ativar {#how-to-switch-it-on}

Nada precisa ser ativado: o watcher lê a fonte como o jogo ou a plataforma a entrega.

## Como funciona {#how-it-works}

O que o lançador e o driver de vídeo guardam sobre o jogo: as estatísticas do Steam, conquistas, tempo de jogo e linhas do tempo, e os destaques e clipes da NVIDIA.

Nenhuma dessas fontes precisa que um jogo coopere ou esteja a correr, então os três adaptadores
daqui estão sempre ligados e olham alguns ficheiros a cada poucos segundos.

#### Estatísticas do Steam (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<conta>_<appid>.bin`, reescrito pelo cliente do Steam
sempre que um jogo guarda as estatísticas dele, decodificado com o esquema
`UserGameStatsSchema_<appid>.bin` ao lado (KeyValues binário, veja `_steam.py`). As estatísticas
são inteiros ou decimais, como o jogo as define; as conquistas são bits com uma hora de
desbloqueio em segundos Unix. O tempo de jogo está em
`<Steam>\userdata\<conta>\config\localconfig.vdf` em apps/&lt;appid>: Playtime e Playtime2wks em
minutos, LastPlayed em segundos Unix. O Steam é encontrado por HKCU\Software\Valve\Steam SteamPath.
API de estatísticas: <https://partner.steamgames.com/doc/features/achievements>

A mesma parte também serve: [NVIDIA highlights (plataforma)](game-nvidia-highlights.md), [Linha do tempo do Steam (plataforma)](game-steam-timeline.md).

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

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Uma chave entre chaves é completada na execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela dos campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte contém é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e os campos guardados por nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- toda estatística do ficheiro de estatísticas pelo nome na API (int, float, avgrate), cada bit de conquista com a hora de desbloqueio, nomeado e descrito pelo esquema
- mudanças em relação à última leitura (antigo, novo, diferença), novos desbloqueios; tempo de jogo, tempo das últimas duas semanas e última vez jogado, do localconfig.vdf

**Guardado em bruto**

- `UserGameStats`: os bytes inteiros do ficheiro de estatísticas, a cada gravação (o `crc`, `PendingChanges`, os bits de conquista que o esquema não define mais e qualquer chave que o decodificador pula estão nele)
- `UserGameStatsSchema`: os bytes do ficheiro de esquema ao lado, para que as estatísticas possam ser decodificadas só a partir da sessão (os nomes de cada estatística e conquista em todos os idiomas, ícones, flags)
- `localconfig_app`: o bloco inteiro do jogo no localconfig.vdf como JSON (estado da sincronização na nuvem, opções de inicialização, insígnias e toda outra chave que o Steam mantém por jogo) quando o tempo de jogo é gravado
- um ficheiro de estatísticas que o decodificador não consegue ler (cortado no meio de uma gravação, ou um layout novo): os bytes dele e o esquema, numa sessão sem linhas (`used` falso; `unreadable` no meta.json)

**Não disponível**

- o resto do localconfig.vdf (amigos, chat, configurações do Steam): não é do jogo, e é privado
- valores de estatística entre duas gravações: o Steam reescreve o ficheiro quando o jogo guarda as estatísticas dele, geralmente ao fechar
- percentagens globais de conquistas e estatísticas de outros jogadores: estão nos servidores do Steam, não aqui

**Tamanho**: alguns KB por sessão gravada, mais o esquema (até algumas centenas de KB para um jogo com muitas conquistas) - bem abaixo de 1 MB por hora de jogo; o zstd reduz o texto do esquema à metade ou mais

## Verificado {#verified}

testado em ficheiros de estatísticas e esquemas reais de uma instalação local; a deteção de mudanças, testada em ficheiros montados no formato KeyValues binário

## Fonte {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
