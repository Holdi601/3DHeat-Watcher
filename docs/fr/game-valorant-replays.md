---
title: "VALORANT (replays)"
nav_order: 44
lang: "fr"
source: game-valorant-replays.md
source_hash: "617e23a33a4c"
nav_exclude: true
search_exclude: true
---
# VALORANT (replays) {#valorant-replays}

Après une partie de VALORANT, le watcher transforme le replay que le jeu a sauvegardé en fichiers que vous pouvez regarder sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `valorant-replays`, type [`replay`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 5 s.*

## Ce qui est enregistré {#what-is-recorded}

- la carte, l'identifiant de la partie et les agents choisis ; le bloc d'informations du replay (durée, versions, nom, date d'enregistrement, drapeaux de compression et de chiffrement)
- la chronologie des événements du serveur : éliminations (tueur et victime en identifiants réseau), débuts de manche, spikes posés, désamorcés et explosés, ultimes utilisés, changements de camp - chacun avec son identifiant et ses métadonnées
- chaque morceau du fichier conservé en entier dans heat.raw.parquet ; non décodé : les positions, les noms ou les scores - ils sont dans le flux brouillé

## D'où viennent les données {#where-it-comes-from}

les replays que VALORANT sauvegarde : %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (seulement les parties qui ne sont pas brouillées)

## Comment l'activer {#how-to-switch-it-on}

sauvegardez un replay dans VALORANT (carrière > partie > télécharger le replay) et installez le lecteur : github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Réglages par variables d'environnement :

- `HEAT3D_RIOT_REPLAYS` : le dossier du lecteur (un clone ou une version décompressée), quand il n'est pas installé ou à côté du watcher

## Fonctionnement {#how-it-works}

Replays de League of Legends et de Valorant : ce qu'on peut en lire tel quel.

Les deux jeux sauvegardent les replays sur le disque du joueur, et protègent ce qui est à l'intérieur :
les données de la partie seconde par seconde sont brouillées, et différemment à chaque patch, pour empêcher qu'on s'en serve pour tricher. En venir à bout supposerait de démonter le code du jeu, ce que les conditions de Riot interdisent (conditions d'utilisation 3.1 et 7.1) - donc ce n'est fait nulle part dans 3DHeat. Ce qui figure en clair dans chaque fichier est lu, et le reste est conservé tel quel : chaque partie du fichier, en entier, dans `heat.raw.parquet` de la session (règle du convertisseur de 3DHeat, docs/converters.md dans le dépôt du visualiseur), comptée dans `selfCheck.completeness` de meta.json.

Le watcher ne lit pas lui-même les fichiers : un lecteur externe le fait (3DHeat Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`, commande `heat3d-riot-replays`), tenu à part pour qu'un problème avec les conditions de Riot ne touche que ce lecteur. Trouvé dans le PATH, installé, ou à côté du watcher, il lit chaque nouveau replay ; s'il manque, le watcher indique une fois comment l'installer. Ce qu'il lit, le watcher le consigne dans la session ; la chronologie Match-V5 décrite plus bas est récupérée par le watcher lui-même, car elle ne se trouve pas dans le fichier.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, un replay local d'Unreal Engine. En clair :
le bloc d'informations du replay (durée, version réseau, changelist, son nom, date d'enregistrement,
compressé ou chiffré ou non), la carte, l'identifiant de la partie et les agents
choisis (dans l'en-tête), et la chronologie propre au serveur - éliminations
(tueur et victime en identifiants réseau, pas en noms), débuts de manche, spikes posés,
désamorcés et explosés, ultimes utilisés, changements de camp - chacun avec son heure,
son identifiant et ses métadonnées. Les positions, les noms, les scores et tout le reste sont dans le
flux brouillé (les morceaux de données du replay et de points de contrôle), conservé en entier et non lu.

Ce même module sert aussi : [League of Legends (replays)](game-lol-replays.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | non |
| Axe vertical | `z` |
| Unités | unités du monde de VALORANT |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `replay` : il ne lit que ce que le jeu ou la plateforme fournit (les replays et démos que le jeu sauvegarde), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- le bloc d'informations, chaque champ (`vrf` dans meta.json) : version du fichier, versions personnalisées, durée, version réseau, changelist, nom, drapeau de direct, date d'enregistrement, drapeaux compressé et chiffré, la clé telle qu'elle est stockée
- le morceau d'en-tête : la carte, l'identifiant de la partie et les agents choisis (reconnus à leur forme)
- chaque morceau d'événement : identifiant, groupe, métadonnées, heure de début et de fin, et de ses données le nom de l'événement, son heure en secondes et les nombres qui le précèdent (identifiants réseau du tueur et de la victime) - une ligne chacun

**Conservé brut**

- chaque morceau en entier, dans l'ordre du fichier (`offset`), si bien que les parties forment le fichier : `info`, `header`, `event <groupe>`, `replay_data`, `checkpoint`, `chunk <n>` pour un type que la structure ne nomme pas, `trailing` pour les octets après le dernier morceau complet

**Non disponible**

- positions, noms, scores, capacités, chaque image du jeu : les morceaux de données du replay et de points de contrôle sont brouillés ; les lire supposerait de démonter le client, ce que les conditions de Riot interdisent. Conservé en entier, non lu
- le contenu d'un replay chiffré : parcouru et conservé en entier, rien n'est lu à l'intérieur

**Taille** : le fichier brut conservé fait à peu près la taille du replay lui-même : le flux brouillé ne se compresse pas

## Vérifié {#verified}

le lecteur (heat3d-riot-replays) est construit à partir de la structure de conteneur documentée par vrfkit (Apache-2.0) ; non testé sur un vrai replay, aucun n'était disponible - il contrôle avant de lire et ignore ce qui ne correspond pas

## Source {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
