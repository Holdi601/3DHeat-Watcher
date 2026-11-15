---
title: "NVIDIA highlights (plataforma)"
nav_order: 34
lang: "pt"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (plataforma) {#nvidia-highlights-platform}

O watcher guarda o que o NVIDIA highlights guarda sobre os jogos, para se poder ver o histórico depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `nvidia-highlights`, tipo [`platform`](sources-and-rules.md); ele corre o tempo todo (não espera um jogo começar) e procura novos dados a cada 10 s.*

## O que é gravado {#what-is-recorded}

- cada clipe, destaque ou captura de ecrã novo: jogo, ficheiro, tipo, duração e o momento (hora de relógio em ms)
- o id e o nome do destaque, quando o jogo o registou no NVIDIA
- onde o jogador estava naquele momento, quando outro adaptador gravou o mesmo jogo naquele tempo
- as chamadas de destaque que os jogos com GfeSDK registam em log, mesmo quando nenhum clipe é guardado

## De onde vêm os dados {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;jogo>\config.json; os clipes na pasta de captura (%USERPROFILE%\Videos\NVIDIA\\&lt;Jogo>\\\*.mp4) e &lt;temp>\Highlights\\&lt;jogo>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Como ativar {#how-to-switch-it-on}

NVIDIA App: Instant Replay ou Highlights ligados, clipes guardados por tecla de atalho ou pelo jogo

## Como funciona {#how-it-works}

O que o iniciador e o driver de vídeo guardam sobre o jogo: estatísticas, conquistas, tempo de jogo e linhas do tempo da Steam, e os destaques e clipes da NVIDIA.

Nenhuma dessas fontes precisa que um jogo coopere ou esteja a correr, então os três adaptadores daqui estão sempre ligados e olham alguns ficheiros a cada poucos segundos.

#### Destaques e clipes da NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

O que o NVIDIA App / GeForce Experience guarda, tudo em `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      o índice da galeria: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, quando o ficheiro foi escrito), profileName, drsName
                     (o exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (onde os clipes são guardados),
                     settings.tempDirectory (os destaques esperam em
                     <temp>\Highlights\<jogo> até serem guardados)
Highlights\<jogo>\config.json  os tipos de destaque que um jogo registou:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
e os próprios ficheiros de clipe, `<pasta de captura>\<Jogo>\<Jogo> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (capturas de ecrã: `<Jogo> Screenshot yyyy.mm.dd - ...png`), sendo que a hora do nome é a hora local em que o clipe foi guardado. Os jogos com GfeSDK também registam as chamadas de destaque delas em `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

O que isto pode e não pode entregar: um jogo que suporta NVIDIA Highlights (GfeSDK) regista os tipos de destaque uma vez — um id como "kill", uma importância, tags, um nome de apresentação — e depois diz só "highlight <id>, from <ms> before now to <ms> after". Não há posições, nem partida ou ronda, nem oponente, nem dados personalizados: o SDK não tem campo para nada disso. Um clipe guardado acrescenta um ficheiro, um nome de jogo, uma duração e um horário. Então o que é gravado é "este tipo de momento, neste jogo, nesta hora" — e um lugar só ao procurar a hora na gravação de outro adaptador do mesmo jogo (`position_at`), o que este adaptador faz para cada clipe que grava.
<https://developer.nvidia.com/highlights>

Cada adaptador guarda o que já viu em `<dados>\state\<id>.json`, então um reinício não grava nada duas vezes.

Cada sessão também guarda, inteiro, o de onde vieram as linhas dela (regra do conversor do 3DHeat, docs/converters.md no repositório do visualizador), no `heat.raw.parquet`: os bytes do ficheiro de estatísticas e do esquema dele e o bloco localconfig do jogo (steam-stats; um ficheiro de estatísticas que o decodificador não consegue ler gera uma sessão com só os seus bytes), o cabeçalho do ficheiro de linha do tempo e cada entrada em JSON (steam-timeline), cada entrada do índice de galeria de um clipe, as definições de destaque do jogo e cada linha do log GfeSDK (nvidia-highlights).

O mesmo módulo também serve: [Estatísticas da Steam (plataforma)](game-steam-stats.md), [Steam Timeline (plataforma)](game-steam-timeline.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | só emprestadas: o lugar que outra gravação do mesmo jogo tem para aquele momento |
| Eixo para cima | `y` |
| Unidades | metros |
| Espelhado para o visualizador | nenhum |
| Escala da unidade (`scale`: o visualizador multiplica as posições por ele) | 1 |

Estes valores vão para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`. Assim o visualizador do 3DHeat gira e dimensiona as linhas sozinho: veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **não**. `games --markdown` mostra isso como "um jogador".
- Tipo `platform`: lê só o que o jogo ou a plataforma entrega (o que a Steam ou o driver de vídeo guarda), por isso grava também em jogo online, além do offline; a marcação decide apenas se a memória pode ser lida.
- Memória: **nunca** lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online: veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). Chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, todo pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e `selfCheck.completeness` no `meta.json` conta cada `type`; `lost` é 0.

**Lido**

- cada clipe e captura de ecrã novos: jogo, ficheiro, tipo, mídia, duração (do índice, senão do cabeçalho do MP4), o momento a partir do nome do ficheiro, o id e o nome do destaque quando o jogo os registou, e o lugar do jogador naquele momento, a partir da gravação de outro adaptador
- pedidos de destaque GfeSDK (cada `Posted Request HL...`, menos as chamadas de configuração) com a sua hora

**Mantido bruto**

- `UGC`: a entrada inteira do clipe no índice de galeria UGCTracker.json, cada campo que a NVIDIA escreve
- `clip_file`: para um clipe que o índice não lista, o caminho, o tamanho, a hora e a pasta do ficheiro
- `highlights_config`: o `Highlights\<jogo>\config.json` do jogo como foi escrito (importância, tags, nomes em todos os idiomas), uma vez por sessão
- `gfesdk_log`: cada linha dos logs GfeSDK lidos depois da primeira execução, `used` verdadeiro para os pedidos de destaque e falso para o resto (configuração, ajustes de vídeo, as mensagens do próprio SDK)

**Não disponível**

- os clipes e capturas de ecrã em si: o vídeo e as imagens ficam onde a NVIDIA os guardou; as linhas dão o nome do ficheiro
- o que existia antes da primeira execução do adaptador: tudo é tomado como já visto, então anos de clipes não passam a sessões de uma vez (`baseline`; False grava tudo)
- `apps` e `info` do UGCTracker.json e o GallerySettings.json: são configurações da aplicação, não momentos de jogo; a pasta de captura que eles citam é usada
- posições, rondas, oponentes: o GfeSDK não tem campo para eles

**Tamanho**: cerca de 1 KB por clipe e alguns KB de definições e linhas de log por início de jogo: bem abaixo de 1 MB por hora

## Verificado {#verified}

testado com um índice de galeria real, ajustes, definições de destaque e clipes de uma instalação local; as linhas de pedido de destaque do GfeSDK e os ids de destaque nos clipes não foram testados

## Fonte {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
