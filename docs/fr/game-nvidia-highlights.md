---
title: "NVIDIA highlights (plateforme)"
nav_order: 34
lang: fr
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (plateforme) {#nvidia-highlights-platform}

Le watcher enregistre ce que NVIDIA highlights garde de vos jeux, pour que vous puissiez consulter votre historique plus tard sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `nvidia-highlights`, type [`platform`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 10 s.*

## Ce qui est enregistré {#what-is-recorded}

- chaque nouveau clip, moment fort ou capture d'écran : jeu, fichier, type, durée et moment (ms en heure murale)
- l'identifiant et le nom du moment fort quand le jeu l'a enregistré auprès de NVIDIA
- où se trouvait le joueur à ce moment-là, quand un autre adaptateur a enregistré ce même jeu à ce moment-là
- les demandes de moment fort que les jeux GfeSDK consignent, même quand aucun clip n'est gardé

## D'où viennent les données {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;jeu>\config.json ; les clips dans le dossier de capture (%USERPROFILE%\Videos\NVIDIA\\&lt;Jeu>\\\*.mp4) et &lt;temp>\Highlights\\&lt;jeu> ; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Comment l'activer {#how-to-switch-it-on}

NVIDIA App : Instant Replay ou Highlights activé, clips enregistrés par raccourci ou par le jeu

## Fonctionnement {#how-it-works}

Ce que le lanceur et le pilote graphique gardent de vos parties : statistiques, succès, temps de jeu et chronologies de Steam, ainsi que les moments forts et les clips de NVIDIA.

Aucune de ces sources n'a besoin qu'un jeu coopère ou tourne, donc les trois adaptateurs ici sont toujours actifs et regardent quelques fichiers toutes les quelques secondes.

#### Moments forts et clips NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Ce que NVIDIA App / GeForce Experience garde, tout sous `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay` :
```text
UGCTracker.json      the gallery index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (where clips are saved),
                     settings.tempDirectory (highlights wait in
                     <temp>\Highlights\<game> until saved)
Highlights\<game>\config.json  the highlight kinds a game registered:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
et les fichiers de clips eux-mêmes, `<dossier de capture>\<Jeu>\<Jeu> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (captures d'écran : `<Jeu> Screenshot yyyy.mm.dd - ...png`), l'heure dans le nom étant l'heure locale d'enregistrement du clip. Les jeux GfeSDK consignent aussi leurs appels de moment fort dans `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Ce que cela peut et ne peut pas fournir : un jeu compatible avec NVIDIA Highlights (GfeSDK) enregistre ses types de moments une seule fois - un identifiant comme « kill », une importance, des étiquettes, un nom affiché - puis dit plus tard seulement « highlight <id>, from <ms> before now to <ms> after ». Il n'y a ni position, ni match ou manche, ni adversaire, ni donnée personnalisée : le SDK n'a pas de champ pour cela. Un clip sauvegardé ajoute un fichier, un nom de jeu, une durée et une heure. Donc ce qui est enregistré est « ce type de moment, dans ce jeu, à cette heure » - et un lieu seulement en cherchant l'heure dans l'enregistrement d'un autre adaptateur pour le même jeu (`position_at`), ce que cet adaptateur fait pour chaque clip qu'il enregistre.
<https://developer.nvidia.com/highlights>

Chaque adaptateur garde ce qu'il a déjà vu dans `<données>\state\<id>.json`, donc un redémarrage n'enregistre rien deux fois.

Chaque session garde aussi d'où viennent ses lignes, entier (règle du convertisseur de 3DHeat, docs/converters.md dans le dépôt de la visionneuse), dans `heat.raw.parquet` : les octets du fichier de statistiques et de son schéma, et le bloc localconfig du jeu (steam-stats ; un fichier de statistiques que le décodeur ne peut pas lire donne une session qui ne contient que ses octets), les en-têtes du fichier de chronologie et chaque entrée en JSON (steam-timeline), l'entrée d'index de galerie de chaque clip, les définitions de moments forts du jeu et chaque ligne de journal GfeSDK, celles qui ne sont pas des demandes de moment fort aussi (nvidia-highlights).

Le même module sert aussi : [Statistiques Steam (plateforme)](game-steam-stats.md), [Steam Timeline (plateforme)](game-steam-timeline.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | seulement empruntées : le lieu qu'un autre enregistrement du même jeu a pour ce moment |
| Axe vertical | `y` |
| Unités | mètres |
| Miroir pour la visionneuse | aucun |
| Échelle des unités (`scale` : la visionneuse multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **non**. `games --markdown` affiche « solo ».
- Type `platform` : il ne lit que ce que le jeu ou la plateforme fournit (ce que Steam ou le pilote graphique conserve), donc il enregistre aussi en ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur définit par leur nom (`stats` de chaque `meta.json` de session et table `stats` de `watcher.sqlite`) :

`clip_seconds`, `clips`, `placed`, `screenshots`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans ses propres noms de statistiques ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Complétude {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais écarté. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé entier dans le `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` de `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- chaque nouveau clip et capture d'écran : jeu, fichier, type, support, durée (index, sinon en-tête du MP4), le moment d'après le nom du fichier, l'identifiant et le nom du moment fort quand le jeu les a enregistrés, et la place du joueur à ce moment-là d'après l'enregistrement d'un autre adaptateur
- les demandes de moment fort GfeSDK (chaque `Posted Request HL...`, sauf les appels de configuration) avec leur heure

**Conservé brut**

- `UGC` : l'entrée complète du clip dans l'index de galerie UGCTracker.json, chaque champ écrit par NVIDIA
- `clip_file` : pour un clip que l'index ne liste pas, le chemin du fichier, sa taille, son heure et son dossier
- `highlights_config` : le `Highlights\<jeu>\config.json` du jeu tel qu'écrit (importance, étiquettes, noms dans chaque langue), une fois par session
- `gfesdk_log` : chaque ligne des journaux GfeSDK lus après la première exécution, `used` vrai pour les demandes de moment fort et faux pour le reste (configuration, réglages vidéo, messages propres au SDK)

**Non disponible**

- les clips et captures d'écran eux-mêmes : la vidéo et les images restent là où NVIDIA les a enregistrées ; les lignes en nomment le fichier
- ce qui existait avant la première exécution de l'adaptateur : considéré comme déjà vu, pour que des années de clips ne deviennent pas des sessions d'un coup (`baseline` ; False les enregistre)
- `apps` et `info` de UGCTracker.json et GallerySettings.json : les réglages de l'application, pas des moments de jeu ; le dossier de capture qu'ils nomment est utilisé
- positions, manches, adversaires : le GfeSDK n'a pas de champ pour eux

**Taille** : environ 1 Ko par clip et quelques Ko de définitions et de lignes de journal par lancement de jeu : bien moins de 1 Mo par heure

## Vérifié {#verified}

testé sur un vrai index de galerie, de vrais réglages, de vraies définitions de moments forts et de vrais clips issus d'une installation locale ; les lignes de demande de moment fort GfeSDK et les identifiants de moment fort dans les clips ne sont pas testés

## Source {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
