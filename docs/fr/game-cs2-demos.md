---
title: "Counter-Strike 2 (replays)"
nav_order: 8
lang: "fr"
source: game-cs2-demos.md
source_hash: "82fe00f0f2f0"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replays) {#counter-strike-2-replays}

Après une partie de Counter-Strike 2, le watcher transforme le replay que le jeu a sauvegardé en fichiers que vous pouvez regarder sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `cs2-demos`, type [`replay`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 5 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position, la direction du regard, la vie et l'argent de chaque joueur (à chaque 8e tick)
- les kills, morts, dégâts, grenades, poses et désamorçages de bombe, là où ils ont eu lieu
- les rounds, le score, l'économie ; la ligne du tableau des scores du joueur connecté, comme statistiques

## D'où viennent les données {#where-it-comes-from}

les démos que CS2 sauvegarde : &lt;CS2>/game/csgo/replays/\*.dem (téléchargées depuis l'historique des matchs) et &lt;CS2>/game/csgo/\*.dem (enregistrées)

## Comment l'activer {#how-to-switch-it-on}

téléchargez la démo d'un match dans CS2 (Regarder > Vos matchs), ou enregistrez-en une avec la commande de console `record`

Paramètres issus de variables d'environnement :

- `HEAT3D_CS2` : le dossier de 3DHeat CS2, quand il n'est pas à côté du watcher ni installé

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

#### Counter-Strike 2 {#counter-strike-2}

CS2 sauvegarde les démos qu'un joueur télécharge depuis l'historique des matchs (onglet Regarder) dans
`<CS2>/game/csgo/replays/`, et celles enregistrées avec la commande de console `record` dans
`<CS2>/game/csgo/`. Chacune est convertie par le convertisseur CS2 de ce dépôt (3DHeat CS2,
github.com/Holdi601/3DHeat-CS2 : la position, la direction du regard, la vie et l'argent de chaque
joueur à chaque huitième tick ; kills, morts, dégâts, grenades, poses et désamorçages de bombe là où
ils ont eu lieu ; rounds, score, économie) dans le dossier de session, sous forme de table
`<map>/<match>.parquet` et de résumé `<match>.match.json` que lisent les onglets Carte de chaleur et
Match du visualiseur. Le tableau des scores du match devient les statistiques de la session : pour
le joueur dont le compte Steam est connecté sur cette machine (depuis le `loginusers.vdf` de Steam),
sous leurs noms simples — kills, morts, assistances, ADR, KAST, pourcentage de headshots, premiers
kills, clutches — ainsi que le score et les rounds.

Le même module sert aussi : [Dota 2 (replays)](game-dota-replays.md),
[Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md),
[World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `z` |
| Unités | pouces (unités Source) |
| Miroir pour le visualiseur | `y` |
| Échelle (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des
positions, dans le pied de `heat.parquet` : le visualiseur 3DHeat tourne et met à l'échelle les lignes
toute seule — voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `replay` : il ne lit que ce que le jeu ou la plateforme remet (les replays et démos que le jeu sauvegarde), donc il enregistre aussi en ligne ; l'indicateur décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne — voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et table `stats` de `watcher.sqlite`) :

`map`, `rounds`, `score.{team}`, `won`

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

le convertisseur est testé sur de vraies démos de tournoi ; la surveillance du dossier et les statistiques par des tests

## Source {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
