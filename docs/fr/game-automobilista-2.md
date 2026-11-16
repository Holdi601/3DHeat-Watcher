---
title: "Automobilista 2 (données en direct)"
nav_order: 6
lang: "fr"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (données en direct) {#automobilista-2-live-data}

Pendant que vous jouez à Automobilista 2, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `automobilista-2`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `AMS2AVX.exe` ou `AMS2.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position de chaque voiture (XYZ dans le monde, m) à 10 Hz, par nom de pilote, votre voiture étant marquée, avec la vitesse et la position en course ; votre rapport, accélérateur et frein
- début de session avec la piste que le jeu indique ; tours par voiture avec leur temps ; arrivées ; vos arrêts au stand
- les téléportations (retour aux stands, redémarrage) : `teleport` là où se trouvait la voiture, `spawn` là où elle est maintenant
- vos tours, meilleur tour, position en course, distance, vitesse maximale
- toute la page de mémoire partagée du jeu dans `heat.raw.parquet`, à chaque changement

## D'où viennent les données {#where-it-comes-from}

Mémoire partagée $pcars2$ (disposition SharedMemory.h de SMS)

## Comment l'activer {#how-to-switch-it-on}

Dans le jeu : Options > Système > Mémoire partagée : « Project CARS 2 »

## Fonctionnement {#how-it-works}

Mémoire partagée que les simulateurs de course publient pour les tableaux de bord, ouverte en lecture seule - et jamais créée.

Plusieurs simulateurs fournissent leur télémétrie sous forme de mappage de fichier Windows nommé, que le jeu crée et que n'importe qui peut lire : les pages `Local\acpmf_*` de Kunos (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` d'AC EVO), `Local\IRSDKMemMapFileName` d'iRacing, `$R3E` de RaceRoom, `$pcars2$` d'Automobilista 2 / Project CARS 2.

Pourquoi pas `mmap.mmap(-1, size, tagname=...)`, la façon habituelle en Python : quand le mappage n'existe pas encore, celle-ci en *crée* un - ici en lecture seule. Un jeu lancé après ouvre alors le mappage du watcher au lieu de créer le sien, et ne peut donc plus y écrire : sa télémétrie est morte tant que le watcher ne le lâche pas. Le watcher démarre un adaptateur dès que le processus du jeu apparaît, c'est-à-dire exactement au moment où le jeu n'a pas encore créé son mappage. Donc ceci ouvre avec `OpenFileMappingW`, qui ne trouve jamais que des mappages existants, le mappe avec `FILE_MAP_READ`, et signale « pas encore là » sinon ; les adaptateurs réessaient un peu plus tard.

Rien ici ne peut écrire : la vue est mappée en lecture seule et n'est copiée qu'avec `ctypes.string_at`.

Deux jeux sont aussi lus ici ; chaque voiture sur la piste figure dans leurs pages.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

`SharedMemory.h` de SMS (livré dans le dossier Support\SharedMemory du jeu ; AMS2 : Options > Système > Mémoire partagée « Project CARS 2 »), `#pragma pack(4)`. `mParticipantInfo[64]` à partir de l'octet 28, 100 octets chacun : mIsActive, mName[64], mWorldPosition[3] (m, Y vers le haut), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector ; mViewedParticipantIndex (20) est la voiture du joueur ; pour chaque participant mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800) ; le mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear du joueur ; mSequenceNumber (7320) est impair pendant que le jeu écrit. Les décalages ont été trouvés à partir de deux copies indépendantes de l'en-tête (la copie du jeu lui-même n'est pas installée ici), qui concordent.

Les deux pages sont aussi conservées entières (docs/converters.md, « Live sources ») : toute la zone mappée, à chaque lecture dont les octets diffèrent de la copie conservée la dernière fois, dans le fichier brut de la session sous le `type` `r3e` ou `pcars2` - chaque emplacement de pilote et chaque champ de la structure, y compris ceux non lus ici, pour qu'un futur décodeur n'ait besoin que du fichier brut.

Le même module sert aussi : [Project CARS 2 (données en direct)](game-project-cars-2.md), [RaceRoom Racing Experience (données en direct)](game-raceroom.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes toute seule : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` affiche « autorisé (lit seulement ce que le jeu publie) ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée publiée par le jeu), donc il enregistre aussi en ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur définit par leur nom (`stats` de chaque `meta.json` de session et table `stats` de `watcher.sqlite`) :

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- par participant (jusqu'à 64) : actif, nom, position dans le monde, position en course, tours effectués ; son dernier temps de tour, son état de course et sa vitesse
- la voiture du joueur (mViewedParticipantIndex), état du jeu et de la session, lieu et variante de la piste, meilleur et dernier tour, vitesse, frein, accélérateur, rapport ; mSequenceNumber pour ignorer une copie prise pendant l'écriture
- décalages issus de deux copies indépendantes de SharedMemory.h de SMS qui concordent, vérifiés sur une page construite à partir d'elles dans les tests ; pas encore contre le jeu

**Conservé brut**

- `pcars2` : tout le mappage $pcars2$ - la structure va bien au-delà des 11 312 octets lus ici - à chaque lecture dont les octets diffèrent de la copie conservée la dernière fois : l'orientation de chaque participant, les temps de secteur, les noms de voiture et de classe, les modes et drapeaux de stand, la physique, les pneus, la suspension, les dégâts du joueur, la météo, et tout ce que les versions ultérieures d'Automobilista 2 ont ajouté
- `used` est vrai pour une page lue en lignes ; faux pour une page prise dans les menus, en pause, dans un replay, d'une autre disposition, ou pendant l'écriture (`torn` 1) ; `unchanged_reads` dans meta.json compte les lectures identiques octet par octet à la copie conservée avant

**Non disponible**

- les entrées et la physique des autres participants : la page ne donne que la voiture regardée
- tout pendant que l'option de mémoire partagée du jeu est désactivée (Automobilista 2 n'écrit alors rien)

**Taille** : le mappage fait environ 20 à 30 Ko (selon la version du jeu), jusqu'à 10 fois par seconde pendant la conduite : environ 0,7 à 1,1 Go par heure avant compression ; zstd réduit les emplacements de participants vides et les noms qui ne changent pas à une fraction (pas encore mesuré sur une vraie session)

## Vérifié {#verified}

testé sur une page construite dans le test ; décalages issus de deux copies indépendantes de SharedMemory.h qui concordent, et non de la copie livrée avec le jeu ; non testé contre le jeu

## Source {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
