---
title: "Squad (replays)"
nav_order: 41
lang: "fr"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (replays) {#squad-replays}

Après une partie de Squad, le watcher transforme le replay que le jeu a sauvegardé en fichiers que vous pouvez regarder sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `squad-demos`, type [`replay`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 5 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position, l'orientation du corps et la vitesse de chaque joueur chaque fois que le serveur la réplique (jusqu'à 8 fois par seconde), à pied et dans les véhicules terrestres
- le nom, l'équipe, la faction et l'escouade de chaque joueur, en suivant les changements d'équipe
- non : le mouvement des hélicoptères, les kills et les déployables — voir le README du lecteur

## D'où viennent les données {#where-it-comes-from}

les démos de serveur que Squad enregistre avec la commande d'admin AdminDemoRec : &lt;server>/SquadGame/Saved/Demos/\*.replay, lues par le lecteur externe `heat3d-squad-demo` (exporters/ext/squad-demo)

## Comment l'activer {#how-to-switch-it-on}

enregistrez sur le serveur : donnez à l'admin la permission `demos` dans Admins.cfg, puis AdminDemoRec &lt;name> et AdminDemoStop dans la console du jeu ; copiez la démo ici et installez le lecteur : pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Paramètres issus de variables d'environnement :

- `HEAT3D_SQUAD_DEMO` : le dossier du convertisseur (un clone ou une version décompressée), quand il n'est pas installé ni à côté du watcher

## Comment ça marche {#how-it-works}

Replays et démos : ce qu'un jeu sauvegarde d'une partie, converti une fois la partie terminée.

Un replay contient tout ce qu'une interface en direct retient dans les jeux multijoueurs —
la position de chaque joueur, chaque kill là où il a eu lieu — et c'est un fichier que le jeu écrit
pour ses joueurs, donc le lire ne touche à rien dans le jeu. Le watcher regarde les dossiers où les
jeux les sauvegardent, attend qu'un nouveau fichier ait cessé de grossir (sinon le jeu est encore en
train de l'écrire), et le convertit dans un thread de travail, pour qu'une longue conversion ne bloque
jamais le reste du watcher.

La première fois qu'un dossier est vu, les replays déjà présents sont seulement notés, pas convertis :
un joueur avec des années de démos verrait sinon le watcher occupé pendant une journée.
`python -m heat3d_watch replays <adapter> [folder]` convertit les existants sur demande.

#### Squad {#squad}

Les serveurs dédiés de Squad enregistrent une démo d'une partie quand un admin ayant la permission
`demos` lance AdminDemoRec &lt;name> (puis AdminDemoStop), dans
`<server>/SquadGame/Saved/Demos/<name>.replay` — un replay de réseau Unreal Engine contenant ce que le
serveur a répliqué, mouvements de tous les joueurs compris. Le watcher ne les lit pas lui-même : un
lecteur externe le fait (lecteur de démos 3DHeat Squad, `exporters/ext/squad-demo`, commande
`heat3d-squad-demo`), gardé à part pour qu'un problème dans celui-ci ne touche à rien d'autre. Il est
lancé sur chaque nouvelle démo des dossiers où écrit un serveur local, ou dans un dossier que les
paramètres ajoutent pour les démos copiées depuis un serveur loué, et produit dans le dossier de
session `<map>/<match>.parquet` et `<match>.match.json`. La couche, la carte, le nombre de joueurs et
la durée du match deviennent les statistiques de la session.

Le même module sert aussi : [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md),
[osu! (replays)](game-osu-replays.md), [War Thunder (replays)](game-warthunder-replays.md),
[World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `z` |
| Unités | unités Unreal (centimètres) |
| Miroir pour la visionneuse | aucun |
| Échelle (`scale` : la visionneuse multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des
positions, dans le pied de `heat.parquet` : la visionneuse 3DHeat tourne et met à l'échelle les lignes
toute seule — voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `replay` : il ne lit que ce que le jeu ou la plateforme remet (les replays et démos que le jeu sauvegarde), donc il enregistre aussi en ligne ; l'indicateur décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne — voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et table `stats` de `watcher.sqlite`) :

`layer`, `map`, `match_seconds`, `players`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés
que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent
pas dans cette liste ; « Ce qui est enregistré » ci-dessus les nomme.

## Exhaustivité {#completeness}

Le convertisseur que lance cet adaptateur suit la [règle des convertisseurs](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)
de 3DHeat : ce que contient le replay est lu ou gardé, jamais abandonné — lu dans la table et dans le
document du match, tout le reste gardé entier dans des fichiers annexes à côté, compté dans
`selfCheck.completeness` du document du match. La documentation du convertisseur liste ce qu'il lit,
garde brut et ne peut pas lire.

## Vérifié {#verified}

le lecteur est vérifié sur des démos publiques de serveurs (le mouvement concorde avec la vitesse qu'il transporte ; l'équipe de chaque ligne correspond à la faction de son soldat) et par des tests sur des démos construites ; ce crochet par des tests avec une commande de remplacement

## Source {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
