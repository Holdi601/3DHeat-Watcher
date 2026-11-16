---
title: "Assetto Corsa (données en direct)"
nav_order: 2
lang: "fr"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (données en direct) {#assetto-corsa-live-data}

Pendant que vous jouez à Assetto Corsa, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `assetto-corsa`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `acs.exe` ou `acs_x86.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position de votre voiture (XYZ dans le monde, en m : moyenne des points de contact des pneus) 10 fois par seconde, avec la vitesse, le rapport, l'accélérateur et le frein
- le début et la fin de la session, avec la piste et la voiture annoncées par le jeu
- les tours selon le compteur de tours du jeu, avec leur temps
- les téléportations (retour aux stands, redémarrage) : `teleport` là où se trouvait la voiture, `spawn` là où elle se trouve maintenant
- les tours, le meilleur tour, la distance et la vitesse maximale

## D'où viennent les données {#where-it-comes-from}

mémoire partagée Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Comment ça marche {#how-it-works}

Télémétrie propre aux jeux de course : Forza, les jeux Assetto Corsa, les jeux de rallye et BeamNG, enregistrée sous forme de trajets, de tours et d'épreuves spéciales.

Chacun de ces jeux publie sa télémétrie exprès, pour les tableaux de bord et les simulateurs de mouvement ; rien n'est injecté et rien que le jeu ne fournit n'est lu. Le décodage n'est pas écrit deux fois : ce sont les enregistreurs de tours de gamecapture, dans `heat3d_capture/telemetry` de 3DHeat GameCapture, recopiés dans `heat3d_watch/decoders` (testés là-bas avec des paquets construits à partir des dispositions publiées). Ce module transforme leurs images en lignes du watcher : la position de la voiture plusieurs fois par seconde avec sa vitesse, son rapport et ses pédales, un événement par tour ou par épreuve, et les chiffres que garde un pilote : tours, meilleur tour, distance, vitesse maximale.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

« Data Out » en UDP, activé dans les réglages HUD et Gameplay du jeu, vers 127.0.0.1 port 5300, format Dash. Un paquet par tick de simulation ; le décalage du bloc dash est retrouvé à partir des paquets (`forza.detect_layout`). Mètres du monde, Y vers le haut ; le repère du monde est gaucher et il est dessiné tel qu'il est envoyé, comme le fait l'enregistreur de tours (documentation « Data Out » de Forza Motorsport et de Forza Horizon). Le jeu envoie vers un seul port, et FH Companion et les autres applications Data Out écoutent sur ce même port. Deux programmes ne peuvent pas le partager : sous Windows, le socket lié à 127.0.0.1 reçoit les paquets, et celui lié à toutes les adresses sur le même port n'en reçoit aucun, quel que soit celui qui est arrivé en premier. Le watcher attend donc un peu après le lancement du jeu avant de prendre le port, ne le prend jamais à une application qui le détient, et le libère dès qu'une autre application se met à écouter dessus. Tant qu'il tient le port, il transmet chaque paquet sans le modifier vers 127.0.0.1:5301 : réglez la case de port de l'onglet télémétrie de FH Companion sur 5301 et les deux enregistrent.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Mémoire partagée que le jeu écrit pour les applications : `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO : `Local\acevo_pmf_*`). Ouverte en lecture seule, et seulement une fois que le jeu l'a créée (`simracing_shm`). La position est la moyenne des quatre points de contact des pneus, en mètres du monde, Y vers le haut. Les tours sont comptés par le compteur du jeu (AC, ACC) ou par le passage de nouveau sur le point de départ (AC EVO, AC Rally), comme le fait `kunos.py` pour l'enregistreur de tours.

#### Tout ce qui est conservé {#everything-kept}

Les lignes sont quelques-unes par seconde ; les jeux en envoient bien davantage. Chaque paquet UDP reçu - dans les menus, entre les tours, ceux qu'aucun décodeur ne lit - est conservé en entier dans `heat.raw.parquet` de la session, sous son format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), et chaque page de mémoire partagée (toute la zone mappée, pas seulement les octets décodés) à chaque changement, sous le nom de sa zone (`acpmf_physics`, ...). `used` marque ce qui est aussi devenu des lignes ; `selfCheck.completeness` dans `meta.json` compte chaque type (règle du convertisseur de 3DHeat).

Ce même module sert aussi : [Assetto Corsa Competizione (données en direct)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (données en direct)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (données en direct)](game-assetto-corsa-rally.md), [BeamNG.drive (données en direct)](game-beamng.md), [DiRT Rally 2.0 (données en direct)](game-dirt-rally-2.md), [EA SPORTS WRC (données en direct)](game-ea-wrc.md), [Forza Horizon 4 (données en direct)](game-forza-horizon-4.md), [Forza Horizon 5 (données en direct)](game-forza-horizon-5.md), [Forza Horizon 6 (données en direct)](game-forza-horizon-6.md), [Forza Motorsport (données en direct)](game-forza-motorsport.md), [Richard Burns Rally (données en direct)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- lignes à 10 Hz depuis la page physique : position (moyenne des points de contact des pneus), vitesse, rapport, accélérateur, frein, lacet/tangage/roulis (rad), régime moteur, direction (telle que la page la donne) ; début de session avec la piste et la voiture de la page statique ; tours, position en course

**Conservé brut**

- chaque page en entier - toute la zone mappée, pas seulement les octets décodés - à chaque fois que ses octets changent, lors des lectures du watcher à 10 Hz : `acpmf_physics`, `acpmf_graphics`, `acpmf_static` ; une relecture identique octet par octet au précédent est comptée dans `unchanged_reads` de meta.json, sans être stockée à nouveau
- tout ce qui est décodé seulement pour les fichiers de tours (`decoders/kunos.py` : glissement, charge, pression, températures, carrossage, suspension, points de contact par roue, températures des freins, taux de glissement et angle ; vitesses monde et locale, vitesse angulaire, aides) est dans ces pages

**Non disponible**

- les positions des autres voitures : les pages ne décrivent que la voiture du joueur (la page graphique d'ACC a des identifiants et des coordonnées pour les autres dans certaines versions - conservés dans la page brute, non décodés)
- les ticks physiques entre deux lectures du watcher : le jeu réécrit la page à son rythme physique (jusqu'à 333 Hz) et le watcher lit 10 fois par seconde

**Taille** : environ 150 à 300 Mo par heure avant compression (une région de 4 Ko par page, jusqu'à 10 changements par seconde) ; les pages sont surtout des zéros et zstd en garde une petite fraction

## Vérifié {#verified}

décodage : celui de l'enregistreur de tours de gamecapture (testé sur des pages synthétiques) ; l'adaptateur testé sur une mémoire partagée construite dans le test à partir de la disposition documentée ; non testé avec le jeu

## Source {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
