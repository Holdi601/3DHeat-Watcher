---
title: NVIDIA Highlights
nav_order: 8
lang: "nl"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Sommige spellen vragen je NVIDIA-grafische driver om een korte video op te slaan wanneer er iets gebeurt, zoals een kill.
De watcher noteert elk van die momenten en zet ze, als dat kan, op de kaart waar ze gebeurden.

De adapter `nvidia-highlights` legt de clips, highlights en screenshots vast die de NVIDIA-app (of GeForce Experience) opslaat, en geeft elk ervan een plek op de kaart als dat lukt. Deze pagina legt uit wat NVIDIA Highlights wel en niet kan leveren, welke bestanden de watcher leest, en hoe een highlight een positie krijgt. De gegenereerde pagina van de adapter is [NVIDIA highlights (platform)](game-nvidia-highlights.md).

## Wat NVIDIA Highlights kan en niet kan leveren {#what-nvidia-highlights-can-and-cannot-deliver}

Een spel dat NVIDIA Highlights ondersteunt, praat via GfeSDK met de NVIDIA-app. De SDK draagt maar twee soorten berichten:

1. **Eenmaal, bij de start**: de soorten highlights die het spel gaat gebruiken - een id (zoals `kill`), een belangrijkheid, tags en een weergavenaam per taal. De NVIDIA-app slaat die per spel op.
2. **Op een moment van spel**: "highlight `<id>`, van `<ms>` geleden tot `<ms>` later". Dat is het hele bericht: het id van een soort die het spel heeft geregistreerd, en twee tijdsverschuivingen die de NVIDIA-app vertellen welk stuk van zijn doorlopende opname hij moet bewaren.

De SDK heeft **geen veld voor iets anders**: geen positie, geen wedstrijd of ronde, geen tegenstander, geen wapen, geen score, geen eigen gegevens van welke soort dan ook. Een spel kan geen positie in een highlight zetten, ook als het dat zou willen. Wanneer de clip wordt opgeslagen, voegt de NVIDIA-app een bestand, een spelnaam, een lengte en een tijd toe.

Een highlight kan dus alleen zeggen "dit soort moment, in dit spel, op dit tijdstip". Alles meer moet ergens anders vandaan komen.

## Wat de watcher leest {#what-the-watcher-reads}

Alles wordt gelezen uit bestanden die de NVIDIA-app schrijft voor zijn eigen galerij. Niets praat met de driver of met de app. De map van de NVIDIA-overlay is
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Bestand | Wat eruit gehaald wordt |
|---|---|
| `UGCTracker.json` | de galerij-index: elke clip en screenshot met zijn pad, type (video, afbeelding), subtype (`InstantReplay`, ...), datum, de profielnaam van het spel, het uitvoerbare bestand en de korte naam, en de lengte (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, de opslagmap van de opnamen, en `settings.tempDirectory`, waar highlights wachten (`<temp>\Highlights\<game>`) tot ze worden opgeslagen |
| `Highlights\<game>\config.json` | de soorten highlights die elk spel heeft geregistreerd: id, en de Engelse weergavenaam (of het id als het spel geen naam gaf) |
| de opslagmap van de opnamen (standaard `%USERPROFILE%\Videos\NVIDIA`) en `<temp>\Highlights` | de clip- en screenshotbestanden zelf (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), één map per spel |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | de verzoeken die spellen met GfeSDK in het logboek zetten - `Posted Request HL...`-regels - zodat een highlight die het spel vroeg, vastgelegd wordt ook als er geen clip is bewaard. Configuratieverzoeken (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) worden overgeslagen. |

Voor elk nieuw item schrijft de adapter één rij: `highlight` voor een video, `screenshot` voor een afbeelding, of `highlight_request` voor een GfeSDK-logregel. De velden:

| Veld | Wat het is |
|---|---|
| `ms` | het moment: de tijd in de bestandsnaam (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, de lokale tijd waarop de clip is opgeslagen), anders de datum uit de index, anders de wijzigingstijd van het bestand |
| `game` | de profielnaam van NVIDIA, de mapnaam of de spelnaam uit de bestandsnaam |
| `clip`, `media` | het pad van het bestand; `video`, `image` of `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (uit de tijdelijke highlightmap) of het subtype uit de index |
| `duration_s`, `clip_start_ms` | de lengte, uit de index of uit de eigen header van de video (`moov/mvhd`, gevonden zonder de video te lezen); het moment waarop de clip begint |
| `highlight_id`, `highlight_name` | de soort highlight, als iets die noemt (zie hieronder) |
| `exe` | het uitvoerbare bestand van het spel, uit de index |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | de geleende positie, als er een gevonden is (zie hieronder) |

De sessiestatistieken zijn `clips`, `screenshots`, `clip_seconds` en `placed` (items die een positie kregen).

**Het highlight-id** staat op geen enkele gedocumenteerde plek. De adapter probeert twee niet-gedocumenteerde manieren: een veld van de galerij-invoer waarvan de naam "highlight" bevat, en - alleen voor bestanden in de tijdelijke highlightmap - een van de geregistreerde id's van het spel (minstens 4 tekens lang) die in de bestandsnaam voorkomt. Een opgeslagen clip is genoemd naar het spel, dat toevallig een id als "kill" zou kunnen bevatten, dus zijn naam wordt niet doorzocht. Deze twee manieren zijn op een echte computer nog niet gezien werken: er is nog geen clip met een highlight-id geweest, en nog geen GfeSDK-verzoekregel, op de computer waarop de adapter is getest. De galerij-index, instellingen, highlightdefinities en clips zijn getest op echte bestanden.

### Wanneer items worden vastgelegd {#when-items-are-recorded}

- Een clip wordt pas een tijd na de toetsaanslag geschreven. De adapter wacht tot een bestand bij twee keer kijken (elke 10 s) dezelfde grootte en tijd heeft en minstens 5 s oud is.
- De eerste keer dat de adapter draait, wordt alles wat al in de galerij en de logboeken staat alleen genoteerd, niet vastgelegd, zodat jaren aan oude clips de statistieken niet overspoelen. Wat hij gezien heeft, wordt bewaard in `<data>\state\nvidia-highlights.json`, zodat een herstart niets dubbel vastlegt.
- Items worden per spel in één sessie gegroepeerd. De sessie van een spel sluit na 30 minuten zonder nieuw item, en eindigt op zijn laatste moment in plaats van op het moment dat het spel sloot. Momenten die meer dan 30 minuten uit elkaar liggen, gaan in aparte sessies.

## Hoe een highlight een positie krijgt {#how-a-highlight-gets-a-position}

De highlight zelf heeft geen plek. De adapter zoekt het moment op in de andere opnamen die de watcher tegelijk van hetzelfde spel maakte:

1. **Hetzelfde spel**: de sessiemappen onder `<data>\sessions\` waarvan de spelnaam overeenkomt met die van de highlight. Namen worden vergeleken in kleine letters, alleen letters en cijfers. Ze komen overeen als ze gelijk zijn, of als de kortste minstens 5 tekens heeft en in de langste voorkomt (`Counter-Strike 2` en `Counter-Strike-2`).
2. **Dezelfde tijd**: sessies waarvan het begin en einde (uit `meta.json`, met een seconde speling aan beide kanten) het moment omvatten. Sessies die eindigden zonder posities, en de eigen sessies van de adapter, worden overgeslagen.
3. **De eigen rij van de speler**: in hun `events.jsonl`, de laatste eigen rij van de speler met een positie, op of vóór het moment en niet meer dan 5 seconden ervoor. Een rij is de eigen rij wanneer de bron dat zegt: `"player": "me"`, of `"own_car": 1` (racespellen die elke auto op naam van de coureur opnemen), of een `player` die de `player` van de sessie in `meta.json` is (de naam die de bron aan de speler geeft). Zie [De eigen rijen van de speler](the-data.md#the-players-own-rows).

Als er een rij gevonden wordt, krijgt de highlight zijn `x`, `y`, `z`, zijn `session` (of de naam van de map), `position_from` (de map waar het vandaan kwam) en `position_lag_ms` (hoeveel eerder dan het moment die rij was). De highlightsessie neemt de assen van die opname over, zodat hij op dezelfde manier getekend wordt. Als er geen rij gevonden wordt, blijft de highlight een moment op de tijdlijn zonder plek.

Dingen om te weten over de geleende positie:

- **Het is waar je was toen de clip werd opgeslagen**, niet waar de actie begon. Het moment is de tijd van opslaan in de bestandsnaam, wat bij een Instant Replay het einde is. `clip_start_ms` zegt wanneer de clip begint.
- **Een andere adapter moet tegelijk hetzelfde spel hebben opgenomen.** De adapters die de eigen rijen van de speler markeren, en zo een highlight kunnen plaatsen: Counter-Strike 2 en Dota 2 game-state integration, Forza, de Assetto Corsa-spellen, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft en geheugenprofielen (als `me`); F1 23/24/25, RaceRoom, Automobilista 2 en Project CARS 2 (de rijen van je eigen auto dragen `own_car` 1, volgens de spelerautoindex van het spel, het eigen slot of de bekeken deelnemer); Elite Dangerous (de naam van de commandant, in `meta.json` als `player`, omdat het logboek altijd van de speler is).
- **Een replay wordt na de wedstrijd omgezet**, dus die kan alleen een clip plaatsen die na de conversie wordt opgezocht: de clip wordt geplaatst wanneer hij wordt vastgelegd, en een later opgeslagen replay wordt niet opnieuw bekeken. Replays van League of Legends noemen hun rijen naar de Riot ID in de instellingen en krijgen, met een Riot API-sleutel, de kloktijd die de tijdlijn van de wedstrijd aangeeft, zodat ze dan gevonden worden. Een CS2-demo kan een highlight helemaal niet plaatsen: zijn posities staan in de eigen tabel van de converter, niet in `events.jsonl`, en een demo heeft de ticks van het spel maar geen kloktijd om het moment van een clip mee te vergelijken.
- In Rocket League zijn de enige rijen met een plek de balgebeurtenissen. Een balraak van jou is een rij van jou, dus een highlight kan geplaatst worden waar je de bal het laatst raakte.
- Spellen zonder enige positiebron (Overwatch 2, Call of Duty, Hunt: Showdown, ...) houden hun highlights als een tijdlijn van momenten.

## Waarom geheugen in multiplayer geen positie kan geven {#why-memory-cannot-give-a-position-in-multiplayer}

De andere manier om een positie te krijgen zou uit het geheugen zijn. Geen van beide werkt:

- **Het geheugen van NVIDIA bevat geen positie.** De NVIDIA-app ontvangt wat de GfeSDK draagt - een highlight-id en twee tijdsverschuivingen - plus de video die hij opneemt. Er is nergens aan NVIDIA's kant een positie om te lezen. (De watcher leest het geheugen van NVIDIA sowieso niet; hij leest de bestanden hierboven.)
- **Het geheugen van het spel is in multiplayer niet toegankelijk.** De positie staat in het proces van het spel, maar de watcher leest het geheugen van een multiplayerspel nooit: een geheugenadapter voor een spel dat als online gespeeld is gemarkeerd, wordt geweigerd voordat er iets geopend wordt (zie [Geheugen lezen](memory-reading.md)). Multiplayerspellen draaien onder anti-cheats (Easy Anti-Cheat, BattlEye, Vanguard, ...) die het door een ander programma laten openen van het proces van het spel als vals spelen zien, wat tot een geblokkeerd account kan leiden. Een highlight in een multiplayerspel krijgt dus alleen een plek uit wat het spel zelf publiceert: zijn game-state integration of telemetrie, vastgelegd door een andere adapter op hetzelfde moment.
