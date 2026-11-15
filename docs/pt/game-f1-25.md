---
title: "EA SPORTS F1 25 (dados ao vivo)"
nav_order: 16
lang: "pt"
source: game-f1-25.md
source_hash: "7476dbb3b308"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 25 (dados ao vivo) {#ea-sports-f1-25-live-data}

Enquanto se joga EA SPORTS F1 25, o watcher guarda os dados que o próprio jogo envia para fora, para que se possa ver depois, num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `f1-25`, tipo [`telemetry`](sources-and-rules.md); ele corre enquanto `F1_25.exe` está aberto e procura dados novos a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- a posição de cada carro (XYZ no mundo, em m) a 10 Hz, pelo nome do piloto, equipa, com o carro próprio marcado (`own_car` 1, a partir do índice do carro do jogador), com velocidade, marcha, acelerador, freio, direção, rpm, DRS, guinada, arfagem, rolagem (graus) e forças g
- voltas de cada carro com o tempo da volta e a posição na corrida; chegadas e abandonos
- os eventos de corrida do jogo: início e fim da sessão, volta mais rápida, penalidades, ultrapassagens, colisões, safety car, bandeira vermelha, luzes de largada, bandeira quadriculada, vencedor, flashbacks (`teleport` onde o carro estava, `spawn` para onde ele voltou)
- pista, tipo de sessão, voltas e pilotos de cada sessão
- as próprias voltas, a melhor volta, posição na corrida e no grid, pit stops, penalidades, ultrapassagens, colisões, distância, velocidade máxima
- cada pacote que o jogo envia, por inteiro, em `heat.raw.parquet` - inclusive os que não passam a linhas

## De onde vem {#where-it-comes-from}

telemetria UDP 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## Como ligar {#how-to-switch-it-on}

No jogo: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, porta 20777 - ou `python -m heat3d_watch setup f1-25 --apply` (edita hardware_settings_config.xml, com backup antes; o jogo precisa estar fechado). Enquanto outra aplicação usa a porta 20777, o watcher deixa a porta com ele

Escreva o comando num terminal aberto na pasta do watcher (veja [Antes de começar](before-you-start.md)). Se falhar, a última linha diz o motivo; [Instalação e execução](installing-and-running.md) explica as causas mais comuns.

`python -m heat3d_watch setup f1-25` lista os ficheiros que seriam alterados; `python -m heat3d_watch setup f1-25 --apply` faz as alterações e guarda o original como `<ficheiro>.heat3d-backup` (veja [Comandos](commands.md#setup)). Ele imprime `f1-25: changed: ...` para cada alteração, ou `f1-25: nothing to change` quando já estiver ligado.

## Como funciona {#how-it-works}

EA SPORTS F1 23, F1 24 e F1 25: a telemetria UDP oficial, todos os carros na pista.

Os jogos enviam tudo por conta própria (Settings > Telemetry Settings, ou `Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`, `<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`). Little-endian, compactado, um cabeçalho de 29 bytes em cada pacote (o mesmo nos formatos 2023, 2024 e 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

O que é lido, por id de pacote:

```text
0 Motion        CarMotionData[22], 60 bytes cada: posição x y z no mundo
                (metros; Y para cima), velocidade no mundo, vetores de frente e
                direita (int16 / 32767), forças g, yaw pitch roll
1 Session       clima, temperaturas, total de voltas, comprimento da pista, tipo
                de sessão, id da pista, ... jogo em rede
2 Lap Data      LapData[22]: tempo da última volta, distância percorrida na volta,
                posição na corrida, número da volta atual, pit stops, penalidades,
                posição no grid, piloto e estado do resultado. 50 bytes por carro
                em 2023; 57 em 2024 e 2025, que acrescentaram as partes em minutos
                das diferenças e a armadilha de velocidade.
3 Event         um código de quatro letras e uma união de detalhes: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: IA ou humano, piloto, equipa, número de corrida,
                nome (48 bytes em 2023 e 2024, 32 em 2025; 58, 60 e 57 bytes por carro)
6 Car Telemetry CarTelemetryData[22], 60 bytes: velocidade em km/h, acelerador,
                direção, freio, embreagem, marcha, rpm, DRS ...
```

Cada pacote também é guardado por inteiro, como chegou, no ficheiro auxiliar bruto da sessão (`heat.raw.parquet`, `type` o nome do pacote - `motion`, `car_status` ... - com `format`, `packet_id`, `frame` e `session_uid`) - os lidos acima e os que nada lê ainda: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, qualquer id posterior, e pacotes num formato que este módulo não lê. Assim, um decodificador futuro precisa apenas do ficheiro auxiliar.

A posição de cada carro está no pacote Motion - também online, quando o próprio jogo a entrega (só os dados de combustível, ERS, dano e conjuntos de pneus são retidos para jogadores cujo "Your Telemetry" está restrito). Cada carro é gravado a cerca de 10 Hz sob o nome do piloto no participante ("car N" até os nomes chegarem), a equipa pelo nome, e o carro do jogador marcado como `own`.

Fontes: "F1 25 UDP Specification" da EA (forums.ea.com, central de informações sobre os jogos F1), as especificações do F1 23 e do F1 24; as mesmas tabelas espelhadas em MacManley/f1-25-udp (MIT). Os pacotes dos testes são montados a partir destes layouts.

O mesmo módulo também serve: [EA SPORTS F1 23 (dados ao vivo)](game-f1-23.md), [EA SPORTS F1 24 (dados ao vivo)](game-f1-24.md).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros |
| Espelhado para o visualizador | nenhum |
| Escala das unidades (`scale`: o visualizador multiplica as posições por ele) | 1 |

Isso vai para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`, de modo que o visualizador do 3DHeat gira e ajusta as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `telemetry`: ele lê apenas o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), por isso grava também em partidas online, e não só offline; a marcação só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem a memória, e nunca num jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado por inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- 0 Motion: posição e velocidade no mundo de cada carro, e agora também guinada, arfagem, rolagem (graus, a partir dos radianos da especificação) e as forças g lateral, longitudinal e vertical, em cada linha de posição do carro
- 1 Session: pista, tipo de sessão, total de voltas, comprimento da pista, online ou não (`sessions` no meta.json)
- 2 Lap Data: tempo da última volta, número da volta, posição na corrida e no grid, pit stops, penalidades, estado do resultado (voltas, chegadas, abandonos, estatísticas)
- 3 Event: cada código, exceto BUTN, como linha própria, com os detalhes
- 4 Participants: nomes dos pilotos, equipas, número de carros ativos (`player` e `team` das linhas, `drivers` no meta.json)
- 6 Car Telemetry: velocidade, marcha, acelerador, freio, e agora também direção (-1..1), rpm e DRS, em cada linha de posição do carro
- verificado com as especificações UDP publicadas pela EA para os formatos 2023, 2024 e 2025 (tamanhos dos pacotes verificados nos testes); ainda não verificado com o jogo

**Guardado bruto**

- cada pacote por inteiro em `heat.raw.parquet`, `payload` o datagrama, `type` o nome do id: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` para um id que as especificações ainda não listam); colunas `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` é verdadeiro para os pacotes lidos acima (Motion, Session, Lap Data, Participants, Car Telemetry, e códigos de Event diferentes de BUTN); o resto - configurações de carro, estado do carro (combustível, ERS, composto e idade dos pneus, sinalizadores), classificação final, lobby, dano do carro, histórico da sessão (cada tempo de volta e de setor por carro), conjuntos de pneus, motion ex (suspensão do próprio carro, velocidades das rodas, velocidade local, velocidade e aceleração angulares), contrarrelógio, posições de voltas, eventos de botão BUTN - é guardado para um decodificador posterior
- `format <ano>`: um pacote de formato anterior a 2023 (outro layout de cabeçalho), por inteiro; `short`: um datagrama menor que o cabeçalho de 29 bytes, por inteiro

**Não disponível**

- combustível, ERS, dano e conjuntos de pneus de outros jogadores online, quando o "Your Telemetry" deles está restrito: o jogo envia zeros para eles
- pacotes enviados enquanto o watcher não está em execução, ou enquanto outra aplicação usa a porta 20777: o UDP não é armazenado pelo jogo

**Tamanho**: com taxa de envio de 60 Hz, cada pacote é de cerca de 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status e Motion Ex a 60 Hz, Session History e Tyre Sets a 20/s, Car Damage a 10/s, Session e Car Setups a 2/s) mais cerca de 0,03 MB/s de cabeçalhos de itens: cerca de 1,5 GB por hora de direção antes da compressão, cerca de 0,55 GB com os 20 Hz padrão; o zstd reduz isso a uma fração (vagas vazias de carros e valores repetidos comprimem bem; ainda não medido numa sessão real)

## Verificado {#verified}

testado com pacotes nos formatos 2023, 2024 e 2025 montados a partir da especificação publicada pela EA, enviados por UDP; não testado com o jogo

## Fonte {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
