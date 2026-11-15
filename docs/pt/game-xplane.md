---
title: "X-Plane (dados ao vivo)"
nav_order: 50
lang: "pt"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (dados ao vivo) {#x-plane-live-data}

Enquanto se voa no X-Plane, o watcher guarda os dados que o próprio jogo envia, para que se possam ver depois num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `xplane`, tipo [`telemetry`](sources-and-rules.md); corre enquanto `X-Plane.exe` estiver em execução e procura dados novos a cada 0,1 s.*

## O que é gravado {#what-is-recorded}

- a própria posição a 10 Hz (latitude/longitude/altitude como metros a leste/acima/ao norte da primeira leitura; lat/lon/alt guardadas como colunas)
- atitude, velocidade indicada e verdadeira, velocidade no solo, Mach, velocidade vertical, AoA, derrapagem, rumo magnético, AGL, g (normal, axial, lateral), velocidades e taxas de rotação, flaps, freios aerodinâmicos, acelerador, em solo
- pesos (total, combustível, carga), alavanca do trem de pouso, piloto automático, rpm do motor e N1, hora e data da simulação, pausa, velocidade da simulação, replay, temperatura externa e pressão ao nível do mar (X-Plane 12) uma vez por segundo
- decolagens, pousos, quedas, reinícios de voo (session_start/session_end por voo)
- tempo de voo, tempo no ar, distância, maior altitude, maior g, pousos
- cada resposta que o X-Plane envia guardada inteira no heat.raw.parquet

## De onde vem {#where-it-comes-from}

a interface UDP do X-Plane em 127.0.0.1:49000 (datarefs RREF e posição RPOS, respondidas ao watcher)

## Como ligar {#how-to-switch-it-on}

X-Plane 12: Configurações > Rede > Aceitar conexões de entrada (o X-Plane 11 responde por predefinição)

## Como funciona {#how-it-works}

X-Plane 11 e 12: a interface UDP própria do simulador, na porta 49000.

O X-Plane responde a quem pede em 127.0.0.1:49000, na taxa pedida, para o endereço e a porta de onde veio o pedido (documento "Exchanging Data with X-Plane" do X-Plane, distribuído em `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

O RPOS dá latitude e longitude como doubles (o RREF só como floats, a meio metro de distância), então ele conduz a posição; o RREF traz o resto e substitui o RPOS quando este não chega. Datarefs (nomes como no `Resources\plugins\DataRefs.txt` do X-Plane 12, <https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

e o resto do voo na mesma taxa (velocidade verdadeira, velocidade vertical, AoA, derrapagem, rumo magnético, Mach, g axial e lateral, taxas de rotação, flaps, freios aerodinâmicos, acelerador: `DATAREFS`), com o estado mais lento da aeronave uma vez por segundo (pesos, alavanca do trem, piloto automático, motores, hora da simulação, pausa e velocidade, clima: `SLOW_DATAREFS`). Cada datagrama também é guardado inteiro no ficheiro auxiliar bruto da sessão, e o meta.json nomeia o dataref por trás de cada índice RREF.

O X-Plane 12 aceita isto só com Configurações > Rede > "Aceitar conexões de entrada" ligado. As posições entram num mapa plano em torno do primeiro ponto do período (`Tangent`): x a leste, z ao norte em metros, y a altitude acima do nível do mar - assim um voo nivelado fica nivelado, não importa a distância, o que um plano tangente real faria a Terra curvar para baixo. A origem do mapa é o `geo` da sessão: o meta.json e o rodapé da tabela a carregam, para que o visualizador possa pôr o mundo real sob o voo.

Este módulo também guarda o que os outros simuladores de voo têm em comum: o mapa plano, a contabilidade de voo (decolagens, pousos, quedas, distância), o socket UDP e a lista da biblioteca Steam.

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

- Marcado como jogado online (`multiplayer`): **não**. `games --markdown` mostra isto como "um jogador".
- Tipo `telemetry`: lê só o que o jogo ou a plataforma entrega (uma porta UDP ou memória partilhada que o jogo publica), então grava também em jogo online, além do offline; a marca só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem memória, e nunca para um jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código retira de uma tabela de campos do jogo, ou dos nomes de estatística do próprio jogo, não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra do conversor do 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): o que a fonte tem é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, depois cada campo guardado pelo nome; `used` marca o que também passou a linha), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- RPOS (10 Hz): longitude, latitude, elevação, AGL, pitch, rumo verdadeiro, roll, velocidade (leste, acima, sul) e taxas de rotação P/Q/R - tudo nas linhas
- RREF (10 Hz): os 27 datarefs de `DATAREFS` - posição, atitude, IAS, velocidade no solo, TAS, velocidade vertical, AoA, derrapagem, rumo magnético, Mach, g normal/axial/lateral, taxas de rotação, flaps, freios aerodinâmicos, acelerador, AGL, caiu, em solo, tempo de voo - nas linhas
- RREF (1 Hz): os 20 datarefs de `SLOW_DATAREFS` - pesos, alavanca do trem, servos do piloto automático, hora e data da simulação, pausa, velocidade da simulação, replay, número de motores, rpm dos motores 1-4, N1 dos motores 1-2, temperatura externa do ar, pressão ao nível do mar - nas linhas, como a última recebida

**Guardado bruto**

- cada datagrama inteiro como `payload`, sob o cabeçalho dele de quatro letras: `RREF` e `RPOS` (usados quando a consulta gerou uma linha; nos menus, sem uma posição, não geram nenhuma), qualquer outra coisa que o X-Plane envie à porta do watcher sob o próprio cabeçalho, ou `unknown`; o `requests` do meta.json diz qual dataref é cada índice RREF, então as cargas úteis se leem sem este módulo

**Não disponível**

- todos os outros datarefs (o X-Plane tem milhares): o RREF envia só o que é pedido, uma assinatura cada; a lista pede o voo, o estado da aeronave e a hora da simulação - mais detalhes de cabine (rádios, luzes, instrumentos de cada motor, falhas) multiplicariam os pedidos
- o nome da aeronave e o tipo ICAO: datarefs de vetor de bytes, que o RREF envia como um float por caractere
- outras aeronaves (IA e multijogador): os datarefs sim/multiplayer/position não são pedidos
- a saída DATA (Configurações > Saída de dados): envia para um endereço fixo escolhido no simulador, não para quem pede; RREF e RPOS cobrem o que o watcher lê

**Tamanho**: cerca de 17 MB por hora antes do zstd (RREF e RPOS a 10 Hz, cerca de 220 e 70 bytes mais um quadro cada, o RREF lento uma vez por segundo), se o X-Plane envia os valores de cada consulta num pacote só, como faz; o zstd reduz os floats várias vezes

## Verificado {#verified}

testado contra um X-Plane falso que responde RREF/RPOS segundo o 'Exchanging Data with X-Plane' do X-Plane 12; nomes dos datarefs verificados com o DataRefs.txt do X-Plane 12; sem teste contra o simulador em execução

## Fonte {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Gerado a partir do adaptador por tools/gen_game_pages.py; altere o adaptador e execute de novo em vez de editar esta página. -->
