---
title: "Hearthstone (fichiers journal)"
nav_order: 25
lang: fr
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (fichiers journal) {#hearthstone-log-files}

Pendant que vous jouez à Hearthstone, le watcher lit les fichiers qu'écrit le jeu et enregistre ce qui s'est passé, pour que vous puissiez le regarder plus tard sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `hearthstone`, type [`log`](sources-and-rules.md) ; il tourne pendant que `Hearthstone.exe` est lancé et cherche de nouvelles données toutes les 0,5 s.*

## Ce qui est enregistré {#what-is-recorded}

- début et fin de partie, avec le résultat (gagnée, perdue, égalité), les tours et le nom de l'adversaire
- chaque tour
- chaque ligne de Power.log et des autres journaux, entière, dans heat.raw.parquet
- parties, victoires, défaites, égalités, tours, partie la plus longue

## D'où viennent les données {#where-it-comes-from}

&lt;installation>\Logs\Power.log (ou Logs\Hearthstone_\*\Power.log), écrit une fois que %LOCALAPPDATA%\Blizzard\Hearthstone\log.config contient une section [Power], et tout autre \*.log que le jeu écrit à cet endroit

## Comment l'activer {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` ajoute la journalisation [Power] à %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (une sauvegarde est gardée) ; redémarrez le jeu

Tapez la commande dans un terminal ouvert dans le dossier du watcher (voir [Avant de commencer](before-you-start.md)). En cas d'échec, la dernière ligne indique pourquoi ; [Installation et lancement](installing-and-running.md) couvre les causes habituelles.

`python -m heat3d_watch setup hearthstone` liste les fichiers qu'il modifierait ; `python -m heat3d_watch setup hearthstone --apply` les modifie, en gardant l'original sous `<fichier>.heat3d-backup` (voir [Commandes](commands.md#setup)). Il affiche `hearthstone: changed: ...` pour chaque modification, ou `hearthstone: nothing to change` si c'est déjà activé.

## Fonctionnement {#how-it-works}

Hearthstone : le Power.log du jeu, que le jeu écrit une fois que `log.config` le demande.

Hearthstone lit `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` au lancement ; une section `[Power]` avec `LogLevel=1` et `FilePrinting=true` lui fait écrire chaque changement d'état de partie dans `<installation>\Logs\Power.log` (les clients récents rangent les journaux de chaque lancement dans un dossier à part, `Logs\Hearthstone_<date>\`). C'est la journalisation de débogage documentée que les outils de suivi de deck activent depuis 2014 (la configuration de Hearthstone Deck Tracker écrit la même section). `setup()` ajoute la section, avec une sauvegarde du fichier tel qu'il était ; le jeu doit être redémarré pour la lire.

Les lignes utilisées, toutes issues de `GameState.DebugPrintPower()` (les répétitions `PowerTaskList` sont ignorées) :

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Le côté du joueur est celui dont les cartes de la main de départ sont nommées (celles de l'adversaire sont cachées), sinon le côté qui n'est pas l'IA (compte 0) ou « UNKNOWN HUMAN PLAYER ». Les lignes ne portent que l'heure ; la date est celle du jour.
Aucune position.

Chaque ligne de Power.log est conservée entière dans le fichier brut de la session (règle du convertisseur de 3DHeat), répétitions `PowerTaskList`, options, choix et mises à jour d'entités compris : `type` est la méthode qui l'a écrite (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Tout autre journal que le jeu écrit à côté - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., chacun présent quand log.config le demande (les outils de suivi de deck le font souvent) - est suivi de la même façon et conservé avec son nom dans `log`.

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | non |
| Axe vertical | `y` |
| Unités | aucune position enregistrée |
| Miroir pour la visionneuse | aucun |
| Échelle des unités (`scale` : la visionneuse multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` affiche « autorisé (lit seulement ce que le jeu publie) ».
- Type `log` : il ne lit que ce que le jeu ou la plateforme fournit (les fichiers écrits par le jeu pendant qu'il tourne), donc il enregistre aussi en ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur définit par leur nom (`stats` de chaque `meta.json` de session et table `stats` de `watcher.sqlite`) :

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- `CREATE_GAME`, les joueurs (entité, identifiant de joueur, compte ; le compte 0 est l'IA) et leurs noms (`DebugPrintGame`)
- le côté du joueur, d'après les cartes nommées de la main de départ
- `TAG_CHANGE` de TURN, PLAYSTATE (won, lost, tied) et STATE COMPLETE : tours, résultat, adversaire

**Conservé brut**

- chaque ligne de Power.log entière, `type` = la méthode qui l'a écrite (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` là où elle est devenue une ligne : chaque carte jouée, piochée et révélée, chaque changement de balise, attaque, option et choix est ici, pas encore en lignes
- chaque ligne des autres journaux du même dossier (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - tout ce que log.config active), mêmes `type`, avec le nom du journal dans `log`
- une ligne sans niveau ni heure comme `untimed`, une ligne sans méthode comme `untagged`

**Non disponible**

- positions : un jeu de cartes n'en a pas
- les cartes cachées de l'adversaire : le journal ne nomme une carte qu'une fois révélée
- les journaux que log.config n'active pas : `setup` ne demande que [Power] ; les autres journaux existent quand un autre outil (un suivi de deck) les a activés
- les journaux des lancements précédents : chaque lancement écrit un nouveau dossier ; ceux plus anciens que cette exécution du jeu ne sont pas relus

**Taille** : Power.log en mode Verbose fait environ 1 à 5 Mo par partie, 10 à 40 Mo par heure de jeu ; les autres journaux ajoutent peu ; zstd dans heat.raw.parquet le réduit à environ un dixième ou moins (les lignes se répètent beaucoup)

## Vérifié {#verified}

testé sur des lignes de Power.log synthétiques dans le format du jeu ; non testé contre le jeu

## Source {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
