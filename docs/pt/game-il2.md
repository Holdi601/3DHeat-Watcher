---
title: "IL-2 Sturmovik: Great Battles (dados ao vivo)"
nav_order: 26
lang: "pt"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (dados ao vivo) {#il-2-sturmovik-great-battles-live-data}

Enquanto se joga IL-2 Sturmovik: Great Battles, o watcher guarda os dados que o próprio jogo envia, para que se possam ver depois como estatísticas e uma linha do tempo.

*Detalhes técnicos: adaptador `il2`, tipo [`telemetry`](sources-and-rules.md); corre enquanto `Il-2.exe` ou `IL2Series.exe` estiver em execução e procura dados novos a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- as surtidas: o avião assumido (spawn) e o momento em que a saída para (session_end) - sem posição no mundo: o jogo não envia nenhuma
- bombas e foguetes lançados (massa), acertos e dano sofrido, explosões, rajadas de tiro - posições locais ao avião
- velocidade indicada, AGL, velocidade vertical, g, rotação do motor uma vez por segundo, com todos os outros indicadores que o pacote traz (pressão do coletor, tremor do motor, estado e pressão do trem de pouso, AoA, derrapagem, aceleração x/y/z, tremor da cabine, flaps, freios aerodinâmicos)
- surtidas, tiros disparados, bombas, foguetes, acertos sofridos, maior velocidade, maior g, tempo de voo; título do servidor e nome do piloto online
- cada pacote de telemetria guardado inteiro no heat.raw.parquet

## De onde vem {#where-it-comes-from}

a saída de telemetria UDP do jogo para 127.0.0.1:41995 ([KEY = telemetrydevice] em &lt;jogo>\data\startup.cfg)

## Como ligar {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (acrescenta addrN = "127.0.0.1:41995", enable = true), reinicie o IL-2

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz porquê; [Instalar e executar](installing-and-running.md) cobre as causas mais comuns.

`python -m heat3d_watch setup il2` lista os ficheiros que ele mudaria; `python -m heat3d_watch setup il2 --apply` os altera e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `il2: changed: ...` para cada mudança, ou `il2: nothing to change` quando já está ligado.

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

Também serve este módulo: [IL-2 Sturmovik: Great Battles (repetições)](game-il2-tacview.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | não |
| Eixo para cima | `y` |
| Unidades | nenhuma: a telemetria não tem posições no mundo |
| Espelhado para o visualizador | nenhum |
| Escala de unidade (`scale`: o visualizador multiplica as posições por ela) | 1 |

Estes valores vão para o `meta.json` (`axes`) de cada sessão e, quando a sessão tem posições, para o rodapé do `heat.parquet`, para que o visualizador 3DHeat gire e escale as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isto como "permitido (lê só o que o jogo publica)".
- Tipo `telemetry`: lê só o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- SET_FOCUS (o avião assumido: uma surtida), DROP_BOMB e ROCKET_LAUNCH (massa, posição local), HIT e DAMAGE (posição local, força), EXPLOSION (posição local, raio), GUN_FIRE (rajadas por consulta) como linhas
- SETUP_ENG (índice, id, posição local, rotação máxima), SETUP_GUN (índice, posição local, massa do projétil, velocidade de saída) e SETUP_LGEAR (índice, id, posição local) como linhas: os motores, canhões e trens de pouso do avião no início da surtida
- SRV_TITLE, SRV_ADDR, SRS_ADDR e CLIENT_DAT (nome do piloto) no meta.json; a coalizão do CTRL_DAT como a equipa da surtida
- todos os quinze indicadores da especificação na linha `state` de um segundo (um valor como número, um por motor, trem de pouso ou eixo como lista); maior velocidade, g e AGL a partir de cada pacote

**Guardado bruto**

- cada datagrama inteiro como `payload`, sob o Packet_ID dele: `0x54000101` para a telemetria (usado quando gerou uma linha ou uma entrada do meta.json), qualquer outro id como ele mesmo, um datagrama curto demais para um como `short`
- o que só o ficheiro bruto guarda: os indicadores entre as linhas de um segundo (o jogo os envia a 50 Hz / decimation), um evento SETUP mais curto que o layout da especificação, ids de evento que a especificação não lista

**Não disponível**

- uma posição no mundo: a saída de telemetria não tem nenhuma (as posições dos eventos são locais ao avião); o adaptador il2-tacview lê as posições das próprias gravações Tacview do jogo
- outros aviões e jogadores: a saída descreve só o avião do próprio jogador

**Tamanho**: cerca de 8 MB por hora na taxa de 10 Hz do setup (decimation 5; um pacote tem cerca de 160 bytes mais o quadro), 40 MB na taxa total de 50 Hz do jogo, antes do zstd; o zstd reduz os floats repetitivos a uma fração

## Verificado {#verified}

testado com pacotes montados a partir da especificação própria do jogo, Il2_TeleOutput (rev 1.2); edições do startup.cfg testadas numa cópia do ficheiro; sem teste contra o jogo em execução

## Fonte {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
