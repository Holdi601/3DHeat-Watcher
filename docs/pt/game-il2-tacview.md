---
title: "IL-2 Sturmovik: Great Battles (repetições)"
nav_order: 27
lang: "pt"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (repetições) {#il-2-sturmovik-great-battles-replays}

Depois de uma partida de IL-2 Sturmovik: Great Battles, o watcher transforma a repetição guardada pelo jogo em ficheiros que se podem ver num mapa no visualizador 3DHeat.

*Detalhes técnicos: adaptador `il2-tacview`, tipo [`replay`](sources-and-rules.md); corre o tempo todo (não espera um jogo começar) e procura dados novos a cada 5 s.*

## O que é gravado {#what-is-recorded}

- cada avião, veículo e navio da gravação: posições uma vez por segundo (metros a leste/acima/ao norte do ponto de referência da gravação; lat/lon/alt como colunas)
- aparições (spawn), destruições (morte) e saídas (left), decolagens e pousos quando gravados
- objetos, destruídos, decolagens, pousos e comprimento por gravação
- cada linha da gravação guardada inteira no heat.raw.parquet, no relógio das linhas

## De onde vem {#where-it-comes-from}

as gravações Tacview do próprio jogo &lt;jogo>\data\Tracks\\\*.acmi (texto ACMI 2.x, simples ou comprimido)

## Como ligar {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 em [KEY = track_record])

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz porquê; [Instalar e executar](installing-and-running.md) cobre as causas mais comuns.

`python -m heat3d_watch setup il2-tacview` lista os ficheiros que ele mudaria; `python -m heat3d_watch setup il2-tacview --apply` os altera e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `il2-tacview: changed: ...` para cada mudança, ou `il2-tacview: nothing to change` quando já está ligado.

## Como funciona {#how-it-works}

IL-2 Sturmovik: Great Battles - a saída de telemetria UDP do jogo, e as gravações Tacview próprias dele.

1. Telemetria ("Telemetry output of IL2 v4.003", revisão 1.2, distribuída como `<jogo>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Ligada em `<jogo>\data\startup.cfg`, seção `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = "IP[:porta]" (vários destinos ao mesmo tempo), `decimation` (50 Hz / n), `enable`, `port`. O `setup` acrescenta um destino, 127.0.0.1:41995 (o JoyPro usa 41994; a predefinição do jogo é 4322), e liga a saída. Pacotes, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indicadores: 0 ENG_RPM, 1 ENG_MP, 2/3 tremor do motor, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz, com a gravidade), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Eventos (empacotados em 2 bytes): 0 SET_FOCUS (STRING: um byte de tamanho + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB e 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT e 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. As posições dos eventos são locais ao avião do jogador; o fluxo não tem posição no mundo nenhuma - então são eventos e números, não um trajeto.

2. Gravação Tacview: `tacviewrecord = 1` em `[KEY = track_record]` faz o jogo escrever `<jogo>\data\Tracks\*.acmi` (em multijogador, quem decide é o servidor). Uma gravação terminada é convertida: cada avião, veículo e navio com as posições dela, aparição e remoção (destruído ou sumido), decolagens e pousos quando a gravação os tem. Formato de texto ACMI 2.x, simples ou comprimido, conforme <https://www.tacview.net/documentation/acmi/en/> - linhas "#t" movem o relógio, linhas "id,Key=Value,..." definem propriedades (ids em hexadecimal, vírgulas escapadas "\\,", uma "\\" no fim continua a linha), "-id" remove um objeto, o objeto 0 traz as globais (ReferenceLongitude/Latitude, RecordingTime, ...) e os eventos ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] ou Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], com longitude e latitude relativas à referência, campos vazios sem mudança. As posições entram num mapa plano em torno do ponto de referência: x a leste, y altitude, z ao norte, em metros. O ponto de referência é o `geo` da sessão, guardado no meta.json e no rodapé da tabela, para que o visualizador possa pôr o mundo real sob os trajetos.

Também serve este módulo: [IL-2 Sturmovik: Great Battles (dados ao vivo)](game-il2.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros (leste, altitude, norte a partir da primeira leitura) |
| Espelhado para o visualizador | `z` |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `replay`: lê só o que o jogo ou a plataforma entrega (repetições e demos que o jogo guarda), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- a posição T de cada objeto (longitude, latitude, altitude, roll, pitch, yaw, U, V, heading) como posições uma vez por segundo por objeto, com Name, Type, Pilot, Coalition/Color, Country, Group e Parent
- aparições, remoções (morte quando um evento Destroyed veio antes, senão saída), eventos TakenOff e Landed, eventos Message e Bookmark como linhas
- as globais ReferenceLongitude/Latitude (a origem do mapa), RecordingTime/ReferenceTime (quando), DataSource, DataRecorder e Title no meta.json

**Guardado bruto**

- cada linha lógica não vazia inteira como `text` (uma linha continuada por uma barra invertida final é unida, como o ACMI a lê), sob o tipo dele: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` e `event` (objeto 0), `object` (id,Key=Value,...)
- o que só o ficheiro bruto guarda: as posições entre as linhas de um segundo, armas, projéteis, sinalizadores, chaff e outros objetos não desenhados como trajetos, cada outra propriedade (telemetria como IAS, AOA, acelerador, combustível quando a gravação a tem), outras globais (Comments, Briefing, Author, Category), eventos além dos lidos (Timeout, LeftArea, ...)

**Não disponível**

- nada além do que a gravação contém; o que o jogo não escreve nas suas gravações não está nelas

**Tamanho**: o próprio texto da gravação mais cerca de 70 bytes por linha, antes do zstd: uma gravação de 100 MB passa a ser cerca de 150-250 MB brutos, que o zstd reduz quase ao tamanho da gravação comprimida

## Verificado {#verified}

testado com ficheiros ACMI 2.2 sintéticos (texto e comprimidos); sem teste numa gravação do jogo

## Fonte {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
