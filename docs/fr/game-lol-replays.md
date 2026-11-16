---
title: "League of Legends (replays)"
nav_order: 30
lang: "fr"
source: game-lol-replays.md
source_hash: "ed26619fa904"
nav_exclude: true
search_exclude: true
---
# League of Legends (replays) {#league-of-legends-replays}

Après une partie de League of Legends, le watcher transforme le replay que le jeu a sauvegardé en fichiers que vous pouvez regarder sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `lol-replays`, type [`replay`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 5 s.*

## Ce qui est enregistré {#what-is-recorded}

- le champion de chaque joueur, son rôle, son équipe, ses éliminations, ses morts, ses passes décisives, son or, les dégâts infligés aux champions et son résultat, ainsi que chaque autre chiffre du tableau de fin de partie
- votre propre ligne comme statistiques, et vos lignes marquées comme les vôtres (`player` dans meta.json), avec votre Riot ID dans les réglages
- avec votre propre clé d'API Riot : la position de chaque joueur chaque minute avec les statistiques de cette minute, et chaque événement de la chronologie (éliminations là où elles ont eu lieu, bâtiments, monstres, balises, objets, sorts), à l'heure murale que donne la chronologie
- chaque partie du fichier de replay conservée en entier dans heat.raw.parquet ; non décodé : le déroulement de la partie seconde par seconde, qui est chiffré et brouillé contre la triche

## D'où viennent les données {#where-it-comes-from}

les replays que le client de League sauvegarde : %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (seulement les métadonnées de fin de partie en clair) ; avec votre propre clé d'API Riot, la chronologie officielle de la partie depuis l'API Match-V5 de Riot

## Comment l'activer {#how-to-switch-it-on}

sauvegardez un replay dans le client de League (historique des parties > télécharger) et installez le lecteur : github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`) ; pour les positions, réglez riot_api_key et riot_platform avec `config --set`

Réglages par variables d'environnement :

- `HEAT3D_RIOT_REPLAYS` : le dossier du lecteur (un clone ou une version décompressée), quand il n'est pas installé ou à côté du watcher

## Fonctionnement {#how-it-works}

Replays de League of Legends et de Valorant : ce qu'on peut en lire tel quel.

Les deux jeux sauvegardent les replays sur le disque du joueur, et protègent ce qui est à l'intérieur :
les données de la partie seconde par seconde sont brouillées, et différemment à chaque patch, pour empêcher qu'on s'en serve pour tricher. En venir à bout supposerait de démonter le code du jeu, ce que les conditions de Riot interdisent (conditions d'utilisation 3.1 et 7.1) - donc ce n'est fait nulle part dans 3DHeat. Ce qui figure en clair dans chaque fichier est lu, et le reste est conservé tel quel : chaque partie du fichier, en entier, dans `heat.raw.parquet` de la session (règle du convertisseur de 3DHeat, docs/converters.md dans le dépôt du visualiseur), comptée dans `selfCheck.completeness` de meta.json.

Le watcher ne lit pas lui-même les fichiers : un lecteur externe le fait (3DHeat Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`, commande `heat3d-riot-replays`), tenu à part pour qu'un problème avec les conditions de Riot ne touche que ce lecteur. Trouvé dans le PATH, installé, ou à côté du watcher, il lit chaque nouveau replay ; s'il manque, le watcher indique une fois comment l'installer. Ce qu'il lit, le watcher le consigne dans la session ; la chronologie Match-V5 décrite plus bas est récupérée par le watcher lui-même, car elle ne se trouve pas dans le fichier.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Les deux versions du conteneur portent le tableau de fin de partie en JSON clair (`statsJson`) : pour chacun des dix joueurs, le champion, les éliminations, les morts, les passes, l'or, les dégâts aux champions, les objets, l'équipe, le rôle, la victoire, leur Riot ID, et chaque autre chiffre que le jeu totalise (plus d'une centaine par joueur) ; tous deviennent la ligne `player_result` du joueur. ROFL1 (patch 14.9 et antérieurs) l'a après un en-tête fixe (`RIOT\0\0`, une signature de 256 octets, puis les longueurs) ; ROFL2 (14.11 et suivants, `RIOT\2\0`) à la fin du fichier, sa longueur dans les quatre derniers octets (indiqué par un ingénieur de Riot, ReplayBook issue 299). L'en-tête de charge utile de ROFL1 (identifiant de partie, longueur, nombre de morceaux et d'images clés, longueur de la clé des morceaux) et sa table des morceaux (identifiant, type, longueur, morceau suivant, décalage) sont en clair et lus ; les morceaux eux-mêmes sont chiffrés et conservés en entier sans être lus.

Les positions ne viennent pas du fichier. Avec une clé développeur Riot à vous (`riot_api_key` dans les réglages ; une clé personnelle est faite exactement pour cela, « afficher les statistiques (propres) du joueur »), la chronologie officielle de la partie est récupérée depuis l'API Match-V5 de Riot : la position de chaque joueur une fois par minute avec tout ce que dit l'image de la minute à son sujet (or, expérience, niveau, sbires, statistiques de champion et de dégâts), et chaque événement de la chronologie - éliminations, bâtiments, monstres élites, balises, objets, sorts, niveaux - en une ligne chacun, placé là où il a un lieu. Sans clé, rien n'est récupéré et rien n'est envoyé.

Ce même module sert aussi : [VALORANT (replays)](game-valorant-replays.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | unités de la carte de la Faille de l'Invocateur (environ 15000 d'un bout à l'autre) |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `replay` : il ne lit que ce que le jeu ou la plateforme fournit (les replays et démos que le jeu sauvegarde), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`champion`, `game_seconds`, `won`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- les métadonnées JSON : durée de la partie, version, identifiants du dernier morceau et des images clés, et `statsJson` - chaque champ du tableau de chaque joueur sur sa ligne `player_result` (les nombres donnés sous forme de texte sont lus comme des nombres)
- ROFL1 : le bloc des longueurs, l'en-tête de charge utile (identifiant de partie, durée de partie, nombre d'images clés et de morceaux, identifiants du morceau de démarrage et du morceau de début de partie, intervalle des images clés, la clé des morceaux telle qu'elle est stockée) et la table des morceaux (identifiant, type, longueur, morceau suivant, décalage) - dans `rofl` de meta.json et dans le `text` des lignes brutes
- ROFL2 : la chaîne de version
- la chronologie Match-V5 (seulement avec votre propre clé d'API) : chaque image de participant sur une ligne `position` (ou `participant_frame` sans lieu) avec tous ses champs aplatis (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...) ; chaque événement comme une ligne nommée d'après son type, placée là où il a une `position`, CHAMPION_KILL comme une élimination et une mort

**Conservé brut**

- chaque partie du .rofl, en entier, dans l'ordre du fichier (`offset`), si bien que les parties forment le fichier : `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1) ; `body`, `metadata`, `metadata_length` (ROFL2) ; toute portion qu'aucune partie ne couvre comme `unknown`
- la chronologie en entier : `timeline <type>` pour chaque événement, `timeline participantFrame` pour l'image de chaque joueur (`participant` son identifiant), `timeline` pour le reste

**Non disponible**

- le jeu lui-même (positions, capacités, chaque unité, seconde par seconde) : les morceaux de ROFL1 et le corps de ROFL2 sont chiffrés et les paquets qu'ils contiennent sont brouillés à chaque patch ; y parvenir supposerait de démonter le client, ce que les conditions de Riot interdisent (3.1, 7.1). Conservé en entier, non lu
- les positions sans votre propre clé d'API Riot : le fichier n'en a pas en clair

**Taille** : le fichier brut conservé fait à peu près la taille du replay lui-même : les morceaux chiffrés ne se compressent pas

## Vérifié {#verified}

le lecteur (heat3d-riot-replays) testé sur des fichiers construits selon les structures de roflxd.cs (MIT) ; la chronologie sur le JSON documenté de Match-V5 ; aucun vrai replay n'était disponible pour vérifier

## Source {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
