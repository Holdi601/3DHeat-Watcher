---
title: "War Thunder (replays)"
nav_order: 45
lang: "fr"
source: game-warthunder-replays.md
source_hash: "4bf6e2f218cb"
nav_exclude: true
search_exclude: true
---
# War Thunder (replays) {#war-thunder-replays}

Après une partie de War Thunder, le watcher transforme le replay que le jeu a sauvegardé en fichiers que vous pouvez regarder sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `warthunder-replays`, type [`replay`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 5 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position et l'attitude de chaque avion environ 4 fois par seconde (autant que le replay en contient)
- les positions des unités au sol, depuis la synchronisation au sol du replay (replays de 2026 ; pas ceux de 2025)
- qui était chaque unité (joueur, identifiant du véhicule, équipe) quand un kill ou un impact la nomme ; kills, morts et impacts là où ils ont eu lieu ; le chat ; la carte
- les kills, morts, score et captures de l'auteur du replay, comme statistiques

## D'où viennent les données {#where-it-comes-from}

les replays que War Thunder sauvegarde : &lt;War Thunder>/Replays/\*.wrpl (avec la sauvegarde des replays activée), convertis par le convertisseur externe `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Comment l'activer {#how-to-switch-it-on}

activez la sauvegarde des replays dans les options de War Thunder, et installez le convertisseur : pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Paramètres issus de variables d'environnement :

- `HEAT3D_WT_REPLAY` : le dossier du convertisseur (un clone ou une version décompressée), quand il n'est pas installé ni à côté du watcher

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

#### War Thunder {#war-thunder}

War Thunder sauvegarde un replay de chaque bataille dans `<War Thunder>/Replays/*.wrpl` quand la
sauvegarde des replays est activée dans ses options. Le watcher ne les lit pas lui-même : un
convertisseur externe le fait (convertisseur de replays War Thunder 3DHeat,
`exporters/ext/warthunder-replay`, commande `heat3d-wt-replay`), un projet à part
entière. Quand la commande est dans le PATH, ou que le paquet est
installé ou à côté du watcher, chaque nouveau replay passe dedans et produit dans le dossier de session
`<map>/<match>.parquet` et `<match>.match.json` ; sinon, le watcher le signale une fois avec la marche à
suivre pour l'installer, et laisse le dossier tranquille. Ce que lit le convertisseur, et ce qu'il ne
lit pas, est dans son README. La ligne de résultat de l'auteur du replay — kills, kills au sol, morts,
assistances, score, captures — devient les statistiques de la session.

Le même module sert aussi : [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md),
[Squad (replays)](game-squad-demos.md), [World of Tanks (replays)](game-wot-replays.md),
[World of Warships (replays)](game-wows-replays.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres (x est, y vertical, z nord) |
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

`map`

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

le convertisseur est vérifié sur des replays publics de plusieurs versions du jeu (les kills et les noms concordent avec les résultats) et par des tests sur des replays construits ; ce crochet par des tests avec une commande de remplacement

## Source {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
