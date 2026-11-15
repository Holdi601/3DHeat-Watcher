---
title: "Dota 2 (replays)"
nav_order: 12
lang: "pt"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replays) {#dota-2-replays}

Depois de uma partida de Dota 2, o watcher transforma o replay que o jogo guardou em ficheiros que se podem ver num mapa no visualizador do 3DHeat.

*Detalhes técnicos: adaptador `dota-replays`, tipo [`replay`](sources-and-rules.md); ele corre o tempo todo (não espera um jogo começar) e procura dados novos a cada 5 s.*

## O que é gravado {#what-is-recorded}

- a posição, a altura, a vida e o nível de cada herói, 7,5 vezes por segundo enquanto vivo
- abates e mortes onde aconteceram; torres, quartéis, Roshan e Tormentors onde caíram; wards onde foram plantadas
- as marcações no mapa (pings), os desenhos no mapa e as ordens (mover, atacar, usar habilidade, comprar, ...) de cada jogador, onde apontavam
- o placar e a linha de cada jogador; a do jogador conectado, como estatísticas
- tudo o mais que o replay contém, guardado por inteiro ao lado da tabela: cada quadro e mensagem de rede, cada mudança de propriedade de entidade, cada entrada de tabela de strings

## De onde vem {#where-it-comes-from}

replays que o Dota 2 guarda: &lt;Dota>/game/dota/replays/&lt;id da partida>.dem (transferidos no cliente, ou com `dota-replay <id da partida>`)

## Como ligar {#how-to-switch-it-on}

transfira o replay de uma partida no Dota 2, ou busque um público: `python -m heat3d_watch dota-replay <id da partida>`; precisa de `pip install gem-dota`

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz o motivo; [Instalação e execução](installing-and-running.md) explica as causas mais comuns.

## Como funciona {#how-it-works}

Replays e demos: o que um jogo guarda de uma partida, convertido quando a partida termina.

Um replay guarda tudo o que uma interface ao vivo esconde em jogos multijogador - a posição de cada jogador, cada abate onde aconteceu - e é um ficheiro que o jogo grava para os jogadores, então lê-lo não toca em nada do jogo. O watcher observa as pastas em que os jogos os guardam, espera até que um ficheiro novo pare de crescer (senão o jogo ainda estaria a escrever), e o converte numa thread de trabalho, de modo que uma conversão longa nunca bloqueia o resto do watcher.

Na primeira vez que uma pasta é vista, os replays que já estão nela apenas são registados, não convertidos: um jogador com anos de demos veria o watcher ocupado por um dia inteiro. `python -m heat3d_watch replays <adaptador> [pasta]` converte os existentes sob pedido.

#### Dota 2 {#dota-2}

O Dota 2 guarda os replays que o jogador transfere (os detalhes de uma partida, ou Assistir > Replays) em `<Dota>/game/dota/replays/<id da partida>.dem`; a Valve mantém o replay de cada partida pública nos servidores dela por algumas semanas, e `python -m heat3d_watch dota-replay <id da partida>` busca um pelo id, via OpenDota. Cada um é lido com o gem (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) num processo próprio (`heat3d_watch/decoders/dota_replay.py`): posição, altura, vida, nível, direção, mana, experiência, atributos e itens de cada herói 7,5 vezes por segundo enquanto vivo; abates e mortes onde aconteceram; torres, quartéis, Roshan e Tormentors onde caíram; cada ward onde foi plantada e onde terminou; as entradas do log de combate sobre os heróis (dano, curas, habilidades, itens, compras, runas, ouro, experiência, modificadores); e as marcações, os desenhos e as ordens de cada jogador - em `dota/<partida>.parquet`; cada outra unidade (criaturas, invocações, ilusões, couriers, construções) a cada segundo em `<partida>.units.parquet`; o log de combate inteiro em `<partida>.combatlog.parquet`; e a partida, o chat, a escolha de heróis, tudo o mais que o parser extrai e o registo de fim de partida do próprio jogo em `<partida>.match.json`, na pasta da sessão. Tudo o mais que o replay contém é guardado por inteiro ao lado deles (regra de conversores do 3DHeat): cada quadro e mensagem de rede em `<partida>.packets.parquet`, cada mudança de propriedade de entidade em `<partida>.entities.parquet`, cada entrada de tabela de strings em `<partida>.strings.parquet`, contados em `selfCheck.completeness` do documento da partida. As posições são as unidades do mundo do Dota, as mesmas que a integração de estado do jogo informa. A linha do placar do jogador conectado passa a ser as estatísticas da sessão: abates, mortes, assistências, last hits, denies, património líquido, GPM, XPM, dano em heróis, wards, e se a partida foi vencida. Um novo patch do Dota pode mudar as entidades do replay antes que o gem as acompanhe; um replay que o gem não consegue ler até o fim é convertido até onde dá e marcado como `incomplete` no seu resumo.

O mesmo módulo também serve: [Counter-Strike 2 (replays)](game-cs2-demos.md), [osu! (replays)](game-osu-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `z` |
| Unidades | unidades do mundo do Dota (unidades do Hammer; o mapa tem cerca de 16400 de lado a lado) |
| Espelhado para o visualizador | `y` |
| Escala das unidades (`scale`: o visualizador multiplica as posições por ele) | 1 |

Isso vai para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`, de modo que o visualizador do 3DHeat gira e ajusta as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `replay`: ele lê apenas o que o jogo ou a plataforma entrega (replays e demos que o jogo guarda), por isso grava também em partidas online, e não só offline; a marcação só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem a memória, e nunca num jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O conversor segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que o replay contém é lido ou guardado, nunca descartado. Além da tabela, tudo o que o replay contém é guardado por inteiro em ficheiros auxiliares ao lado dela, na pasta `dota/` da sessão - `<partida>.packets.parquet`, `<partida>.entities.parquet`, `<partida>.strings.parquet` (colunas `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, conforme se apliquem) - e o `selfCheck.completeness` do documento da partida (`<partida>.match.json`) conta cada `type` - `lost` é 0.

**Lido**

- a tabela (`dota/<partida>.parquet`): posição, altura, vida, nível, direção, mana, experiência, atributos, armadura, velocidade, dano, itens e o cursor do jogador de cada herói, 7,5 vezes por segundo; abates, mortes, objetivos, wards, as entradas do log de combate sobre os heróis; marcações no mapa (`ping`, DOTA_UM_LocationPing), desenhos no mapa (`map_line`, DOTA_UM_MapLine) e cada ordem de unidade (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` o tipo da ordem, `value` o id da habilidade ou do item, `text` a classe do alvo; no ponto da ordem, senão no herói)
- `<partida>.units.parquet`: cada outra unidade a cada segundo; `<partida>.combatlog.parquet`: o log de combate inteiro, como o gem o lê, com todos os campos
- o documento da partida: tudo o que o gem extrai, e por inteiro os registos do próprio replay - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: duração da reprodução, nome, herói, id da Steam e equipa de cada jogador), `matchDetails` (DOTA_UM_MatchDetails: o placar de fim de partida do coordenador do jogo, os números de cada jogador, itens, dano por tipo, escolhas e banimentos) e `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: abates, mortes, assistências, nível, last hits e denies como lidos do fluxo, comparados com `matchDetails`, por jogador

**Guardado bruto**

- `<partida>.packets.parquet`: cada quadro que não é um pacote (`type` `frame <n>`) e cada mensagem de rede (`message <n>`, `name` o nome dado pela Valve), por inteiro em `payload`, na ordem do ficheiro (`seq`, `frame`), com `decoded` o protobuf como JSON (um campo de bytes aparece como o tamanho dele); cada tipo de mensagem decodificado: svc_PacketEntities (o fluxo de entidades), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, as mensagens do log de combate, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projéteis, animações, sangue), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; as tabelas de envio, a lista de classes e as informações do servidor que um decodificador de entidades posterior precisa estão entre elas
- `<partida>.entities.parquet`: cada propriedade de cada entidade cada vez que mudou (`type` a propriedade, `name` a classe, `entity` o índice dela; `value`, `vector` ou `decoded`), o estado completo quando foi criada, e cada criação, entrada, saída e remoção - milhões de linhas para uma partida inteira
- `<partida>.strings.parquet`: cada entrada de tabela de strings de cada atualização e de cada instantâneo completo, o valor por inteiro; `userinfo`, `ActiveModifiers` e `EconItems` decodificados a partir dos protobufs
- `selfCheck.completeness` do documento da partida conta quadros e mensagens pelo nome da Valve, entradas do log de combate (`combatlog <type>`), eventos do jogo (`gameevent <name>`), entradas de tabela de strings (`stringtable <name>`) e atualizações de entidade (`entity <class>`); algumas são guardadas só em bruto (instantâneos completos de entidades que o gem pula porque reconstrói a partir das mudanças, e entradas de tabelas cujos valores nada lê), com lost 0

**Não disponível**

- voz: o replay tem a configuração de voz, mas não os dados de voz
- nomes por trás de hashes e ids: sons e partículas são nomeados por hashes dos ficheiros do jogo, habilidades por ids; o replay não traz os nomes (itens são nomeados pelo catálogo do gem, quando ele os tem)
- o que só os próprios clientes dos jogadores sabiam (a câmara deles, o ecrã deles) além do que o servidor transmitiu; o cursor e cada ordem estão incluídos

**Tamanho**: os ficheiros auxiliares juntos são um pouco maiores que o próprio replay, sendo os maiores os de pacotes e de entidades; uma partida inteira leva um ou dois minutos num processo

## Verificado {#verified}

verificado num replay de partida pública: abates, mortes, assistências, nível, last hits e denies batem com o registo de fim de partida do próprio jogo para os dez jogadores; cada mensagem do ficheiro auxiliar de pacotes é serializada de novo byte a byte; a tabela e as estatísticas por testes com dados sintéticos

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
