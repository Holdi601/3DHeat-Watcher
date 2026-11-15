---
title: "Statistiques Steam (plateforme)"
nav_order: 43
lang: "fr"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Statistiques Steam (plateforme) {#steam-statistics-platform}

Le watcher sauvegarde ce que les statistiques Steam gardent sur vos jeux, pour que vous puissiez consulter plus tard votre historique sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `steam-stats`, type [`platform`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 30 s.*

## Ce qui est enregistré {#what-is-recorded}

- chaque statistique qu'un jeu conserve dans Steam (ses propres noms et valeurs), par jeu, à chaque changement
- les déblocages de succès, avec leur nom affiché, leur description et l'heure du déblocage
- les changements de statistiques, avec l'ancienne valeur, la nouvelle et la différence
- le temps de jeu (minutes, deux dernières semaines) et l'heure de la dernière partie

## D'où viennent les données {#where-it-comes-from}

le cache local des statistiques de Steam %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin avec UserGameStatsSchema_&lt;appid>.bin ; le temps de jeu vient de %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% depuis HKCU\Software\Valve\Steam SteamPath)

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le watcher lit la source telle que le jeu ou la plateforme la fournit.

## Comment ça marche {#how-it-works}

Ce que le lanceur et le pilote graphique gardent sur le jeu : les statistiques, succès, temps de jeu
et chronologies de Steam, ainsi que les moments forts et clips de NVIDIA.

Aucune de ces sources n'a besoin qu'un jeu coopère ou tourne ; les trois adaptateurs ici sont donc
toujours actifs et regardent quelques fichiers toutes les quelques secondes.

#### Statistiques Steam (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, réécrit par le client Steam chaque fois
qu'un jeu enregistre ses statistiques, décodé avec le schéma `UserGameStatsSchema_<appid>.bin` à côté
(KeyValues binaire, voir `_steam.py`). Les statistiques sont des entiers ou des décimaux selon ce que
le jeu définit ; les succès sont des bits avec une heure de déblocage en secondes Unix. Le temps de jeu
est dans `<Steam>\userdata\<account>\config\localconfig.vdf` sous apps/&lt;appid> : Playtime et
Playtime2wks en minutes, LastPlayed en secondes Unix. Steam est trouvé via HKCU\Software\Valve\Steam
SteamPath. API des statistiques : <https://partner.steamgames.com/doc/features/achievements>

Le même module sert aussi : [Moments forts NVIDIA (plateforme)](game-nvidia-highlights.md),
[Steam Timeline (plateforme)](game-steam-timeline.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | non |
| Axe vertical | `y` |
| Unités | mètres |
| Miroir pour la visionneuse | aucun |
| Échelle (`scale` : la visionneuse multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des
positions, dans le pied de `heat.parquet` : la visionneuse 3DHeat tourne et met à l'échelle les lignes
toute seule — voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **non**. `games --markdown` l'affiche comme « solo ».
- Type `platform` : il ne lit que ce que le jeu ou la plateforme remet (ce que Steam ou le pilote graphique garde), donc il enregistre aussi en ligne ; l'indicateur décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne — voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et table `stats` de `watcher.sqlite`) :

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés
que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent
pas dans cette liste ; « Ce qui est enregistré » ci-dessus les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle des convertisseurs](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)
de 3DHeat : ce que contient la source est lu ou gardé, jamais abandonné. En plus des lignes, chaque
paquet, page, ligne ou réponse reçu par l'adaptateur est gardé entier dans `heat.raw.parquet` de la
session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ gardé par nom ; `used`
marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` dans `meta.json` compte chaque
`type` — `lost` vaut 0.

**Lu**

- chaque statistique du fichier de statistiques par son nom d'API (entier, décimal, avgrate), chaque bit de succès avec son heure de déblocage, nommés et décrits par le schéma
- les changements par rapport à la dernière lecture (ancien, nouveau, différence), les nouveaux déblocages ; le temps de jeu, le temps des deux dernières semaines et la dernière partie depuis localconfig.vdf

**Gardé brut**

- `UserGameStats` : les octets du fichier de statistiques, entiers, à chaque enregistrement (le `crc`, `PendingChanges`, les bits de succès que le schéma ne définit plus et toute clé que le décodeur saute s'y trouvent)
- `UserGameStatsSchema` : les octets du fichier de schéma à côté, pour que les statistiques puissent être décodées à partir de la session seule (tous les noms et descriptions des statistiques et succès, dans toutes les langues, icônes, drapeaux)
- `localconfig_app` : le bloc entier du jeu dans localconfig.vdf en JSON (état de la synchronisation cloud, options de lancement, badges et toute autre clé que Steam garde par jeu) quand son temps de jeu est enregistré
- un fichier de statistiques que le décodeur ne peut pas lire (coupé pendant l'écriture, ou une disposition nouvelle) : ses octets et le schéma, dans une session sans lignes (`used` à faux ; `unreadable` dans meta.json)

**Non disponible**

- le reste de localconfig.vdf (amis, chat, paramètres de Steam) : ce n'est pas celui du jeu, et c'est privé
- les valeurs des statistiques entre deux écritures : Steam réécrit le fichier quand le jeu enregistre ses statistiques, en général à la fermeture
- les pourcentages mondiaux de succès et les statistiques des autres joueurs : ils sont sur les serveurs de Steam, pas ici

**Taille** : quelques Ko par séance enregistrée, plus le schéma (jusqu'à quelques centaines de Ko pour un jeu avec beaucoup de succès) — largement moins de 1 Mo par heure de jeu ; zstd réduit le texte du schéma de moitié ou plus

## Vérifié {#verified}

testé sur de vrais fichiers de statistiques et schémas d'une installation locale ; détection des changements testée sur des fichiers construits au format KeyValues binaire

## Source {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
