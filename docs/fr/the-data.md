---
title: "Les données"
nav_order: 5
lang: "fr"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Les données {#the-data}

Tous les enregistrements sont des fichiers simples dans le dossier de données (`%LOCALAPPDATA%\3DHeat\Watcher` sauf changement,
voir [Installation et lancement](installing-and-running.md#where-everything-is)). Vous pouvez les lire, les copier ou les
supprimer sans le watcher. Un fichier `.jsonl` est du texte brut, un événement par ligne (le Bloc-notes l'ouvre) ;
un fichier `.parquet` est un tableau que le visualiseur 3DHeat ouvre (Excel ne l'ouvre pas : `stats --csv` écrit des fichiers CSV
pour les tableurs).

## Dossiers de session {#session-folders}
![un dossier de session](../assets/img/session-folder.svg)


Une **session** est une séance avec une seule source : depuis le moment où le jeu dit quelque chose pour la première fois jusqu'à son arrêt (le jeu
se ferme, un match se termine, une conduite ou un vol est réinitialisé - la page de chaque adaptateur indique ce qui
démarre et termine ses sessions). Chaque session reçoit un dossier :

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` est le nom du jeu où chaque caractère autre que lettres, chiffres, `.`, `_` et `-`
  est remplacé par `-` (60 caractères au plus) : `EA-SPORTS-F1-25`, `Counter-Strike-2`. Les adaptateurs qui couvrent
  plusieurs jeux (statistiques Steam, Steam Timeline, NVIDIA highlights) classent chaque session sous le jeu auquel elle appartient.
- L'heure est le début de la session en heure locale. Les sessions qui décrivent le passé (un replay converti après le match,
  un fichier de statistiques Steam) utilisent l'heure que donnent le jeu ou le fichier. Deux sessions qui commencent à la même
  seconde reçoivent `_2`, `_3`, ... à la fin.
- L'identifiant de la session, dans la base de statistiques, est `<game folder>/<session folder>`.

Une session où rien du tout n'a été enregistré (le jeu est resté dans ses menus, ou a planté au démarrage) est
supprimée à sa fermeture, pour que chaque lancement ne laisse pas un dossier vide.

Certaines sessions contiennent davantage de fichiers. Une session de démo Counter-Strike 2 contient le tableau et le
résumé propres au convertisseur (`<map>/<match>.parquet`, `<match>.match.json`). Une session iRacing liste les fichiers `.ibt` que
le simulateur a écrits pendant la séance, sous forme d'événements `telemetry_file`.

## events.jsonl {#eventsjsonl}

`events.jsonl` contient un objet JSON par ligne, une ligne par événement, écrite au moment où l'événement
se produit. Le fichier est tamponné par ligne, donc un plantage, une coupure de courant ou un processus tué ne fait perdre
rien de ce qui était déjà écrit ; une ligne coupée net par un plantage est ignorée à la lecture du fichier, et chaque ligne
qui la précède reste valable.

Chaque ligne a les mêmes colonnes de base :

| Colonne | Type | Ce que c'est |
|---|---|---|
| `time` | nombre | secondes depuis le début de la session (4 décimales), ou l'horloge propre du jeu quand l'adaptateur la transmet |
| `ms` | entier | heure réelle, en millisecondes Unix |
| `event` | texte | ce qui s'est passé : `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | nombre | où, dans les unités et axes propres au jeu (voir `axes` dans `meta.json`) ; présent seulement quand les trois sont connus et finis |
| `player` | texte | qui : un nom, un identifiant, ou `me` pour la personne qui joue (voir [Les lignes du joueur lui-même](#the-players-own-rows)) |
| `team` | texte | leur camp, quand le jeu le dit |
| `session` | texte | le match, la manche, l'étape, la vie ou le vol auquel appartient la ligne, quand le jeu le dit |

Tout autre champ que le jeu signale suit sous son propre nom (`speed_kmh`, `gear`, `lap_time`, `weapon`,
`victim`, `hero`, ...). Les champs sans valeur sont omis, ainsi que les nombres qui ne sont pas finis.
Deux lignes fictives :

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Les lignes sans position (une ligne du fil d'éliminations, une montée de niveau, un changement de statistique) restent dans `events.jsonl` et
comptent dans les statistiques. Seules les lignes avec une position vont dans le tableau.

### Les lignes du joueur lui-même {#the-players-own-rows}

C'est la source qui dit quelles lignes concernent la personne qui joue, jamais une supposition. Une ligne est celle du joueur quand

- son `player` vaut `me` : la plupart des adaptateurs, dont la source est le jeu du joueur (télémétrie de sa propre
  voiture ou de son avion, intégration d'état de jeu, un journal) ;
- elle porte `own_car` à 1 : les jeux de course qui enregistrent chaque voiture sous le nom de son pilote (EA SPORTS F1
  par l'index de voiture du joueur du jeu, RaceRoom par son propre emplacement, Automobilista 2 et Project CARS 2 par le
  participant regardé) marquent ainsi la voiture du joueur et gardent le nom du pilote dans `player` ;
- son `player` est le `player` de la session dans `meta.json` : le nom que la source donne au joueur - le
  commandant d'Elite Dangerous (le journal est toujours celui du joueur), le Riot ID indiqué dans les réglages, pour un replay de League of Legends.

War Thunder et Rocket League nomment chaque joueur et ne disent pas lequel vous êtes ; avec votre nom dans le réglage
`player_names` (voir [Réglages](installing-and-running.md#settings)), vos lignes deviennent `me`.
[NVIDIA highlights](nvidia-highlights.md) cherchent un instant dans exactement ces lignes.

## heat.parquet {#heatparquet}

Quand une session se ferme, les lignes de `events.jsonl` qui ont `x`, `y` et `z` sont écrites dans
`heat.parquet`. C'est le tableau que le visualiseur 3DHeat ouvre. Si la session n'a pas de positions, aucun
tableau n'est écrit.

- Les colonnes sont `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, suivies de chaque
  autre champ dans l'ordre de sa première apparition.
- `x`, `y`, `z` et `time` sont des flottants 64 bits et `ms` un entier 64 bits. Une colonne supplémentaire dont toutes les
  valeurs sont des nombres est un flottant 64 bits ; toute autre colonne est du texte encodé par dictionnaire (les valeurs
  manquantes sont du texte vide, et les listes ou objets sont écrits en texte JSON).
- Les métadonnées du fichier ont une clé `heat3d` avec les instructions de lecture, pour que le visualiseur associe
  lui-même les colonnes et les axes (un exemple, la liste `extra` raccourcie) :

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

`up` est l'axe vertical du jeu, `flipX`/`flipY`/`flipZ` inversent un axe pour qu'un monde en système gaucher ne soit pas
dessiné en miroir, et `scale` est l'échelle d'unité du visualiseur : elle multiplie chaque position par cette valeur lors du
chargement du tableau (0.01 transformerait des centimètres en mètres). Chaque adaptateur écrit 1 et garde les unités propres
au jeu - des mètres pour la plupart, les unités Source (pouces) pour Counter-Strike 2, les unités Unreal (centimètres) pour
Rocket League - parce qu'un niveau exporté du jeu est dans ces mêmes unités, donc les lignes s'y posent ; les
tableaux du propre convertisseur de CS2 disent la même chose. `units` dans `meta.json` indique ce que vaut une unité. La
page de chaque jeu liste ses valeurs sous « Positions and axes ».

Les simulateurs de vol (DCS World, Microsoft Flight Simulator, X-Plane, les enregistrements Tacview d'IL-2) placent leurs
lignes sur la Terre, et leur pied de page indique où, pour que le visualiseur puisse poser le vrai monde dessous :

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (degrés) sont l'origine de la carte plate où se trouvent les lignes ; `east`, `north` et `up` nomment les
colonnes contenant les mètres à l'est et au nord de cette origine, et l'altitude au-dessus du niveau de la mer. L'origine est le
premier relevé pour X-Plane et MSFS, le point de référence de l'enregistrement pour IL-2, et l'origine fixe du théâtre
pour DCS (le premier relevé arrondi au degré entier sur un théâtre que le watcher ne connaît pas). Un tableau sans
place sur la Terre n'a pas de clé `geo`, et le reste du pied de page est identique dans les deux cas.

`heat.parquet` peut toujours être reconstruit à partir de `events.jsonl` avec
`python -m heat3d_watch table <session folder>` (voir [Commandes](commands.md#table)). C'est utile quand
`pyarrow` manquait pendant l'enregistrement de la session.

## meta.json {#metajson}

`meta.json` résume la session. Il est écrit à l'ouverture de la session, au plus toutes les 30 secondes pendant que des événements ou des
statistiques arrivent, et à la fermeture de la session. Les statistiques ne sont gardées en mémoire qu'entre ces
écritures ; un plantage peut donc faire perdre au plus la dernière demi-minute.

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

Une session dont la source nomme le joueur (voir [Les lignes du joueur lui-même](#the-players-own-rows)) a aussi
`"player"` : le nom que portent les lignes du joueur. Une session sur la Terre (les simulateurs de vol) a aussi
`"geo": {"lat0": .., "lon0": ..}`, l'origine que répète le `geo` du pied de page.

- `started` / `ended` : heure locale à la seconde ; `ended` vaut `null` tant que la session tourne.
- `events` : le nombre de fois où chaque événement s'est produit, du plus fréquent au moins fréquent. `positions` est le nombre de
  lignes avec une position.
- `stats` : les chiffres de la session. Un adaptateur en fixe chacun, y ajoute, ou garde le maximum ou le minimum.
- Tout ce que l'adaptateur sait d'autre sur la séance suit au niveau supérieur : la piste, la carte, la mission,
  l'identifiant du match, l'identifiant d'application Steam, le fichier de replay, le profil mémoire et sa version. Une session
  terminée par la récupération porte `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` est la base de données des statistiques. Une ligne est ajoutée pour chaque session à sa fermeture. Les
trois tables sont simples, donc n'importe quel outil SQL, carnet de notes ou tableur peut les lire sans le watcher :

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,          -- <game folder>/<session folder>
  game TEXT NOT NULL,
  adapter TEXT NOT NULL,
  started REAL NOT NULL,        -- Unix seconds
  ended REAL,                   -- Unix seconds
  seconds REAL,
  folder TEXT NOT NULL,         -- the session folder's full path
  events INTEGER NOT NULL DEFAULT 0,
  positions INTEGER NOT NULL DEFAULT 0,
  multiplayer INTEGER NOT NULL DEFAULT 0,
  source TEXT
);
CREATE TABLE events (           -- per session, how many times each event happened
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (session, event)
);
CREATE TABLE stats (            -- per session, every number the game reported or the watcher counted
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- numbers
  text TEXT,                    -- everything else (a map name, a result, a hero)
  PRIMARY KEY (session, key)
);
```

Réenregistrer une session (récupération, un replay reconverti) remplace ses lignes. `multiplayer` est l'indicateur de
l'adaptateur (certains adaptateurs le fixent par session, par exemple DCS d'après la mission), et non une vérification
de votre connexion en ligne. Une valeur vrai/faux dans `stats` est stockée sous forme de texte.

Un exemple de requête, le meilleur tour par jeu sur toutes les sessions (plus bas, c'est mieux) :

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` affiche les totaux de ces tables (voir [Commandes](commands.md#stats)) ; sa colonne
`best` est la valeur la plus basse pour les temps gardés comme meilleurs et pour les places, la plus haute pour le reste.

## Récupération après un plantage {#recovery-after-a-crash}

Au démarrage de `run`, le watcher cherche les sessions qu'un watcher précédent a laissées ouvertes : un `meta.json` sans
`ended`, et un `events.jsonl` avec au moins une ligne. Il termine chacune :

- le nombre d'événements et de positions est recompté à partir de `events.jsonl`, en sautant une ligne coupée net ;
- la fin est l'heure réelle de la dernière ligne (`ms`) ;
- les statistiques sont celles de la dernière écriture de `meta.json` (au plus 30 secondes plus anciennes) ;
- `"recovered": true` est ajouté, `heat.parquet` est écrit, et la session entre dans `watcher.sqlite`.

Le journal indique « finished N session(s) left open by an earlier run ». Le fichier de verrouillage empêche un
second watcher de « récupérer » les sessions d'un watcher encore en cours d'exécution.

## Export CSV {#csv-export}
![stats --csv et table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

écrit `out\sessions.csv`, `out\events.csv` et `out\stats.csv`. Chaque fichier est une table complète de
`watcher.sqlite`, avec une ligne d'en-tête, en UTF-8. Les heures sont des secondes Unix, comme dans la base.
`--game` ne restreint pas l'export ; toutes les sessions sont écrites.

## Ouvrir une session dans le visualiseur 3DHeat {#opening-a-session-in-the-3dheat-viewer}

Le visualiseur : [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), documentation
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - sa page
[conteneur `.3dheat`](https://holdi601.github.io/3DHeat/container.html) décrit le format d'un fichier par match que les
convertisseurs de replays peuvent écrire.

Ouvrez le `heat.parquet` d'une session dans le visualiseur 3DHeat. Le pied de page indique à le visualiseur quelle colonne est la
position, l'heure, le joueur, l'équipe et la session, et dans quel sens est le haut, donc rien n'a besoin d'être associé
à la main. Les positions sont dans les coordonnées propres au monde du jeu. Dessinées par-dessus un niveau exporté avec
les autres outils 3DHeat (par exemple depuis [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)),
elles se posent là où elles se sont produites.

- **Cartes de chaleur** utilisent chaque ligne avec une position, filtrée par `event`, `player`, `team` ou `session` comme
  n'importe quelle autre colonne.
- **Chaleur en lignes** trace une ligne de chacune des lignes d'un joueur vers sa suivante, et en lecture chaque
  joueur est un point qui se déplace le long du trajet avec une traînée derrière lui. Le panneau Parcours du
  visualiseur choisit, à partir de la colonne `event`, quels événements **démarrent** un trajet et lesquels en **terminent** un. Le watcher écrit
  les événements de bornage comme lignes avec une position, pour qu'ils puissent être choisis là :
  - débuts : `spawn`, `respawn`, `session_start`. Un début ferme le trajet resté ouvert sans
    tracer de ligne jusqu'au nouvel endroit.
  - fins : `death`, `finish`, `session_end`, et `teleport`. La ligne va jusqu'à la ligne de fin elle-même,
    là où le joueur est mort, s'est arrêté ou a été emporté.

  Un saut - un endroit atteint sans y avoir voyagé - compte deux lignes : `teleport` à l'endroit **quitté**,
  et un début à l'endroit **atteint**, juste après. Les adaptateurs de course en écrivent un chaque fois que la voiture
  a bougé plus loin qu'elle n'aurait pu rouler (un retour en arrière ou un flashback, une remise sur la route, un retour aux
  stands, un voyage rapide), avec `spawn` à l'arrivée (`respawn` pour la remise à zéro de BeamNG) ; la ligne `teleport` porte
  l'arrivée comme `to_x`, `to_y`, `to_z` et la distance comme `metres`, la ligne de début
  `after: "teleport"`. Les adaptateurs de camions font de même pour un ferry, un train ou une sauvegarde chargée, et les
  adaptateurs de vol pour un saut qu'aucun avion ne pourrait effectuer. Ainsi, avec `teleport` parmi les fins et `spawn`
  parmi les débuts - ce que le visualiseur propose de lui-même -, un trajet se termine là où le saut a quitté
  et le suivant commence là où il est arrivé, et aucune ligne ne traverse la carte. Un trajet ne traverse jamais un
  changement de la colonne `session`. Une ligne de position est écrite quelques fois par seconde
  (10 Hz pour la plupart des télémétries), ce qui donne une ligne lisse.
- La colonne `session` découpe une séance en ses manches, étapes, vies ou corps (Elite Dangerous
  sépare ainsi les lignes de la galaxie et celles de la surface de chaque planète). Choisissez-en une dans le visualiseur pour
  ne regarder que cette partie.

Ce que le visualiseur fait des lignes - filtres, couleurs, lecture - est décrit dans la documentation propre au visualiseur. Les sessions de démos Counter-Strike 2 s'ouvrent par le `<map>/<match>.parquet` et le
`<match>.match.json` du convertisseur, dans les onglets Carte de chaleur et Match du visualiseur. Les positions d'iRacing viennent des
fichiers `.ibt` listés dans la session, que le visualiseur lit lui-même.
