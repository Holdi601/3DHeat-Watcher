---
title: "League of Legends (état de la partie)"
nav_order: 29
lang: fr
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (état de la partie) {#league-of-legends-game-state}

Pendant que vous jouez à League of Legends, le watcher enregistre ce que le jeu signale aux programmes de votre propre ordinateur, pour que vous puissiez le regarder plus tard sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `lol-live`, type [`gsi`](sources-and-rules.md) ; il tourne pendant que `League of Legends.exe` est lancé et cherche de nouvelles données toutes les 0,5 s.*

## Ce qui est enregistré {#what-is-recorded}

- aucune position : l'API n'en a pas
- le fil des éliminations : vos kills, morts et assistances, les kills d'autres champions avec le tueur, la victime et les assistants
- dragons, hérauts, barons, tourelles, inhibiteurs, multikills, aces, premier sang, début et fin de partie
- vos kills, morts, assistances, score de creeps, score de balises, niveau, or, champion, temps de jeu, résultat
- les objectifs pris par l'équipe du joueur

## D'où viennent les données {#where-it-comes-from}

API de données du client en direct du client du jeu, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), pendant une partie

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Fonctionnement {#how-it-works}

League of Legends : l'API de données en direct que le client du jeu sert pendant une partie.

Pendant qu'une partie tourne (aussi en mode entraînement et en mode spectateur), `League of Legends.exe` répond sur <https://127.0.0.1:2999> avec ce que le joueur peut voir dans l'interface du jeu :

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Il n'y a pas de positions : l'API n'en a pas, donc une partie de League donne des événements et des statistiques, sans table de chaleur. Le certificat est autosigné, par la racine même de Riot (`riotgames.pem`, publié à <https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Ses conditions d'utilisation ne sont pas précisées, donc il n'est pas livré : placez-le dans `<données>\riotgames.pem` et la connexion est vérifiée avec lui ; sans lui, la vérification est désactivée - et seulement pour 127.0.0.1, la seule adresse à laquelle cet adaptateur parle.

La politique de Riot autorise les outils à montrer ce que le joueur pourrait savoir grâce au jeu lui-même, et rien de calculé au-delà (pas de minuteurs ennemis) : cela enregistre le fil des éliminations et le tableau des scores que voit le joueur, ainsi que les propres chiffres du joueur.

Chaque réponse est aussi conservée entière (règle du convertisseur de 3DHeat, docs/converters.md dans le dépôt de la visionneuse) : `heat.raw.parquet`, `type` le point d'accès (« allgamedata », « eventdata »), `text` le JSON tel que le client l'a envoyé, `status` quand la réponse n'était pas 200. Une réponse identique octet par octet à la précédente de son point d'accès (la liste d'événements quand il ne se passe rien) est conservée une fois et comptée dans `unchanged_replies` de meta.json. allgamedata contient tout ce que servent les autres points d'accès (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), donc ceux-ci ne sont pas demandés séparément. Les réponses avant une partie (l'écran de chargement) attendent dans un arriéré et entrent dans la session de la partie ; après GameEnd, la session reste ouverte jusqu'au départ du client, pour que les réponses de l'écran de fin y soient conservées.

Source : <https://developer.riotgames.com/docs/lol#game-client-api>

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | non |
| Axe vertical | `z` |
| Unités | aucune (pas de positions) |
| Miroir pour la visionneuse | aucun |
| Échelle des unités (`scale` : la visionneuse multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` affiche « autorisé (lit seulement ce que le jeu publie) ».
- Type `gsi` : il ne lit que ce que le jeu ou la plateforme fournit (une intégration d'état de jeu ou une API locale servie par le jeu), donc il enregistre aussi en ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur définit par leur nom (`stats` de chaque `meta.json` de session et table `stats` de `watcher.sqlite`) :

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- le fil des éliminations depuis eventdata : chaque événement une seule fois, ses champs nommés décodés (tueur, victime et assistants avec champion et équipe, structures et leur camp, type de dragon, vols, multikills, aces, premier sang, résultat) et chaque autre champ d'un événement sur sa ligne sous son propre nom
- depuis allgamedata : vos kills, morts, assistances, score de creeps, score de balises, niveau, or, champion, temps de jeu, mode et carte de jeu

**Conservé brut**

- `allgamedata` : chaque réponse entière (`text`), toutes les 2 s - activePlayer (capacités, chaque statistique de champion, runes complètes, or, niveau), allPlayers (objets avec emplacements et prix, runes, sorts d'invocateur, scores, niveau, mort et délai de réapparition, skin, voie, bot), les événements, gameData (mode, temps, carte, terrain) ; `used` vrai pendant la partie, faux sur l'écran de fin
- `eventdata` : chaque réponse entière, demandée toutes les 0,5 s à partir du prochain identifiant d'événement ; `used` vrai quand elle apporte de nouveaux événements
- une réponse identique octet par octet à la précédente de son point d'accès est conservée une fois et comptée (`unchanged_replies` dans meta.json) ; les réponses d'erreur (le RESOURCE_NOT_FOUND de l'écran de chargement) sont conservées avec leur `status`, avant le début de la partie

**Non disponible**

- les positions : l'API n'en a pas (ni minimap, ni coordonnées)
- les autres points d'accès (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats) : chacun sert une partie d'allgamedata, donc ils ne sont pas demandés
- l'API de rediffusion (`/replay/*` sur le même port) : elle rejoue les rediffusions et les parties suivies une fois activée dans game.cfg ; elle ne fait pas partie d'une partie jouée
- les points d'accès du fichier de verrouillage du client de League : ce n'est pas une API publiée (voir Sources et règles)
- les valeurs entre deux lectures : l'API répond quand on la demande et ne pousse rien ; le tableau des scores est demandé toutes les 2 s, les événements toutes les 0,5 s

**Taille** : allgamedata fait 15 à 40 Ko (il contient toute la liste des événements, qui grandit) toutes les 2 s : environ 30 à 70 Mo par heure dans `raw.bin` ; eventdata ajoute peu, car les réponses identiques sont comptées, pas stockées ; zstd réduit le JSON répété dans `heat.raw.parquet` à quelques Mo par heure (estimé d'après le format documenté)

## Vérifié {#verified}

testé contre un faux serveur local qui sert des réponses au format documenté ; non testé contre le jeu

## Source {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
