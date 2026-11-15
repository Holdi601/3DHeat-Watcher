---
title: "Elite Dangerous (fichiers journaux)"
nav_order: 18
lang: "fr"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (fichiers journaux) {#elite-dangerous-log-files}

Pendant que vous jouez à Elite Dangerous, le watcher lit les fichiers que le jeu écrit et enregistre ce qui s'est passé, pour que vous puissiez le regarder plus tard sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `elite`, type [`log`](sources-and-rules.md) ; il tourne pendant que `EliteDangerous64.exe` est lancé et cherche de nouvelles données toutes les 0,25 s.*

## Ce qui est enregistré {#what-is-recorded}

- chaque événement du journal, sous son nom de journal, avec ses champs simples
- la position galactique (StarPos, en années-lumière) lors des sauts, des positions, des apparitions, des morts, des amarrages, des atterrissages
- apparition à LoadGame/Resurrect, mort à Died, amarré/désamarré, posé/décollé, saut, session_end
- le tracé à la surface d'une planète d'après Status.json : latitude, longitude, altitude, cap, et des mètres dans un plan tangent par corps (session = nom du corps), avec les autres champs simples de Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- chaque ligne du journal et chaque annexe en entier dans heat.raw.parquet
- sauts, distance parcourue en saut, morts, éliminations, crédits gagnés, missions accomplies, corps scannés, systèmes visités, amarrages, atterrissages

## D'où viennent les données {#where-it-comes-from}

Journal du joueur %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (le fichier le plus récent, suivi pendant son écriture), Status.json et les autres annexes \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) dans le même dossier

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Comment ça marche {#how-it-works}

Elite Dangerous : le journal du joueur et Status.json que le jeu écrit pendant qu'il tourne.

Où : `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - un objet JSON par ligne, un fichier par lancement (une longue session continue en partie .02, .03 ...). Chaque ligne a `timestamp` (UTC, ISO 8601) et `event`. Les positions galactiques sont le `StarPos` [x, y, z] du système, en années-lumière depuis Sol, dans `FSDJump`, `Location` et `CarrierJump`. Le repère galactique d'Elite a Y vers le haut (vers le nord galactique), Z vers le centre galactique et X vers la longitude galactique 270 - un repère gaucher, donc le visualiseur inverse Z pour le dessiner dans le bon sens.
* `Status.json` - réécrit en entier à chaque changement d'état du vaisseau : `Flags`, et près d'une planète `Latitude`, `Longitude` (degrés), `Altitude` (mètres), `Heading`, `BodyName` et `PlanetRadius` (mètres).
* Les autres annexes, chacun réécrit en entier quand l'événement de journal correspondant est écrit : `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Chaque `*.json` du dossier que le jeu écrit pendant cette session est conservé en entier à chaque changement (règle du convertisseur de 3DHeat : ce que la source contient est lu ou conservé), sous son nom de fichier.

Chaque ligne du journal est conservée en entier dans le fichier brut de la session sous son `event`, chaque annexe sous son nom de fichier ; une ligne qui n'est pas du JSON va sous `unparsed`.

Les positions de surface sont placées dans un plan tangent local par corps, en mètres : le premier relevé sur un corps en est l'origine, x vers l'est, z vers le nord, y vers le haut (altitude), même sens que le repère galactique, et les lignes portent le nom du corps comme `session`, si bien qu'une conduite ou une marche sur une planète se trace comme un parcours à part. Les lignes galactiques ont la session « galaxy ». Les deux échelles sont dans une même table ; choisissez la session dans le visualiseur.

Format : manuel « Elite Dangerous Player Journal » de Frontier (publié avec chaque mise à jour sur les forums officiels, <https://forums.frontier.co.uk/> - « Journal Manual », v4.x), événements et champs tels que décrits dans ce manuel ; drapeaux de Status.json selon le chapitre « Status File » du même manuel.

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | années-lumière (lignes galactiques, session « galaxy ») ; mètres est/haut/nord du premier relevé sur un corps (lignes de surface, session = nom du corps) |
| Miroir pour le visualiseur | `z` |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `log` : il ne lit que ce que le jeu ou la plateforme fournit (des fichiers que le jeu écrit pendant qu'il tourne), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- chaque ligne du journal comme une ligne sous son `event`, avec ses champs simples (le texte localisé quand le jeu en donne un ; les textes de plus de 300 caractères sont coupés dans la ligne)
- lignes galactiques (StarPos) à FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown ; lignes de surface depuis Status.json et Touchdown/Liftoff
- les champs simples de Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) sur les lignes de surface
- les statistiques : sauts, distance, morts, éliminations, crédits gagnés, missions, corps scannés, systèmes visités, amarrages, atterrissages

**Conservé brut**

- chaque ligne du journal en entier, `type` = son `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` vrai : les listes et objets que les lignes laissent de côté (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) ne sont que là
- une ligne du journal qui n'est pas du JSON, `type` `unparsed`
- chaque annexe en entier à chaque réécriture par le jeu, `type` = son nom de fichier : `Status.json` (`used` quand il a fait une ligne de surface), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, et tout autre `*.json` que le jeu écrit là

**Non disponible**

- la position entre deux sauts (dans un système, en supercroisière ou en espace normal) : le jeu n'écrit que le StarPos du système et, près d'une planète, la latitude, la longitude et l'altitude
- les positions des autres vaisseaux et des autres joueurs : le journal est le compte rendu du commandant lui-même
- la vitesse, l'accélérateur et les autres télémesures de vol : le jeu ne les écrit pas
- les journaux et annexes des sessions précédentes : conservés quand ils ont été joués (le suiveur démarre à la fin d'un fichier plus ancien que cette exécution du jeu)
- l'API web compagnon de Frontier (cAPI) : demande la connexion Frontier du joueur ; ce n'est pas un fichier que le jeu écrit

**Taille** : environ 1 à 5 Mo de texte brut par heure : le journal 0,2 à 2 Mo, Status.json (moins de 1 Ko, réécrit jusqu'à chaque seconde) 1 à 2 Mo, un jeu market/outfitting/shipyard 20 à 150 Ko par station visitée ; zstd dans heat.raw.parquet le ramène à environ un dixième

## Vérifié {#verified}

analyseur rejoué sur de vrais fichiers de journal d'une installation locale (le nombre d'événements correspond aux statistiques) ; les relevés de surface de Status.json testés seulement sur des instantanés synthétiques

## Source {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
