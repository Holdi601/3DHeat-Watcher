---
title: "World of Warships (replays)"
nav_order: 48
lang: "fr"
source: game-wows-replays.md
source_hash: "e7d24a56747e"
nav_exclude: true
search_exclude: true
---
# World of Warships (replays) {#world-of-warships-replays}

Après une partie de World of Warships, le watcher transforme le replay que le jeu a sauvegardé en fichiers que vous pouvez regarder sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `wows-replays`, type [`replay`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 5 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position et le cap de chaque navire tant que le client d'enregistrement le voyait (environ 6 à 7 fois par seconde en mouvement), le navire du joueur tout du long
- allié ou ennemi, et le navire (celui du joueur qui enregistrait par son nom, les autres par le numéro de navire du jeu) ; les navires coulés là où ils ont sombré, et leurs tueurs là où ils se tenaient
- la carte ; le navire, les kills et la survie du joueur qui enregistrait, comme statistiques

## D'où viennent les données {#where-it-comes-from}

les replays que World of Warships sauvegarde : &lt;World of Warships>/replays/\*.wowsreplay (avec les replays activés), convertis par le convertisseur externe `heat3d-wows-replay` (exporters/ext/wows-replay)

## Comment l'activer {#how-to-switch-it-on}

activez l'enregistrement des replays dans World of Warships (`isReplayEnabled` dans son preferences.xml, ou le réglage du jeu quand il en a un), et installez le convertisseur : pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Paramètres issus de variables d'environnement :

- `HEAT3D_WOWS_REPLAY` : le dossier du convertisseur (un clone ou une version décompressée), quand il n'est pas installé ni à côté du watcher

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

#### World of Tanks et World of Warships {#world-of-tanks-and-world-of-warships}

Les deux sauvegardent un replay de chaque bataille dans `<jeu>/replays/` quand l'enregistrement est
activé (`*.wotreplay`, `*.wowsreplay`) ; les installations sont trouvées via la liste du Wargaming Game
Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, et via Steam. Comme pour War Thunder, le
watcher ne lit pas les fichiers lui-même : un convertisseur externe de chacun le fait
(`exporters/ext/wot-replay`, commande `heat3d-wot-replay` ; `exporters/ext/wows-replay`, commande
`heat3d-wows-replay`), chacun un projet à part entière.
Trouvé dans le PATH, installé ou à côté du watcher, il transforme chaque nouveau replay en
`<map>/<match>.parquet` et `<match>.match.json` dans le dossier de session ; sinon, le watcher le signale
une fois avec la marche à suivre pour l'installer. La ligne du joueur qui enregistrait — véhicule ou
navire, kills, dégâts (World of Tanks), survie, et résultat (World of Tanks) — devient les statistiques de
la session. Ce que lit chaque convertisseur, et ce qu'il ne lit pas, est dans son README.

Le même module sert aussi : [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md),
[Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md),
[World of Tanks (replays)](game-wot-replays.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | unités-monde de World of Warships (x est, y vertical, z nord ; une unité vaut 15 m selon la géométrie de la coque, 30 m selon les portées du jeu) |
| Miroir pour le visualiseur | `z` |
| Échelle (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des
positions, dans le pied de `heat.parquet` : le visualiseur 3DHeat tourne et met à l'échelle les lignes
toute seule — voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `replay` : il ne lit que ce que le jeu ou la plateforme remet (les replays et démos que le jeu sauvegarde), donc il enregistre aussi en ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne — voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et table `stats` de `watcher.sqlite`) :

`map`, `survived`, `vehicle`, `won`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés
que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent
pas dans cette liste ; « Ce qui est enregistré » ci-dessus les nomme.

## Exhaustivité {#completeness}

Le convertisseur que lance cet adaptateur suit la [règle des convertisseurs](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)
de 3DHeat : ce que contient le replay est lu ou gardé, jamais abandonné — lu dans la table et dans le
document de partie, tout le reste gardé entier dans des fichiers annexes à côté, compté dans
`selfCheck.completeness` du document de partie. La documentation du convertisseur liste ce qu'il lit,
garde brut et ne peut pas lire.

## Vérifié {#verified}

le convertisseur est vérifié sur des replays publics de plusieurs versions du jeu et par des tests sur des replays construits ; ce crochet par des tests avec une commande de remplacement

## Source {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
