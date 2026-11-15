---
title: "Os dados"
nav_order: 5
lang: "pt"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Os dados {#the-data}

Todas as gravações são ficheiros simples na pasta de dados (`%LOCALAPPDATA%\3DHeat\Watcher`, a menos que seja
alterada, veja [Instalar e executar](installing-and-running.md#where-everything-is)). Podem ler-se, copiar-se ou
apagar-se sem o watcher. Um ficheiro `.jsonl` é texto simples, um evento por linha (abre-se no Bloco de Notas); um
ficheiro `.parquet` é uma tabela que o visualizador do 3DHeat abre (o Excel não - `stats --csv` grava ficheiros CSV
para folhas de cálculo).

## Pastas de sessão {#session-folders}
![uma pasta de sessão](../assets/img/session-folder.svg)


Uma **sessão** é um período de uso com uma fonte: desde o momento em que o jogo diz algo pela primeira vez até ele parar (o jogo fecha, uma
partida termina, uma corrida ou um voo é reiniciado - a página de cada adaptador diz o que começa e termina as sessões dele). Cada sessão ganha uma pasta:

```text
<dados>\sessions\<jogo>\<AAAA-MM-DD_HH-MM-SS>_<id do adaptador>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<jogo>` é o nome do jogo com cada carácter que não seja letra, dígito, `.`, `_` ou `-`
  substituído por `-` (no máximo 60 caracteres): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Os adaptadores que cobrem
  muitos jogos (estatísticas da Steam, Steam Timeline, destaques da NVIDIA) guardam cada sessão sob o jogo a que ela
  pertence.
- A hora é o início da sessão, na hora local. As sessões que descrevem o passado (um replay convertido depois da
  partida, um ficheiro de estatísticas da Steam) usam a hora que o jogo ou o ficheiro indica. Duas sessões que começam
  no mesmo segundo recebem `_2`, `_3`, ... no fim.
- O id da sessão, na base de dados de estatísticas, é `<pasta do jogo>/<pasta da sessão>`.

Uma sessão em que nada foi registado (o jogo ficou nos menus, ou bloqueou ao arrancar) é apagada quando fecha,
para que cada arranque não deixe uma pasta vazia.

Algumas sessões têm mais ficheiros. Uma sessão de demo do Counter-Strike 2 guarda a tabela e o resumo do próprio
conversor (`<mapa>/<partida>.parquet`, `<partida>.match.json`). Uma sessão do iRacing lista os ficheiros `.ibt` que o
simulador gravou durante o uso como eventos `telemetry_file`.

## events.jsonl {#eventsjsonl}

`events.jsonl` tem um objeto JSON por linha, uma linha por evento, gravada no momento em que o evento
acontece. O ficheiro tem buffer de linha, por isso uma queda, um corte de energia ou um processo terminado não perde nada
do que já foi gravado; uma linha cortada por uma queda é saltada na leitura, e todas as linhas antes dela ficam.

Toda linha tem as mesmas colunas básicas:

| Coluna | Tipo | O que é |
|---|---|---|
| `time` | número | segundos desde o início da sessão (4 casas decimais), ou o relógio do próprio jogo quando o adaptador o reencaminha |
| `ms` | inteiro | hora de relógio, milissegundos Unix |
| `event` | texto | o que aconteceu: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | número | onde, nas unidades e eixos próprios do jogo (veja `axes` em `meta.json`); presente só quando as três são conhecidas e finitas |
| `player` | texto | quem: um nome, um id, ou `me` para quem joga (veja [As linhas do próprio jogador](#the-players-own-rows)) |
| `team` | texto | o lado deles, quando o jogo informa |
| `session` | texto | a partida, ronda, fase, vida ou voo a que a linha pertence, quando o jogo informa |

Qualquer outro campo que o jogo informa segue com o próprio nome (`speed_kmh`, `gear`, `lap_time`, `weapon`,
`victim`, `hero`, ...). Os campos sem valor ficam de fora, e também os números que não são finitos.
Duas linhas de exemplo:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

As linhas sem posição (uma linha do feed de abates, uma subida de nível, uma mudança de estatística) ficam em `events.jsonl` e
contam nas estatísticas. Só as linhas com posição vão para a tabela.

### As linhas do próprio jogador {#the-players-own-rows}

Quais linhas são de quem joga é dito pela fonte, nunca adivinhado. Uma linha é a do jogador quando

- o `player` dela é `me`: a maioria dos adaptadores, cuja fonte é o próprio jogo do jogador (telemetria do carro ou
  avião próprio, uma integração de estado do jogo, um diário);
- ela traz `own_car` 1: os jogos de corrida que registam cada carro sob o nome do piloto (EA SPORTS F1 pelo
  índice de carro do jogador, RaceRoom pelo slot próprio, Automobilista 2 e Project CARS 2 pelo participante visto)
  marcam o carro do jogador desta forma e guardam o nome do piloto em `player`;
- o `player` dela é o `player` da sessão no `meta.json`: o nome que a fonte dá ao jogador - o comandante do Elite
  Dangerous (o diário é sempre do jogador), uma linha do Riot ID das configurações num replay do League of Legends.

War Thunder e Rocket League nomeiam todos os jogadores e não dizem qual é o jogador; com o nome dele na configuração
`player_names` (veja [Configurações](installing-and-running.md#settings)), as linhas dele passam a `me`.
[Destaques da NVIDIA](nvidia-highlights.md) procuram um momento exatamente nessas linhas.

## heat.parquet {#heatparquet}

Quando uma sessão fecha, as linhas de `events.jsonl` que têm `x`, `y` e `z` são gravadas em
`heat.parquet`. Esta é a tabela que o visualizador do 3DHeat abre. Se a sessão não tem posições, nenhuma
tabela é gravada.

- As colunas são `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, seguidas de todos os
  outros campos na ordem em que aparecem pela primeira vez.
- `x`, `y`, `z` e `time` são números de ponto flutuante de 64 bits e `ms` é um inteiro de 64 bits. Uma coluna
  extra cujos valores são todos números é um ponto flutuante de 64 bits; qualquer outra coluna é texto com
  codificação de dicionário (os valores em falta são texto vazio, e listas ou objetos são gravados como texto JSON).
- Os metadados do ficheiro têm uma chave `heat3d` com as instruções de leitura, para que o visualizador associe as colunas
  e os eixos sozinho (um exemplo, com a lista `extra` encurtada):

```json
{
  "version": 1,
  "kind": "heat3d-watch",
  "game": "EA SPORTS F1 25",
  "axes": {"up": "y", "flipX": false, "flipY": false, "flipZ": false, "scale": 1.0},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player", "teamId": "team", "sessionId": "session",
    "extra": ["event", "speed_kmh", "gear", "lap_time", "lap"]
  }
}
```

`up` é o eixo para cima do jogo, `flipX`/`flipY`/`flipZ` espelham um eixo para que um mundo de mão esquerda não
apareça espelhado, e `scale` é a escala de unidade do visualizador: o visualizador multiplica cada posição por ela ao
carregar a tabela (0,01 transformaria centímetros em metros). Todo adaptador grava 1 e mantém as unidades próprias do
jogo - metros para a maioria, unidades Source (polegadas) para o Counter-Strike 2, unidades Unreal (centímetros) para o
Rocket League - porque um nível exportado do jogo está nessas mesmas unidades, então as linhas caem sobre ele; as
tabelas próprias do conversor do CS2 dizem o mesmo. `units` em `meta.json` diz o que é uma unidade. A página de cada
jogo lista os valores dele em "Posições e eixos".

Os simuladores de voo (DCS World, Microsoft Flight Simulator, X-Plane, as gravações Tacview do IL-2) põem as linhas sobre a Terra, e o rodapé diz onde, para que o visualizador possa colocar o mundo real por baixo:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (graus) são a origem do mapa plano em que as linhas estão; `east`, `north` e `up` dizem quais colunas
guardam os metros a leste e a norte dela e a altitude acima do nível do mar. A origem é a primeira posição obtida para
o X-Plane e o MSFS, o ponto de referência da gravação para o IL-2, e a origem fixa do teatro para o DCS (a primeira posição
arredondada para graus inteiros, num teatro que o watcher não conhece). Uma tabela sem um lugar na Terra não tem
a chave `geo`, e o resto do rodapé é o mesmo de qualquer forma.

`heat.parquet` pode sempre ser recriado a partir de `events.jsonl` com
`python -m heat3d_watch table <pasta da sessão>` (veja [Comandos](commands.md#table)). Isto é útil quando
o `pyarrow` estava em falta enquanto a sessão era gravada.

## meta.json {#metajson}

`meta.json` resume a sessão. É escrito quando a sessão abre, no máximo a cada 30 segundos enquanto chegam eventos ou
estatísticas, e quando a sessão fecha. As estatísticas só ficam na memória entre essas gravações, por isso uma queda pode
perder no máximo o último meio minuto delas.

```json
{
  "format": "heat3d-watch-session",
  "version": 1,
  "watcher": "1.0.2",
  "game": "EA SPORTS F1 25",
  "adapter": "f1-25",
  "source": "UDP telemetry 127.0.0.1:20777 (...)",
  "multiplayer": true,
  "started": "2026-05-01T20:15:03",
  "ended": "2026-05-01T21:02:11",
  "seconds": 2828.0,
  "axes": {"up": "y", "flip_x": false, "flip_y": false, "flip_z": false, "scale": 1.0, "units": "metres"},
  "events": {"position": 52110, "lap": 412, "teleport": 3},
  "positions": 52530,
  "stats": {"laps": 20, "best_lap": 91.874, "distance_km": 106.3, "race_position": 4},
  "track": "..."
}
```

Uma sessão cuja fonte nomeia o jogador (veja [As linhas do próprio jogador](#the-players-own-rows)) também tem
`"player"`: o nome que as linhas do jogador carregam. Uma sessão sobre a Terra (os simuladores de voo) também tem
`"geo": {"lat0": .., "lon0": ..}`, a origem que o `geo` do rodapé repete.

- `started` / `ended`: hora local até ao segundo; `ended` é `null` enquanto a sessão corre.
- `events`: quantas vezes cada evento aconteceu, do mais frequente para o menos. `positions` é o número de linhas
  com posição.
- `stats`: os números da sessão. Um adaptador define cada um, soma-lhe valores, ou guarda o máximo ou o mínimo.
- O que mais o adaptador sabe sobre a sessão aparece no nível de cima: a pista, o mapa, a missão,
  o id da partida, o id da aplicação da Steam, o ficheiro do replay, o perfil de memória e a versão. Uma sessão terminada
  pela recuperação tem `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` é a base de dados de estatísticas. Uma linha é adicionada para cada sessão quando ela fecha. As
três tabelas são simples, por isso qualquer ferramenta SQL, caderno ou folha de cálculo pode lê-las sem o watcher:

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,          -- <pasta do jogo>/<pasta da sessão>
  game TEXT NOT NULL,
  adapter TEXT NOT NULL,
  started REAL NOT NULL,        -- segundos Unix
  ended REAL,                   -- segundos Unix
  seconds REAL,
  folder TEXT NOT NULL,         -- o caminho completo da pasta da sessão
  events INTEGER NOT NULL DEFAULT 0,
  positions INTEGER NOT NULL DEFAULT 0,
  multiplayer INTEGER NOT NULL DEFAULT 0,
  source TEXT
);
CREATE TABLE events (           -- por sessão, quantas vezes cada evento aconteceu
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (session, event)
);
CREATE TABLE stats (            -- por sessão, cada número que o jogo informou ou o watcher contou
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- números
  text TEXT,                    -- todo o resto (um nome de mapa, um resultado, um herói)
  PRIMARY KEY (session, key)
);
```

Gravar uma sessão de novo (recuperação, um replay convertido de novo) substitui as linhas dela. `multiplayer` é o
indicador do adaptador (alguns adaptadores o definem por sessão, por exemplo o DCS pela missão), não uma verificação
de se o jogador estava online. Um valor verdadeiro/falso em `stats` é guardado como texto.

Um exemplo de consulta, a melhor volta por jogo entre todas as sessões (menor é melhor):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` mostra os totais dessas tabelas (veja [Comandos](commands.md#stats)); a coluna `best`
é o menor valor para tempos guardados como melhor e para classificações, o maior para o resto.

## Recuperação depois de uma queda {#recovery-after-a-crash}

Quando o `run` inicia, procura sessões que um watcher anterior deixou abertas: um `meta.json` sem
`ended`, e um `events.jsonl` com pelo menos uma linha. Termina cada uma:

- as contagens de eventos e o número de posições são contados de novo a partir do `events.jsonl`, a saltar uma linha
  cortada;
- o fim é a hora de relógio da última linha (`ms`);
- as estatísticas são as da última gravação do `meta.json` (com no máximo 30 segundos);
- `"recovered": true` é acrescentado, o `heat.parquet` é gravado, e a sessão entra no `watcher.sqlite`.

O log diz "finished N session(s) left open by an earlier run". O ficheiro de bloqueio impede que um
watcher a correr "recupere" as sessões de outro.

## Exportação CSV {#csv-export}
![stats --csv e table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

grava `out\sessions.csv`, `out\events.csv` e `out\stats.csv`. Cada ficheiro é uma tabela do
`watcher.sqlite`, completa, com uma linha de cabeçalho, em UTF-8. Os tempos são segundos Unix, como na base de dados.
`--game` não restringe a exportação; todas as sessões são escritas.

## Abrir uma sessão no visualizador do 3DHeat {#opening-a-session-in-the-3dheat-viewer}

O visualizador: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), documentação em
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - a página do
[contentor `.3dheat`](https://holdi601.github.io/3DHeat/container.html) descreve o formato de um ficheiro por partida
que os conversores de replay podem gravar.

Abra o `heat.parquet` de uma sessão no visualizador do 3DHeat. O rodapé diz ao visualizador qual coluna é a
posição, o tempo, o jogador, a equipa e a sessão, e qual é o eixo para cima, por isso nada precisa de ser associado
à mão. As posições estão nas coordenadas próprias do mundo do jogo. Desenhadas sobre um nível exportado com as
outras ferramentas do 3DHeat (por exemplo do [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)),
caem onde aconteceram.

- **Mapas de calor** usam cada linha com uma posição, filtradas por `event`, `player`, `team` ou `session` como qualquer
  outra coluna.
- **Mapa de calor de linhas** desenha uma linha de cada posição de um jogador até à seguinte, e na reprodução cada
  jogador é um ponto que se move ao longo da rota, com uma cauda atrás dele. O painel Percursos do visualizador escolhe,
  pela coluna `event`, quais eventos **começam** uma rota e quais a **terminam**. O watcher grava os eventos
  delimitadores como linhas com posição, para que possam ser escolhidos ali:
  - inícios: `spawn`, `respawn`, `session_start`. Um início fecha a rota que estava aberta sem desenhar uma linha até ao
    novo lugar.
  - fins: `death`, `finish`, `session_end` e `teleport`. A linha vai até à própria linha de fim, que é onde o
    jogador morreu, parou ou foi levado embora.

  Um salto - um lugar alcançado sem percorrer o caminho até lá - são duas linhas: `teleport` no lugar **deixado**, e um
  início no lugar **chegado**, logo depois. Os adaptadores de corrida gravam um sempre que o carro andou mais do que
  poderia ter conduzido (um rewind ou flashback, um reset para a estrada, de volta às boxes, uma viagem rápida), com
  `spawn` na chegada (`respawn` para o reset do BeamNG); a linha `teleport` traz a chegada como `to_x`, `to_y`, `to_z` e
  a distância como `metres`, a linha de início traz `after: "teleport"`. Os adaptadores de camião fazem o mesmo
  para uma balsa, um comboio ou uma gravação de jogo carregada, e os adaptadores de voo para um salto que nenhuma aeronave poderia
  fazer. Assim, com `teleport` entre os fins e `spawn` entre os inícios - que é o que o visualizador sugere
  por conta própria - uma rota termina onde o salto deixou e a próxima começa onde ele chegou, e nenhuma linha
  atravessa o mapa. Uma rota nunca atravessa uma mudança na coluna `session`. Uma linha de posição é gravada algumas
  vezes por segundo (10 Hz para a maioria das telemetrias), o que dá uma linha suave.
- A coluna `session` divide uma sessão em rondas, fases, vidas ou corpos (o Elite Dangerous separa desta forma as linhas da galáxia e as linhas da superfície de cada planeta). Escolha uma no visualizador para ver só essa parte.

O que o visualizador faz com as linhas - filtros, cores, reprodução - é descrito na documentação própria dele.
As sessões de demo do Counter-Strike 2 são abertas pelo `<mapa>/<partida>.parquet` e pelo `<partida>.match.json` do conversor
nos separadores Mapa de calor e Partida do visualizador. As posições do iRacing vêm dos ficheiros `.ibt` listados na sessão, que o
próprio visualizador lê.
