---
title: "NVIDIA highlights (platforma)"
nav_order: 34
lang: "sk"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platforma) {#nvidia-highlights-platform}

Watcher ukladá to, čo NVIDIA highlights uchováva o vašich hrách, aby ste si históriu neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `nvidia-highlights`, typ [`platform`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 10 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- každý nový klip, highlight alebo snímka: hra, súbor, typ, dĺžka a okamih (čas v ms)
- ID a názov highlightu, keď ho hra zaregistrovala u NVIDIA
- kde bol hráč v tom okamihu, keď ten istý zápas zaznamenal iný adaptér
- žiadosti o highlight, ktoré hry GfeSDK zapisujú, aj keď sa žiadny klip neuchová

## Odkiaľ to berie {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;hra>\config.json; klipy v priečinku záznamov (%USERPROFILE%\Videos\NVIDIA\\&lt;Hra>\\\*.mp4) a &lt;temp>\Highlights\\&lt;hra>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Ako to zapnúť {#how-to-switch-it-on}

NVIDIA App: zapnuté Instant Replay alebo Highlights, klipy ukladané klávesom alebo hrou

## Ako to funguje {#how-it-works}

Čo spúšťač a ovládač grafiky uchovávajú o hraní: štatistiky Steamu, úspechy, čas hrania a časové osi, a klipy a highlighty NVIDIA.

Žiadny z týchto zdrojov nepotrebuje, aby hra spolupracovala alebo bežala, takže tri adaptéry tu sú vždy zapnuté a každých niekoľko sekúnd pozerajú na pár súborov.

#### Highlighty a klipy NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Čo uchováva NVIDIA App / GeForce Experience, všetko pod
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      index galérie: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, kedy bol súbor zapísaný), profileName, drsName
                     (exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (kam sa klipy ukladajú),
                     settings.tempDirectory (highlighty čakajú v
                     <temp>\Highlights\<hra>, kým sa neuložia)
Highlights\<hra>\config.json  druhy highlightov, ktoré hra zaregistrovala:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
a samotné súbory klipov, `<priečinok záznamov>\<Hra>\<Hra> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (snímky: `<Hra> Screenshot yyyy.mm.dd - ...png`), pričom čas v názve je miestny čas uloženia klipu. Hry s GfeSDK zapisujú aj svoje volania highlightov do `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Čo to môže a nemôže doručiť: hra, ktorá podporuje NVIDIA Highlights (GfeSDK), zaregistruje druhy highlightov raz – ID ako „kill“, význam, značky, zobrazovaný názov – a neskôr povie len „highlight <id>, od <ms> pred teraz do <ms> po“. Nie sú tu žiadne polohy, zápas ani kolo, žiadny súper, žiadne vlastné dáta: SDK na to nemá pole. Uložený klip pridá len súbor, názov hry, dĺžku a čas. Takže zaznamenáva sa „tento druh okamihu, v tejto hre, v tomto čase“ – a miesto len vyhľadaním času v záznamu iného adaptéra pre tú istú hru (`position_at`), čo tento adaptér robí pre každý klip, ktorý zaznamená.
<https://developer.nvidia.com/highlights>

Každý adaptér si ponecháva, čo už videl, v `<data>\state\<id>.json`, takže reštart nič nezaznamená dvakrát.

Každá relácia tiež uchováva celé to, z čoho jej riadky vznikli (pravidlo konvertorov 3DHeat, docs/converters.md v repozitári prehliadača), v `heat.raw.parquet`: bajty súboru štatistík a jeho schémy a blok localconfig hry (steam-stats; súbor štatistík, ktorý dekodér nedokáže prečítať, dá reláciu obsahujúcu len svoje bajty), hlavičku súboru časovej osi a každú položku ako JSON (steam-timeline), každý záznam indexu galérie klipu, definície highlightov hry a každý riadok logu GfeSDK (nvidia-highlights).

Rovnaký modul slúži aj: [Steam štatistiky (platforma)](game-steam-stats.md), [Steam Timeline (platforma)](game-steam-timeline.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | len vypožičané: miesto, ktoré pre ten okamih má iný záznam tej istej hry |
| Os nahor | `y` |
| Jednotky | metre |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **nie**. `games --markdown` to zobrazí ako „jeden hráč“.
- Typ `platform`: číta len to, čo hra alebo platforma vydáva (čo uchováva Steam alebo ovládač grafiky), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- každý nový klip a snímka: hra, súbor, druh, médium, dĺžka (z indexu, inak z hlavičky MP4), okamih z názvu súboru, ID a názov highlightu, ak ho hra zaregistrovala, a miesto hráča v tom čase z iného adaptéra
- žiadosti o highlight GfeSDK (každé `Posted Request HL...` okrem konfiguračných volaní) s ich časom

**Uchované surové**

- `UGC`: celý záznam klipu z indexu galérie UGCTracker.json, každé pole, ktoré NVIDIA zapisuje
- `clip_file`: pre klip, ktorý index nevypisuje, cesta k súboru, veľkosť, čas a priečinok
- `highlights_config`: `Highlights\<hra>\config.json` hry tak, ako je zapísaný (význam, značky, názvy vo všetkých jazykoch), raz za reláciu
- `gfesdk_log`: každý riadok logov GfeSDK prečítaný po prvom spustení, `used` pravda pre žiadosti o highlight a nepravda pre ostatné (konfigurácia, nastavenia videa, vlastné správy SDK)

**Nedostupné**

- samotné klipy a snímky: video a obrázky zostávajú tam, kde ich NVIDIA uložila; riadky uvádzajú len súbor
- to, čo tam bolo pred prvým spustením adaptéra: berie sa ako už videné, takže roky klipov sa nezmenia naraz na relácie (`baseline`; ak je False, zaznamenajú sa)
- `apps` a `info` v UGCTracker.json a GallerySettings.json: nastavenia aplikácie, nie okamihy hrania; používa sa priečinok záznamov, ktorý uvádzajú
- polohy, kolá, súperi: GfeSDK pre ne nemá pole

**Veľkosť**: približne 1 KB na klip a niekoľko KB definícií a riadkov logu na spustenie hry: hlboko pod 1 MB za hodinu

## Overené {#verified}

testované na skutočnom indexe galérie, nastaveniach, definíciách highlightov a klipoch z lokálnej inštalácie; riadky žiadostí o highlight GfeSDK a ID highlightov v klipoch nie sú otestované

## Zdroj {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
