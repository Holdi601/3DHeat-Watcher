---
title: "Minecraft (ficheiros de log)"
nav_order: 33
lang: "pt"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (ficheiros de log) {#minecraft-log-files}

Enquanto se joga Minecraft, o watcher lê os ficheiros que o jogo escreve e guarda o que aconteceu, para que se possa ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `minecraft`, tipo [`log`](sources-and-rules.md); corre enquanto `javaw.exe` ou `java.exe` estiver em execução e procura dados novos a cada 0,5 s.*

## O que é gravado {#what-is-recorded}

- posição do próprio jogador e dos outros (blocos = m, y para cima) cada vez que o mundo é guardado, com a dimensão como sessão
- aparição com posição quando um jogador entra no servidor (integrado)
- entradas, saídas, mortes com a mensagem de morte, conquistas, linhas de chat
- mortes, conquistas, mensagens de chat; do ficheiro de estatísticas: tempo de jogo, distância, abates de mobs e de jogadores, pulos, dano, blocos minerados, itens fabricados (a parte desta sessão)
- cada linha de log e cada ficheiro guardado de estatísticas, conquistas e jogador inteiros no heat.raw.parquet

## De onde vem {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (acompanhado), saves\\&lt;mundo>\stats\\&lt;uuid>.json e saves\\&lt;mundo>\playerdata\\&lt;uuid>.dat e level.dat (NBT compactado em gzip), lidos quando o jogo os guarda

## Como ligar {#how-to-switch-it-on}

Não é preciso ligar nada: o watcher lê a fonte como o jogo ou a plataforma a disponibiliza.

## Como funciona {#how-it-works}

Minecraft (Edição Java): o log, as estatísticas e os ficheiros de jogador que o jogo escreve.

Onde (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - o log do jogo, novo a cada inicialização (o antigo é compactado num .log.gz com data). Linhas `[hh:mm:ss] [thread/NÍVEL]: mensagem` (os carregadores de mods escrevem `[ddMMMyyyy hh:mm:ss.mmm] [thread/NÍVEL] [logger/]: ...`). O que os jogadores veem no chat está nele: entradas e saídas, mensagens de morte, conquistas, chat - o servidor integrado de um mundo para um jogador escreve as mesmas linhas mais uma vez, então uma linha repetida no mesmo segundo conta uma vez. "Setting user: <nome>" nomeia o jogador; a linha "<nome>[...] logged in with entity id N at (x, y, z)" do servidor diz onde ele apareceu.
* `saves\<mundo>\stats\<uuid>.json` - o ecrã de estatísticas, escrita quando o mundo é guardado (gravação automática a cada poucos minutos, e ao sair): `stats` -> `minecraft:custom` (play_time em ticks, mob_kills, distâncias `*_one_cm`, jump, ...), `minecraft:mined`, `minecraft:crafted`, ... Totais do mundo; os números da sessão são a diferença em relação ao que o ficheiro dizia quando o jogo começou. Formato: <https://minecraft.wiki/w/Statistics>
* `saves\<mundo>\playerdata\<uuid>.dat` (e `level.dat` -> Data -> Player para um host de um jogador) - NBT compactado em gzip, escrito nas mesmas `saves`: `Pos` [x, y, z] como doubles, `Rotation` [yaw, pitch], `Dimension` ("minecraft:overworld"; um int 0/-1/1 antes da 1.16). NBT conforme <https://minecraft.wiki/w/NBT_format> - lido aqui por um pequeno leitor próprio.
* `saves\<mundo>\advancements\<uuid>.json` - o progresso do ecrã de conquistas, escrito nas mesmas `saves`.

As coordenadas são blocos, um bloco por metro, y para cima; x a leste, z ao sul - um quadro destro, desenhado como ele é. As posições só vêm quando o mundo é guardado, então um trajeto são alguns pontos por gravação automática, não um rasto contínuo; a dimensão é a `session`, então o Nether não é desenhado sobre o Overworld.

Tudo o que é lido é guardado inteiro no ficheiro auxiliar bruto da sessão (regra do conversor do 3DHeat): cada linha do latest.log sob o seu nível (`INFO`, `WARN`, `ERROR`, ...; uma linha sem o cabeçalho entre colchetes, como um rastro de pilha, como `untagged`), e cada ficheiro guardado sob o tipo dele (`stats`, `advancements`, `playerdata`, `level.dat`) - JSON como texto, NBT como bytes. Os números de um ficheiro de estatísticas só são entendidos em relação ao que ele dizia quando o jogo começou, então essa primeira cópia também é guardada (`baseline`), na primeira vez que o ficheiro muda.

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | blocos (1 bloco = 1 m) |
| Espelhado para o visualizador | nenhum |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `log`: lê só o que o jogo ou a plataforma entrega (ficheiros que o jogo escreve enquanto corre), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- latest.log: o nome do jogador (`Setting user`), entradas com posição, entradas, saídas, mortes com a mensagem de morte, conquistas, linhas de chat, o servidor a parar
- stats/<uuid>.json: tempo de jogo, distância, abates de mobs e de jogadores, pulos, dano causado e sofrido, blocos minerados, itens fabricados - a parte desta sessão
- playerdata/<uuid>.dat e level.dat (NBT): posição, dimensão, yaw, pitch, vida, nível de XP

**Guardado bruto**

- cada linha do latest.log inteira, `type` = o seu nível (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`), com a thread do logger em `thread`, `used` onde passou a linha; uma linha sem o cabeçalho entre colchetes (um rastro de pilha, o banner de um mod) como `untagged`
- cada stats/<uuid>.json inteiro como texto, `type` `stats` (`used`: os números dele estão nas estatísticas), com a primeira cópia do início do jogo como `baseline`
- cada advancements/<uuid>.json inteiro como texto, `type` `advancements` (cada critério e quando foi cumprido; ainda não transformados em linhas)
- cada playerdata/<uuid>.dat e level.dat inteiros como bytes (NBT em gzip), `type` `playerdata` / `level.dat`, `used` onde deram uma posição: inventário, baú do ender, efeitos, ponto de spawn, regras do jogo, semente do mundo e hora estão só aqui
- todo ficheiro guardado tem `world` e `file` (o seu caminho dentro de `saves`)

**Não disponível**

- um rastro de posições: o jogo escreve a posição do jogador só quando o mundo é guardado (a cada poucos minutos e ao sair)
- posições num servidor que outra pessoa hospeda: os ficheiros do mundo dele estão no servidor, não aqui; só o log é lido nesse caso
- o próprio mundo (ficheiros de região .mca, entidades, mapas e raides em data/\*.dat): grande, e é o terreno, não a partida
- logs de sessões anteriores (logs/\*.log.gz): guardados quando foram jogados
- Minecraft Bedrock Edition: não escreve esse log nem esses ficheiros

**Tamanho**: latest.log 0,1-2 MB por hora (mais com mods); um ficheiro de estatísticas 5-50 KB e um ficheiro de jogador 5-100 KB por gravação automática, level.dat 1-20 KB - cerca de 1-5 MB por hora no total; o zstd no heat.raw.parquet deixa o texto em cerca de um décimo (os ficheiros NBT já vêm em gzip)

## Verificado {#verified}

testado com linhas de log sintéticas, JSON de estatísticas e ficheiros NBT montados a partir dos formatos publicados; sem teste contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
