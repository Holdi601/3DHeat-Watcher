---
title: "Path of Exile (fichiers journal)"
nav_order: 35
lang: "fr"
source: game-poe.md
source_hash: "b5783b5a5690"
nav_exclude: true
search_exclude: true
---
# Path of Exile (fichiers journal) {#path-of-exile-log-files}

Pendant que vous jouez à Path of Exile, le watcher lit les fichiers qu'écrit le jeu et enregistre ce qui s'est passé, pour que vous puissiez le regarder plus tard sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `poe`, type [`log`](sources-and-rules.md) ; il tourne pendant que `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` ou `PathOfExile_x64_KG.exe` est lancé et cherche de nouvelles données toutes les 0,5 s.*

## Ce qui est enregistré {#what-is-recorded}

- les zones entrées, avec le niveau de zone, son identifiant et sa graine
- les montées de niveau, avec la classe et le niveau
- les morts (« has been slain »)
- les joueurs qui entrent et sortent de la zone, les chuchotements reçus et envoyés, les demandes d'échange, les échanges acceptés
- chaque ligne de Client.txt de cette session, entière, dans heat.raw.parquet
- morts, niveaux gagnés, niveau le plus haut, zones entrées, zones distinctes, chuchotements, demandes d'échange, échanges

## D'où viennent les données {#where-it-comes-from}

&lt;installation>\logs\Client.txt de Path of Exile ou Path of Exile 2 (suivi ; le dossier d'installation est celui de l'exécutable lancé)

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Fonctionnement {#how-it-works}

Path of Exile et Path of Exile 2 : le journal du client, `<installation>\logs\Client.txt`.

Les deux jeux ajoutent à la suite dans un seul Client.txt, dans leur dossier d'installation, tant qu'ils sont installés (il grandit d'un lancement à l'autre). Les lignes ressemblent à ceci :

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- l'heure locale, un compteur en millisecondes, un hachage, le niveau et le thread, puis ce qu'affiche la fenêtre de discussion. Les messages sont ceux du client en anglais ; un client dans une autre langue les écrit traduits et n'est pas compris ici. Rien ne donne une position. Le format n'est pas documenté par Grinding Gear Games ; c'est le journal en texte brut du jeu, tel que des outils communautaires (aides aux échanges, guides de niveau) le lisent depuis des années - par ex. <https://github.com/klayveR/poe-log-monitor> (MIT) pour la liste des événements.

Le dossier d'installation est celui de l'exécutable lancé ; sans lui, les bibliothèques Steam et le dossier par défaut du client autonome sont cherchés.

Chaque ligne de cette session est conservée entière dans le fichier brut de la session (règle du convertisseur de 3DHeat), qu'elle ait un sens ici ou non : `type` est le niveau et le journaliseur entre crochets (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), une ligne horodatée sans crochets est `untagged`, une ligne sans heure `untimed`.

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | non |
| Axe vertical | `y` |
| Unités | aucune position enregistrée |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes tout seul : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` affiche « autorisé (lit seulement ce que le jeu publie) ».
- Type `log` : il ne lit que ce que le jeu ou la plateforme fournit (les fichiers écrits par le jeu pendant qu'il tourne), donc il enregistre aussi en ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur définit par leur nom (`stats` de chaque `meta.json` de session et table `stats` de `watcher.sqlite`) :

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- `You have entered <zone>`, avec le niveau de zone, l'identifiant de zone et la graine de la ligne `Generating level` qui précède
- `<nom> (<classe>) is now level <n>`, `<nom> has been slain`, les joueurs qui entrent et sortent de la zone, les chuchotements reçus et envoyés (avec l'indication qu'il s'agit ou non d'une demande d'échange), les échanges acceptés et annulés

**Conservé brut**

- chaque ligne de cette session, entière, `type` = le niveau et le journaliseur entre crochets (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` là où elle est devenue une ligne : chat global, échange, groupe et guilde, `Connecting to instance server`, les avis AFK et DND, les réponses aux commandes de chat comme `/played` et `/deaths`, les lignes de chargement et du moteur du client - conservées, pas encore transformées en lignes
- une ligne horodatée sans crochets (`***** LOG FILE OPENING *****`) comme `untagged`, une ligne sans heure comme `untimed`

**Non disponible**

- positions : rien dans le journal n'en donne
- ce qu'écrit un client dans une autre langue : les lignes sont conservées, mais seuls les messages anglais deviennent des lignes
- les lignes des lancements précédents : Client.txt grandit d'un lancement à l'autre ; les lignes horodatées avant cette exécution du jeu sont laissées (elles ont été conservées au moment où elles ont été jouées)
- les tués, les dégâts, le butin et l'arbre des passifs : le jeu ne les journalise pas

**Taille** : Client.txt grandit d'environ 0,3 à 3 Mo par heure (surtout à cause des lignes DEBUG pendant le chargement des zones, davantage avec un chat d'échanges chargé) ; zstd dans heat.raw.parquet le réduit à environ un dixième

## Vérifié {#verified}

testé sur des lignes Client.txt synthétiques au format du jeu ; non testé contre le jeu

## Source {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
