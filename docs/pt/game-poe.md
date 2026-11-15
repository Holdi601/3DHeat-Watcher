---
title: "Path of Exile (ficheiros de log)"
nav_order: 36
lang: "pt"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (ficheiros de log) {#path-of-exile-log-files}

Enquanto se joga Path of Exile, o watcher lê os ficheiros que o jogo escreve e guarda o que aconteceu, para se poder ver depois como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `poe`, tipo [`log`](sources-and-rules.md); ele corre enquanto `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` ou `PathOfExile_x64_KG.exe` está em execução e procura novos dados a cada 0,5 s.*

## O que é gravado {#what-is-recorded}

- zonas em que o jogador entra, com o nível da área, o id da área e a sua semente
- subidas de nível, com a classe e o nível
- mortes ("has been slain")
- jogadores que entram e saem da área, sussurros recebidos e enviados, pedidos de troca, trocas aceitas
- cada linha do Client.txt desta sessão, inteira, no heat.raw.parquet
- mortes, níveis ganhos, nível máximo, zonas visitadas, zonas distintas, sussurros, pedidos de troca, trocas

## De onde vêm os dados {#where-it-comes-from}

&lt;instalação>\logs\Client.txt do Path of Exile ou do Path of Exile 2 (acompanhado; a pasta de instalação é a do executável em execução)

## Como ativar {#how-to-switch-it-on}

Nada precisa ser ligado: o watcher lê a fonte da forma que o jogo ou a plataforma a disponibiliza.

## Como funciona {#how-it-works}

Path of Exile e Path of Exile 2: o log do cliente, `<instalação>\logs\Client.txt`.

Os dois jogos acrescentam a um mesmo Client.txt na pasta de instalação enquanto estiverem instalados (ele cresce entre as execuções). As linhas têm este aspeto:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- hora local, um contador de milissegundos, um hash, o nível e a thread, depois o que a janela de chat mostra. As mensagens são as do cliente em inglês; um cliente noutro idioma as escreve traduzidas e não é entendido aqui. Nada dá uma posição. O formato não é documentado pela Grinding Gear Games; é o log de texto simples do jogo, como ferramentas da comunidade (assistentes de troca, guias de nível) o leem há anos — por exemplo <https://github.com/klayveR/poe-log-monitor> (MIT) para a lista de eventos.

A pasta de instalação é a do executável em execução; sem um, são procuradas as bibliotecas da Steam e a pasta predefinida do cliente independente.

Cada linha desta sessão é guardada inteira no ficheiro bruto anexo da sessão (regra do conversor do 3DHeat), tenha ou não um significado aqui: `type` é o nível e o registador entre colchetes (`INFO Client`, `DEBUG Client`, `WARN Client`, ...); uma linha com carimbo mas sem colchetes é `untagged`; uma linha sem carimbo de hora é `untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- `You have entered <zona>`, com o nível da área, o id da área e a semente da linha `Generating level` que vem antes
- `<nome> (<classe>) is now level <n>`, `<nome> has been slain`, jogadores que entram e saem da área, sussurros recebidos e enviados (com a marcação de se são um pedido de troca), trocas aceitas e canceladas

**Mantido bruto**

- cada linha desta sessão inteira, `type` = o nível e o registador entre colchetes (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` onde passou a linha: chat global, de troca, de grupo e de guilda, `Connecting to instance server`, avisos de AFK e DND, as respostas a comandos de chat como `/played` e `/deaths`, as linhas de carregamento e de motor do cliente — guardadas, ainda não transformadas em linhas
- uma linha com carimbo mas sem colchetes (`***** LOG FILE OPENING *****`) como `untagged`, uma linha sem carimbo de hora como `untimed`

**Não disponível**

- posições: nada no log dá uma
- o que um cliente noutro idioma escreve: as linhas são guardadas, mas só as mensagens em inglês passam a linhas
- linhas de execuções anteriores: o Client.txt cresce entre as execuções; linhas com carimbo anterior a esta execução do jogo ficam de fora (foram guardadas quando foram jogadas)
- abates, dano, saques e a árvore de passivas: o jogo não os regista no log

**Tamanho**: o Client.txt cresce cerca de 0,3 a 3 MB por hora (a maior parte vem de linhas DEBUG ao carregar áreas; mais com chat de troca movimentado); o zstd no heat.raw.parquet deixa cerca de um décimo

## Verificado {#verified}

testado com linhas sintéticas de Client.txt no formato do jogo; não testado contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
