---
title: "VALORANT (repetições)"
nav_order: 45
lang: "pt"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (repetições) {#valorant-replays}

Depois de uma partida de VALORANT, o watcher transforma a repetição guardada pelo jogo em ficheiros que se podem ver como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `valorant-replays`, tipo [`replay`](sources-and-rules.md); corre o tempo todo (não espera um jogo começar) e procura dados novos a cada 5 s.*

## O que é gravado {#what-is-recorded}

- o mapa, o id da partida e os agentes escolhidos; o bloco de informações da repetição (duração, versões, nome, hora da gravação, flags de compressão e de cifragem)
- a linha do tempo de eventos do servidor: abates (matador e vítima como ids de rede), início das rondas, spikes plantados, desarmados e explodidos, ultimates usados, troca de lados - cada um com o seu id e metadados
- cada bloco do ficheiro guardado inteiro no heat.raw.parquet; não decodificado: posições, nomes ou placares - estão no fluxo ofuscado

## De onde vem {#where-it-comes-from}

repetições que o VALORANT guarda: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (só as partes que não são ofuscadas)

## Como ligar {#how-to-switch-it-on}

guarde uma repetição no VALORANT (carreira > partida > transferir repetição)

## Como funciona {#how-it-works}

League of Legends e VALORANT (repetições): o que delas pode ser lido como está.

Os dois jogos guardam repetições no disco do jogador, e os dois protegem o que está dentro: os dados do jogo momento a momento são ofuscados, e de forma diferente a cada atualização, para impedir que sejam usados para trapacear. Vencer isso significa desmontar o código do próprio jogo, o que os termos da Riot proíbem (Termos de Serviço 3.1 e 7.1) - então isso não é feito aqui. O que cada ficheiro traz às claras é lido, e o resto é guardado como está: cada parte do ficheiro, inteira, no `heat.raw.parquet` da sessão (regra do conversor do 3DHeat, docs/converters.md no repositório do visualizador), contada no `selfCheck.completeness` do meta.json.

#### VALORANT (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, uma repetição local do Unreal Engine (layout do vrfkit, Apache-2.0, e do ValorantReplayParser, MIT). Às claras: o bloco de informações da repetição (duração, versão de rede, changelist, o nome dela, quando foi gravada, se é comprimida ou cifrada), o mapa, o id da partida e os agentes escolhidos (no cabeçalho), e a linha do tempo de eventos do próprio servidor - abates (matador e vítima como ids de rede, não nomes), início das rondas, spikes plantados, desarmados e explodidos, ultimates usados, troca de lados - cada um com o seu tempo, id e metadados. Posições, nomes, placares e tudo o mais estão no fluxo ofuscado (os blocos de dados da repetição e de checkpoint), que é guardado inteiro e não lido.

Também serve este módulo: [League of Legends (repetições)](game-lol-replays.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | não |
| Eixo para cima | `z` |
| Unidades | unidades do mundo do VALORANT |
| Espelhado para o visualizador | nenhum |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `replay`: lê só o que o jogo ou a plataforma entrega (repetições e demos que o jogo guarda), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- o bloco de informações, cada campo (meta.json `vrf`): versão do ficheiro, versões personalizadas, duração, versão de rede, changelist, nome, flag de ao vivo, hora da gravação, flags de comprimido e de cifrado, a chave como está guardada
- o bloco de cabeçalho: o mapa, o id da partida e os agentes escolhidos (reconhecidos pela sua forma)
- cada bloco de evento: id, grupo, metadados, tempo de início e de fim, e, dos seus dados, o nome do evento, o tempo em segundos e os números antes dele (ids de rede de quem matou e de quem morreu) - uma linha cada

**Guardado bruto**

- cada bloco inteiro, na ordem do ficheiro (`offset`), para que as partes sejam o ficheiro: `info`, `header`, `event <grupo>`, `replay_data`, `checkpoint`, `chunk <n>` para um tipo que o layout não nomeia, `trailing` para os bytes depois do último bloco completo

**Não disponível**

- posições, nomes, placares, habilidades, cada quadro do jogo: os blocos de dados da repetição e de checkpoint são ofuscados; lê-los significa desmontar o cliente, o que os termos da Riot proíbem. Guardados inteiros, não lidos
- o conteúdo de uma repetição cifrada: percorrida e guardada inteira, nada é lido por dentro

**Tamanho**: o ficheiro bruto tem cerca do tamanho da própria repetição: o fluxo ofuscado não comprime

## Verificado {#verified}

montado a partir do layout do contêiner documentado pelo vrfkit (Apache-2.0); não testado numa repetição real, que não estava disponível - o adaptador verifica antes de ler e salta o que não coincide

## Fonte {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
