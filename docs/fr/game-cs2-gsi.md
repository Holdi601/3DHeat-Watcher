---
title: "Counter-Strike 2 (état du jeu)"
nav_order: 9
lang: fr
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (état du jeu) {#counter-strike-2-game-state}

Pendant que vous jouez à Counter-Strike 2, le Watcher enregistre ce que le jeu indique à des programmes sur votre propre ordinateur, afin que vous puissiez le regarder plus tard sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `cs2-gsi`, type [`gsi`](sources-and-rules.md) ; il tourne pendant que `cs2.exe` est lancé et cherche de nouvelles données toutes les 0,05 s.*

## Ce qui est enregistré {#what-is-recorded}

- votre propre position (coordonnées XYZ du monde, en pouces) et direction de regard jusqu'à 10 fois par seconde tant que vous êtes en vie
- les apparitions (la première fois que le jeu vous voit à chaque manche, et les réapparitions) et les morts (vie à 0, ou nombre de morts)
- les frags avec l'arme active, d'après les statistiques de la partie
- les manches (début, fin, vainqueur), la bombe posée, désamorcée ou explosée, les phases de la partie et le résultat
- frags, assistances, morts, MVP, score, argent, dégâts, frags à la tête, manches gagnées et perdues

## D'où viennent les données {#where-it-comes-from}

Game State Integration : requêtes HTTP POST vers 127.0.0.1:3311, configurées par &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Comment l'activer {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, puis lancez CS2 (il lit le fichier au démarrage)

Saisissez la commande dans un terminal ouvert dans le dossier du Watcher (voir [Avant de commencer](before-you-start.md)). Si la commande échoue, la dernière ligne indique pourquoi ; [Installation et lancement](installing-and-running.md) décrit les causes les plus fréquentes.

`python -m heat3d_watch setup cs2-gsi` liste les fichiers qu'il modifierait ; `python -m heat3d_watch setup cs2-gsi --apply` les modifie, en gardant l'original sous le nom `<file>.heat3d-backup` (voir [Commandes](commands.md#setup)). Il affiche `cs2-gsi: changed: ...` pour chaque modification, ou `cs2-gsi: nothing to change` si c'est déjà activé.

Réglages par variables d'environnement :

- `HEAT3D_CS2_GSI_PORT` : le port vers lequel le jeu envoie ses données (3311 par défaut) ; le fichier cfg du jeu doit indiquer le même port

## Fonctionnement {#how-it-works}

Valve Game State Integration : Counter-Strike 2 et Dota 2 indiquent à un serveur web local ce qui se passe.

Les deux jeux lisent chaque `gamestate_integration_*.cfg` de leur dossier cfg au démarrage, puis envoient à partir de là un document JSON en POST vers le `uri` de chaque fichier à chaque changement d'état (au plus une fois toutes les `throttle` secondes, et toutes les `heartbeat` secondes quand rien ne change). Le Watcher est ce serveur web : il écoute sur 127.0.0.1 uniquement, répond 200 à chaque POST tout de suite et fait le travail dans son propre thread d'interrogation.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Ce qu'un joueur reçoit - et donc ce qui peut être enregistré - est ce que le jeu décide qu'un joueur peut voir :

- CS2 : `provider` (le steamid propre), `map` (nom, mode, phase warmup/live/intermission/gameover, round, score team_ct/team_t), `round` (phase freezetime/live/over, bombe posée/explosée/désamorcée, win_team), `player` (le joueur *regardé* : vous-même quand vous êtes en vie, un coéquipier après votre mort) avec `state` (vie, armure, argent, round_kills, round_killhs, round_totaldmg), `match_stats` (frags, assistances, morts, mvps, score), `position` et `forward` sous forme de chaînes « x, y, z » en unités du monde (pouces, Z vers le haut), `weapons` ; `bomb` seulement pour les spectateurs. Les positions des autres joueurs (`allplayers_*`) ne sont envoyées qu'aux spectateurs et au GOTV, donc le Watcher ne les demande pas.
- Dota 2 : `map` (matchid, game_state, game_time, clock_time, win_team), `player` (frags, morts, assistances, last_hits, denies, or, gpm, xpm, team_name), `hero` (xpos/ypos en unités du monde, niveau, vivant, respawn_seconds), `buildings` (vie par tour, caserne et ancien), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Il n'y a pas de hauteur : z vaut 0. Sont aussi demandés et gardés en entier : `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (le jeu envoie ce que le client du joueur possède ; lesquels contiennent quelque chose pendant qu'on joue plutôt qu'en spectateur n'a pas été testé).

Chaque document est aussi gardé en entier (règle du convertisseur de 3DHeat, docs/converters.md dans le dépôt de la visionneuse) : `heat.raw.parquet`, `type` « gsi », `text` le JSON tel qu'envoyé - seul le jeton du fichier cfg est effacé, c'est le secret propre du Watcher, pas une donnée du jeu. Les documents envoyés alors qu'aucune partie n'est ouverte (menus, chargement, entre deux parties) attendent dans un `Backlog` et vont dans la session de la partie suivante, avant son début ; ce qui reste quand le jeu se ferme reçoit une session à part, qui ne contient que ceux-là. Les envois illisibles et les envois avec un mauvais jeton sont eux aussi gardés (« gsi-unreadable », « gsi-bad-auth »).

Sources : <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (le format repris par CS2), <https://github.com/antonpup/CounterStrike2GSI> et <https://github.com/antonpup/Dota2GSI> (listes de champs ; MIT, lues pour les faits seulement).

Le même module sert aussi : [Dota 2 (état du jeu)](game-dota2-gsi.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `z` |
| Unités | pouces (unités Hammer) |
| Miroir pour la visionneuse | `y` |
| Échelle (`scale` : la visionneuse multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de `heat.parquet`, afin que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule - voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `gsi` : il ne lit que ce que le jeu ou la plateforme fournit (une intégration d'état de jeu ou une API locale que le jeu sert), donc il enregistre aussi en ligne ; l'indicateur ne décide que de la possibilité de lire la mémoire.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne - voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et la table `stats` de `watcher.sqlite`) :

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le Watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou gardé, jamais jeté. En plus des lignes, chaque paquet, page, ligne ou réponse que reçoit l'adaptateur est gardé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ gardé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- la position, la direction de regard, la vie, l'armure, l'argent, l'arme active, le casque, le kit de désamorçage, les quantités de flash, fumigène et feu et la valeur de l'équipement du joueur regardé, sur chaque ligne de position tant que c'est le joueur lui-même (steamid du fournisseur = steamid du joueur)
- apparitions, morts (vie à 0, ou nombre de morts des statistiques de la partie), frags (le nombre de frags qui augmente)
- phases de la partie, manches (temps de gel, en direct, terminées, vainqueur), bombe posée, désamorcée, explosée, le résultat
- frags, assistances, morts, MVP, score, argent, dégâts, frags à la tête, manches gagnées et perdues, en statistiques

**Gardé brut**

- `gsi` : chaque document envoyé par le jeu, en entier, tel qu'envoyé (`text`), `used` vrai quand il a été lu pendant une partie - fournisseur (version, horodatage), map (mode, noms des équipes, défaites consécutives de manches, temps morts, victoires de série, `round_wins` avec la condition de victoire de chaque manche), round, le joueur regardé (clan, emplacement d'observateur, activité, chaque arme avec skin, munitions et réserve), bomb, compte à rebours des phases, et le diff `previously`/`added` du jeu par rapport à l'envoi précédent
- documents des menus, du chargement et d'entre deux parties : gardés de la même façon, à leur heure propre avant le début de la partie suivante ; après la dernière partie, dans une session à part (`raw_only` dans meta.json)
- `gsi-unreadable` : un envoi qui n'est pas un objet JSON, ses octets en `payload` et `length`
- `gsi-bad-auth` : un envoi avec un autre jeton que celui du fichier cfg

**Non disponible**

- les autres joueurs (`allplayers_*`) et les grenades (`allgrenades`) : le jeu ne les envoie qu'aux spectateurs et au GOTV, et le Watcher ne les demande pas (voir Sources et règles) ; une démo contient tous les joueurs - voir [Counter-Strike 2 (replays)](game-cs2-demos.md)
- les états entre deux envois : le jeu envoie au plus toutes les 0,1 s (`throttle`) et seulement en cas de changement, toutes les 10 s (`heartbeat`) sinon
- le jeton du fichier cfg, effacé dans chaque document gardé : le secret propre du Watcher, pas une donnée du jeu
- les envois au-delà de 10 000 en attente (le Watcher était bloqué) sont comptés comme `dropped_packets`, non gardés ; un envoi de plus de 4 Mo est gardé comme `gsi-unreadable` avec sa longueur mais sans ses octets

**Taille** : le document d'un joueur fait 2 à 4 Ko, envoyé jusqu'à 10 fois par seconde quand quelque chose change : environ 30 à 150 Mo par heure dans `raw.bin` pendant la partie, un dixième ou moins dans le `heat.raw.parquet` compressé en zstd (estimé d'après le format publié, non mesuré sur le jeu)

## Vérifié {#verified}

testé sur des documents au format GSI publié, envoyés à l'adaptateur en cours d'exécution ; l'installation et la recherche du dossier cfg testées sur une installation locale ; non testé avec le jeu lancé

## Source {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
