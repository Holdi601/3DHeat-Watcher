---
title: "Richard Burns Rally (données en direct)"
nav_order: 39
lang: fr
source: game-richard-burns-rally.md
source_hash: "1b9866f5a1f6"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (données en direct) {#richard-burns-rally-live-data}

Pendant que vous jouez à Richard Burns Rally, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `richard-burns-rally`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `RichardBurnsRally_SSE.exe` ou `RichardBurnsRally.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position de votre voiture (XYZ dans le monde, m) à 10 Hz, avec la vitesse, le rapport, l'accélérateur, le frein et la distance dans l'étape
- début d'étape (le chronomètre d'étape démarre), arrivée avec le temps d'étape, redémarrages
- les téléportations (retour sur la route) : `teleport` là où se trouvait la voiture, `spawn` là où elle est maintenant
- étapes, meilleur temps d'étape, distance, vitesse maximale

## D'où viennent les données {#where-it-comes-from}

Télémétrie UDP du plugin NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Comment l'activer {#how-to-switch-it-on}

RSF/NGP : dans RichardBurnsRally.ini, section [NGP], réglez udpTelemetry=1 et le point d'arrivée sur 127.0.0.1:6776

## Fonctionnement {#how-it-works}

La télémétrie propre aux jeux de course : Forza, les jeux Assetto Corsa, les jeux de rallye et BeamNG, enregistrée sous forme de trajets, de tours et d'étapes.

Tous ces jeux publient leur télémétrie exprès, pour des tableaux de bord et des simulateurs de mouvement ; rien n'est injecté et rien de ce que le jeu ne fournit n'est lu. Le décodage n'est pas écrit deux fois : ce sont les enregistreurs de tours de gamecapture, dans `heat3d_capture/telemetry` de 3DHeat GameCapture, copiés dans `heat3d_watch/decoders` (testés là-bas avec des paquets construits à partir des formats publiés). Ce module transforme leurs trames en lignes du watcher : la position de la voiture quelques fois par seconde avec sa vitesse, son rapport et ses pédales, un événement par tour ou étape, et les chiffres qu'un pilote garde : tours, meilleur tour, distance, vitesse maximale.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP « Data Out », activé dans le HUD et les réglages de jeu du jeu, vers 127.0.0.1 port 5300, format Dash. Un paquet par tick de simulation ; le décalage du bloc du tableau de bord est trouvé à partir des paquets (`forza.detect_layout`). Mètres dans le monde, Y vers le haut ; le monde est gaucher et est dessiné tel qu'envoyé, comme le fait l'enregistreur de tours (documentation « Data Out » de Forza Motorsport et de Forza Horizon).
Le jeu envoie vers un seul port, et FH Companion et les autres applications Data Out écoutent sur ce même port. Deux programmes ne peuvent pas le partager : sous Windows, le socket lié à 127.0.0.1 reçoit les paquets, et celui lié à toutes les adresses sur le même port n'en reçoit aucun, quel que soit celui arrivé en premier. Le watcher attend donc un peu après le lancement du jeu avant de prendre le port, ne le prend jamais à une application qui le détient, et le libère dès qu'une autre application se met à écouter dessus.
Tant qu'il tient le port, il transmet chaque paquet sans le modifier vers 127.0.0.1:5301 : réglez le champ de port de FH Companion (son onglet télémétrie) sur 5301 et les deux enregistrent.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP : `Documents/My Games/WRC/telemetry/config.json` de WRC (le paquet `session_update` de la structure `wrc`), `hardware_settings_config.xml` de DiRT (`<udp enabled="true" extradata="3" port="20777">`), le plugin NGP de RBR (`udpTelemetry=1`, port 6776). Les étapes sont données par le chronomètre d'étape du jeu (`rally.StageSplitter`). RBR ne documente pas ses axes : l'axe vertical est celui le long duquel l'étape varie le moins, décidé à la fin de la session.

#### Tout est conservé {#everything-kept}

Les lignes sont quelques-unes par seconde ; les jeux en envoient bien davantage. Chaque paquet UDP reçu - dans les menus, entre les tours, ceux qu'aucun décodeur ne lit - est conservé entier dans `heat.raw.parquet` de la session, sous son format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Chaque page de mémoire partagée (toute la zone mappée, pas seulement les octets décodés) est conservée à chaque changement, sous le nom de sa zone (`acpmf_physics`, ...). `used` marque ce qui est aussi devenu des lignes ; `selfCheck.completeness` de `meta.json` compte chaque type (règle du convertisseur de 3DHeat).

Le même module sert aussi : [Assetto Corsa (données en direct)](game-assetto-corsa.md), [Assetto Corsa Competizione (données en direct)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (données en direct)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (données en direct)](game-assetto-corsa-rally.md), [BeamNG.drive (données en direct)](game-beamng.md), [DiRT Rally 2.0 (données en direct)](game-dirt-rally-2.md), [EA SPORTS WRC (données en direct)](game-ea-wrc.md), [Forza Horizon 4 (données en direct)](game-forza-horizon-4.md), [Forza Horizon 5 (données en direct)](game-forza-horizon-5.md), [Forza Horizon 6 (données en direct)](game-forza-horizon-6.md), [Forza Motorsport (données en direct)](game-forza-motorsport.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres ; axe vertical décidé d'après la course (RBR ne documente pas ses axes) |
| Miroir pour la visionneuse | aucun |
| Échelle des unités (`scale` : la visionneuse multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **non**. `games --markdown` affiche « solo ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée publiée par le jeu), donc il enregistre aussi en ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur définit par leur nom (`stats` de chaque `meta.json` de session et table `stats` de `watcher.sqlite`) :

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- lignes à 10 Hz : position, vitesse, rapport, accélérateur, frein, distance dans l'étape, lacet, régime, direction ; début d'étape, arrivée avec le temps d'étape, redémarrages

**Conservé brut**

- chaque paquet qui atteint le port, entier, au rythme du jeu, sous son format : `telemetry` (TelemetryData de NGP, 664 octets), `rbr <n>-byte` pour les autres
- dans le paquet, au-delà des lignes : l'assiette, les vitesses et accélérations propres de la voiture, pour chaque roue la déflexion et la force des ressorts, la progression de l'étape et la distance jusqu'à la fin ; le reste des 664 octets (blocs moteur, pneus et freins par roue) n'est encore décodé nulle part

**Non disponible**

- les autres voitures : les jeux n'envoient que la voiture du joueur
- son unité de vitesse et ses axes : non documentés - la vitesse est prise des positions, la verticale de la conduite

**Taille** : environ 160 Mo par heure à 60 paquets par seconde (664 octets plus un en-tête de 70 octets par élément) ; zstd en garde une fraction

## Vérifié {#verified}

décodage de l'enregistreur de tours de gamecapture (testé sur des paquets construits à partir des formats documentés) ; adaptateur testé sur des paquets construits dans le test, envoyés par UDP ; non testé contre le jeu

## Source {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
