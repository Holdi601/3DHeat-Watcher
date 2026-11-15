---
title: "DiRT Rally 2.0 (données en direct)"
nav_order: 11
lang: "fr"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (données en direct) {#dirt-rally-20-live-data}

Pendant que vous jouez à DiRT Rally 2.0, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `dirt-rally-2`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `dirtrally2.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position de votre voiture (XYZ dans le monde, en m) 10 fois par seconde, avec la vitesse, le rapport, l'accélérateur, le frein et la distance dans l'épreuve
- le départ de l'épreuve (le chrono de l'épreuve qui démarre), l'arrivée avec le temps de l'épreuve, les redémarrages
- les téléportations (retour sur la route) : `teleport` là où se trouvait la voiture, `spawn` là où elle se trouve maintenant
- les épreuves, le meilleur temps d'épreuve, la distance, la vitesse maximale

## D'où viennent les données {#where-it-comes-from}

UDP 127.0.0.1:20777, extradata=3 (Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml) ; tant qu'une autre application détient le port 20777, le watcher le lui laisse

## Comment l'activer {#how-to-switch-it-on}

`python -m heat3d_watch setup dirt-rally-2 --apply` règle &lt;udp enabled="true" extradata="3"> (sauvegarde d'abord)

Tapez la commande dans un terminal ouvert dans le dossier du watcher (voir [Avant de commencer](before-you-start.md)). Si elle échoue, la dernière ligne indique pourquoi ; [Installation et lancement](installing-and-running.md) couvre les causes habituelles.

`python -m heat3d_watch setup dirt-rally-2` liste les fichiers qu'il modifierait ; `python -m heat3d_watch setup dirt-rally-2 --apply` les modifie, en gardant l'original sous `<file>.heat3d-backup` (voir [Commandes](commands.md#setup)). Il affiche `dirt-rally-2: changed: ...` pour chaque modification, ou `dirt-rally-2: nothing to change` quand c'est déjà activé.

## Comment ça marche {#how-it-works}

Télémétrie propre aux jeux de course : Forza, les jeux Assetto Corsa, les jeux de rallye et BeamNG, enregistrée sous forme de trajets, de tours et d'épreuves spéciales.

Chacun de ces jeux publie sa télémétrie exprès, pour les tableaux de bord et les simulateurs de mouvement ; rien n'est injecté et rien que le jeu ne fournit n'est lu. Le décodage n'est pas écrit deux fois : ce sont les enregistreurs de tours de gamecapture, dans `heat3d_capture/telemetry` de 3DHeat GameCapture, recopiés dans `heat3d_watch/decoders` (testés là-bas avec des paquets construits à partir des dispositions publiées). Ce module transforme leurs images en lignes du watcher : la position de la voiture plusieurs fois par seconde avec sa vitesse, son rapport et ses pédales, un événement par tour ou par épreuve, et les chiffres que garde un pilote : tours, meilleur tour, distance, vitesse maximale.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

« Data Out » en UDP, activé dans les réglages HUD et Gameplay du jeu, vers 127.0.0.1 port 5300, format Dash. Un paquet par tick de simulation ; le décalage du bloc dash est retrouvé à partir des paquets (`forza.detect_layout`). Mètres du monde, Y vers le haut ; le repère du monde est gaucher et il est dessiné tel qu'il est envoyé, comme le fait l'enregistreur de tours (documentation « Data Out » de Forza Motorsport et de Forza Horizon). Le jeu envoie vers un seul port, et FH Companion et les autres applications Data Out écoutent sur ce même port. Deux programmes ne peuvent pas le partager : sous Windows, le socket lié à 127.0.0.1 reçoit les paquets, et celui lié à toutes les adresses sur le même port n'en reçoit aucun, quel que soit celui qui est arrivé en premier. Le watcher attend donc un peu après le lancement du jeu avant de prendre le port, ne le prend jamais à une application qui le détient, et le libère dès qu'une autre application se met à écouter dessus. Tant qu'il tient le port, il transmet chaque paquet sans le modifier vers 127.0.0.1:5301 : réglez la case de port de l'onglet télémétrie de FH Companion sur 5301 et les deux enregistrent.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP : `Documents/My Games/WRC/telemetry/config.json` de WRC (paquet `session_update` de la structure `wrc`), `hardware_settings_config.xml` de DiRT (`<udp enabled="true" extradata="3" port="20777">`), le plugin NGP de RBR (`udpTelemetry=1`, port 6776). Épreuves par le chrono d'épreuve du jeu (`rally.StageSplitter`). RBR ne documente pas ses axes : l'axe vertical est celui le long duquel l'épreuve varie le moins, décidé à la fermeture de la session.

#### Tout ce qui est conservé {#everything-kept}

Les lignes sont quelques-unes par seconde ; les jeux en envoient bien davantage. Chaque paquet UDP reçu - dans les menus, entre les tours, ceux qu'aucun décodeur ne lit - est conservé en entier dans `heat.raw.parquet` de la session, sous son format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), et chaque page de mémoire partagée (toute la zone mappée, pas seulement les octets décodés) à chaque changement, sous le nom de sa zone (`acpmf_physics`, ...). `used` marque ce qui est aussi devenu des lignes ; `selfCheck.completeness` dans `meta.json` compte chaque type (règle du convertisseur de 3DHeat).

Ce même module sert aussi : [Assetto Corsa (données en direct)](game-assetto-corsa.md), [Assetto Corsa Competizione (données en direct)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (données en direct)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (données en direct)](game-assetto-corsa-rally.md), [BeamNG.drive (données en direct)](game-beamng.md), [EA SPORTS WRC (données en direct)](game-ea-wrc.md), [Forza Horizon 4 (données en direct)](game-forza-horizon-4.md), [Forza Horizon 5 (données en direct)](game-forza-horizon-5.md), [Forza Horizon 6 (données en direct)](game-forza-horizon-6.md), [Forza Motorsport (données en direct)](game-forza-motorsport.md), [Richard Burns Rally (données en direct)](game-richard-burns-rally.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée que le jeu publie), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- lignes à 10 Hz : position, vitesse, rapport, accélérateur, frein, distance dans l'épreuve, lacet, régime moteur, direction ; départ d'épreuve, arrivée avec le temps d'épreuve, redémarrages

**Conservé brut**

- chaque paquet qui atteint le port, en entier, au rythme du jeu, sous son format : `extradata3` (66 flottants, 264 octets), `extradata3-64` (64 pour DiRT Rally), `<n>-byte` sinon
- dans le paquet, au-delà des lignes : les 66 flottants - vitesse dans le monde, vecteurs latéral et avant, position et vitesse de suspension par roue, vitesse de la surface de contact et température des freins, forces g, tours, longueur de l'épreuve ; les flottants sans nom établi sont dans les fichiers de tours sous `float<i>`

**Non disponible**

- les autres voitures : les jeux n'envoient que la voiture du joueur
- une voie de frein à main : le paquet n'en a pas

**Taille** : environ 70 Mo par heure à 60 paquets par seconde (264 octets plus un en-tête d'élément de 70 octets) ; zstd en garde une fraction

## Vérifié {#verified}

décodage : celui de l'enregistreur de tours de gamecapture (testé sur des paquets construits à partir des dispositions documentées) ; l'adaptateur testé sur des paquets construits dans le test, envoyés en UDP ; non testé avec le jeu

## Source {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
