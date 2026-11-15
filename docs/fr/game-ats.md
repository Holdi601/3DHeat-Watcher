---
title: "American Truck Simulator (données en direct)"
nav_order: 1
lang: fr
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (données en direct) {#american-truck-simulator-live-data}

Pendant que vous jouez à American Truck Simulator, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `ats`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `amtrucks.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position mondiale du camion (x est, y haut, z sud, m) à 10 Hz pendant le déplacement, toutes les 5 s à l'arrêt ; cap, vitesse, compteur kilométrique
- livraisons commencées (cargaison, départ, arrivée), livrées (revenu, XP, km), annulées ; amendes, péages, bacs, trains, pleins de carburant
- les bacs, les trains et les sauvegardes chargées coupent le trajet (teleport, spawn)
- distance, vitesse maximale, livraisons, revenu, XP, amendes
- toute la mémoire partagée du plugin dans `heat.raw.parquet`, à chaque changement

## D'où viennent les données {#where-it-comes-from}

Mémoire partagée Local\SCSTelemetry écrite par le plugin scs-sdk-plugin de RenCloud (révision 12) dans &lt;jeu>\bin\win_x64\plugins

## Comment l'activer {#how-to-switch-it-on}

Installez scs-telemetry.dll (révision 12) depuis github.com/RenCloud/scs-sdk-plugin dans &lt;jeu>\bin\win_x64\plugins ; le jeu demande une fois à chaque lancement d'autoriser le SDK

## Fonctionnement {#how-it-works}

Euro Truck Simulator 2 et American Truck Simulator : le SDK de télémétrie de SCS, par le plugin de RenCloud.

SCS publie un SDK de télémétrie (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) pour les plugins que le joueur place dans `<jeu>\bin\win_x64\plugins\`. Le jeu lui-même ne publie rien ; le plugin largement utilisé depuis <https://github.com/RenCloud/scs-sdk-plugin> (MIT) copie les canaux du SDK dans la mémoire partagée `Local\SCSTelemetry` (32 Kio), dont la disposition est décrite dans `scs-telemetry/inc/scs-telemetry-common.hpp`. Ce module lit la révision 12 de cette disposition (PLUGIN_REVID 12) et rien d'autre : le plugin écrit sa révision à l'octet 40, et toute autre révision est laissée non lue plutôt que lue de travers. Décalages utilisés (zones telles que l'en-tête les marque ; alignement naturel) :

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

Le placement mondial du camion est le repère monde de SCS : x est, y haut, z sud, en mètres (droitier, y haut - la visionneuse le dessine tel quel). Les bacs, les trains et le chargement d'une sauvegarde déplacent le camion sans conduite : le trajet est coupé à cet endroit.

Toute la zone mémoire (les 32 Kio du plugin : chaque zone ci-dessus et celles non lues - configuration du camion, roues, usure, autres canaux du camion, et ce que la révision dispose après l'octet 4400, les remorques) est conservée dans le fichier brut de la session à chaque changement, de `type` `SCSTelemetry` avec la `revision` à côté - une page d'une autre révision est aussi conservée entière plutôt que lue de travers.

Le même module sert aussi : [Euro Truck Simulator 2 (données en direct)](game-ets2.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres (monde SCS : x est, y haut, z sud) |
| Miroir pour la visionneuse | aucun |
| Échelle des unités (`scale` : la visionneuse multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` affiche « autorisé (lit seulement ce que le jeu publie) ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée publiée par le jeu), donc il enregistre aussi en ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur définit par leur nom (`stats` de chaque `meta.json` de session et table `stats` de `watcher.sqlite`) :

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- état du SDK et de la pause, révision du plugin, jeu et version, heure dans le jeu, position et cap du camion, vitesse, compteur kilométrique, marque et nom du camion, cargaison, ville et entreprise de départ et d'arrivée, revenu de la livraison, XP et distance, pénalité d'annulation, amendes et leur motif, péages, bacs, trains, les drapeaux des événements spéciaux (lignes, événements et statistiques)
- désormais aussi sur les lignes de position : `pitch` et `roll` (degrés, depuis les tours du SDK), `gear` et `rpm`
- décalages vérifiés contre une transcription champ par champ de l'en-tête de la révision 12 du plugin, dont les débuts de zones sont vérifiés dans les tests ; pas encore contre le jeu

**Conservé brut**

- `SCSTelemetry` : toute la zone de 32 Kio du plugin, à chaque lecture dont les octets diffèrent de la copie conservée la dernière fois (`unchanged_reads` dans meta.json compte les autres), `revision` à côté : chaque zone - configuration du camion et de la remorque, canaux du camion (pédales, direction, carburant, AdBlue, pressions, températures, usure, feux, roues), vecteurs de placement et d'accélération, chaînes de travail et de jeu, et tout ce que la révision dispose après l'octet 4400 (les remorques) ; `used` vaut vrai tant que le SDK est actif et que la révision est 12
- une page d'une autre révision du plugin est conservée entière avec `used` à faux plutôt que lue de travers

**Non disponible**

- tout ce que le plugin ne copie pas hors du SDK, et tout pendant que le plugin n'est pas installé : le jeu ne publie aucune télémétrie propre
- les camions des autres joueurs dans TruckersMP ou les convois : le SDK ne donne que le camion du joueur

**Taille** : 32 Kio jusqu'à 10 fois par seconde pendant la conduite (les lectures diffèrent alors toutes) : environ 1,2 Go par heure avant compression, une seule copie en pause ; la plus grande part de la page est faite de zéros et de configuration qui ne change pas, donc zstd la réduit beaucoup (pas encore mesuré sur une vraie session)

## Vérifié {#verified}

testé sur de la mémoire partagée construite à partir de la disposition d'en-tête de la révision 12 du plugin ; non testé contre le jeu

## Source {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
