---
title: "Steam Timeline (plateforme)"
nav_order: 44
lang: fr
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (plateforme) {#steam-timeline-platform}

Le watcher sauvegarde ce que Steam Timeline garde sur vos jeux, pour que vous puissiez consulter plus tard votre historique sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `steam-timeline`, type [`platform`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 10 s.*

## Ce qui est enregistré {#what-is-recorded}

- une session par fichier de chronologie : son début et sa fin (session_start, session_end)
- les succès débloqués pendant le jeu, avec l'heure
- les changements de mode de jeu (en jeu, préparation, menus, écran de chargement)
- les événements ajoutés par les jeux via ISteamTimeline, avec titre et description, sous le nom de leur icône
- les phases de jeu (une partie, une mission) avec leurs tags ; les événements à l'intérieur portent son identifiant comme session
- les descriptions d'état que le jeu affiche sur la chronologie (« Round 3 »)
- les erreurs d'enregistrement de Steam elles-mêmes

## D'où viennent les données {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Comment l'activer {#how-to-switch-it-on}

Steam > Paramètres > Enregistrement de jeu : enregistrer en arrière-plan ou à la demande (Steam écrit alors les chronologies)

## Comment ça marche {#how-it-works}

Ce que le lanceur et le pilote graphique gardent sur le jeu : les statistiques, succès, temps de jeu
et chronologies de Steam, ainsi que les moments forts et clips de NVIDIA.

Aucune de ces sources n'a besoin qu'un jeu coopère ou tourne ; les trois adaptateurs ici sont donc
toujours actifs et regardent quelques fichiers toutes les quelques secondes.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
écrit pendant que l'enregistrement de jeu de Steam est activé. Le fichier est du JSON aux nombres en
chaînes : "daterecorded" (secondes Unix), "starttime"/"endtime" (ms) et "entries", chacun
{"id", "time" (ms depuis daterecorded), "type", ...}. Types vus sur de vrais fichiers :
```text
achievement        achievement_name - Steam en ajoute pour chaque jeu
gamemode           mode, un ETimelineGameMode : 1 en jeu, 2 préparation,
                   3 menus, 4 écran de chargement
error              description - celle de Steam (« #GameRecording_RecordingFailed »)
event              AddInstantaneousTimelineEvent/AddRangeTimelineEvent d'un jeu :
                   title, description, icon, priority, duration (ms),
                   possible_clip - « You killed <name> » / « with the <weapon> »
state_description  title - SetTimelineTooltip (« Round 3 »)
phase              un intervalle StartGamePhase..EndGamePhase : duration (ms), tags
                   [{name, icon, group, priority}] (mode, carte ...)
```
La structure du fichier est celle de Steam et n'est pas documentée ; les champs sont les paramètres de
l'API. Tout autre type est enregistré sous son propre nom avec ses champs.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Le même module sert aussi : [Moments forts NVIDIA (plateforme)](game-nvidia-highlights.md),
[Statistiques Steam (plateforme)](game-steam-stats.md).

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

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

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

- chaque entrée une fois, comme une ligne à son heure : son type, chaque champ simple (title, description, icon, priority, duration, possible_clip, nom du succès, mode, ...), les tags d'une phase par groupe, le nom affiché du succès depuis le schéma des statistiques ; le début et la fin du fichier

**Gardé brut**

- chaque entrée entière en JSON sous le `type` de Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, tout autre) : les champs imbriqués — l'icône et la priorité d'un tag, tout ce qu'un Steam plus récent ajoute — ne sont que là
- `timeline` : les champs propres au fichier (daterecorded, starttime, endtime, tout autre), à l'ouverture de la session et à chaque changement

**Non disponible**

- l'enregistrement lui-même (la vidéo) : Steam le garde dans ses propres dossiers ; la session renvoie au fichier de chronologie par son nom
- une lecture d'un fichier que Steam est en train d'écrire et qui ne peut pas être analysé même une fois fermé : compté (`bad` dans l'état de l'adaptateur) et relu au prochain changement, où ses entrées sont prises

**Taille** : quelques centaines d'entrées de 100 à 300 octets par heure de jeu — largement moins de 1 Mo par heure

## Vérifié {#verified}

testé sur de vrais fichiers de chronologie d'une installation locale : entrées achievement, gamemode, error, ainsi que event, state_description et phase propres aux jeux ; le format du fichier lui-même n'est pas documenté

## Source {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
