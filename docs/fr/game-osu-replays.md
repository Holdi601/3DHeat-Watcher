---
title: "osu! (replays)"
nav_order: 35
lang: fr
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (replays) {#osu-replays}

Après une partie d'osu!, le watcher transforme le replay que le jeu a sauvegardé en fichiers que vous pouvez regarder sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `osu-replays`, type [`replay`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 5 s.*

## Ce qui est enregistré {#what-is-recorded}

- le trajet du curseur sur la zone de jeu (x 0..512, y 0..384) et les touches maintenues, à chaque image
- score, combo, 300, 100, 50, gekis, katus, fautes, précision, mods, combo parfait
- la barre de vie pendant la partie, les empreintes du beatmap et du replay, la graine aléatoire, l'identifiant de score en ligne

## D'où viennent les données {#where-it-comes-from}

replays qu'osu! (version stable) sauvegarde : %LOCALAPPDATA%/osu!/Data/r/\*.osr (chaque partie) et osu!/Replays/\*.osr (exportés)

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Fonctionnement {#how-it-works}

Replays et démos : ce qu'un jeu sauvegarde d'une partie, converti une fois la partie terminée.

Un replay contient tout ce qu'une interface en direct retient dans les jeux multijoueurs - la position de chaque joueur, chaque élimination à l'endroit où elle s'est produite - et c'est un fichier que le jeu écrit pour ses joueurs, donc le lire ne touche pas au jeu. Le watcher regarde les dossiers où les jeux les sauvegardent, attend qu'un nouveau fichier cesse de grossir (sinon le jeu est encore en train de l'écrire), et le convertit dans un thread de travail, pour qu'une longue conversion ne bloque jamais le reste du watcher.

La première fois qu'un dossier est vu, les replays déjà présents sont seulement notés, non convertis : un joueur avec des années de démos verrait sinon le watcher occupé pendant une journée. `python -m heat3d_watch replays <adaptateur> [dossier]` convertit les existants sur demande.

#### osu! {#osu}

osu! (version stable) sauvegarde chaque partie dans `osu!/Data/r/*.osr` et les replays exportés dans `osu!/Replays/`. Le watcher les lit lui-même, selon le format publié par le wiki d'osu! : le trajet du curseur et les touches à chaque image, la ligne de score, la barre de vie, la graine et l'identifiant de score ; le fichier est conservé entier à côté, par morceaux, dans le `heat.raw.parquet` de la session.

Le même module sert aussi : [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | pixels d'osu! (zone de jeu 512 x 384) |
| Miroir pour la visionneuse | `z` |
| Échelle des unités (`scale` : la visionneuse multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` affiche « autorisé (lit seulement ce que le jeu publie) ».
- Type `replay` : il ne lit que ce que le jeu ou la plateforme fournit (les replays et démos que le jeu sauvegarde), donc il enregistre aussi en ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur définit par leur nom (`stats` de chaque `meta.json` de session et table `stats` de `watcher.sqlite`) :

`accuracy`, `full_combo`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- chaque image : une ligne à son moment (millisecondes cumulées), x et y sur la zone de jeu, `keys` les bits de touches (souris 1 et 2, touches 1 et 2, fumée) ; en mania, x contient les touches maintenues au lieu d'un emplacement
- l'en-tête, chaque champ : mode, version, le MD5 du beatmap (le fichier ne nomme le beatmap que par lui), le joueur, le MD5 du replay, 300, 100, 50, gekis, katus, fautes, score, combo maximal, combo parfait, mods (par leur nom dans `osu.modNames` de meta.json), l'heure de la partie - en statistiques et dans `osu` de meta.json
- la courbe de la barre de vie : une ligne `life` par point (temps, vie 0..1)
- l'image `-12345` : la graine aléatoire (`osu.seed`) ; l'identifiant de score en ligne (`osu.scoreId`) ; avec Target Practice, sa précision (`osu.targetPracticeAccuracy`)

**Conservé brut**

- le fichier entier, par morceaux, dans heat.raw.parquet (`offset` où chacun commence, pour que les morceaux forment le fichier) : `header`, `replay_data` (les images compressées en LZMA telles qu'elles sont stockées), `score_id`, `mod_info`, et `trailing` pour tout ce qui suit les morceaux que le format décrit (les exports d'osu!lazer y ajoutent des données) - conservé, non lu

**Non disponible**

- le beatmap lui-même (objets à toucher, rythme) : il n'est pas dans un replay ; il n'est nommé que par son MD5
- les replays d'osu!lazer : ils sont dans sa base de données, pas sous forme de fichiers

**Taille** : le fichier brut conservé a à peu près la taille du replay (des dizaines à des centaines de kilo-octets)

## Vérifié {#verified}

testé sur des replays construits selon le format .osr publié ; osu!lazer garde ses replays dans son propre magasin et n'est pas lu

## Source {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
