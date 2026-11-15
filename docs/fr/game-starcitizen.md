---
title: "Star Citizen (fichiers journal)"
nav_order: 42
lang: fr
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (fichiers journal) {#star-citizen-log-files}

Pendant que vous jouez à Star Citizen, le watcher lit les fichiers qu'écrit le jeu et enregistre ce qui s'est passé, pour que vous puissiez le regarder plus tard sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `starcitizen`, type [`log`](sources-and-rules.md) ; il tourne pendant que `StarCitizen.exe` est lancé et cherche de nouvelles données toutes les 0,5 s.*

## Ce qui est enregistré {#what-is-recorded}

- les morts avec la victime, le tueur, l'arme, le type de dégât et la zone (joueurs et PNJ)
- véhicules mis hors service et détruits, avec le pilote, la cause et la zone
- cibles de saut quantique, changements de système solaire, apparitions, réapparitions, mises hors de combat
- chaque ligne de Game.log, entière, dans heat.raw.parquet
- tués (joueur et PNJ), morts, suicides, véhicules détruits et perdus, sauts quantiques

## D'où viennent les données {#where-it-comes-from}

&lt;installation>\StarCitizen\LIVE\Game.log (le dossier de version de StarCitizen.exe en cours d'exécution), seul le fichier journal écrit par le jeu - un jeu avec Easy Anti-Cheat : rien ne touche à son processus

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Fonctionnement {#how-it-works}

Star Citizen : le journal propre du client, `<installation>\StarCitizen\LIVE\Game.log`.

Le jeu réécrit Game.log à chaque lancement (le précédent part dans `logbackups\`). Seul ce fichier est lu : Star Citizen utilise Easy Anti-Cheat, et rien ici ne touche au processus du jeu. Les lignes commencent par une heure UTC et un niveau, puis une balise entre chevrons :

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(coupé ici pour la lecture ; une ligne par entrée dans le fichier). La zone d'une mort est en général le vaisseau dans lequel la victime était assise, pas un lieu. Le format n'est pas documenté par Cloud Imperium et change d'un patch à l'autre ; les motifs suivent les lignes que lisent les trackers communautaires de morts (par ex. <https://github.com/DimmaDont/all-slain>, MIT - faits seulement), et tout ce qui ne correspond pas est ignoré, pas deviné. Le `pos` d'un véhicule est relatif à la zone et n'est conservé que comme texte : aucune coordonnée n'est dessinée.

Chaque ligne est conservée entière dans le fichier brut de la session (règle du convertisseur de 3DHeat), reconnue ou non : `type` est la balise de la ligne entre chevrons (`Actor Death`, `Spawn Flow`, ...), sinon son premier mot entre crochets (`Notice`, `CSessionManager::OnClientSpawned`), sinon `untagged` ; une ligne sans heure est `untimed`.

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

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- `<Actor Death>` : victime, tueur, arme et sa classe, type de dégât, zone ; PNJ ou joueur
- `<Vehicle Destruction>` : véhicule, zone, position relative à la zone sous forme de texte, pilote, cause, mode, niveau de destruction
- cibles `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, réapparitions à l'hôpital, mises hors de combat avec leurs causes, `EndSession`
- l'identifiant du joueur d'après `<AccountLoginCharacterStatus_Character>` ou la ligne de connexion

**Conservé brut**

- chaque ligne de Game.log entière, `type` = sa balise entre chevrons (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), sinon son premier mot entre crochets (`Notice`, `CSessionManager::OnClientSpawned`, ...), sinon `untagged` ; les lignes sans heure (l'en-tête du journal, le texte coupé) comme `untimed` ; `used` là où la ligne est devenue une ligne

**Non disponible**

- positions : le journal n'en donne aucune dans un cadre qu'on peut dessiner (le `pos` d'un véhicule détruit est relatif à une zone dont le lieu n'est pas journalisé)
- tout ce qui vient du processus du jeu ou du réseau : Star Citizen utilise Easy Anti-Cheat ; seul le fichier journal est lu
- les journaux des lancements précédents (`logbackups`) : le Game.log de chaque lancement est conservé quand il est joué
- les lignes dans un format qu'un patch modifie : conservées brutes, décodées de nouveau une fois la nouvelle forme connue

**Taille** : Game.log grandit d'environ 5 à 15 Mo par heure de jeu (davantage dans les zones chargées et en cas d'erreurs) ; zstd dans heat.raw.parquet le réduit à environ un dixième

## Vérifié {#verified}

testé sur des lignes Game.log synthétiques, dans le format documenté par les trackers communautaires ; non testé contre le jeu

## Source {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
