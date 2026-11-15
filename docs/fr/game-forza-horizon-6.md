---
title: "Forza Horizon 6 (données en direct)"
nav_order: 23
lang: "fr"
source: game-forza-horizon-6.md
source_hash: "164d188cb521"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 6 (données en direct) {#forza-horizon-6-live-data}

Pendant que vous jouez à Forza Horizon 6, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `forza-horizon-6`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `forzahorizon6.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position de votre voiture (XYZ dans le monde, en m) 10 fois par seconde, avec la vitesse, le rapport, l'accélérateur, le frein et le tour
- le début et la fin de conduite (session_start/session_end), les tours avec leur temps selon le jeu
- le départ et l'arrivée des courses avec la position en course
- les téléportations (retour en arrière, voyage rapide) : `teleport` là où se trouvait la voiture, `spawn` là où elle se trouve maintenant
- les tours, le meilleur tour, la distance, la vitesse maximale, les courses

## D'où viennent les données {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (format Dash) ; chaque paquet transmis sans modification vers 127.0.0.1:5301

## Comment l'activer {#how-to-switch-it-on}

Dans le jeu : Paramètres > HUD et jeu > Data Out activé, IP 127.0.0.1, port 5300 (Motorsport : format Dash). FH Companion ou une autre application Data Out : réglez son port sur 5301 - le watcher transmet chaque paquet ; tant qu'une autre application écoute sur 5300, le watcher lui laisse le port et n'enregistre rien

## Comment ça marche {#how-it-works}

Télémétrie propre aux jeux de course : Forza, les jeux Assetto Corsa, les jeux de rallye et BeamNG, enregistrée sous forme de trajets, de tours et d'épreuves spéciales.

Chacun de ces jeux publie sa télémétrie exprès, pour les tableaux de bord et les simulateurs de mouvement ; rien n'est injecté et rien que le jeu ne fournit n'est lu. Le décodage n'est pas écrit deux fois : ce sont les enregistreurs de tours de gamecapture, dans `heat3d_capture/telemetry` de 3DHeat GameCapture, recopiés dans `heat3d_watch/decoders` (testés là-bas avec des paquets construits à partir des dispositions publiées). Ce module transforme leurs images en lignes du watcher : la position de la voiture plusieurs fois par seconde avec sa vitesse, son rapport et ses pédales, un événement par tour ou par épreuve, et les chiffres que garde un pilote : tours, meilleur tour, distance, vitesse maximale.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

« Data Out » en UDP, activé dans les réglages HUD et Gameplay du jeu, vers 127.0.0.1 port 5300, format Dash. Un paquet par tick de simulation ; le décalage du bloc dash est retrouvé à partir des paquets (`forza.detect_layout`). Mètres du monde, Y vers le haut ; le repère du monde est gaucher et il est dessiné tel qu'il est envoyé, comme le fait l'enregistreur de tours (documentation « Data Out » de Forza Motorsport et de Forza Horizon). Le jeu envoie vers un seul port, et FH Companion et les autres applications Data Out écoutent sur ce même port. Deux programmes ne peuvent pas le partager : sous Windows, le socket lié à 127.0.0.1 reçoit les paquets, et celui lié à toutes les adresses sur le même port n'en reçoit aucun, quel que soit celui qui est arrivé en premier. Le watcher attend donc un peu après le lancement du jeu avant de prendre le port, ne le prend jamais à une application qui le détient, et le libère dès qu'une autre application se met à écouter dessus. Tant qu'il tient le port, il transmet chaque paquet sans le modifier vers 127.0.0.1:5301 : réglez la case de port de l'onglet télémétrie de FH Companion sur 5301 et les deux enregistrent.

#### Tout ce qui est conservé {#everything-kept}

Les lignes sont quelques-unes par seconde ; les jeux en envoient bien davantage. Chaque paquet UDP reçu - dans les menus, entre les tours, ceux qu'aucun décodeur ne lit - est conservé en entier dans `heat.raw.parquet` de la session, sous son format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), et chaque page de mémoire partagée (toute la zone mappée, pas seulement les octets décodés) à chaque changement, sous le nom de sa zone (`acpmf_physics`, ...). `used` marque ce qui est aussi devenu des lignes ; `selfCheck.completeness` dans `meta.json` compte chaque type (règle du convertisseur de 3DHeat).

Ce même module sert aussi : [Assetto Corsa (données en direct)](game-assetto-corsa.md), [Assetto Corsa Competizione (données en direct)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (données en direct)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (données en direct)](game-assetto-corsa-rally.md), [BeamNG.drive (données en direct)](game-beamng.md), [DiRT Rally 2.0 (données en direct)](game-dirt-rally-2.md), [EA SPORTS WRC (données en direct)](game-ea-wrc.md), [Forza Horizon 4 (données en direct)](game-forza-horizon-4.md), [Forza Horizon 5 (données en direct)](game-forza-horizon-5.md), [Forza Motorsport (données en direct)](game-forza-motorsport.md), [Richard Burns Rally (données en direct)](game-richard-burns-rally.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres ; le monde de Forza est gaucher, dessiné tel qu'envoyé comme le fait l'enregistreur de tours |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée que le jeu publie), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- lignes à 10 Hz : position, vitesse, rapport, accélérateur, frein, tour, lacet/tangage/roulis (rad), régime moteur, direction (-1..1) ; session_start avec l'ordinal de la voiture, la classe, le PI et la transmission ; tours avec le temps de tour selon le jeu ; position en course

**Conservé brut**

- chaque paquet qui atteint le port, en entier, au rythme du jeu (un par tick de simulation), sous son format : `dash-horizon` (324 octets, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023 : usure des pneus et identifiant de piste), `sled` (232, sans position), `<n>-byte` pour tout le reste - y compris les paquets de menus (isRaceOn 0), les paquets retenus tant que la disposition du tableau de bord n'est pas prouvée, et les ~13 octets du paquet Horizon qu'aucune disposition publiée ne nomme
- chaque canal de roue du bloc Sled (taux de glissement, angle de glissement, glissement combiné, suspension, vitesse de roue, rumble, flaque), les accélérations, la vitesse angulaire, la puissance, le couple, le boost, le carburant, les températures des pneus, l'embrayage, le frein à main, la trajectoire, la différence de freinage IA : tout est dans les paquets, décodé à partir d'eux par `decoders/fulllap.decode_full`

**Non disponible**

- les autres voitures : Data Out ne décrit que la voiture du joueur
- le nom de la piste ou du parcours : Forza Horizon n'en envoie jamais ; Motorsport 2023 n'envoie qu'un numéro de piste
- les paquets pendant qu'une autre application (FH Companion) détient le port UDP 5300 : le watcher laisse le port à cette application

**Taille** : environ 85 Mo par heure avant compression (60 paquets par seconde de 324 octets plus un en-tête d'élément de 70 octets) ; les paquets successifs diffèrent peu, donc zstd en garde une fraction

## Vérifié {#verified}

décodage : celui de l'enregistreur de tours de gamecapture (testé sur des paquets construits à partir de la disposition Data Out) ; l'adaptateur testé sur des paquets synthétiques et sur des trajectoires de tours enregistrées rejouées en paquets ; non testé avec le jeu lui-même

## Source {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
