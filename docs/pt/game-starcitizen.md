---
title: "Star Citizen (ficheiros de log)"
nav_order: 42
lang: "pt"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (ficheiros de log) {#star-citizen-log-files}

Enquanto se joga Star Citizen, o watcher lê os ficheiros que o jogo escreve e guarda o que aconteceu, para se poder ver depois como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `starcitizen`, tipo [`log`](sources-and-rules.md); ele corre enquanto `StarCitizen.exe` está em execução e procura novos dados a cada 0,5 s.*

## O que é gravado {#what-is-recorded}

- mortes, com vítima, assassino, arma, tipo de dano e zona (jogadores e NPCs)
- veículos desativados e destruídos, com piloto, causa e zona
- alvos de viagem quântica, mudanças de sistema solar, surgimentos, reaparecimentos, incapacitações
- cada linha do Game.log, inteira, no heat.raw.parquet
- abates (de jogadores e de NPCs), mortes, suicídios, veículos destruídos e perdidos, saltos quânticos

## De onde vêm os dados {#where-it-comes-from}

&lt;instalação>\StarCitizen\LIVE\Game.log (a pasta de build do StarCitizen.exe em execução), apenas o ficheiro de log que o jogo escreve — um jogo com Easy Anti-Cheat: nada toca no processo dele

## Como ativar {#how-to-switch-it-on}

Nada precisa ser ligado: o watcher lê a fonte da forma que o jogo ou a plataforma a disponibiliza.

## Como funciona {#how-it-works}

Star Citizen: o log do próprio cliente, `<instalação>\StarCitizen\LIVE\Game.log`.

O jogo escreve o Game.log do zero a cada arranque (o anterior vai para `logbackups\`). Só esse ficheiro é lido: o Star Citizen corre o Easy Anti-Cheat, e nada daqui chega perto do processo do jogo. As linhas começam com uma hora UTC e um nível, depois uma tag entre colchetes angulares:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(quebrado aqui por causa da largura; uma linha por entrada no ficheiro). A zona de uma morte costuma ser a nave em que a vítima estava, não um lugar. O formato não é documentado pela Cloud Imperium e muda entre patches; os padrões seguem as linhas que rastreadores de abates da comunidade leem (por exemplo <https://github.com/DimmaDont/all-slain>, MIT — só factos), e o que não casa é ignorado, não adivinhado. A `pos` de um veículo é relativa à zona e é guardada só como texto: nenhuma coordenada é desenhada.

Cada linha é guardada inteira no ficheiro bruto anexo da sessão (regra do conversor do 3DHeat), tenha casado ou não: `type` é a tag da linha entre colchetes angulares (`Actor Death`, `Spawn Flow`, ...), senão a sua primeira palavra entre colchetes (`Notice`, `CSessionManager::OnClientSpawned`), senão `untagged`; uma linha sem carimbo de hora é `untimed`.

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

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- `<Actor Death>`: vítima, assassino, arma e a sua classe, tipo de dano, zona; NPC ou jogador
- `<Vehicle Destruction>`: veículo, zona, posição relativa à zona como texto, piloto, causa, modo, nível de destruição
- alvos de `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, reaparecimentos no hospital, incapacitações com as suas causas, `EndSession`
- o identificador do jogador a partir de `<AccountLoginCharacterStatus_Character>` ou da linha de login

**Mantido bruto**

- cada linha do Game.log inteira, `type` = a sua tag entre colchetes angulares (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), senão a sua primeira palavra entre colchetes (`Notice`, `CSessionManager::OnClientSpawned`, ...), senão `untagged`; linhas sem carimbo de hora (o cabeçalho do log, texto quebrado) como `untimed`; `used` onde a linha passou a ser uma linha de dados

**Não disponível**

- posições: o log não dá nenhuma num quadro que possa ser desenhado (a `pos` de um veículo destruído é relativa a uma zona cujo lugar não é registado)
- qualquer coisa do processo ou da rede do jogo: o Star Citizen corre o Easy Anti-Cheat; só o ficheiro de log é lido
- logs de inícios anteriores (`logbackups`): o Game.log de cada início é guardado quando é jogado
- linhas num formato que um patch muda: guardadas brutas, decodificadas de novo quando a nova forma for conhecida

**Tamanho**: o Game.log cresce cerca de 5 a 15 MB por hora de jogo (mais em áreas movimentadas e com erros); o zstd no heat.raw.parquet deixa cerca de um décimo

## Verificado {#verified}

testado com linhas sintéticas de Game.log no formato que os rastreadores da comunidade documentam; não testado contra o jogo

## Fonte {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
