---
title: "Elite Dangerous (ficheiros de log)"
nav_order: 18
lang: "pt"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (ficheiros de log) {#elite-dangerous-log-files}

Enquanto se joga Elite Dangerous, o watcher lê os ficheiros que o jogo escreve e guarda o que aconteceu, para que se possa ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `elite`, tipo [`log`](sources-and-rules.md); corre enquanto `EliteDangerous64.exe` estiver em execução e procura dados novos a cada 0,25 s.*

## O que é gravado {#what-is-recorded}

- cada evento do diário de bordo, sob o nome dele no diário, com os campos simples dele
- posição na galáxia (StarPos, anos-luz) em saltos, locais, aparições, mortes, atracagens, pousos
- aparição em LoadGame/Resurrect, morte em Died, atracado/desatracado, toque no solo/decolagem, salto, session_end
- rota na superfície de um planeta a partir do Status.json: latitude, longitude, altitude, rumo, e metros num plano tangente por corpo (sessão = nome do corpo), com os outros campos simples do Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- cada linha do diário e cada ficheiro de apoio inteiros no heat.raw.parquet
- saltos, distância percorrida em saltos, mortes, abates, créditos ganhos, missões concluídas, corpos escaneados, sistemas visitados, atracagens, pousos

## De onde vem {#where-it-comes-from}

Diário do jogador %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (o ficheiro mais novo, acompanhado enquanto é escrito), Status.json e os outros ficheiros de apoio \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) na mesma pasta

## Como ligar {#how-to-switch-it-on}

Não é preciso ligar nada: o watcher lê a fonte como o jogo ou a plataforma a disponibiliza.

## Como funciona {#how-it-works}

Elite Dangerous: o Diário do Jogador e o Status.json que o jogo escreve enquanto corre.

Onde: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<parte>.log` - uma linha JSON por linha, um ficheiro por inicialização do jogo (uma sessão longa continua na parte .02, .03 ...). Cada linha tem `timestamp` (UTC, ISO 8601) e `event`. As posições galácticas são o `StarPos` [x, y, z] do sistema, em anos-luz a partir do Sol, em `FSDJump`, `Location` e `CarrierJump`. O quadro galáctico do Elite tem y para cima (em direção ao norte galáctico), z em direção ao centro da galáxia e x em direção à longitude galáctica 270 - um quadro canhoto, então o visualizador espelha z para desenhá-lo da forma certa.
* `Status.json` - reescrito inteiro sempre que o estado da nave muda: `Flags`, e perto de um planeta `Latitude`, `Longitude` (graus), `Altitude` (metros), `Heading`, `BodyName` e `PlanetRadius` (metros).
* Os outros ficheiros de apoio, cada um reescrito inteiro quando o evento correspondente do diário é escrito: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Cada `*.json` da pasta que o jogo escreve nesta sessão é guardado inteiro a cada mudança (regra do conversor do 3DHeat: o que a fonte tem é lido ou guardado), sob o nome do ficheiro.

Cada linha do diário é guardada inteira no ficheiro auxiliar bruto da sessão sob o `event` dele, cada ficheiro de apoio sob o nome dele; uma linha que não é JSON fica sob `unparsed`.

As posições de superfície entram num plano tangente local por corpo, em metros: a primeira leitura num corpo é a sua origem, x a leste, z ao norte, y para cima (altitude), com a mesma lateralidade do quadro galáctico; e as linhas trazem o nome do corpo como `session`, para que uma viagem de carro ou uma caminhada sobre um planeta seja desenhada como um trajeto próprio. As linhas galácticas têm a sessão "galaxy". As duas escalas ficam numa só tabela; escolha a sessão no visualizador.

Formato: o manual "Elite Dangerous Player Journal" da Frontier (publicado a cada atualização nos fóruns oficiais, <https://forums.frontier.co.uk/> - "Journal Manual", v4.x), com eventos e campos como documentados ali; as flags do Status.json seguem o capítulo "Status File" do mesmo manual.

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | anos-luz (linhas galácticas, sessão 'galaxy'); metros a leste/acima/ao norte da primeira leitura num corpo (linhas de superfície, sessão = nome do corpo) |
| Espelhado para o visualizador | `z` |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `log`: lê só o que o jogo ou a plataforma entrega (ficheiros que o jogo escreve enquanto corre), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- cada linha do diário como uma linha sob o `event` dele, com os campos simples dele (o texto localizado quando o jogo o dá; textos com mais de 300 caracteres cortados na linha)
- linhas galácticas (StarPos) em FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; linhas de superfície a partir do Status.json e de Touchdown/Liftoff
- os campos simples do Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) nas linhas de superfície
- as estatísticas: saltos, distância, mortes, abates, créditos ganhos, missões, corpos escaneados, sistemas visitados, atracagens, pousos

**Guardado bruto**

- cada linha do diário inteira, `type` = o seu `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` verdadeiro: as listas e objetos que as linhas deixam de fora (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) só estão aqui
- uma linha do diário que não é JSON, `type` `unparsed`
- cada ficheiro de apoio inteiro a cada vez que o jogo o reescreve, `type` = o nome do ficheiro: `Status.json` (`used` quando gerou uma linha de superfície), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, e qualquer outro `*.json` que o jogo escrever ali

**Não disponível**

- a posição entre saltos (dentro de um sistema, em supercruzeiro ou no espaço normal): o jogo escreve só o StarPos do sistema e, perto de um planeta, latitude, longitude e altitude
- as posições de outras naves e de outros jogadores: o diário é o relato do próprio comandante
- velocidade, acelerador e outros dados de voo: o jogo não os escreve
- diários e ficheiros de apoio de sessões anteriores: guardados quando foram jogados (o acompanhador começa no fim de um ficheiro mais antigo que esta execução do jogo)
- a API web de apoio da Frontier (cAPI): precisa do login Frontier do jogador; não é um ficheiro que o jogo escreve

**Tamanho**: cerca de 1-5 MB de texto bruto por hora: o diário 0,2-2 MB, o Status.json (menos de 1 KB, reescrito até a cada segundo) 1-2 MB, um conjunto market/outfitting/shipyard 20-150 KB por estação visitada; o zstd no heat.raw.parquet deixa cerca de um décimo

## Verificado {#verified}

leitor do diário reproduzido sobre ficheiros reais de diário de uma instalação local (as contagens de eventos batem com as estatísticas); as correções de superfície do Status.json testadas só com instantâneos sintéticos

## Fonte {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
