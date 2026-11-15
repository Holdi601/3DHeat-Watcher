---
title: "Rocket League (état de la partie)"
nav_order: 40
lang: fr
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (état de la partie) {#rocket-league-game-state}

Pendant que vous jouez à Rocket League, le watcher enregistre ce que le jeu indique aux programmes de votre ordinateur, pour que vous puissiez le regarder plus tard sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `rocketleague-stats`, type [`gsi`](sources-and-rules.md) ; il tourne pendant que `RocketLeague.exe` est lancé et cherche de nouvelles données toutes les 0,05 s.*

## Ce qui est enregistré {#what-is-recorded}

- les touches de balle avec l'endroit où se trouve la balle (XYZ, unités Unreal), qui l'a touchée et les vitesses
- les buts avec le point d'impact, le buteur, le passeur et la vitesse ; les coups sur la barre transversale avec leur endroit
- le fil de statistiques (démolitions, arrêts, tirs, arrêts spectaculaires, ...), les coups d'envoi, les replays, le début et la fin du match, le vainqueur
- les contres, passes, arrêts, tirs, démolitions, touches, score et scores des équipes, d'après UpdateState
- la ligne finale de chaque joueur à la fin du match
- vos propres lignes sous `me` : le joueur nommé dans les réglages (`config --set player_names.rocketleague-stats=<nom>`), sinon celui que suit la caméra du jeu hors des replays
- aucune position de voiture : l'API n'en a pas

## D'où viennent les données {#where-it-comes-from}

API de statistiques : flux JSON TCP depuis 127.0.0.1:49123 (port dans <RL>\TAGame\Config\TAStatsAPI.ini ou DefaultStatsAPI.ini)

## Comment l'activer {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (règle PacketSendRate=30), puis lancez Rocket League

Tapez la commande dans un terminal ouvert dans le dossier du watcher (voir [Avant de commencer](before-you-start.md)). Si elle échoue, la dernière ligne indique pourquoi ; [Installation et lancement](installing-and-running.md) couvre les causes habituelles.

`python -m heat3d_watch setup rocketleague-stats` liste les fichiers qu'il modifierait ; `python -m heat3d_watch setup rocketleague-stats --apply` les modifie, en gardant l'original sous `<file>.heat3d-backup` (voir [Commandes](commands.md#setup)). Il affiche `rocketleague-stats: changed: ...` pour chaque modification, ou `rocketleague-stats: nothing to change` quand c'est déjà activé.

## Comment ça marche {#how-it-works}

Rocket League : l'API de statistiques officielle, un socket local vers lequel le jeu envoie les données du match.

Activée dans `<RL>\TAGame\Config\TAStatsAPI.ini` - ou `DefaultStatsAPI.ini`
quand le premier n'existe pas, que le jeu ne lit que dans ce cas - sous
`[TAGame.MatchStatsExporter_TA]` :

```text
PacketSendRate   messages UpdateState par seconde ; 0 (par défaut) coupe l'API, au plus 120
Port             le port TCP où le jeu écoute, 49123 par défaut (WebPort 49124 est une copie WebSocket)
```

Le jeu est le serveur : un client se connecte à 127.0.0.1:49123 et lit un flux
d'objets JSON `{"Event": nom, "Data": {...}}` (certaines versions envoient Data sous forme
de chaîne JSON), l'un après l'autre, sans séparateurs. Les événements sont envoyés au tick
où ils se produisent, indépendamment du débit :

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 bleu / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos ; état de la voiture
              seulement pour les spectateurs), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Les positions sont en unités Unreal (centimètres), Z vers le haut ; le terrain fait environ 8200 x 10240
avec les buts à Y = +-5120. Les positions des voitures ne font pas partie de l'API : ce qui a un lieu, c'est
la balle à l'endroit où elle a été touchée, marquée ou a heurté la barre transversale.

Chaque message est aussi conservé en entier (règle du convertisseur de 3DHeat, docs/converters.md
dans le dépôt du visualiseur) : `heat.raw.parquet`, `type` le nom d'événement du message, `text` l'objet tel
qu'il est sorti du flux. Un UpdateState identique octet par octet au précédent (match en pause, menu) n'est
conservé qu'une fois et compté dans `unchanged_replies` de meta.json. Les messages entre les matchs attendent
dans un arriéré pour la session du match suivant ; ce qui reste quand le jeu se ferme a une session à part.
Les caractères entre les objets qui ne sont pas du JSON sont conservés comme « junk ».

Sources : <https://www.rocketleague.com/en/developer/stats-api> (la page officielle) ;
casse des champs et découpage TCP confirmés avec le client rlstatsapi
(<https://docs.rs/crate/rlstatsapi>, MIT ; lu seulement pour les faits).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `z` |
| Unités | unités Unreal (centimètres) |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `gsi` : il ne lit que ce que le jeu ou la plateforme fournit (une intégration d'état de jeu ou une API locale que le jeu sert), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- BallHit (endroit, qui, équipe, vitesses avant et après), GoalScored (point d'impact, buteur, passeur, vitesse, temps du but), CrossbarHit (endroit, dernière touche, vitesse, force), StatfeedEvent (événement, type, cibles principale et secondaire), MatchEnded (vainqueur, résultat), le nom de chaque autre événement comme ligne
- depuis UpdateState : le terrain, la cible de la caméra hors des replays (qui est `me`), les scores d'équipe, les buts, passes, arrêts, tirs, démolitions, touches, touches de voiture et score de chaque joueur (les siens en statistiques, ceux de tous en `player_result` à la fin du match) ; les prolongations depuis ClockUpdatedSeconds

**Conservé brut**

- chaque message en entier tel qu'il est sorti du flux (`text`), sous son propre nom d'événement : `UpdateState` (le PrimaryId et le Shortcut de chaque joueur, l'horloge, la vitesse et l'équipe de la balle, les noms et couleurs des équipes, les indicateurs de replay et de vainqueur, et l'état des voitures là où le jeu l'envoie), `BallHit`, `GoalScored` (avec la dernière touche de la balle), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` et tout événement qu'une version ultérieure ajoute
- un UpdateState identique octet par octet au précédent (pause, menus) est conservé une fois et compté (`unchanged_replies` dans meta.json)
- messages entre les matchs : à leur heure propre avant le début du match suivant ; après le dernier match, dans une session à part (`raw_only` dans meta.json)
- `unreadable` : un objet qui n'est pas un message de l'API de statistiques ; `junk` : des caractères entre les objets

**Non disponible**

- les positions et l'état des voitures pendant la partie : le jeu ne les envoie qu'aux spectateurs
- les UpdateState entre deux envois : le jeu envoie PacketSendRate fois par seconde (`setup` règle 30, le jeu permet jusqu'à 120) ; les événements sont envoyés au tick où ils se produisent
- la copie WebSocket sur WebPort (49124) : les mêmes messages que sur le port TCP, non lus deux fois

**Taille** : un UpdateState fait 1 à 3 Ko pour six joueurs, 30 par seconde : environ 100 à 300 Mo par heure dans `raw.bin` pendant un match, un dixième ou moins dans le `heat.raw.parquet` zstd (estimé d'après le format documenté, non mesuré sur le jeu)

## Vérifié {#verified}

testé sur des messages au format documenté envoyés par un faux serveur local ; non testé avec le jeu

## Source {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
