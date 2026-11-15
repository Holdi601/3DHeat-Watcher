---
title: "Minecraft (fichiers journaux)"
nav_order: 33
lang: fr
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (fichiers journaux) {#minecraft-log-files}

Pendant que vous jouez à Minecraft, le watcher lit les fichiers que le jeu écrit et enregistre ce qui s'est passé, pour que vous puissiez le regarder plus tard sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `minecraft`, type [`log`](sources-and-rules.md) ; il tourne pendant que `javaw.exe` ou `java.exe` est lancé et cherche de nouvelles données toutes les 0,5 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position de vous et des autres joueurs (blocs = m, Y vers le haut) à chaque sauvegarde du monde, la dimension comme session
- l'apparition avec la position quand un joueur se connecte au serveur (intégré)
- connexions, déconnexions, morts avec le message de mort, progrès, lignes de chat
- morts, progrès, messages de chat ; depuis le fichier de statistiques : temps de jeu, distance, éliminations de monstres et de joueurs, sauts, dégâts, blocs minés, objets fabriqués (la part de cette session)
- chaque ligne du journal et chaque fichier de statistiques, de progrès et de joueur sauvegardé, en entier, dans heat.raw.parquet

## D'où viennent les données {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (suivi), saves\\&lt;monde>\stats\\&lt;uuid>.json et saves\\&lt;monde>\playerdata\\&lt;uuid>.dat / level.dat (NBT gzip), lus quand le jeu les sauvegarde

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Comment ça marche {#how-it-works}

Minecraft (édition Java) : les fichiers de journal, de statistiques et de joueurs que le jeu écrit.

Où (`%APPDATA%\.minecraft\`) :

* `logs\latest.log` - le journal du jeu, neuf à chaque lancement (l'ancien est
  rangé dans un .log.gz daté). Lignes `[hh:mm:ss] [thread/LEVEL]: message`
  (les chargeurs de mods écrivent `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`).
  Ce que les joueurs voient dans le chat s'y trouve : connexions et déconnexions, messages de mort,
  progrès, chat - le serveur intégré d'un monde solo écrit les mêmes lignes une fois de plus, donc une ligne
  répétée dans la même seconde ne compte qu'une fois. « Setting user: <nom> » nomme le joueur ; la ligne du serveur
  « <nom>[...] logged in with entity id N at (x, y, z) » indique où il est apparu.
* `saves\<monde>\stats\<uuid>.json` - l'écran des statistiques, écrit quand le monde
  est sauvegardé (sauvegarde automatique toutes les quelques minutes, et en quittant) : `stats` ->
  `minecraft:custom` (play_time en ticks, mob_kills, \*_one_cm distances, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Totaux du monde ; les chiffres de la
  session sont la différence avec ce que disait le fichier au lancement du jeu. Format : <https://minecraft.wiki/w/Statistics>
* `saves\<monde>\playerdata\<uuid>.dat` (et `level.dat` -> Data -> Player
  pour un hôte solo) - NBT compressé en gzip, écrit lors de ces mêmes sauvegardes :
  `Pos` [x, y, z] en doubles, `Rotation` [lacet, tangage], `Dimension`
  (« minecraft:overworld » ; un int 0/-1/1 avant la 1.16). NBT selon
  <https://minecraft.wiki/w/NBT_format> - lu ici par un petit lecteur à nous.
* `saves\<monde>\advancements\<uuid>.json` - la progression de l'écran des progrès,
  écrite lors des mêmes sauvegardes.

Les coordonnées sont en blocs, un bloc par mètre, Y vers le haut ; x vers l'est, z vers le sud - un repère
droitier, dessiné tel quel. Les positions n'arrivent qu'à la sauvegarde du monde, donc un parcours
est quelques points par sauvegarde automatique, pas une trace continue ; la dimension est la
`session`, si bien que le Nether n'est pas dessiné par-dessus l'Overworld.

Tout ce qui est lu est conservé en entier dans le fichier brut de la session (règle du convertisseur de 3DHeat) :
chaque ligne du journal sous son niveau (`INFO`, `WARN`, `ERROR`, ...; une ligne sans
l'en-tête entre crochets, comme une trace de pile, est `untagged`), et chaque fichier sauvegardé sous son
genre (`stats`, `advancements`, `playerdata`, `level.dat`) - le JSON en texte, le NBT en octets. Les chiffres
d'un fichier de statistiques ne se comprennent qu'à côté de ce qu'il disait au lancement du jeu, donc cette
première copie est aussi conservée (`baseline`), la première fois que le fichier change.

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | blocs (1 bloc = 1 m) |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `log` : il ne lit que ce que le jeu ou la plateforme fournit (des fichiers que le jeu écrit pendant qu'il tourne), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- latest.log : le nom du joueur (`Setting user`), les connexions avec la position, les connexions, les déconnexions, les morts avec le message de mort, les progrès, les lignes de chat, l'arrêt du serveur
- stats/<uuid>.json : temps de jeu, distance, éliminations de monstres et de joueurs, sauts, dégâts infligés et subis, blocs minés, objets fabriqués - la part de cette session
- playerdata/<uuid>.dat et level.dat (NBT) : position, dimension, lacet, tangage, vie, niveau d'expérience

**Conservé brut**

- chaque ligne de latest.log en entier, `type` = son niveau (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) avec le thread du journal dans `thread`, `used` là où elle est devenue une ligne ; une ligne sans l'en-tête entre crochets (une trace de pile, la bannière d'un mod) en `untagged`
- chaque stats/<uuid>.json en entier en texte, `type` `stats` (`used` : ses chiffres sont dans les statistiques), avec sa première copie depuis le démarrage du jeu comme `baseline`
- chaque advancements/<uuid>.json en entier en texte, `type` `advancements` (chaque critère et quand il a été atteint ; pas encore transformé en lignes)
- chaque playerdata/<uuid>.dat et level.dat en entier en octets (NBT gzip), `type` `playerdata` / `level.dat`, `used` là où il a donné une position : l'inventaire, le coffre de l'Ender, les effets, le point d'apparition, les règles du jeu, la graine du monde et l'heure ne sont que là
- chaque fichier sauvegardé a `world` et `file` (son chemin sous `saves`)

**Non disponible**

- une trace de position : le jeu n'écrit la position du joueur qu'à la sauvegarde du monde (toutes les quelques minutes et en quittant)
- les positions sur un serveur hébergé par quelqu'un d'autre : ses fichiers de monde sont sur le serveur, pas ici ; seul le journal est lu dans ce cas
- le monde lui-même (fichiers de région .mca, entités, cartes data/\*.dat et raids) : volumineux, et c'est le terrain, pas le jeu
- les journaux des sessions précédentes (logs/\*.log.gz) : conservés quand ils ont été joués
- l'édition Bedrock : elle n'écrit ni ce journal ni ces fichiers

**Taille** : latest.log 0,1 à 2 Mo par heure (davantage avec des mods) ; un fichier de statistiques 5 à 50 Ko et un fichier de joueur 5 à 100 Ko par sauvegarde automatique, level.dat 1 à 20 Ko - environ 1 à 5 Mo par heure au total ; zstd dans heat.raw.parquet ramène le texte à environ un dixième (les fichiers NBT sont déjà en gzip)

## Vérifié {#verified}

testé sur des lignes de journal synthétiques, du JSON de statistiques et des fichiers NBT construits à partir des formats publiés ; non testé avec le jeu

## Source {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
