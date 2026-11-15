---
title: "EVE Online (ficheiros de log)"
nav_order: 20
lang: "pt"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (ficheiros de log) {#eve-online-log-files}

Enquanto se joga EVE Online, o watcher lê os ficheiros que o jogo escreve e guarda o que aconteceu, para se poder ver depois como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `eve`, tipo [`log`](sources-and-rules.md); ele corre enquanto `exefile.exe` está em execução e procura novos dados a cada 0,5 s.*

## O que é gravado {#what-is-recorded}

- dano causado e recebido com a outra nave, o piloto, a sigla da corporação, a arma e a qualidade do acerto
- tiros errados causados e recebidos
- recompensas de caçada pagas (abates de NPC) com ISK
- saltos entre sistemas
- cada linha de gamelog e de chat, inteira, no heat.raw.parquet
- dano causado e recebido, acertos, erros, abates com recompensa e ISK, saltos

## De onde vêm os dados {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt e os Chatlogs\\\*.txt ao lado deles (cada ficheiro escrito desde que o cliente foi iniciado)

## Como ativar {#how-to-switch-it-on}

Nada precisa ser ligado: o watcher lê a fonte da forma que o jogo ou a plataforma a disponibiliza.

## Como funciona {#how-it-works}

EVE Online: os logs de jogo do cliente, `Documents\EVE\logs\Gamelogs\*.txt`.

O cliente escreve um ficheiro por personagem a cada login, `<yyyymmdd>_<hhmmss>[_<id do personagem>].txt`; o registo em ficheiro vem ativado por predefinição. Vários clientes abertos ao mesmo tempo escrevem cada um o seu, então cada ficheiro escrito desde que o jogo começou é acompanhado. Cabeçalho e linhas (a hora do EVE é UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(a linha de combate é uma linha só no ficheiro). As tags de formatação são removidas antes da comparação. O ficheiro foi UTF-8 e UTF-16 ao longo dos anos; os dois são lidos.
O formato não é documentado pela CCP; é o log de texto simples do cliente, lido como ferramentas comunitárias de log de combate o leem (por exemplo <https://docs.rs/crate/eve-log-parser>). Sem posições.

Ao lado, `Documents\EVE\logs\Chatlogs\<canal>_<yyyymmdd>_<hhmmss>[_<id>].txt`: um ficheiro por canal de chat a cada login (quando o registo de chat está ligado, o padrão do cliente), em UTF-16, com um cabeçalho que nomeia o canal e o listener, depois `[ yyyy.mm.dd hh:mm:ss ] Remetente > mensagem`.

Cada linha dos dois tipos é guardada inteira no ficheiro bruto anexo da sessão (regra do conversor do 3DHeat): uma linha de gamelog sob o seu canal entre colchetes (`combat`, `notify`, `bounty`, `None`, ...), uma linha de chat como `chat` com o seu canal, e as linhas de cabeçalho como `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- acertos de dano causados e recebidos no gamelog `(combat)` (quantidade, outro piloto, sigla da corporação, nave, arma, qualidade do acerto) e os erros nos dois sentidos
- pagamentos de recompensa `(bounty)` com ISK, e as linhas `Jumping from A to B`
- o Listener do cabeçalho do gamelog: de quem é aquele log

**Mantido bruto**

- cada linha de gamelog inteira, `type` = o seu canal entre colchetes (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), com `file` e `listener`; `used` onde passou a linha; as linhas de cabeçalho como `gamelog header`
- cada linha de chat inteira (Local, corporação, frota, canais privados, os avisos `EVE System`, como a mudança de canal Local ao saltar), `type` `chat`, com `channel`, `listener` e `file`; as linhas de cabeçalho como `chatlog header`. Ainda não passaram a linhas
- as tags de formatação (`<color>`, `<b>`, `<font>`) ficam no texto bruto; nas linhas elas são removidas

**Não disponível**

- posições: o cliente não as escreve nos logs
- combates de outros pilotos: um gamelog é do próprio listener
- logs de logins anteriores: cada login escreve ficheiros novos; os mais antigos que esta execução do cliente não são lidos de novo
- chat quando o jogador desligou o registo de chat nas configurações do cliente
- os ficheiros de cache e de configuração do cliente: não são logs, e não são documentados

**Tamanho**: um gamelog tem 0,1 a 2 MB por hora (a maior parte em combate); os logs de chat dependem dos canais abertos: um canal Local ou de frota movimentado, 0,5 a 3 MB por hora; o zstd no heat.raw.parquet deixa cerca de um décimo

## Verificado {#verified}

testado com linhas de gamelog sintéticas no formato publicado por analisadores comunitários; não testado contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
