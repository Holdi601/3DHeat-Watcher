---
title: "NVIDIA Highlights"
nav_order: 8
lang: fr
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Certains jeux demandent à votre pilote graphique NVIDIA de sauvegarder une courte vidéo quand quelque chose se produit, comme un frag.
Le Watcher note chacun de ces moments et, quand il le peut, le place sur la carte à l'endroit où il a eu lieu.

L'adaptateur `nvidia-highlights` enregistre les clips, les moments forts et les captures d'écran que l'application NVIDIA (ou GeForce Experience) sauvegarde, et donne à chacun un lieu sur la carte quand il le peut. Cette page explique ce que NVIDIA Highlights peut fournir et ce qu'il ne peut pas, quels fichiers le Watcher lit, et comment un moment fort obtient une position. La page générée de l'adaptateur est [NVIDIA highlights (plateforme)](game-nvidia-highlights.md).

## Ce que NVIDIA Highlights peut et ne peut pas fournir {#what-nvidia-highlights-can-and-cannot-deliver}

Un jeu qui gère NVIDIA Highlights parle à l'application NVIDIA par le GfeSDK de NVIDIA. Le SDK ne transporte que deux sortes de messages :

1. **Une fois, au démarrage** : les types de moments forts que le jeu utilisera - un identifiant (comme `kill`), une importance, des étiquettes, et un nom affiché par langue. L'application NVIDIA les garde par jeu.
2. **À un moment de la partie** : « moment fort `<id>`, de `<ms>` avant maintenant à `<ms>` après ». C'est tout le message : l'identifiant d'un type que le jeu a enregistré, et deux décalages temporels qui indiquent à l'application NVIDIA quel bout de son enregistrement glissant garder.

Le SDK n'a **aucun champ pour autre chose** : ni position, ni match ou manche, ni adversaire, ni arme, ni score, ni donnée personnalisée de quelque sorte. Un jeu ne peut pas mettre une position dans un moment fort, même s'il le voulait. Quand le clip est sauvegardé, l'application NVIDIA ajoute un fichier, un nom de jeu, une durée et une heure.

Un moment fort ne peut donc dire qu'une chose : « ce type de moment, dans ce jeu, à cette heure ». Tout le reste doit venir d'ailleurs.

## Ce que lit le Watcher {#what-the-watcher-reads}

Tout est lu dans les fichiers que l'application NVIDIA écrit pour sa propre galerie. Rien ne parle au pilote ni à l'application. Le dossier de superposition NVIDIA est `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Fichier | Ce qui en est pris |
|---|---|
| `UGCTracker.json` | l'index de la galerie : chaque clip et capture d'écran avec son chemin, son type (vidéo, image), son sous-type (`InstantReplay`, ...), sa date, le nom de profil du jeu, l'exécutable et le nom court, et la durée (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, le dossier de capture, et `settings.tempDirectory`, où attendent les moments forts (`<temp>\Highlights\<game>`) jusqu'à leur sauvegarde |
| `Highlights\<game>\config.json` | les types de moments forts que chaque jeu a enregistrés : identifiant, et le nom affiché en anglais (ou l'identifiant quand le jeu n'en a pas donné) |
| le dossier de capture (par défaut `%USERPROFILE%\Videos\NVIDIA`) et `<temp>\Highlights` | les fichiers de clips et de captures eux-mêmes (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), un dossier par jeu |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | les requêtes que les jeux GfeSDK journalisent - les lignes `Posted Request HL...` - pour qu'un moment fort demandé par le jeu soit enregistré même quand aucun clip n'a été gardé. Les requêtes de configuration (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) sont ignorées. |

Pour chaque nouvel élément, l'adaptateur écrit une ligne : `highlight` pour une vidéo, `screenshot` pour une image, ou `highlight_request` pour une ligne du journal GfeSDK. Ses champs :

| Champ | Ce que c'est |
|---|---|
| `ms` | le moment : l'heure du nom de fichier (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, l'heure locale de la sauvegarde du clip), sinon la date de l'index, sinon l'heure de modification du fichier |
| `game` | le nom de profil NVIDIA, le nom du dossier ou le nom du jeu dans le nom de fichier |
| `clip`, `media` | le chemin du fichier ; `video`, `image` ou `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (du dossier temporaire des moments forts) ou le sous-type de l'index |
| `duration_s`, `clip_start_ms` | la durée, depuis l'index ou depuis l'en-tête de la vidéo (`moov/mvhd`, trouvé sans lire la vidéo) ; le moment où le clip commence |
| `highlight_id`, `highlight_name` | le type de moment fort, quand quelque chose le nomme (voir plus bas) |
| `exe` | l'exécutable du jeu, depuis l'index |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | la position empruntée, quand une a été trouvée (voir plus bas) |

Les statistiques de session sont `clips`, `screenshots`, `clip_seconds` et `placed` (les éléments qui ont reçu une position).

**L'identifiant du moment fort** n'est écrit dans aucun endroit documenté. L'adaptateur en essaie deux, non documentés : un champ de l'entrée de galerie dont le nom contient « highlight », et - seulement pour les fichiers du dossier temporaire des moments forts - l'un des identifiants enregistrés par le jeu (d'au moins 4 caractères) qui apparaît dans le nom du fichier. Un clip sauvegardé est nommé d'après le jeu, qui pourrait contenir par hasard un identifiant comme « kill », donc son nom n'est pas cherché. Ces deux méthodes n'ont pas encore été vues fonctionner sur une vraie machine : aucun clip avec identifiant de moment fort, et aucune ligne de requête GfeSDK, ne s'est présenté là où l'adaptateur a été testé. L'index de la galerie, les réglages, les définitions des moments forts et les clips ont été testés sur de vrais fichiers.

### Quand les éléments sont enregistrés {#when-items-are-recorded}

- Un clip continue d'être écrit un moment après l'appui sur la touche. L'adaptateur attend qu'un fichier ait la même taille et la même heure à deux regards (toutes les 10 s) et qu'il ait au moins 5 s.
- La première fois que l'adaptateur tourne, tout ce qui est déjà dans la galerie et dans les journaux n'est que noté, pas enregistré, pour que des années de vieux clips n'inondent pas les statistiques. Ce qu'il a vu est gardé dans `<data>\state\nvidia-highlights.json`, donc un redémarrage n'enregistre rien deux fois.
- Les éléments sont regroupés en une session par jeu. La session d'un jeu se ferme après 30 minutes sans nouvel élément, et finit à son dernier moment plutôt qu'à la fermeture du jeu. Des moments séparés de plus de 30 minutes vont dans des sessions distinctes.

## Comment un moment fort obtient une position {#how-a-highlight-gets-a-position}

Le moment fort lui-même n'a pas de lieu. L'adaptateur cherche le moment dans les autres enregistrements que le Watcher a faits du même jeu, au même moment :

1. **Le même jeu** : les dossiers de session sous `<data>\sessions\` dont le nom de jeu correspond à celui du moment fort. Les noms sont comparés en minuscules, lettres et chiffres seulement. Ils correspondent quand ils sont égaux, ou quand le plus court a au moins 5 caractères et est contenu dans le plus long (`Counter-Strike 2` et `Counter-Strike-2`).
2. **Le même moment** : les sessions dont le début et la fin (depuis `meta.json`, avec une seconde de marge à chaque bout) couvrent le moment. Les sessions terminées sans positions, et les sessions propres à l'adaptateur, sont ignorées.
3. **La ligne propre au joueur** : dans son `events.jsonl`, la plus récente des lignes propres au joueur qui ont une position, au moment du moment fort ou avant, et au plus 5 secondes avant. Une ligne est propre au joueur quand sa source le dit : `"player": "me"`, ou `"own_car": 1` (jeux de course qui enregistrent chaque voiture par son pilote), ou un `player` qui est le `player` de la session dans `meta.json` (le nom que la source donne au joueur). Voir [Les lignes propres au joueur](the-data.md#the-players-own-rows).

Si une ligne est trouvée, le moment fort reçoit ses `x`, `y`, `z`, sa `session` (ou le nom du dossier), `position_from` (le dossier d'où elle vient) et `position_lag_ms` (il y a combien de temps, avant le moment, était cette ligne). La session du moment fort prend les axes de cet enregistrement, donc il est dessiné dans le même sens. Si aucune ligne n'est trouvée, le moment fort reste un instant sur la chronologie, sans lieu.

Points à connaître sur la position empruntée :

- **C'est l'endroit où vous étiez quand le clip a été sauvegardé**, pas l'endroit où l'action a commencé. Le moment est l'heure de la sauvegarde indiquée dans le nom du fichier, qui pour un Instant Replay est sa fin. `clip_start_ms` indique où commence le clip.
- **Un autre adaptateur doit avoir enregistré le même jeu à ce moment.** Ceux qui marquent les lignes propres au joueur, et peuvent donc placer un moment fort : l'intégration d'état de jeu de Counter-Strike 2 et de Dota 2, Forza, les jeux Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft et les profils de mémoire (comme `me`) ; F1 23/24/25, RaceRoom, Automobilista 2 et Project CARS 2 (les lignes de votre voiture portent `own_car` 1, selon l'index de voiture du joueur donné par le jeu, son propre emplacement ou le participant regardé) ; Elite Dangerous (le nom du commandant, dans `meta.json` comme `player`, puisque le journal est toujours celui du joueur).
- **Un replay est converti après le match**, donc il ne peut placer qu'un clip recherché après la conversion : le clip est placé quand il est enregistré, et un replay sauvegardé plus tard n'est pas revu. Les replays de League of Legends nomment vos lignes par le Riot ID des réglages et, avec une clé d'API Riot, leur donnent l'heure réelle que la chronologie du match indique, pour qu'ils soient trouvés à ce moment-là. Une démo CS2 ne peut pas placer de moment fort du tout : ses positions sont dans la table propre au convertisseur, pas dans `events.jsonl`, et une démo a les ticks du jeu mais pas d'heure réelle à laquelle comparer le moment d'un clip.
- Dans Rocket League, les seules lignes avec un lieu sont les événements de balle. Un coup de balle de votre part est une ligne à vous, donc un moment fort peut être placé là où vous avez touché la balle en dernier.
- Les jeux sans aucune source de position (Overwatch 2, Call of Duty, Hunt: Showdown, ...) gardent leurs moments forts comme une chronologie de moments.

## Pourquoi la mémoire ne peut pas donner une position en multijoueur {#why-memory-cannot-give-a-position-in-multiplayer}

L'autre façon d'obtenir une position serait de la lire dans la mémoire. Aucune des deux mémoires ne convient :

- **La mémoire de NVIDIA ne contient pas de position.** L'application NVIDIA reçoit ce que le GfeSDK transporte - un identifiant de moment fort et deux décalages temporels - plus la vidéo qu'elle enregistre. Il n'y a nulle part de position côté NVIDIA à lire. (Le Watcher ne lit de toute façon pas la mémoire de NVIDIA ; il lit les fichiers ci-dessus.)
- **La mémoire du jeu est interdite en multijoueur.** La position est dans le processus du jeu, mais le Watcher ne lit jamais la mémoire d'un jeu multijoueur : un adaptateur mémoire pour un jeu marqué comme joué en ligne est refusé avant que quoi que ce soit ne soit ouvert (voir [Lecture de la mémoire](memory-reading.md)). Les jeux multijoueurs tournent sous des anti-triches (Easy Anti-Cheat, BattlEye, Vanguard, ...) qui considèrent comme de la triche qu'un autre programme ouvre le processus du jeu, ce qui peut faire bannir le compte. Lire l'état du jeu de l'extérieur est aussi ce que les conditions des jeux interdisent. Un moment fort dans un jeu multijoueur n'a donc un lieu que grâce à ce que le jeu publie : son intégration d'état de jeu ou sa télémétrie, enregistrées par un autre adaptateur au même moment.
