---
title: "Développement"
nav_order: 12
lang: "fr"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Développement {#development}

Cette page est destinée à l'ajout d'un jeu : comment un adaptateur est construit, comment il est testé, et comment sa
documentation est produite.

## Le dépôt {#the-repository}

| Chemin | Ce qu'il contient |
|---|---|
| `heat3d_watch/cli.py` | les commandes ([Commandes](commands.md)) |
| `heat3d_watch/watcher.py` | la boucle en arrière-plan : liste des processus, un thread par adaptateur, mises à jour |
| `heat3d_watch/session.py` | un enregistrement : `events.jsonl`, `heat.parquet`, `meta.json`, récupération |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | les réglages et le dossier de données |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | les contrôles de mémoire et le lecteur en lecture seule ([Lecture de la mémoire](memory-reading.md)) |
| `heat3d_watch/notify.py` | notifications Windows |
| `heat3d_watch/adapters/` | un module par jeu ou famille de jeux ; les modules dont le nom commence par `_` sont des aides partagées |
| `heat3d_watch/decoders/` | les décodeurs de télémétrie de course, copiés des enregistreurs de tours de 3DHeat GameCapture |
| `heat3d_update/` | le programme de mise à jour ([Mises à jour](updates.md)) |
| `mods/beamng/heat3d/` | le mod de protocole BeamNG que `setup beamng` installe |
| `tests/` | les tests |
| `tools/gen_game_pages.py` | écrit les pages de jeux de cette documentation |

## Un adaptateur {#an-adapter}

Un adaptateur est une dataclass dérivée de `heat3d_watch.adapters.base.Adapter`. Ses champs disent ce qu'il
est ; ses méthodes font le travail.

| Champ | Valeur par défaut | Ce que c'est |
|---|---|---|
| `id` | `""` | court et stable : les dossiers de session, `disabled`, `replay_folders` et `player_names` s'y réfèrent |
| `game` | `""` | le nom du jeu tel que les gens l'écrivent ; les sessions sont classées sous ce nom |
| `kind` | `"telemetry"` | l'un de `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Sources et règles](sources-and-rules.md)) |
| `exes` | `()` | noms d'exécutables (quelle que soit la casse) qui signifient que le jeu tourne. Vide : l'adaptateur est toujours actif (`always` vaut vrai) |
| `multiplayer` | `True` | le jeu se joue en ligne : sa mémoire n'est jamais lue |
| `source` | `""` | d'où viennent les nombres, dit une fois |
| `records` | `()` | ce qui est enregistré, un élément par type de chose |
| `enable` | `""` | comment activer la source ; vide quand rien n'est nécessaire |
| `interval` | `0.1` | secondes entre deux interrogations |
| `axes` | `Axes()` | l'axe vertical du monde, les axes en miroir, l'échelle d'unité du visualiseur (garder 1) et une note sur les unités |
| `verified` | `""` | ce qui a été vérifié, honnêtement (voir plus bas) |
| `completeness` | `{}` | le récit de la source selon la [règle de convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : `read` (ce qui devient des lignes), `raw` (ce qui est gardé entier, sous quel `type`), `missing` (ce que la source ne donne pas, et pourquoi), `size` (la taille du flux brut en une heure). La section « Completeness » de la page du jeu en est issue |

`source`, `records`, `enable`, `verified` et `completeness` sont de la documentation, pas de la décoration. `games` les affiche,
`games --markdown` produit le tableau de [Tous les jeux dans un seul tableau](watcher.md), et les pages de jeux
sont générées à partir d'eux. Écrivez-les pour qu'elles disent exactement ce que fait le code.

Les méthodes, toutes facultatives :

| Méthode | Appelée | Ce qu'elle doit faire |
|---|---|---|
| `missing(self) -> str \| None` | par `games`, `status`, et avant le démarrage | dire pourquoi l'adaptateur ne peut pas tourner ici (une DLL introuvable, un dossier manquant), ou `None` |
| `setup(self, ctx, *, apply) -> list[str]` | par `setup` | activer la sortie de données du jeu ; renvoyer une ligne par changement, et ne modifier les fichiers que si `apply` est vrai. Sauvegarder un fichier sous `<file>.heat3d-backup` avant sa première modification, et ne jamais écraser cette sauvegarde. Ne la redéfinir que s'il y a quelque chose à activer : `can_setup` (vrai quand `setup` est redéfinie) décide si `setup` l'exécute ou dit qu'il n'y a rien à changer ; une classe qui sert plusieurs jeux redéfinit `can_setup` pour ceux qu'elle ne peut pas configurer (`RallyAdapter` pour Richard Burns Rally). |
| `start(self, ctx)` | quand le processus du jeu apparaît (adaptateurs toujours actifs : quand `run` démarre) | ouvrir les sockets, trouver les fichiers, mémoriser où commencer |
| `poll(self, ctx)` | toutes les `interval` secondes, dans le thread propre de l'adaptateur | prendre ce que le jeu a dit depuis la dernière interrogation et l'enregistrer |
| `stop(self, ctx)` | quand le jeu a disparu ou que le watcher s'arrête | fermer les sessions et les sockets |

Chaque adaptateur tourne dans son propre thread (`Runner`). Une exception dans `poll` est journalisée et l'adaptateur attend
`min(5, interval × 10 + 0.5)` secondes avant la prochaine interrogation. Après 20 échecs d'affilée, ou un échec dans
`start`, l'adaptateur est arrêté et n'est pas redémarré tant que l'identifiant du processus du jeu ne change pas.
`missing()` est vérifié à chaque analyse, donc gardez-la légère.

Un objet adaptateur est réutilisé quand son jeu redémarre ; `start` doit donc réinitialiser tout ce qu'une exécution
précédente a laissé.

### L'enregistrer {#registering-it}

Mettez le module dans `heat3d_watch/adapters/` et listez les adaptateurs à sa fin :

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importe chaque module du paquet (sauf `base` et les noms commençant par `_`) et
récupère leurs `ADAPTERS`. Deux adaptateurs avec le même identifiant arrêtent le chargement avec une `ValueError`. Un module qui
ne peut pas être importé (une dépendance manquante) exclut ses jeux et est signalé par `games` avec l'erreur, pour que
le problème d'un jeu n'arrête pas les autres.

## Contexte et Session {#context-and-session}

`start`, `poll`, `stop` et `setup` reçoivent un `Context` :

| Membre | Ce que c'est |
|---|---|
| `settings` | le `Settings` ([Installation et lancement](installing-and-running.md#settings)) |
| `data` | le dossier de données |
| `pid`, `exe` | l'identifiant du processus du jeu et le chemin de l'exécutable, quand l'adaptateur a été lancé pour un jeu en cours ; le dossier d'installation est à côté de `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | une nouvelle `Session`. `game` remplace le nom de jeu de l'adaptateur (pour les adaptateurs qui couvrent plusieurs jeux) ; `when` fixe le début pour les sessions qui décrivent le passé ; `axes`, `source` et `multiplayer` prennent par défaut ceux de l'adaptateur ; `meta` est un dictionnaire écrit dans `meta.json` ; `geo` (`{"lat0": .., "lon0": ..}`, ou à définir plus tard avec `session.geo`) place une session de carte plate sur la Terre, dans `meta.json` et le pied de page du tableau |
| `close(session)` | termine une session : le tableau, `heat.raw.parquet`, `meta.json`, sa ligne dans `watcher.sqlite`. Une session sans événements ni éléments bruts est supprimée ; une session qui n'a que des éléments bruts est conservée (pas de tableau, pas de ligne dans la base). Accepte `None`. Renvoie le chemin du tableau ou `None`. |

Une `Session` enregistre :

| Membre | Ce qu'il fait |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | une ligne. `t` vaut par défaut les secondes depuis le début de la session, `ms` l'instant présent. Une position ne compte que lorsque `x`, `y` et `z` sont tous donnés et finis. Les attributs `None` sont omis. |
| `position(x, y, z, **kw)` | un événement nommé `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | garder une chose envoyée par la source, entière : les octets d'un paquet ou d'une page (`payload`), une ligne ou une réponse JSON telle qu'elle est arrivée (`text`), ou les valeurs d'une lecture par nom (`fields`, chacune dans sa propre colonne). `type` est le mot de la source pour cela (un identifiant de paquet, le nom d'un mappage, un événement de journal, un point d'accès) ; `used` indique qu'elle est aussi devenue des lignes. Encadrée dans `raw.bin` dès l'appel, écrite en `heat.raw.parquet` (zstd) à la fermeture ou à la récupération de la session, et comptée par `type` dans `selfCheck.completeness` de `meta.json` |
| `stat(key, value, how="set")` | une statistique : `set` la fixe, `add` lui ajoute, garde le `max` ou le `min` |
| `now()` | secondes depuis le début de la session |
| `meta` | un dictionnaire écrit dans `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | quand, où, et ce qui a été enregistré jusqu'ici |

`event`, `stat` et `raw` sont thread-safe et peuvent être appelés depuis un thread de travail.

**Chaque adaptateur garde tout ce que sa source envoie.** Les lignes sont ce que le visualiseur dessine ; elles ne sont
pas l'enregistrement. Chaque paquet qui arrive sur un port, chaque page de mémoire partagée lue (la totalité du mappage,
à chaque changement), chaque ligne d'un journal ou d'un script d'export (y compris celles que l'adaptateur ignore), chaque
réponse JSON ou document envoyé va dans `session.raw(...)` dès son arrivée, qu'il devienne ou non une
ligne - et rien n'est allégé en dessous du débit auquel l'adaptateur lit. Un élément qui arrive avant qu'une session
soit ouverte en ouvre une (une session qui n'a que des éléments bruts est conservée), ou est retenu jusqu'à son ouverture ; il n'est
jamais perdu. Les champs peu coûteux à décoder et certains dans leur sens vont aussi dans les lignes. C'est la
[règle de convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : un flux en direct est perdu
dès qu'il est envoyé, donc ce qu'un adaptateur ne garde pas est perdu pour de bon, et ce qu'il garde entier peut
être décodé le jour où quelqu'un le comprend. La taille est le prix à payer ; l'encodage zstd et par dictionnaire la
maintient basse, sans rien omettre. Le test de chaque adaptateur envoie quelque chose qu'il n'utilise pas et vérifie qu'il
revient entier depuis `heat.raw.parquet`, et que `selfCheck.completeness.lost` vaut 0. `racing.Driving.raw`
fait la même chose pour les adaptateurs de course (et ouvre la session), et `racing.Pages` garde les pages de mémoire
partagée chaque fois que leurs octets changent, en comptant dans `unchanged_reads` de `meta.json` les relectures qui n'ont rien
trouvé de neuf.

Conventions sur lesquelles le reste du système s'appuie :

- **Les lignes du joueur lui-même sont marquées, d'après ce que dit la source.** `player="me"` quand la source est
  celle du joueur ; quand chaque joueur est enregistré sous un nom, `own_car=1` sur les lignes de la voiture du joueur
  (par l'index de joueur du jeu ou le participant regardé), ou le nom du joueur comme `session.meta["player"]`
  (écrit tout de suite dans `meta.json`) quand la source nomme le joueur. Ne devinez jamais : quand la source ne le dit pas,
  prenez le nom d'un réglage (`player_names`, `riot_id`) ou ne marquez rien.
  [NVIDIA highlights](nvidia-highlights.md) n'emprunte des positions qu'à ces lignes-là
  (`platform.own_row`). Les autres joueurs sont identifiés par leur nom ou leur identifiant.
- **Les trajets sont bornés par des événements avec positions** : `spawn`, `respawn` et `session_start` en démarrent un ;
  `death`, `finish`, `session_end` et `teleport` en terminent un. Chaque fois que le joueur s'est déplacé sans
  voyager (une remise à zéro, un retour en arrière, un voyage rapide, une sauvegarde chargée), écrivez `teleport` à l'endroit
  quitté, puis un début (`spawn`, ou `respawn` pour une remise à zéro que le jeu nomme) à l'endroit d'arrivée, pour que la
  chaleur de trajet du visualiseur termine un trajet et en commence un autre au lieu de tracer à travers la carte. `Driving.jumped` le fait
  pour les véhicules.
- **Les positions restent dans les coordonnées et unités propres au monde du jeu**, décrites par `axes`. Ne les convertissez pas
  dans un autre repère, sauf si le jeu ne donne aucun repère mondial utilisable (les simulateurs de vol mettent la latitude
  et la longitude dans une carte plate, `Tangent`, autour du premier relevé - DCS autour de l'origine fixe de son théâtre -
  et passent `geo=tangent.geo()` à `open`, pour que le pied de page dise où sur la Terre se trouve la carte). `axes.scale` est l'échelle
  d'unité du visualiseur - elle multiplie chaque position - et reste à 1, pour que les lignes s'alignent avec un niveau
  exporté du même jeu dans les mêmes unités ; indiquez l'unité dans `axes.units`.
- **Les clés de statistiques** sont en minuscules avec des tirets bas, et portent leur unité quand il y en a une
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Un temps gardé comme meilleur commence par
  `best_` (gardé avec `min`), une place se termine par `_position` : `stats` affiche la plus basse de celles-ci comme
  meilleure, et la plus haute de toute autre clé (`db.lower_is_better`).

## Aides {#helpers}

| Aide | Module | Pour |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | suivre un journal que le jeu écrit : lectures partagées, seulement les lignes de cette session, fichiers nouveaux ou remplacés, lignes entières uniquement |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` avec `try_open(who)`, `receive()`, `close()` | `racing` | un port de télémétrie UDP sur 127.0.0.1, pris seulement s'il est libre, rendu à un autre programme, relayé en option |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` avec `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | sessions de véhicules : positions à débit fixe, distance, vitesse maximale, tours ; en cas de saut, `teleport` là où la voiture était et `spawn` là où elle est (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | la mémoire partagée nommée d'un jeu, en lecture seule, jamais créée |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | un dossier de replays surveillé : fichiers convertis une fois qu'ils cessent de grossir, dans un thread de travail ; le premier regard ne fait que noter ce qui s'y trouve, et `convert_existing(ctx, folder=None)` - la commande [`replays`](commands.md#replays) - convertit ceux-ci à la demande |
| `load_state`, `save_state` | `platform` | mémoriser ce qu'un adaptateur toujours actif a vu, dans `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | suivi de vol (décollages, atterrissages, écrasements, distance) et la carte plate autour du premier relevé (`Tangent.geo()` est le `geo` de la session) |
| `backup_once(path)` | `gsi`, `racing` | la règle `<file>.heat3d-backup` |
| Les fichiers de Steam | `_steam` | KeyValues binaires et texte, le dossier Steam depuis le registre |

Un adaptateur de journal minimal, à titre d'illustration (un jeu fictif) :

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

Ouvrez la session avec la première chose qui vaut la peine d'être enregistrée, et non dans `start`, pour qu'un jeu resté dans
ses menus ne laisse rien derrière lui (une session vide est de toute façon supprimée).

## Tests {#tests}

```bash
python -m pytest
```

`tests/conftest.py` donne à chaque test un dossier de données jetable (`HEAT3D_WATCH_HOME`) et désactive les
vérifications de mise à jour et les notifications (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Un test d'adaptateur construit la
sortie du jeu à partir de son format publié - paquets selon la spécification, lignes de journal au format du jeu,
fichiers dans la disposition documentée - et pilote l'adaptateur directement (raccourci de
`tests/test_poe.py` ; `data` et `install` sont des dossiers temporaires) :

```python
from dataclasses import replace
from heat3d_watch.adapters import poe
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

ctx = Context(Settings(data=str(data)), data, exe=install / "PathOfExileSteam.exe")
a = replace(poe.ADAPTERS[0])   # a fresh copy of the adapter
a.start(ctx); a.poll(ctx); a.stop(ctx)
[session] = list((data / "sessions").glob("*/*"))
rows = read_rows(session)      # then check the rows and meta.json's stats
```

Les adaptateurs réseau sont testés contre un faux serveur local, ou avec des paquets envoyés en UDP à l'adaptateur.
Les tests qui vérifient contre de vraies données de jeu sur la machine du développeur sont marqués `@pytest.mark.local` et
sont ignorés là où ces données sont absentes. Ces données ne vont jamais dans le dépôt. `test_core.py` contient aussi le
test qui échoue si un code capable d'écrire dans un autre processus apparaît dans le paquet
(`test_memory_reading_cannot_write`).

## Un `verified` honnête {#an-honest-verified}

`verified` dit ce qui a été vérifié et comment, et ce qui ne l'a pas été. Il est affiché par `games` et sur chaque
page de jeu, et les joueurs s'y fient. Exemples tirés du code :

- « tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game »
- « tested on documents in the published GSI format posted to the running adapter; untested against the
  running game »
- « tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format »

Écrivez « untested against the game » tant que l'adaptateur n'a pas enregistré le jeu en cours d'exécution. Indiquez la méthode et
la tolérance seulement : jamais une carte, un identifiant de match, un nom de joueur, une date, une taille de corpus ou un
compte exact tiré de vrais fichiers, et jamais « cette machine » (les lecteurs ne la connaissent pas). Nommez la source de
chaque décalage et de chaque disposition, et dites où deux sources ont été comparées. Ne prétendez jamais plus que ce qui a été fait. Un
format deviné ou repris d'outils de la communauté est présenté comme tel.

## Les pages de jeux {#the-game-pages}

Chaque page sous [Jeux](games.md) est générée à partir des adaptateurs, elle correspond donc toujours au code. Après
avoir ajouté ou modifié un adaptateur, régénérez-les depuis le dossier du dépôt :

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(Dans PowerShell : `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Ajoutez `--check` pour seulement
comparer : rien n'est écrit, et le script quitte avec 1 si une page est périmée (aussi le tableau des jeux de
`docs/watcher.md`).

Le script :

- charge les adaptateurs avec `heat3d_watch.adapters.load()`, contre un dossier de données temporaire vide, pour qu'aucun
  profil mémoire ni réglage de votre machine n'arrive dans les pages. Les adaptateurs de mémoire sont exclus,
  car ils viennent des profils propres aux joueurs ;
- refuse d'écrire quoi que ce soit si un module d'adaptateur ne peut pas être importé (les pages perdraient ces jeux) ;
- écrit `docs/game-<adapter id>.md` pour chaque adaptateur et `docs/games.md` avec le tableau d'ensemble, et
  supprime les pages des adaptateurs qui n'existent plus ;
- tire « What is recorded », « Where it comes from », « How to switch it on », les axes, l'indicateur multijoueur et
  « Verified » des champs de l'adaptateur ;
- transforme la docstring du module en « How it works ». Écrivez les docstrings dans le style texte brut que les
  modules utilisent déjà, que le script convertit : paragraphes ; listes avec `*`, `-` ou `1.` ; dispositions et exemples
  indentés sous la ligne qui les présente (ils deviennent des blocs de code) ; un titre souligné de tirets, ou une
  ligne de titre courte dont le texte est indenté directement dessous (ils deviennent des titres) ;
- liste les clés de statistiques que le code de l'adaptateur fixe par leur nom - `.stat("key", ...)`, les deux côtés d'une
  expression `if`, et les modèles de f-string tels que `score.{team}` - dans les classes de l'adaptateur et dans les
  aides qu'elles utilisent. Les clés prises d'une variable (une table des champs du jeu) ne sont pas listées ;
- décide « Positions » d'après `axes.units` de l'adaptateur (une note commençant par « no » ou « none » signifie pas de
  positions) et d'après ce que son code écrit.

Ne modifiez pas les pages générées à la main : changez l'adaptateur et relancez le script. Le tableau de
[Tous les jeux dans un seul tableau](watcher.md) est la sortie de `python -m heat3d_watch games --markdown`.
