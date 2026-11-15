---
title: "War Thunder (estado do jogo)"
nav_order: 47
lang: "pt"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (estado do jogo) {#war-thunder-game-state}

Enquanto se joga War Thunder, o watcher guarda o que o jogo informa a programas no próprio computador, para que se possa ver depois, num mapa do visualizador 3DHeat.

*Detalhes técnicos: adaptador `warthunder-webmap`, tipo [`gsi`](sources-and-rules.md); ele corre enquanto `aces.exe` está aberto e procura dados novos a cada 0,5 s.*

## O que é gravado {#what-is-recorded}

- a própria posição (leste/norte no mapa, em metros; altura a partir de /state, em aeronave, senão 0) duas vezes por segundo, rumo, velocidade
- nascimentos e a saída do próprio veículo do mapa (destruído, pousou, voltou ao hangar), uma surtida para cada
- outras aeronaves e unidades terrestres do minimapa, como posições com ids acompanhados e lado (sem altura)
- aeródromos, zonas de captura e bases, uma vez; zonas que mudam de lado
- linhas do feed de abates e de dano (quem, veículo, verbo); os abates e mortes do jogador quando o nome do jogador está definido (`config --set player_names.warthunder-webmap=<nome>`)
- nascimentos, distância, maior altitude, maior velocidade verdadeira (TAS), veículo; abates e mortes com o nome do jogador definido
- cada resposta do mapa web guardada por inteiro em heat.raw.parquet - o /state e o /indicators completos, o chat, os objetivos da batalha e a imagem do mapa inclusive; entre batalhas, numa sessão própria

## De onde vem {#where-it-comes-from}

o mapa web local do jogo, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Como ligar {#how-to-switch-it-on}

Nada precisa ser ligado: o watcher lê a fonte como o jogo ou a plataforma a fornece.

## Como funciona {#how-it-works}

War Thunder: o mapa web local do próprio jogo, em <http://127.0.0.1:8111>.

O jogo serve a página que um segundo ecrã ou um telemóvel pode mostrar (o "mapa web"), e o JSON por trás dela, enquanto corre - em todos os modos, inclusive multijogador:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: a extensão do mapa em metros; valid false no hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 da imagem do mapa, y para baixo), "dx", "dy" (direção),
                  airfields "sx", "sy", "ex", "ey"}]: o que o minimapa mostra, o veículo próprio
                  do jogador com icon "Player"; sem ids, sem alturas
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: valores de voo,
                  válidos só numa aeronave
/indicators      {"valid", "army": air|tank|..., "type": o veículo}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} mais novos que os ids dados, cada um
                  {"id", "msg", "sender", "enemy", "mode", "time"}; linhas de dano são como
                  "Nome (Veículo) shot down Nome (Veículo)"
/gamechat?lastId=N  o chat mais novo que o id dado, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    os objetivos da batalha e o estado deles
/map.img         a imagem do mapa sobre a qual a página desenha os objetos
```

Cada resposta é guardada por inteiro no ficheiro auxiliar bruto da sessão, sob o endpoint dele (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); entre batalhas, as respostas vão para uma sessão própria.

Uma posição do mapa passa a metros com a extensão: u = min_x + x \* (max_x - min_x) a leste, v = max_y - y \* (max_y - min_y) ao norte (o y da imagem desce). As linhas são x = u, y = altura (o "H, m" da própria aeronave; 0 para o resto), z = v, então Y é para cima; z é espelhado para o visualizador, para que o norte não seja desenhado para o sul.

As cores mostram os lados como o jogador os vê: próprio amarelo (#faC81E por predefinição), esquadrão verde, aliados azul (#174DFF), inimigos vermelho (#f40C00); paletas para daltonismo mudam essas cores, então o matiz decide, não o valor exato. O jogo não dá nome a ninguém no mapa e não dá ids aos objetos: outros objetos recebem ids aqui, seguindo-os de consulta em consulta (o mais próximo do mesmo tipo e ícone), o que pode trocar dois aviões do mesmo tipo que passam perto um do outro. O nome do próprio jogador também não está na API: informe-o nas configurações (`config --set player_names.warthunder-webmap=<nome>`), e as linhas do feed de abates sobre o jogador viram abates e mortes; sem isso, são gravadas como feed de abates.

Fontes: a página própria do jogo em <http://127.0.0.1:8111> e o JSON dele; factos sobre os campos conforme documentados pelo projeto JoyPro 2 (docs/telemetry-recording.md; GPL, usado só para os factos).

## Posições e eixos {#positions-and-axes}

| | |
|---|---|
| Posições gravadas | sim |
| Eixo para cima | `y` |
| Unidades | metros (leste/norte do mapa; altura só para a própria aeronave) |
| Espelhado para o visualizador | `z` |
| Escala das unidades (`scale`: o visualizador multiplica as posições por ele) | 1 |

Isso vai para o `meta.json` de cada sessão (`axes`) e, quando a sessão tem posições, para o rodapé do `heat.parquet`, de modo que o visualizador do 3DHeat gira e ajusta as linhas sozinho - veja [Os dados](the-data.md).

## Multijogador {#multiplayer}

- Marcado como jogado online (`multiplayer`): **sim**. `games --markdown` mostra isso como "permitido (lê só o que o jogo publica)".
- Tipo `gsi`: ele lê apenas o que o jogo ou a plataforma entrega (uma integração de estado ou uma API local que o jogo oferece), por isso grava também em partidas online, e não só offline; a marcação só decide se a memória pode ser lida.
- Memória: **nunca** é lida por este adaptador. Só os adaptadores `memory` leem a memória, e nunca num jogo marcado como jogado online - veja [Fontes e regras](sources-and-rules.md).

## Estatísticas gravadas {#statistics-recorded}

Chaves de estatística que o código deste adaptador define pelo nome (o `stats` de cada sessão no `meta.json` e a tabela `stats` do `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Uma chave entre chaves é completada em tempo de execução (`score.{team}` é uma chave por equipa). As chaves que o código tira de uma tabela de campos do jogo ou dos nomes de estatística do próprio jogo não estão nesta lista; "O que é gravado" acima as nomeia.

## Completude {#completeness}

O watcher segue a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: o que a fonte traz é lido ou guardado, nunca descartado. Além das linhas, cada pacote, página, linha ou resposta que o adaptador recebe é guardado por inteiro no `heat.raw.parquet` da sessão (colunas `time`, `ms`, `type`, `used`, `payload`, `text`, e depois qualquer campo guardado pelo nome; `used` marca o que também passou a linhas), e o `selfCheck.completeness` do `meta.json` conta cada `type` - `lost` é 0.

**Lido**

- /map_info.json: a extensão do mapa e a grade (metros, o id do mapa) no meta.json; um inválido encerra a batalha
- /map_obj.json (duas vezes por segundo): o próprio veículo, outras aeronaves e unidades terrestres (ids acompanhados, lado pela cor, ícone, rumo, cor) e aeródromos, zonas e bases como linhas
- /state (duas vezes por segundo, em aeronave): altura, TAS, IAS, Mach e Vy nas linhas próprias
- /indicators (a cada 2 s): tipo do exército e do veículo
- /hudmsg (uma vez por segundo): linhas do feed de abates e de dano como abates, mortes, acertos e linhas de feed; outros eventos do HUD como linhas

**Guardado bruto**

- cada resposta por inteiro, `text` o JSON como o jogo o enviou, sob o endpoint dele: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` os bytes da imagem do mapa como `payload`, uma vez por batalha
- o que só o ficheiro auxiliar bruto guarda: cada campo de /state além dos cinco lidos (AoA, AoS, Ny, Wx, acelerador, RPM, combustível, ... - o conjunto de uma aeronave difere do de outra), cada campo de /indicators (os instrumentos de cabine das aeronaves, a velocidade, a marcha, a tripulação e o estabilizador dos tanques), as outras chaves dos objetos do mapa (color[], blink, icon_bg, extremos de aeródromo), sender, enemy e mode do hudmsg, o chat (/gamechat, uma vez por segundo), os objetivos da batalha e o estado deles (/mission.json, a cada 10 s em batalha), linhas ditas antes de o watcher iniciar
- entre batalhas (hangar, carregamento), as respostas vão para uma sessão própria, marcada como `between_battles` no meta.json, que não tem linhas

**Não disponível**

- nomes, ids e alturas dos veículos de outros jogadores: o mapa web não os tem (os ids são dados aqui seguindo os objetos de consulta em consulta); o feed de abates nomeia jogadores sem posições
- tudo fora do mapa web: os replays do jogo são lidos pelo conversor de replays do War Thunder, e a memória do jogo nunca é lida (é um jogo online)
- /map_obj.json mais de duas vezes por segundo: a taxa de consulta é mantida baixa, para que o servidor web do próprio jogo não seja sobrecarregado

**Tamanho**: cerca de 50 a 120 MB por hora de JSON antes do zstd em batalha (map_obj de 5 a 15 KB duas vezes por segundo, state de cerca de 1,5 KB duas vezes por segundo, indicators a cada 2 s, chat e linhas do HUD pequenos) mais a imagem do mapa uma vez por batalha (menos de 2 MB); 1 a 2 MB por hora entre batalhas (a aparência do mapa duas vezes por segundo, HUD e chat uma vez, cada um uma resposta curta); o zstd reduz bem o JSON repetido, mais de dez vezes

## Verificado {#verified}

testado com um servidor local falso que serve respostas no formato do mapa web do jogo; não testado com o jogo em execução

## Fonte {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
