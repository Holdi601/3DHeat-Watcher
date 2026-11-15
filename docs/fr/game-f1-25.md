---
title: "EA SPORTS F1 25 (données en direct)"
nav_order: 16
lang: fr
source: game-f1-25.md
source_hash: "7476dbb3b308"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 25 (données en direct) {#ea-sports-f1-25-live-data}

Pendant que vous jouez à EA SPORTS F1 25, le Watcher enregistre les données que le jeu envoie lui-même, afin que vous puissiez les regarder plus tard sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `f1-25`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `F1_25.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position de chaque voiture (XYZ du monde, m) à 10 Hz, par nom de pilote, équipe, votre propre voiture marquée (`own_car` 1, d'après l'index de la voiture du joueur), avec vitesse, rapport, accélérateur, frein, direction, régime, DRS, lacet, tangage, roulis (degrés) et forces g
- les tours par voiture avec le temps au tour et la position en course ; arrivées et abandons
- les événements de course du jeu : début et fin de session, meilleur tour, pénalités, dépassements, collisions, safety car, drapeau rouge, feux de départ, drapeau à damier, vainqueur, retours en arrière (`teleport` où était la voiture, `spawn` où elle est revenue)
- circuit, type de session, nombre de tours et pilotes de chaque session
- vos tours, meilleur tour, position en course et sur la grille, arrêts au stand, pénalités, dépassements, collisions, distance, vitesse maximale
- chaque paquet envoyé par le jeu, en entier, dans `heat.raw.parquet` - y compris ceux qui ne deviennent pas des lignes

## D'où viennent les données {#where-it-comes-from}

Télémétrie UDP 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## Comment l'activer {#how-to-switch-it-on}

Dans le jeu : Paramètres > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - ou `python -m heat3d_watch setup f1-25 --apply` (modifie hardware_settings_config.xml, sauvegardé avant ; le jeu doit être fermé). Tant qu'une autre application tient le port 20777, le Watcher le lui laisse

Saisissez la commande dans un terminal ouvert dans le dossier du Watcher (voir [Avant de commencer](before-you-start.md)). Si la commande échoue, la dernière ligne indique pourquoi ; [Installation et lancement](installing-and-running.md) décrit les causes les plus fréquentes.

`python -m heat3d_watch setup f1-25` liste les fichiers qu'il modifierait ; `python -m heat3d_watch setup f1-25 --apply` les modifie, en gardant l'original sous le nom `<file>.heat3d-backup` (voir [Commandes](commands.md#setup)). Il affiche `f1-25: changed: ...` pour chaque modification, ou `f1-25: nothing to change` si c'est déjà activé.

## Fonctionnement {#how-it-works}

EA SPORTS F1 23, F1 24 et F1 25 : la télémétrie UDP officielle, chaque voiture sur la piste.

Les jeux l'envoient eux-mêmes (Paramètres > Telemetry Settings, ou `Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`, `<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`). Little-endian, compact, un en-tête de 29 octets sur chaque paquet (le même dans les formats 2023, 2024 et 2025) :

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Ce qui est lu, par identifiant de paquet :

```text
0 Motion        CarMotionData[22], 60 bytes each: world position x y z
                (metres; Y is up), world velocity, forward and right
                vectors (int16 / 32767), g-forces, yaw pitch roll
1 Session       weather, temperatures, total laps, track length, session
                type, track id, ... network game
2 Lap Data      LapData[22]: last lap time, lap distance, race position,
                current lap number, pit stops, penalties, grid position,
                driver and result status. 50 bytes per car in 2023; 57 in
                2024 and 2025, which added the minutes parts of the deltas
                and the speed trap.
3 Event         a four-letter code and a union of details: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI or human, driver, team, race
                number, name (48 bytes in 2023 and 2024, 32 in 2025; 58,
                60 and 57 bytes per car)
6 Car Telemetry CarTelemetryData[22], 60 bytes: speed km/h, throttle,
                steer, brake, clutch, gear, rpm, DRS ...
```

Chaque paquet est aussi gardé en entier, tel qu'il est arrivé, dans le fichier brut annexe de la session (`heat.raw.parquet`, `type` le nom du paquet - `motion`, `car_status` ... - avec `format`, `packet_id`, `frame` et `session_uid`) : ceux lus ci-dessus et ceux que rien ne lit encore : 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, tout identifiant ultérieur, et les paquets dans un format que cela ne lit pas. Ainsi, un futur décodeur n'a besoin que du fichier annexe.

La position de chaque voiture est dans le paquet Motion - en ligne aussi, là où le jeu la transmet lui-même (seules les données de carburant, ERS, dégâts et jeux de pneus sont retenues pour les joueurs dont « Your Telemetry » est restreint). Chaque voiture est enregistrée à environ 10 Hz sous le nom de son pilote (« car N » tant que les noms n'arrivent pas), l'équipe par son nom, et votre voiture est marquée `own`.

Sources : « F1 25 UDP Specification » de EA (forums.ea.com, hub d'informations sur les jeux F1), les spécifications F1 23 et F1 24 ; les mêmes tableaux repris dans MacManley/f1-25-udp (MIT). Les paquets des tests sont construits à partir de ces dispositions.

Le même module sert aussi : [EA SPORTS F1 23 (données en direct)](game-f1-23.md), [EA SPORTS F1 24 (données en direct)](game-f1-24.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres |
| Miroir pour la visionneuse | aucun |
| Échelle (`scale` : la visionneuse multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de `heat.parquet`, afin que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule - voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée que le jeu publie), donc il enregistre aussi en ligne ; l'indicateur ne décide que de la possibilité de lire la mémoire.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne - voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et la table `stats` de `watcher.sqlite`) :

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le Watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou gardé, jamais jeté. En plus des lignes, chaque paquet, page, ligne ou réponse que reçoit l'adaptateur est gardé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ gardé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- 0 Motion : la position et la vitesse du monde de chaque voiture, et désormais aussi le lacet, le tangage, le roulis (degrés, à partir des radians de la spécification) et les forces g latérale, longitudinale et verticale, sur les lignes de position de chaque voiture
- 1 Session : circuit, type de session, nombre total de tours, longueur du circuit, en ligne ou non (`sessions` de meta.json)
- 2 Lap Data : temps du dernier tour, numéro de tour, position en course et sur la grille, arrêts au stand, pénalités, statut du résultat (tours, arrivées, abandons, statistiques)
- 3 Event : chaque code sauf BUTN en ligne à part, avec ses détails
- 4 Participants : noms des pilotes, équipes, nombre de voitures actives (`player` et `team` des lignes, `drivers` de meta.json)
- 6 Car Telemetry : vitesse, rapport, accélérateur, frein, et désormais aussi la direction (-1..1), le régime et le DRS, sur les lignes de position de chaque voiture
- vérifié contre les spécifications UDP publiées par EA pour les formats 2023, 2024 et 2025 (tailles de paquets vérifiées dans les tests) ; pas encore contre le jeu

**Gardé brut**

- chaque paquet en entier dans `heat.raw.parquet`, `payload` le datagramme, `type` le nom de son identifiant : `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` pour un identifiant que les spécifications ne listent pas encore) ; colonnes `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` est vrai pour les paquets lus ci-dessus (Motion, Session, Lap Data, Participants, Car Telemetry, et les codes d'événement autres que BUTN) ; le reste - réglages de voiture, état de la voiture (carburant, ERS, composé et âge des pneus, drapeaux), classement final, salon, dégâts de voiture, historique de session (chaque temps de tour et de secteur par voiture), jeux de pneus, motion ex (suspension de la voiture propre, vitesses de roue, vitesse locale, vitesse et accélération angulaires), contre-la-montre, positions de tour, événements de boutons BUTN - est gardé pour un décodeur ultérieur
- `format <year>` : un paquet dans un format antérieur à 2023 (autre disposition d'en-tête), en entier ; `short` : un datagramme plus court que l'en-tête de 29 octets, en entier

**Non disponible**

- le carburant, l'ERS, les dégâts et les jeux de pneus des autres joueurs en ligne quand leur « Your Telemetry » est restreint : le jeu envoie des zéros pour eux
- les paquets envoyés pendant que le Watcher ne tourne pas, ou pendant qu'une autre application tient le port 20777 : l'UDP n'est pas stocké par le jeu

**Taille** : à une fréquence d'envoi de 60 Hz, chaque paquet représente environ 0,38 Mo/s (Motion, Lap Data, Car Telemetry, Car Status et Motion Ex à 60 Hz, Session History et Tyre Sets à 20/s, Car Damage à 10/s, Session et Car Setups à 2/s) plus environ 0,03 Mo/s d'en-têtes d'éléments : environ 1,5 Go par heure de conduite avant compression, environ 0,55 Go à la fréquence par défaut de 20 Hz ; zstd le réduit à une fraction de cela (les emplacements de voiture vides et les valeurs répétées se compressent bien ; pas encore mesuré sur une vraie session)

## Vérifié {#verified}

testé sur des paquets aux formats 2023, 2024 et 2025 construits à partir de la spécification UDP publiée par EA, envoyés par UDP ; non testé avec le jeu

## Source {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
