---
title: "RaceRoom Racing Experience (données en direct)"
nav_order: 37
lang: "fr"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (données en direct) {#raceroom-racing-experience-live-data}

Pendant que vous jouez à RaceRoom Racing Experience, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `raceroom`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `RRRE64.exe` ou `RRRE.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position de chaque voiture (XYZ dans le monde, m) à 10 Hz, par nom de pilote, votre voiture étant marquée, avec la vitesse et la position en course ; votre rapport, accélérateur et frein
- début de session avec la piste que le jeu indique ; tours par voiture avec leur temps ; arrivées ; vos arrêts au stand
- les téléportations (retour aux stands, redémarrage) : `teleport` là où se trouvait la voiture, `spawn` là où elle est maintenant
- vos tours, meilleur tour, position en course, distance, vitesse maximale
- toute la page de mémoire partagée du jeu dans `heat.raw.parquet`, à chaque changement
- vos points d'incident

## D'où viennent les données {#where-it-comes-from}

Mémoire partagée $R3E (r3e.h de Sector3, version 3)

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Fonctionnement {#how-it-works}

Mémoire partagée que les simulateurs de course publient pour les tableaux de bord, ouverte en lecture seule - et jamais créée.

Plusieurs simulateurs fournissent leur télémétrie sous forme de mappage de fichier Windows nommé, que le jeu crée et que n'importe qui peut lire : les pages `Local\acpmf_*` de Kunos (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` d'AC EVO), `Local\IRSDKMemMapFileName` d'iRacing, `$R3E` de RaceRoom, `$pcars2$` d'Automobilista 2 / Project CARS 2.

Pourquoi pas `mmap.mmap(-1, size, tagname=...)`, la façon habituelle en Python : quand le mappage n'existe pas encore, celle-ci en *crée* un - ici en lecture seule. Un jeu lancé après ouvre alors le mappage du watcher au lieu de créer le sien, et ne peut donc plus y écrire : sa télémétrie est morte tant que le watcher ne le lâche pas. Le watcher démarre un adaptateur dès que le processus du jeu apparaît, c'est-à-dire exactement au moment où le jeu n'a pas encore créé son mappage. Donc ceci ouvre avec `OpenFileMappingW`, qui ne trouve jamais que des mappages existants, le mappe avec `FILE_MAP_READ`, et signale « pas encore là » sinon ; les adaptateurs réessaient un peu plus tard.

Rien ici ne peut écrire : la vue est mappée en lecture seule et n'est copiée qu'avec `ctypes.string_at`.

Deux jeux sont aussi lus ici ; chaque voiture sur la piste figure dans leurs pages.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

r3e.h de Sector3 (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, version 3.6), `#pragma pack(1)`. L'en-tête indique où commencent les pilotes et leur taille (`all_drivers_offset`, `driver_data_size`), donc la partie de chaque pilote - nom, emplacement, place, position dans le monde (float x y z, m), tours effectués, temps du tour en cours, statut d'arrivée, voie des stands, vitesse - est lue grâce à eux. Les champs propres au joueur (meilleur et précédent tour, position en course, points d'incident, rapport, pédales, noms de piste et de tracé) ne sont lus à leurs décalages de la version 3.6 que lorsque `all_drivers_offset` vaut 2008, ce que cette disposition prévoit. Y est pris comme vertical ; l'en-tête ne le précise pas.

Le même module sert aussi : [Automobilista 2 (données en direct)](game-automobilista-2.md), [Project CARS 2 (données en direct)](game-project-cars-2.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres ; Y vers le haut supposé (r3e.h ne le précise pas) |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes tout seul : voir [Les données](the-data.md).

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

- par emplacement de pilote (selon le décalage et la taille donnés par l'en-tête) : nom, emplacement, statut d'arrivée, place, position dans le monde, tours effectués, temps du tour en cours, voie des stands, vitesse
- les champs propres au joueur, seulement quand la page est de la disposition r3e.h 3.6 : noms de piste et de tracé, type de session, position en course, meilleur et précédent tour, points d'incident, rapport, accélérateur, frein, emplacement du joueur
- décalages établis d'après le r3e.h 3.6 de Sector3 et vérifiés sur une page construite à partir de lui dans les tests ; pas encore contre le jeu

**Conservé brut**

- `r3e` : tout le mappage $R3E, à chaque lecture dont les octets diffèrent de la copie conservée la dernière fois - chaque champ de r3e.h : la physique du joueur (orientation, vitesses, accélérations, forces g), moteur, carburant, pneus, freins, dégâts, drapeaux, menu des stands, temps de secteur, et toutes les données de chaque emplacement de pilote (classe, modèle, équipe, temps de secteur, écarts, pénalités, pneus)
- `used` est vrai pour une page lue en lignes ; faux pour une page prise dans les menus, en pause, dans un replay, d'une autre disposition, ou pendant l'écriture (`torn` 1) ; `unchanged_reads` dans meta.json compte les lectures identiques octet par octet à la copie conservée avant

**Non disponible**

- les entrées et la physique des autres pilotes : la page ne donne que celles du joueur
- les temps exacts au tour des autres voitures : un emplacement n'a que son temps de tour en cours, donc un tour est le dernier temps en cours vu (à environ 0,1 s près)
- les champs propres au joueur sur une disposition autre que la 3.6 : conservés bruts, non lus, jusqu'à vérification

**Taille** : la page fait 44 Ko (r3e.h 3.6 ; le mappage est arrondi à des pages entières de 4 Ko), jusqu'à 10 fois par seconde pendant la conduite : environ 1,6 Go par heure avant compression ; les emplacements de pilotes vides et les champs qui ne changent pas se compressent très bien avec zstd (pas encore mesuré sur une vraie session)

## Vérifié {#verified}

testé sur une page construite dans le test à partir de r3e.h 3.6 (décalages établis d'après l'en-tête officiel) ; non testé contre le jeu ; les temps au tour des autres voitures sont le dernier temps de tour en cours vu (à environ 0,1 s près)

## Source {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
