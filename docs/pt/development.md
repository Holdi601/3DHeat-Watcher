---
title: "Desenvolvimento"
nav_order: 12
lang: "pt"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Desenvolvimento {#development}

Esta página serve para acrescentar um jogo: como se faz um adaptador, como é testado e como a
documentação dele é gerada.

## O repositório {#the-repository}

| Caminho | O que contém |
|---|---|
| `heat3d_watch/cli.py` | os comandos ([Comandos](commands.md)) |
| `heat3d_watch/watcher.py` | o ciclo em segundo plano: lista de processos, uma thread por adaptador, atualizações |
| `heat3d_watch/session.py` | uma gravação: `events.jsonl`, `heat.parquet`, `meta.json`, recuperação |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | as configurações e a pasta de dados |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | as verificações de memória e o leitor só de leitura ([Ler a memória](memory-reading.md)) |
| `heat3d_watch/notify.py` | notificações do Windows |
| `heat3d_watch/adapters/` | um módulo por jogo ou família de jogos; módulos que começam com `_` são auxiliares partilhados |
| `heat3d_watch/decoders/` | os descodificadores de telemetria de corrida, copiados dos gravadores de voltas do 3DHeat GameCapture |
| `heat3d_update/` | o atualizador ([Atualizações](updates.md)) |
| `mods/beamng/heat3d/` | o mod de protocolo do BeamNG que `setup beamng` instala |
| `tests/` | os testes |
| `tools/gen_game_pages.py` | gera as páginas de jogos desta documentação |

## Um adaptador {#an-adapter}

Um adaptador é uma dataclass derivada de `heat3d_watch.adapters.base.Adapter`. Os campos dizem o que ele
é; os métodos fazem o trabalho.

| Campo | Predefinição | O que é |
|---|---|---|
| `id` | `""` | curto e estável: as pastas de sessão, `disabled`, `replay_folders` e `player_names` referem-se a ele |
| `game` | `""` | o nome do jogo como as pessoas o escrevem; as sessões são guardadas sob ele |
| `kind` | `"telemetry"` | um de `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Fontes e regras](sources-and-rules.md)) |
| `exes` | `()` | nomes de executável (sem distinguir maiúsculas) que significam que o jogo está a correr. Vazio: o adaptador fica sempre ligado (`always` é verdadeiro) |
| `multiplayer` | `True` | o jogo é jogado online: a memória dele nunca é lida |
| `source` | `""` | de onde vêm os números, dito uma vez |
| `records` | `()` | o que é registado, um item por tipo de coisa |
| `enable` | `""` | como ligar a fonte; vazio quando não é preciso nada |
| `interval` | `0.1` | segundos entre as consultas |
| `axes` | `Axes()` | o eixo para cima do mundo, os eixos espelhados, a escala de unidade do visualizador (mantenha 1) e uma nota sobre as unidades |
| `verified` | `""` | o que foi verificado, com honestidade (veja abaixo) |
| `completeness` | `{}` | o relato da fonte segundo a [regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: `read` (o que passa a linhas), `raw` (o que é guardado inteiro, sob qual `type`), `missing` (o que a fonte não dá, e porquê), `size` (quanto ocupa por hora o fluxo bruto). A secção "Completeness" da página do jogo é escrita a partir disso |

`source`, `records`, `enable`, `verified` e `completeness` são documentação, não enfeite. `games` mostra-os,
`games --markdown` gera a tabela em [Todos os jogos numa tabela](watcher.md), e as páginas dos jogos são
geradas a partir deles. Escreva-os para dizer exatamente o que o código faz.

Os métodos, todos opcionais:

| Método | Chamado | O que deve fazer |
|---|---|---|
| `missing(self) -> str \| None` | por `games`, `status` e antes de iniciar | dizer porque é que o adaptador não pode correr aqui (uma DLL não encontrada, uma pasta em falta), ou `None` |
| `setup(self, ctx, *, apply) -> list[str]` | por `setup` | ligar a saída do jogo; devolver uma linha por alteração, e alterar ficheiros só quando `apply` for verdadeiro. Guardar um ficheiro como `<ficheiro>.heat3d-backup` antes da primeira alteração, e nunca substituir essa cópia. Substitua só quando há algo a ligar: `can_setup` (verdadeiro quando `setup` é substituído) decide se `setup` o executa ou diz que não há nada a mudar; uma classe que abrange vários jogos substitui `can_setup` para os que não consegue configurar (`RallyAdapter` para Richard Burns Rally). |
| `start(self, ctx)` | quando o processo do jogo aparece (adaptadores sempre ligados: quando o `run` arranca) | abrir sockets, encontrar ficheiros, lembrar de onde começar |
| `poll(self, ctx)` | a cada `interval` segundos, na thread própria do adaptador | apanhar o que o jogo disse desde a última consulta e registar |
| `stop(self, ctx)` | quando o jogo sai ou o watcher para | fechar sessões e sockets |

Cada adaptador corre na própria thread (`Runner`). Uma exceção em `poll` é registada e o adaptador espera
`min(5, interval × 10 + 0.5)` segundos antes da próxima consulta. Depois de 20 falhas seguidas, ou uma falha em
`start`, o adaptador é parado e não volta a ser iniciado até o id do processo do jogo mudar.
`missing()` é verificado a cada análise, por isso mantenha-o barato.

Um objeto adaptador é reutilizado quando o jogo volta a ser iniciado, por isso `start` tem de repor tudo o que uma
execução anterior deixou.

### Registar {#registering-it}

Coloque o módulo em `heat3d_watch/adapters/` e liste os adaptadores no fim dele:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importa cada módulo do pacote (exceto `base` e nomes que começam com `_`) e
reúne os `ADAPTERS` deles. Dois adaptadores com o mesmo id interrompem o carregamento com um `ValueError`. Um módulo que
falha ao importar (uma dependência em falta) deixa os seus jogos de fora e é indicado por `games` com o
erro, assim, o problema de um jogo não para os outros.

## Contexto e Sessão {#context-and-session}

`start`, `poll`, `stop` e `setup` recebem um `Context`:

| Membro | O que é |
|---|---|
| `settings` | o `Settings` ([Instalar e executar](installing-and-running.md#settings)) |
| `data` | a pasta de dados |
| `pid`, `exe` | o id do processo do jogo e o caminho do executável, quando o adaptador foi iniciado para um jogo a correr; a pasta de instalação fica ao lado de `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | uma nova `Session`. `game` substitui o nome do jogo do adaptador (para adaptadores que abrangem muitos jogos); `when` define o início para sessões que descrevem o passado; `axes`, `source` e `multiplayer` usam por predefinição os do adaptador; `meta` é um dicionário guardado em `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, ou defina `session.geo` depois) coloca uma sessão de mapa plano na Terra, em `meta.json` e no rodapé da tabela |
| `close(session)` | fecha uma sessão: a tabela, `heat.raw.parquet`, `meta.json`, a linha dela em `watcher.sqlite`. Uma sessão sem eventos nem itens brutos é apagada; uma com só itens brutos é mantida (sem tabela, sem linha na base de dados). Aceita `None`. Devolve o caminho da tabela ou `None`. |

Uma `Session` regista:

| Membro | O que faz |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | uma linha. `t` por predefinição são os segundos desde o início da sessão, `ms` é o agora. Uma posição conta só quando `x`, `y` e `z` são todos dados e finitos. Atributos `None` são deixados de fora. |
| `position(x, y, z, **kw)` | um evento chamado `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | guardar uma coisa que a fonte enviou, inteira: os bytes de um pacote ou página (`payload`), uma linha ou uma resposta JSON como veio (`text`), ou os valores de uma leitura pelo nome (`fields`, cada um com a própria coluna). `type` é a palavra da fonte para isso (um id de pacote, o nome de um mapeamento, um evento de diário, um endpoint); `used` diz que também passou a linhas. Empacotado em `raw.bin` no momento da chamada, gravado como `heat.raw.parquet` (zstd) quando a sessão fecha ou é recuperada, e contado por `type` em `selfCheck.completeness` do `meta.json` |
| `stat(key, value, how="set")` | uma estatística: `set` a define, `add` soma-lhe valores, guarda o `max` ou o `min` |
| `now()` | segundos desde o início da sessão |
| `meta` | um dicionário gravado em `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | quando, onde, e o que foi registado até agora |

`event`, `stat` e `raw` são seguros entre threads e podem ser chamados de uma thread de trabalho.

**Cada adaptador guarda tudo o que a fonte envia.** As linhas são o que o visualizador desenha; elas não são o
registo. Cada pacote que chega a uma porta, cada página de memória partilhada lida (o mapeamento inteiro,
a cada mudança), cada linha de um log ou script de exportação (inclusive as que o adaptador ignora), cada
resposta JSON ou documento enviado vai para `session.raw(...)` assim que chega - tenha ou não passado a linha -
e nada é reduzido abaixo da taxa em que o adaptador lê. Um item que chega antes de uma sessão estar
aberta abre uma (uma sessão com só itens brutos é mantida), ou fica retido até uma ser aberta; nunca é descartado.
Campos baratos de descodificar e certos no significado também passam a linhas. Esta é a
[regra de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) do 3DHeat: um feed ao vivo
desaparece no instante em que é enviado, por isso o que um adaptador não guarda perde-se para sempre, e o que ele guarda
inteiro pode ser descodificado no dia em que alguém o entender. O tamanho é o preço; zstd e codificação por
dicionário mantêm isso baixo, em vez de deixar coisas de fora. O teste de cada adaptador envia algo que ele não usa
e verifica que volta inteiro de `heat.raw.parquet`, e que `selfCheck.completeness.lost` é 0. `racing.Driving.raw`
faz o mesmo pelos adaptadores de corrida (e abre a sessão), e `racing.Pages` guarda páginas de memória
partilhada sempre que os bytes mudam, a contar as releituras que não encontraram nada de novo em `unchanged_reads`
no `meta.json`.

Convenções das quais o resto do sistema depende:

- **As linhas do próprio jogador são marcadas, pelo que a fonte diz.** `player="me"` onde a fonte é o próprio
  jogador; onde todo jogador é registado sob um nome, `own_car=1` nas linhas do carro do jogador (pelo índice de
  jogador do jogo ou pelo participante visto), ou o nome do jogador como `session.meta["player"]`
  (gravado em `meta.json` logo) quando a fonte nomeia o jogador. Nunca adivinhe: onde a fonte não diz, use o
  nome de uma configuração (`player_names`, `riot_id`) ou não marque nada.
  [Destaques da NVIDIA](nvidia-highlights.md) recebem posições só dessas linhas (`platform.own_row`). Os outros
  jogadores são identificados pelo nome ou pelo id.
- **As rotas são delimitadas por eventos com posições**: `spawn`, `respawn` e `session_start` começam uma;
  `death`, `finish`, `session_end` e `teleport` a terminam. Sempre que o jogador se moveu sem viajar (um reset, um
  rewind, uma viagem rápida, uma gravação de jogo carregada), escreva `teleport` no lugar deixado e depois um início
  (`spawn`, ou `respawn` para um reset que o jogo nomeia) no lugar chegado, para que o mapa de calor de linhas
  do visualizador termine uma rota e comece a próxima, em vez de atravessar o mapa com um traço. `Driving.jumped` faz isso
  para veículos.
- **As posições ficam nas coordenadas e unidades do próprio mundo do jogo**, descritas por `axes`. Não as converta
  para outro referencial, a não ser que o jogo não dê um referencial de mundo utilizável (os simuladores de voo
  põem latitude e longitude num mapa plano, `Tangent`, em torno da primeira posição (fix) - o DCS em torno da origem fixa
  do teatro - e passam `geo=tangent.geo()` para `open`, para que o rodapé diga onde na Terra
  fica o mapa). `axes.scale` é a escala de unidade do visualizador - ele multiplica cada posição por ela - e fica
  em 1, para que as linhas se alinhem com um nível exportado do mesmo jogo nas mesmas unidades; indique a unidade em
  `axes.units`.
- **As chaves de estatística** são minúsculas com sublinhados, e levam a unidade quando há uma
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Um tempo guardado como melhor começa com
  `best_` (guardado com `min`), uma classificação termina em `_position`: `stats` mostra o menor desses como o
  melhor, e o maior de cada outra chave (`db.lower_is_better`).

## Auxiliares {#helpers}

| Auxiliar | Módulo | Para |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | acompanhar um log que o jogo escreve: leituras partilhadas, só as linhas desta sessão, ficheiros novos e substituídos, só linhas inteiras |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` com `try_open(who)`, `receive()`, `close()` | `racing` | uma porta UDP de telemetria em 127.0.0.1, usada só quando livre, cedida a outro programa, opcionalmente reencaminhada |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` com `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | sessões de veículo: posições em taxa fixa, distância, velocidade máxima, voltas; num salto, `teleport` onde o carro estava e `spawn` onde ele está (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | a memória partilhada com nome de um jogo, só leitura, nunca criada |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | uma pasta de replays observada: ficheiros convertidos quando param de crescer, numa thread de trabalho; a primeira vista só regista o que lá está, e `convert_existing(ctx, folder=None)` - o comando [`replays`](commands.md#replays) - converte esses a pedido |
| `load_state`, `save_state` | `platform` | lembrar o que um adaptador sempre ligado já viu, em `<dados>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | registo de voos (descolagens, aterragens, quedas, distância) e o mapa plano em torno da primeira posição (fix) (`Tangent.geo()` é o `geo` da sessão) |
| `backup_once(path)` | `gsi`, `racing` | a regra do `<ficheiro>.heat3d-backup` |
| Os ficheiros da Steam | `_steam` | KeyValues binários e de texto, a pasta da Steam pelo registo |

Um adaptador de log mínimo, como ilustração (um jogo inventado):

```python
from dataclasses import dataclass, field
from pathlib import Path

from ..session import Axes, Session
from ._logfollow import Follower, game_started, newest
from .base import Adapter, Context


@dataclass
class ExampleAdapter(Adapter):
    _session: Session | None = field(default=None, repr=False)
    _follow: Follower | None = field(default=None, repr=False)

    def start(self, ctx: Context) -> None:
        log = (ctx.exe.parent if ctx.exe else Path(".")) / "logs" / "game.log"
        self._session = None
        self._follow = Follower(lambda: newest(p for p in [log] if p.exists()), game_started(ctx.pid))

    def poll(self, ctx: Context) -> None:
        for line in self._follow.lines() if self._follow else []:
            if line.startswith("DIED "):
                if self._session is None:
                    self._session = ctx.open(self)
                self._session.event("death", player="me")
                self._session.stat("deaths", 1, "add")

    def stop(self, ctx: Context) -> None:
        self.poll(ctx)
        ctx.close(self._session)
        self._session = None


ADAPTERS = [
    ExampleAdapter(
        id="example",
        game="Example Game",
        kind="log",
        exes=("ExampleGame.exe",),
        source=r"<install>\logs\game.log (followed)",
        records=("deaths",),
        interval=0.5,
        axes=Axes(units="no positions recorded"),
        verified="tested on synthetic log lines in the game's format; untested against the game",
    )
]
```

Abra a sessão com a primeira coisa que vale a pena registar, não em `start`, para que um jogo parado nos
menus não deixe nada para trás (uma sessão vazia é apagada de qualquer forma).

## Testes {#tests}

```bash
python -m pytest
```

`tests/conftest.py` dá a cada teste uma pasta de dados descartável (`HEAT3D_WATCH_HOME`) e desliga as
verificações de atualização e as notificações (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Um teste de adaptador monta a
saída do jogo a partir do formato publicado - pacotes da especificação, linhas de log no formato do jogo, ficheiros no
layout documentado - e dirige o adaptador diretamente (resumido de
`tests/test_poe.py`; `data` e `install` são pastas temporárias):

```python
from dataclasses import replace
from heat3d_watch.adapters import poe
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

ctx = Context(Settings(data=str(data)), data, exe=install / "PathOfExileSteam.exe")
a = replace(poe.ADAPTERS[0])   # uma cópia nova do adaptador
a.start(ctx); a.poll(ctx); a.stop(ctx)
[session] = list((data / "sessions").glob("*/*"))
rows = read_rows(session)      # depois verifique as linhas e as estatísticas do meta.json
```

Adaptadores de rede são testados contra um servidor local falso ou com pacotes enviados por UDP ao adaptador.
Testes que verificam com dados reais de jogo no computador do programador são marcados com `@pytest.mark.local` e
são saltados onde esses dados não existem. Esses dados nunca entram no repositório. `test_core.py` também
tem o teste que falha se algum código capaz de escrever noutro processo aparecer no pacote
(`test_memory_reading_cannot_write`).

## Um `verified` honesto {#an-honest-verified}

`verified` diz o que foi verificado e como, e o que não foi. Ele é mostrado por `games` e em cada página de
jogo, e as pessoas apoiam-se nele. Exemplos tirados do código:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the
  running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format"

Diga "untested against the game" até que o adaptador tenha registado o jogo a correr. Diga só o método e a
tolerância: nunca um mapa, id de partida, nome de jogador, data, tamanho de amostra ou contagem exata de ficheiros
reais, e nunca "esta máquina" (os leitores não conhecem o computador). Nomeie a fonte de
cada deslocamento e layout, e diga onde duas fontes foram comparadas. Nunca afirme mais do que foi feito. Um
formato que foi adivinhado ou tirado de ferramentas da comunidade é dito como tal.

## As páginas dos jogos {#the-game-pages}

Cada página em [Jogos](games.md) é gerada a partir dos adaptadores, por isso coincide sempre com o código. Depois de
adicionar ou alterar um adaptador, gere-as de novo a partir da pasta do repositório:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(No PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Acrescente `--check` para só
comparar: ele não escreve nada e sai com 1 quando uma página está desatualizada (também a tabela de jogos de
`docs/watcher.md`).

O script:

- carrega os adaptadores com `heat3d_watch.adapters.load()`, contra uma pasta de dados temporária vazia, para que
  nenhum perfil de memória ou configuração do computador de quem gera entre nas páginas. Adaptadores de memória ficam de fora,
  pois vêm dos perfis próprios de cada jogador;
- recusa-se a escrever seja o que for se um módulo de adaptador falha ao importar (as páginas perderiam esses jogos);
- escreve `docs/game-<id do adaptador>.md` para cada adaptador e `docs/games.md` com a tabela geral, e apaga as
  páginas de adaptadores que já não existem;
- retira "What is recorded", "Where it comes from", "How to switch it on", os eixos, o
  indicador de multijogador e "Verified" dos campos do adaptador;
- transforma a docstring do módulo em "How it works". Escreva docstrings no estilo de texto simples que os
  módulos já usam, que o script converte: parágrafos; listas com `*`, `-` ou `1.`; layouts e
  exemplos recuados sob a linha que os introduz (viram blocos de código); um título sublinhado
  com traços, ou uma linha de título curta com o texto recuado logo abaixo (viram títulos);
- lista as chaves de estatística que o código do adaptador define pelo nome - `.stat("key", ...)`, os dois lados de uma
  expressão `if`, e padrões de f-string como `score.{team}` - nas classes do adaptador e nos
  auxiliares que elas usam. Chaves tiradas de uma variável (uma tabela dos campos do jogo) não são listadas;
- decide "Positions" pelo `axes.units` do adaptador (uma nota que começa com "no" ou "none" significa sem posições) e
  pelo que o código dele grava.

Não edite as páginas geradas à mão: altere o adaptador e corra o script de novo. A tabela em
[Todos os jogos numa tabela](watcher.md) é a saída de `python -m heat3d_watch games --markdown`.
