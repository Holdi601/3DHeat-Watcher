---
title: "NVIDIA-highlights (platform)"
nav_order: 34
lang: "nl"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA-highlights (platform) {#nvidia-highlights-platform}

De watcher bewaart wat NVIDIA-highlights over je spellen bijhoudt, zodat je je geschiedenis later kunt bekijken op een kaart in de 3DHeat-viewer.

*Technische details: adapter `nvidia-highlights`, soort [`platform`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en zoekt elke 10 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- elke nieuwe clip, highlight of screenshot: spel, bestand, soort, lengte en het moment (wandkloktijd in ms)
- de id en naam van de highlight, als het spel die bij NVIDIA heeft geregistreerd
- waar de speler op dat moment was, als een andere adapter datzelfde spel dan heeft opgenomen
- highlight-verzoeken die GfeSDK-spellen loggen, ook als er geen clip wordt bewaard

## Waar het vandaan komt {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; clips in de opslagmap (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) en &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Hoe je het aanzet {#how-to-switch-it-on}

NVIDIA App: Instant Replay of Highlights aan, clips bewaard met een sneltoets of door het spel

## Hoe het werkt {#how-it-works}

Wat de launcher en de grafische driver bewaren over het spelen: Steam-statistieken, achievements, speeltijd en tijdlijnen, en NVIDIA's highlights en clips.

Geen van deze bronnen heeft nodig dat een spel meewerkt of draait, dus de drie adapters hier staan altijd aan en kijken elke paar seconden naar een paar bestanden.

#### NVIDIA-highlights en clips (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Wat NVIDIA App / GeForce Experience bewaart, alles onder
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      de galerij-index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, wanneer het bestand is geschreven), profileName, drsName
                     (de exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (waar clips worden bewaard),
                     settings.tempDirectory (highlights wachten in
                     <temp>\Highlights\<game> tot ze bewaard zijn)
Highlights\<game>\config.json  de highlight-soorten die een spel heeft geregistreerd:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
en de clipbestanden zelf, `<capture folder>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (screenshots: `<Game> Screenshot yyyy.mm.dd - ...png`), waarbij
de tijd in de naam de lokale tijd is waarop de clip is bewaard. Spellen met GfeSDK
loggen hun highlight-aanroepen ook in `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Wat dit wel en niet kan leveren: een spel dat NVIDIA Highlights (GfeSDK) ondersteunt,
registreert highlight-soorten één keer - een id zoals "kill", een belangrijkheid,
tags, een weergavenaam - en zegt later alleen "highlight &lt;id>, from &lt;ms> before
now to &lt;ms> after". Er zijn geen posities, geen wedstrijd of ronde, geen tegenstander,
geen eigen data: de SDK heeft er geen veld voor. Een bewaarde clip voegt een bestand
toe, een spelnaam, een lengte en een tijd. Dus wat wordt opgenomen is "dit soort
moment, in dit spel, op dit tijdstip" - en een plek alleen door de tijd op te zoeken
in de opname van een andere adapter van hetzelfde spel (`position_at`), wat deze
adapter voor elke clip die hij opneemt doet.
<https://developer.nvidia.com/highlights>

Elke adapter houdt bij wat hij al heeft gezien in `<data>\state\<id>.json`, zodat een
herstart niets dubbel opneemt.

Elke sessie bewaart ook, helemaal, waar zijn rijen vandaan komen (de converterregel
van 3DHeat, docs/converters.md in de repository van de viewer), in
`heat.raw.parquet`: de bytes van het statistiekenbestand en zijn schema en het
localconfig-blok van het spel (steam-stats; een statistiekenbestand dat de decoder
niet kan lezen krijgt een sessie die alleen zijn bytes bevat), de kop van het
tijdlijnbestand en elk item als JSON (steam-timeline), het volledige item van elke
clip uit de galerij-index, de highlight-definities van het spel en elke GfeSDK-logregel,
ook die die geen highlight-verzoek zijn (nvidia-highlights).

Dezelfde module dient ook: [Steam-statistieken (platform)](game-steam-stats.md), [Steam Timeline (platform)](game-steam-timeline.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | alleen geleend: de plek die een andere opname van hetzelfde spel voor dat moment heeft |
| Opwaartse as | `y` |
| Eenheden | meters |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities daarmee) | 1 |

Deze gaan naar de `meta.json` van elke sessie (`axes`) en, als de sessie posities heeft, naar de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **nee**. `games --markdown` toont dit als "single-player".
- Soort `platform`: hij leest alleen wat het spel of platform uitgeeft (wat Steam of de grafische driver bewaart), dus hij legt ook online spel vast, net als offline spel; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam zet (de `stats` van elke sessie in `meta.json` en de `stats`-tabel van `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt helemaal bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam wordt bewaard; `used` markeert wat ook rijen werd), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- elke nieuwe clip en screenshot: spel, bestand, soort, media, lengte (uit de index, anders uit de MP4-header), het moment uit de bestandsnaam, de highlight-id en -naam waar het spel die heeft geregistreerd, en de plek van de speler op dat moment uit de opname van een andere adapter
- GfeSDK-highlight-verzoeken (elke `Posted Request HL...` behalve configuratieaanroepen) met hun tijd

**Ruw bewaard**

- `UGC`: het hele item van de clip uit de galerij-index UGCTracker.json, elk veld dat NVIDIA schrijft
- `clip_file`: voor een clip die de index niet noemt, het pad, de grootte, tijd en map van het bestand
- `highlights_config`: de `Highlights\<game>\config.json` van het spel zoals die is geschreven (belangrijkheid, tags, namen in elke taal), één keer per sessie
- `gfesdk_log`: elke regel van de GfeSDK-logs die na de eerste run is gelezen, `used` true voor de highlight-verzoeken en false voor de rest (configuratie, videoinstellingen, de eigen berichten van de SDK)

**Niet beschikbaar**

- de clips en screenshots zelf: video en afbeeldingen blijven waar NVIDIA ze bewaarde; de rijen noemen het bestand
- wat er was vóór de eerste run van de adapter: die wordt als gezien genomen, zodat jaren aan clips niet in één keer tot sessies worden (`baseline`; False neemt ze wel op)
- `apps` en `info` in UGCTracker.json en GallerySettings.json: de instellingen van de app, geen momenten van spel; de opslagmap die ze noemen wordt gebruikt
- posities, rondes, tegenstanders: de GfeSDK heeft er geen veld voor

**Grootte**: ongeveer 1 KB per clip en een paar KB aan definities en logregels per spelstart: ruim onder 1 MB per uur

## Gecontroleerd {#verified}

getest op een echte galerij-index, instellingen, highlight-definities en clips van een lokale installatie; GfeSDK-highlight-verzoekregels en highlight-id's in clips zijn nog niet getest

## Bron {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
