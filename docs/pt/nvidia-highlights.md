---
title: NVIDIA Highlights
nav_order: 8
lang: "pt"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Alguns jogos pedem ao driver gráfico NVIDIA que guarde um vídeo curto quando algo acontece, como um abate.
O watcher regista cada um desses momentos e, quando consegue, coloca-o no mapa onde aconteceu.

O adaptador `nvidia-highlights` regista os clipes, os destaques e as capturas de ecrã que o NVIDIA App (ou
o GeForce Experience) guarda, e dá a cada um um lugar no mapa quando possível. Esta página explica o que o
NVIDIA Highlights pode entregar e o que não pode, quais ficheiros o watcher lê, e como um destaque ganha uma
posição. A página gerada do adaptador é [NVIDIA highlights (plataforma)](game-nvidia-highlights.md).

## O que o NVIDIA Highlights pode e não pode entregar {#what-nvidia-highlights-can-and-cannot-deliver}

Um jogo que suporta o NVIDIA Highlights comunica com o NVIDIA App por meio do GfeSDK da NVIDIA. O SDK
transporta apenas dois tipos de mensagem:

1. **Uma vez, no início**: os tipos de destaque que o jogo vai usar - um id (como `kill`), uma importância,
   tags e um nome de apresentação em cada idioma. O NVIDIA App guarda isso por jogo.
2. **Num momento da partida**: "destaque `<id>`, de `<ms>` antes de agora a `<ms>` depois". Essa é a
   mensagem inteira: o id de um tipo que o jogo registou, e dois deslocamentos de tempo que dizem ao NVIDIA
   Aplicação qual trecho da gravação contínua deve manter.

O SDK **não tem campo para mais nada**: nada de posição, partida ou ronda, adversário, arma, placar ou dado
personalizado de qualquer tipo. Um jogo não consegue colocar uma posição num destaque, mesmo que quisesse.
Quando o clipe é guardado, o NVIDIA App acrescenta um ficheiro, um nome de jogo, uma duração e uma hora.

Assim, tudo o que um destaque pode dizer é "este tipo de momento, neste jogo, nesta hora". Todo o resto
tem de vir de outro lugar.

## O que o watcher lê {#what-the-watcher-reads}

Tudo é lido de ficheiros que o NVIDIA App escreve para a própria galeria. Nada comunica com o driver nem com a aplicação. A pasta do NVIDIA Overlay é `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Ficheiro | O que é tirado dele |
|---|---|
| `UGCTracker.json` | o índice da galeria: cada clipe e captura de ecrã com o caminho, o tipo (vídeo, imagem), o subtipo (`InstantReplay`, ...), a data, o nome do perfil do jogo, o executável e o nome curto, e a duração (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, a pasta de captura, e `settings.tempDirectory`, onde os destaques esperam (`<temp>\Highlights\<jogo>`) até serem guardados |
| `Highlights\<jogo>\config.json` | os tipos de destaque que cada jogo registou: id, e o nome de apresentação em inglês (ou o id, quando o jogo não deu nenhum) |
| a pasta de captura (predefinição `%USERPROFILE%\Videos\NVIDIA`) e `<temp>\Highlights` | os próprios ficheiros de clipe e de captura de ecrã (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), uma pasta por jogo |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | os pedidos que os jogos GfeSDK registam - linhas `Posted Request HL...` - assim um destaque pedido pelo jogo fica registado mesmo quando nenhum clipe foi guardado. Os pedidos de configuração (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) são ignorados. |

Para cada item novo, o adaptador escreve uma linha: `highlight` para um vídeo, `screenshot` para uma imagem,
ou `highlight_request` para uma linha do log do GfeSDK. Os campos dela:

| Campo | O que é |
|---|---|
| `ms` | o momento: a hora no nome do ficheiro (`<Jogo> 2026.05.01 - 20.31.28.115.DVR.mp4`, a hora local em que o clipe foi guardado), senão a data do índice, senão a hora de modificação do ficheiro |
| `game` | o nome do perfil no NVIDIA, o nome da pasta ou o nome do jogo no nome do ficheiro |
| `clip`, `media` | o caminho do ficheiro; `video`, `image` ou `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (da pasta temporária de destaques) ou o subtipo do índice |
| `duration_s`, `clip_start_ms` | a duração, do índice ou do próprio cabeçalho do vídeo (`moov/mvhd`, encontrado sem ler o vídeo); o momento em que o clipe começa |
| `highlight_id`, `highlight_name` | o tipo de destaque, quando algo o nomeia (veja abaixo) |
| `exe` | o executável do jogo, do índice |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | a posição emprestada, quando uma foi encontrada (veja abaixo) |

As estatísticas da sessão são `clips`, `screenshots`, `clip_seconds` e `placed` (itens que receberam uma
posição).

**O id do destaque** não está escrito em nenhum lugar documentado. O adaptador tenta dois caminhos não
documentados: um campo da entrada da galeria cujo nome contém "highlight", e - só para ficheiros da pasta
temporária de destaques - um dos ids registados pelo jogo (com pelo menos 4 caracteres) que aparece no nome
do ficheiro. Um clipe guardado leva o nome do jogo, que poderia conter por acaso um id como "kill", por isso o nome
dele não é pesquisado. Estes dois caminhos ainda não se mostraram a funcionar num computador real: nenhum
clipe com id de destaque e nenhuma linha de pedido do GfeSDK apareceu onde o adaptador foi testado. O
índice da galeria, as configurações, as definições de destaque e os clipes foram testados com ficheiros reais.

### Quando os itens são registados {#when-items-are-recorded}

- Um clipe continua a ser escrito durante algum tempo depois de a tecla ser premida. O adaptador espera até que um
  ficheiro tenha o mesmo tamanho e a mesma hora de modificação em duas verificações (a cada 10 s) e tenha pelo menos 5 s de
  idade.
- Na primeira vez que o adaptador corre, tudo o que já está na galeria e nos logs apenas é registado como visto, não gravado, para que anos de clipes antigos não encham as estatísticas. O que ele já viu fica guardado em
  `<dados>\state\nvidia-highlights.json`, por isso um reinício não regista nada duas vezes.
- Os itens são agrupados numa sessão por jogo. A sessão de um jogo fecha depois de 30 minutos sem um item
  novo, e termina no último momento dela, não quando o jogo fechou. Momentos com mais de 30 minutos de
  distância vão para sessões separadas.

## Como um destaque ganha uma posição {#how-a-highlight-gets-a-position}

O destaque em si não tem lugar. O adaptador procura o momento nas outras gravações que o watcher fez do mesmo
jogo, na mesma hora:

1. **O mesmo jogo**: as pastas de sessão em `<dados>\sessions\` cujo nome de jogo coincide com o do destaque.
   Os nomes são comparados em minúsculas, apenas letras e dígitos. Coincidem quando são iguais, ou quando o
   menor tem pelo menos 5 caracteres e está contido no maior (`Counter-Strike 2` e `Counter-Strike-2`).
2. **A mesma hora**: sessões cujo início e fim (do `meta.json`, com um segundo de folga em cada ponta) cobrem o momento. Sessões que terminaram sem posições, e as sessões do próprio adaptador, são ignoradas.
3. **A linha do próprio jogador**: no `events.jsonl` dela, a mais recente das linhas do jogador com uma posição,
   no momento ou antes dele e no máximo 5 segundos antes. Uma linha é do próprio jogador quando a fonte o diz:
   `"player": "me"`, ou `"own_car": 1` (jogos de corrida que gravam cada carro pelo nome do piloto), ou
   um `player` que é o `player` da sessão no `meta.json` (o nome que a fonte dá ao jogador). Veja
   [As linhas do próprio jogador](the-data.md#the-players-own-rows).

Se uma linha for encontrada, o destaque recebe o `x`, o `y`, o `z`, a `session` dele (ou o nome da pasta),
`position_from` (a pasta de onde veio) e `position_lag_ms` (quanto tempo antes do momento estava aquela
linha). A sessão do destaque herda os eixos dessa gravação, por isso é desenhado do mesmo modo. Se nenhuma
linha for encontrada, o destaque fica como um momento na linha do tempo, sem lugar.

Coisas a saber sobre a posição emprestada:

- **É onde o jogador estava quando o clipe foi guardado**, não onde a ação começou. O momento é a hora de gravação
  no nome do ficheiro, que, para um Instant Replay, é o fim. `clip_start_ms` diz quando o clipe começa.
- **Outro adaptador precisa de ter gravado o mesmo jogo na hora.** Os que marcam as linhas do próprio jogador, e
  por isso podem posicionar um destaque: a integração de estado de Counter-Strike 2 e Dota 2, Forza, os jogos
  Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2,
  American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft e os perfis
  de memória (como `me`); F1 23/24/25, RaceRoom, Automobilista 2 e Project CARS 2 (as linhas do carro do jogador
  trazem `own_car` 1, pelo índice de carro do jogador no jogo, pelo slot próprio ou pelo participante
  observado); Elite Dangerous (o nome do comandante, em `meta.json` como `player`, já que o diário é sempre do
  jogador).
- **Um replay é convertido depois da partida**, por isso só pode posicionar um clipe que seja procurado depois
  da conversão: o clipe é posicionado quando é gravado, e um replay guardado depois não é revisto de novo.
  Os replays de League of Legends marcam as linhas próprias pelo Riot ID nas configurações e, com uma chave de API da Riot,
  recebem a hora de relógio que a linha do tempo da partida indica, por isso são encontrados nesse momento. Uma
  demo de CS2 não consegue posicionar nenhum destaque: as posições dela estão na tabela própria do conversor,
  não em `events.jsonl`, e uma demo tem os ticks do jogo mas nenhuma hora de relógio para comparar com o momento
  de um clipe.
- No Rocket League, as únicas linhas com lugar são eventos da bola. Uma batida na bola do jogador é uma linha dele,
  por isso um destaque pode ser posicionado onde o jogador tocou a bola por último.
- Jogos sem nenhuma fonte posicional (Overwatch 2, Call of Duty, Hunt: Showdown, ...) mantêm os destaques
  como uma linha do tempo de momentos.

## Porque a memória não pode dar uma posição em multijogador {#why-memory-cannot-give-a-position-in-multiplayer}

A outra forma de obter uma posição seria lê-la da memória. Nenhuma das duas memórias funciona:

- **O lado da NVIDIA não tem posição.** O NVIDIA App recebe o que o GfeSDK transporta - um id de destaque e
  dois deslocamentos de tempo - mais o vídeo que grava. Não há posição em lugar nenhum do lado da NVIDIA para
  ler. (O watcher, de qualquer forma, não lê a memória da NVIDIA; lê os ficheiros acima.)
- **A memória do jogo está fora de alcance em multijogador.** A posição está no processo do jogo, mas o watcher
  nunca lê a memória de um jogo multijogador: um adaptador de memória para um jogo marcado como jogado online é
  recusado antes de qualquer coisa ser aberta (veja [Ler a memória](memory-reading.md)). Os jogos multijogador
  correm sob anti-cheats (Easy Anti-Cheat, BattlEye, Vanguard, ...) que tratam outro programa a abrir o processo
  do jogo como batota, o que pode levar ao banimento da conta.
  Um destaque num jogo multijogador, portanto, só ganha um lugar a partir do
  que o jogo publica: a integração de estado ou a telemetria dele, gravadas por outro adaptador no mesmo
  momento.
