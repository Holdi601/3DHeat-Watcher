---
title: "League of Legends (repetições)"
nav_order: 30
lang: "pt"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (repetições) {#league-of-legends-replays}

Depois de uma partida de League of Legends, o watcher transforma a repetição guardada pelo jogo em ficheiros que se podem ver num mapa no visualizador 3DHeat.

*Detalhes técnicos: adaptador `lol-replays`, tipo [`replay`](sources-and-rules.md); corre o tempo todo (não espera um jogo começar) e procura dados novos a cada 5 s.*

## O que é gravado {#what-is-recorded}

- o campeão, a função, a equipa, abates, mortes, assistências, ouro, dano a campeões e resultado de cada jogador, e todo outro número da tabela de fim de jogo
- a própria linha como estatísticas, e as linhas do jogador marcadas como dele (`player` no meta.json), com o Riot ID definido nas configurações
- com a própria chave de API da Riot: a posição de cada jogador a cada minuto, com as estatísticas do minuto, e cada evento da linha do tempo (abates onde aconteceram, construções, monstros, wards, itens, habilidades), no horário de relógio que a linha do tempo informa
- cada parte do ficheiro de repetição guardada inteira no heat.raw.parquet; não decodificado: o jogo momento a momento, que é cifrado e ofuscado contra trapaças

## De onde vem {#where-it-comes-from}

repetições que o cliente do League guarda: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (só os metadados simples do fim de jogo); com a própria chave de API da Riot, a linha do tempo oficial da partida pela Match-V5 API da Riot

## Como ligar {#how-to-switch-it-on}

guarde uma repetição no cliente do League (histórico de partidas > transferir); para posições, defina riot_api_key e riot_platform com `config --set`

## Como funciona {#how-it-works}

League of Legends e VALORANT (repetições): o que delas pode ser lido como está.

Os dois jogos guardam repetições no disco do jogador, e os dois protegem o que está dentro: os dados do jogo momento a momento são ofuscados, e de forma diferente a cada atualização, para impedir que sejam usados para trapacear. Vencer isso significa desmontar o código do próprio jogo, o que os termos da Riot proíbem (Termos de Serviço 3.1 e 7.1) - então isso não é feito aqui. O que cada ficheiro traz às claras é lido, e o resto é guardado como está: cada parte do ficheiro, inteira, no `heat.raw.parquet` da sessão (regra do conversor do 3DHeat, docs/converters.md no repositório do visualizador), contada no `selfCheck.completeness` do meta.json.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. As duas versões do contêiner trazem a tabela de fim de jogo como JSON simples (`statsJson`): para cada um dos dez jogadores, o campeão, abates, mortes, assistências, ouro, dano a campeões, itens, equipa, função, vitória, o Riot ID dele, e cada outro número que o jogo totaliza (mais de cem por jogador); todos passam a ser a linha `player_result` do jogador. O ROFL1 (patch 14.9 e anteriores) o tem depois de um cabeçalho fixo (`RIOT\0\0`, uma assinatura de 256 bytes, depois os tamanhos); o ROFL2 (14.11 em diante, `RIOT\2\0`) no fim do ficheiro, com o tamanho nos últimos quatro bytes (informado por um engenheiro da Riot, ReplayBook issue 299). O cabeçalho da carga do ROFL1 (id do jogo, tamanho, contagens de blocos e de quadros-chave, o tamanho da chave do bloco) e a tabela de blocos dele (id, tipo, tamanho, próximo bloco, deslocamento) estão às claras e são lidos; os blocos em si são cifrados, e guardados inteiros sem leitura. Layouts do roflxd.cs (MIT).

As posições não vêm do ficheiro. Com uma chave de programador da Riot do próprio jogador (`riot_api_key` nas configurações; uma chave pessoal serve exatamente para isto, "mostrar estatísticas do próprio jogador (self)"), a linha do tempo oficial da partida é obtida da Match-V5 API da Riot: a posição de cada jogador uma vez por minuto com tudo o que o quadro do minuto diz sobre ele (ouro, experiência, nível, lacaios, estatísticas de campeão e de dano), e cada evento da linha do tempo - abates, construções, monstros de elite, wards, itens, habilidades, níveis - como uma linha, onde aconteceu quando tem um lugar. Sem uma chave, nada é obtido e nada é enviado.

Também serve este módulo: [VALORANT (repetições)](game-valorant-replays.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | unidades do mapa Summoner's Rift (cerca de 15000 de lado a lado) |
| Espelhado para o visualizador | nenhum |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `replay`: lê só o que o jogo ou a plataforma entrega (repetições e demos que o jogo guarda), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- o JSON de metadados: duração do jogo, versão, ids do último bloco e do quadro-chave, e `statsJson` - cada campo da tabela de cada jogador na linha `player_result` dele (números dados como texto são lidos como números)
- ROFL1: o bloco de tamanhos, o cabeçalho da carga (id do jogo, duração, contagens de quadros-chave e de blocos, ids dos blocos de início e de começo do jogo, intervalo de quadro-chave, a chave do bloco como está guardada) e a tabela de blocos (id, tipo, tamanho, próximo bloco, deslocamento) - em `rofl` no meta.json e no `text` das linhas brutas
- ROFL2: a string de versão
- a linha do tempo da Match-V5 (só com a própria chave de API): cada quadro de participante numa linha `position` (ou `participant_frame` sem lugar), com todos os seus campos achatados (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); cada evento como uma linha com o nome do tipo, colocada onde tem uma `position`; CHAMPION_KILL como abate e morte

**Guardado bruto**

- cada parte do .rofl, inteira, na ordem do ficheiro (`offset`), para que as partes sejam o ficheiro: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); qualquer trecho que nenhuma parte cubra como `unknown`
- a linha do tempo inteira: `timeline <tipo>` para cada evento, `timeline participantFrame` para o quadro de cada jogador (`participant` o id dele), `timeline` para o resto

**Não disponível**

- o próprio jogo (posições, habilidades, cada unidade, momento a momento): os blocos do ROFL1 e o corpo do ROFL2 são cifrados, e os pacotes internos são ofuscados a cada atualização; passar por isso significa desmontar o cliente, o que os termos da Riot proíbem (3.1, 7.1). Guardado inteiro, não lido
- posições sem a própria chave de API da Riot: o ficheiro não as tem às claras

**Tamanho**: o ficheiro bruto tem cerca do tamanho da própria repetição: os blocos cifrados não comprimem

## Verificado {#verified}

o leitor de metadados testado com ficheiros montados segundo os layouts do roflxd.cs (MIT); a linha do tempo, com o JSON documentado da Match-V5; nenhuma repetição real estava disponível para verificar

## Fonte {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
