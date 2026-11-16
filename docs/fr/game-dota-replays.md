---
title: "Dota 2 (replays)"
nav_order: 12
lang: "fr"
source: game-dota-replays.md
source_hash: "88539ee6dc65"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replays) {#dota-2-replays}

Après une partie de Dota 2, le watcher transforme le replay sauvegardé par le jeu en fichiers que vous pouvez regarder sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `dota-replays`, type [`replay`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas qu'un jeu démarre) et cherche de nouvelles données toutes les 5 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position, la hauteur, la vie et le niveau de chaque héros, 7,5 fois par seconde tant qu'il est en vie
- les frags et les morts là où ils ont eu lieu ; les tours, casernes, Roshan et Tormentors là où ils sont tombés ; les wards là où ils ont été posés
- les pings sur la carte, les dessins sur la carte et les ordres de chaque joueur (déplacer, attaquer, lancer, acheter, ...) là où ils visaient
- le score et la ligne de chaque joueur ; celle du joueur connecté, en statistiques
- tout le reste que contient le replay, gardé en entier à côté de la table : chaque trame et chaque message réseau, chaque changement de propriété d'entité, chaque entrée de table de chaînes

## D'où viennent les données {#where-it-comes-from}

les replays que Dota 2 sauvegarde : &lt;Dota>/game/dota/replays/&lt;match id>.dem (téléchargés dans le client, ou avec `dota-replay <match id>`)

## Comment l'activer {#how-to-switch-it-on}

téléchargez le replay d'une partie dans Dota 2, ou récupérez-en un public : `python -m heat3d_watch dota-replay <match id>` ; installez le lecteur : github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, apporte gem-dota)

Saisissez la commande dans un terminal ouvert dans le dossier du watcher (voir [Avant de commencer](before-you-start.md)). Si la commande échoue, la dernière ligne indique pourquoi ; [Installation et lancement](installing-and-running.md) décrit les causes les plus fréquentes.

Réglages par variables d'environnement :

- `HEAT3D_DOTA_REPLAY` : le dossier du lecteur (un clone ou une version décompressée), quand il n'est pas installé ou à côté du watcher

## Fonctionnement {#how-it-works}

Replays et démos : ce qu'un jeu sauvegarde d'une partie, converti une fois la partie terminée.

Un replay contient tout ce qu'une interface en direct retient dans les parties multijoueur - la position de chaque joueur, chaque frag à l'endroit où il a eu lieu - et c'est un fichier que le jeu écrit pour ses joueurs, donc le lire ne touche en rien au jeu. Le watcher surveille les dossiers où les jeux les sauvegardent, attend qu'un nouveau fichier ait cessé de grossir (sinon le jeu est encore en train de l'écrire), et le convertit dans un thread de travail, pour qu'une longue conversion ne bloque jamais le reste du watcher.

La première fois qu'un dossier est vu, les replays déjà présents ne sont que notés, pas convertis : un joueur qui a des années de démos verrait sinon le watcher occupé pendant une journée. `python -m heat3d_watch replays <adaptateur> [dossier]` convertit les existants sur demande.

#### Dota 2 {#dota-2}

Dota 2 sauvegarde les replays que le joueur télécharge (les détails d'une partie, ou Regarder > Replays) dans `<Dota>/game/dota/replays/<match id>.dem` ; Valve garde le replay de chaque partie publique sur ses serveurs pendant quelques semaines, et `python -m heat3d_watch dota-replay <match id>` en récupère un par son identifiant via OpenDota. Le watcher ne les lit pas lui-même : un lecteur externe le fait (3DHeat Dota Replay, github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, commande `heat3d-dota-replay`, qui lit avec gem-dota, MIT), un projet à part entière. Il tourne dans son propre processus sur chaque nouveau replay quand il est dans le PATH, installé, ou à côté du watcher ; s'il manque, le watcher indique une fois comment l'installer. Il écrit la position, la hauteur, la vie, le niveau, l'orientation, la mana, l'expérience, les attributs et les objets de chaque héros, 7,5 fois par seconde tant qu'il est en vie ; les frags et les morts là où ils ont eu lieu ; les tours, casernes, Roshan et Tormentors là où ils sont tombés ; chaque ward là où il a été posé et où il a pris fin ; les entrées du journal de combat concernant les héros (dégâts, soins, sorts, objets, achats, runes, or, expérience, modificateurs) ; et les pings, dessins et ordres de chaque joueur sur la carte - dans `dota/<match>.parquet` ; chaque autre unité (creeps, invocations, illusions, courriers, bâtiments) une fois par seconde dans `<match>.units.parquet` ; tout le journal de combat dans `<match>.combatlog.parquet` ; et la partie, le chat, la draft, tout le reste extrait par le lecteur et l'enregistrement de fin de partie du jeu dans `<match>.match.json`, dans le dossier de la session. Tout le reste que contient le replay est gardé en entier à côté (règle du convertisseur de 3DHeat) : chaque trame et chaque message réseau dans `<match>.packets.parquet`, chaque changement de propriété d'entité dans `<match>.entities.parquet`, chaque entrée de table de chaînes dans `<match>.strings.parquet`, comptés dans `selfCheck.completeness` du document du match. Les positions sont en unités du monde de Dota, les mêmes que celles que signale l'intégration d'état de jeu. La ligne de tableau des scores du joueur connecté devient les statistiques de la session : frags, morts, assistances, last hits, denies, valeur nette, GPM, XPM, dégâts aux héros, wards, et si la partie a été gagnée. Un nouveau patch de Dota peut modifier les entités du replay avant que gem ne suive ; un replay que gem ne peut pas lire jusqu'au bout est converti aussi loin que possible et marqué `incomplete` dans son résumé.

Le même module sert aussi : [Counter-Strike 2 (replays)](game-cs2-demos.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `z` |
| Unités | unités du monde de Dota (unités Hammer ; la carte fait environ 16400 de large) |
| Miroir pour le visualiseur | `y` |
| Échelle (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de `heat.parquet`, afin que le visualiseur 3DHeat tourne et mette à l'échelle les lignes toute seule - voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `replay` : il ne lit que ce que le jeu ou la plateforme fournit (les replays et démos que le jeu sauvegarde), donc il enregistre aussi en ligne ; l'indicateur ne décide que de la possibilité de lire la mémoire.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne - voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et la table `stats` de `watcher.sqlite`) :

`duration`, `hero`, `score.{team}`, `team`, `won`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le convertisseur suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que le replay contient est lu ou gardé, jamais jeté. En plus de la table, tout le reste que contient le replay est gardé en entier dans des fichiers annexes à côté, dans le dossier `dota/` de la session - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (colonnes `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, selon ce qui s'applique) - et `selfCheck.completeness` du document du match (`<match>.match.json`) compte chaque `type` - `lost` vaut 0.

**Lu**

- la table (`dota/<match>.parquet`) : la position, la hauteur, la vie, le niveau, l'orientation, la mana, l'expérience, les attributs, l'armure, la vitesse, les dégâts, les objets et le curseur du joueur, 7,5 fois par seconde ; les frags, les morts, les objectifs, les wards, les entrées du journal de combat concernant les héros ; les pings de carte (`ping`, DOTA_UM_LocationPing), les dessins de carte (`map_line`, DOTA_UM_MapLine) et chaque ordre d'unité (`order`, DOTA_UM_SpectatorPlayerUnitOrders : `other` le type d'ordre, `value` l'identifiant du sort ou de l'objet, `text` la classe de la cible ; au point visé, sinon au héros)
- `<match>.units.parquet` : chaque autre unité une fois par seconde ; `<match>.combatlog.parquet` : tout le journal de combat tel que gem le lit, chaque champ
- le document du match : tout ce qu'extrait gem, et en entier les enregistrements propres au replay - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo : durée de lecture, nom, héros, identifiant Steam et équipe de chaque joueur), `matchDetails` (DOTA_UM_MatchDetails : le tableau des scores de fin de partie du coordinateur de jeu, les chiffres de chaque joueur, objets, dégâts par type, choix et bans) et `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck` : frags, morts, assistances, niveau, last hits et denies tels que lus dans le flux, comparés à `matchDetails`, joueur par joueur

**Gardé brut**

- `<match>.packets.parquet` : chaque trame qui n'est pas un paquet (`type` `frame <n>`) et chaque message réseau (`message <n>`, `name` le nom donné par Valve), en entier dans `payload`, dans l'ordre du fichier (`seq`, `frame`), avec `decoded` le protobuf en JSON (un champ d'octets donné par sa longueur), chaque type de message décodé : svc_PacketEntities (le flux d'entités), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, les messages du journal de combat, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projectiles, animations, sang), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ... ; les tables d'envoi, la liste des classes et les informations du serveur dont un décodeur d'entités aura besoin plus tard en font partie
- `<match>.entities.parquet` : chaque propriété de chaque entité à chaque changement (`type` la propriété, `name` la classe, `entity` son index ; `value`, `vector` ou `decoded`), son état entier à sa création, et chaque création, entrée, sortie et suppression - des millions de lignes pour une partie entière
- `<match>.strings.parquet` : chaque entrée de table de chaînes de chaque mise à jour et de chaque instantané complet, la valeur en entier ; `userinfo`, `ActiveModifiers` et `EconItems` décodés à partir de leurs protobufs
- `selfCheck.completeness` du document du match compte les trames et messages par leur nom Valve, les entrées du journal de combat (`combatlog <type>`), les événements du jeu (`gameevent <name>`), les entrées de table de chaînes (`stringtable <name>`) et les mises à jour d'entités (`entity <class>`) ; quelques-uns ne sont gardés qu'en brut (les instantanés complets d'entités que gem saute parce qu'il reconstruit à partir des deltas, et les entrées de tables dont aucune valeur n'est lue), `lost` vaut 0

**Non disponible**

- la voix : le replay contient la configuration de voix mais pas les données vocales
- les noms cachés derrière des hachages et des identifiants : les sons et les particules sont nommés par des hachages des fichiers du jeu, les sorts par des identifiants ; le replay ne porte pas les noms (les objets sont nommés grâce au catalogue de gem quand il en a)
- ce que seuls les clients des joueurs connaissaient (leur caméra, leur écran) au-delà de ce que le serveur a diffusé ; le curseur et chaque ordre sont présents

**Taille** : les fichiers annexes ensemble sont un peu plus gros que le replay lui-même, les paquets et les entités étant les plus lourds ; une partie entière prend une à deux minutes dans un seul processus

## Vérifié {#verified}

vérifié sur le replay d'une partie publique : frags, morts, assistances, niveau, last hits et denies correspondent au tableau de fin de partie du jeu pour les dix joueurs ; chaque message du fichier annexe des paquets se resérialise octet pour octet ; le tableau et les statistiques par des tests sur des données synthétiques

## Source {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
