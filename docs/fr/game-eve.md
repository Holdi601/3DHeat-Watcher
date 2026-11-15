---
title: "EVE Online (fichiers journal)"
nav_order: 20
lang: fr
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (fichiers journal) {#eve-online-log-files}

Pendant que vous jouez à EVE Online, le watcher lit les fichiers qu'écrit le jeu et enregistre ce qui s'est passé, pour que vous puissiez le regarder plus tard sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `eve`, type [`log`](sources-and-rules.md) ; il tourne pendant que `exefile.exe` est lancé et cherche de nouvelles données toutes les 0,5 s.*

## Ce qui est enregistré {#what-is-recorded}

- les dégâts infligés et subis avec l'autre vaisseau, le pilote, le sigle de la corporation, l'arme et la qualité du coup
- les tirs manqués infligés et subis
- les primes encaissées (abattages de PNJ) avec les ISK
- les sauts entre systèmes
- chaque ligne des journaux de jeu et de chat, entière, dans heat.raw.parquet
- dégâts infligés et subis, coups, tirs manqués, primes et ISK, sauts

## D'où viennent les données {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt et les Chatlogs\\\*.txt à côté (chaque fichier écrit depuis le lancement du client)

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Fonctionnement {#how-it-works}

EVE Online : les journaux de jeu du client, `Documents\EVE\logs\Gamelogs\*.txt`.

Le client écrit un fichier par personnage et par connexion, `<yyyymmdd>_<hhmmss>[_<identifiant du personnage>].txt` ; la journalisation dans un fichier est activée par défaut. Plusieurs clients lancés côte à côte écrivent chacun le leur, donc chaque fichier écrit depuis le lancement du jeu est suivi. En-tête et lignes (l'heure d'EVE est en UTC) :

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(la ligne de combat ne fait qu'une ligne dans le fichier). Les balises de mise en forme sont retirées avant la comparaison. Le fichier a été en UTF-8 et en UTF-16 au fil des années ; les deux sont lus.
Le format n'est pas documenté par CCP ; c'est le journal en texte brut du client, lu comme le font les outils communautaires d'analyse de combat (par ex. <https://docs.rs/crate/eve-log-parser>).
Aucune position.

À côté, `Documents\EVE\logs\Chatlogs\<canal>_<yyyymmdd>_<hhmmss>[_<id>].txt` : un fichier par canal de discussion et par connexion (quand la journalisation du chat est activée, valeur par défaut du client), en UTF-16, avec un en-tête qui nomme le canal et l'écouteur, puis `[ yyyy.mm.dd hh:mm:ss ] Expéditeur > message`.

Chaque ligne des deux est conservée entière dans le fichier brut de la session (règle du convertisseur de 3DHeat) : une ligne de journal de jeu sous son canal entre crochets (`combat`, `notify`, `bounty`, `None`, ...), une ligne de chat en `chat` avec son canal, les lignes d'en-tête en `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- coups infligés et subis dans le journal de jeu `(combat)` (montant, autre pilote, sigle de la corporation, vaisseau, arme, qualité du coup) et les tirs manqués dans les deux sens
- versements de primes `(bounty)` avec les ISK, et les lignes `Jumping from A to B`
- l'`Listener` de l'en-tête du journal de jeu : à qui est ce journal

**Conservé brut**

- chaque ligne du journal de jeu entière, `type` = son canal entre crochets (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), avec `file` et `listener` ; `used` là où elle est devenue une ligne ; les lignes d'en-tête en `gamelog header`
- chaque ligne du journal de chat entière (Local, corporation, flotte, canaux privés, les avis `EVE System` comme un changement de canal Local lors d'un saut), `type` `chat`, avec `channel`, `listener` et `file` ; les lignes d'en-tête en `chatlog header`. Pas encore transformées en lignes
- les balises de mise en forme (`<color>`, `<b>`, `<font>`) restent dans le texte brut ; les lignes les ont retirées

**Non disponible**

- positions : le client n'en écrit aucune dans ses journaux
- les combats des autres pilotes : un journal de jeu appartient à l'écouteur seul
- les journaux des connexions précédentes : chaque connexion écrit de nouveaux fichiers ; ceux plus anciens que cette exécution du client ne sont pas relus
- le chat quand le joueur a désactivé la journalisation du chat dans les réglages du client
- les fichiers de cache et de réglages du client : ce ne sont pas des journaux, et ils ne sont pas documentés

**Taille** : un journal de jeu fait 0,1 à 2 Mo par heure (surtout en combat) ; les journaux de chat dépendent des canaux ouverts - un canal Local ou de flotte chargé 0,5 à 3 Mo par heure ; zstd dans heat.raw.parquet le réduit à environ un dixième

## Vérifié {#verified}

testé sur des lignes de journal de jeu synthétiques dans le format publié par les analyseurs communautaires ; non testé contre le jeu

## Source {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
