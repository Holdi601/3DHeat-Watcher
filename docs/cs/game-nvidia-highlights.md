---
title: "NVIDIA highlights (platforma)"
nav_order: 34
lang: "cs"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platforma) {#nvidia-highlights-platform}

Watcher ukládá, co NVIDIA highlights uchovává o vašich hrách, abyste se na svou historii mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `nvidia-highlights`, druh [`platform`](sources-and-rules.md); běží pořád (nečeká, až se hra spustí) a hledá nová data každých 10 s.*

## Co se zaznamenává {#what-is-recorded}

- každý nový klip, highlight nebo snímek: hra, soubor, druh, délka a okamžik (čas ve ms podle hodin)
- ID a název highlightu, pokud ho hra zaregistrovala u NVIDIA
- kde se hráč v tu chvíli nacházel, pokud v tu chvíli zaznamenal stejnou hru jiný adaptér
- žádosti o highlight, které hry s GfeSDK zapisují do logu, i když se žádný klip neuloží

## Odkud to pochází {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;hra>\config.json; klipy ve složce záznamů (%USERPROFILE%\Videos\NVIDIA\\&lt;Hra>\\\*.mp4) a &lt;temp>\Highlights\\&lt;hra>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Jak to zapnout {#how-to-switch-it-on}

NVIDIA App: zapnutý Instant Replay nebo Highlights, klipy ukládané klávesovou zkratkou nebo hrou

## Jak to funguje {#how-it-works}

Co launcher a ovladač grafiky uchovávají o hraní: statistiky Steamu,
achievementy, čas hraní a časové osy, a klipy a highlighty NVIDIA.

Žádný z těchto zdrojů nepotřebuje, aby hra spolupracovala nebo běžela, takže tři
adaptéry zde jsou stále zapnuté a každých několik sekund se podívají na pár souborů.

#### Highlighty a klipy NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Co uchovává NVIDIA App / GeForce Experience, vše pod
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      rejstřík galerie: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, kdy byl soubor zapsán), profileName, drsName
                     (exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (kam se klipy ukládají),
                     settings.tempDirectory (highlighty čekají v
                     <temp>\Highlights\<hra>, dokud se neuloží)
Highlights\<hra>\config.json  druhy highlightů, které hra zaregistrovala:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
a samotné soubory klipů, `<složka záznamů>\<Hra>\<Hra> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (snímky: `<Hra> Screenshot yyyy.mm.dd - ...png`), přičemž
čas v názvu je místní čas uložení klipu. Hry s GfeSDK zapisují
svá volání highlightů také do `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Co to umí a neumí: hra, která podporuje NVIDIA Highlights (GfeSDK), zaregistruje druhy
highlightů jednou - ID jako „kill“, významnost, značky, zobrazovaný název - a později
řekne jen „highlight <id>, od <ms> před teď do <ms> po teď“. Nejsou zde žádné pozice, žádný zápas ani kolo, žádný
soupeř, žádná vlastní data: SDK pro nic z toho nemá pole. Uložený klip přidá jen
soubor, název hry, délku a čas. Zaznamenává se tedy „tento druh okamžiku, v této
hře, v tuto dobu“ - a místo jen vyhledáním času v záznamu jiného
adaptéru pro tutéž hru (`position_at`), což tento adaptér dělá pro každý zaznamenaný klip.
<https://developer.nvidia.com/highlights>

Každý adaptér si ukládá, co už viděl, do `<data>\state\<id>.json`, takže restart
nezaznamená nic dvakrát.

Každá relace také uchovává zdroj svých řádků celý (pravidlo převodníků 3DHeat,
docs/converters.md v repozitáři prohlížeče) v `heat.raw.parquet`: bajty souboru statistik
a jeho schématu a blok localconfig hry (steam-stats; soubor statistik, který dekodér nedokáže
přečíst, dostane relace jen se svými bajty), soubor časové osy - hlavičku
a každou položku jako JSON (steam-timeline), každý záznam rejstříku klipu, definice
highlightů hry a každý řádek logu GfeSDK, i ty, které nejsou žádostmi o highlight
(nvidia-highlights).

Stejný modul slouží také: [Steam statistiky (platforma)](game-steam-stats.md), [Steam Timeline (platforma)](game-steam-timeline.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | jen vypůjčené: místo, které má pro tento okamžik jiný záznam stejné hry |
| Osa nahoru | `y` |
| Jednotky | metry |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapíší do `meta.json` (`axes`) každé relace a, pokud relace obsahuje pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků upravuje sám - viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ne**. `games --markdown` to ukazuje jako „single-player“.
- Druh `platform`: čte jen to, co hra nebo platforma vydává (co uchovává Steam nebo ovladač grafiky), takže zaznamenává i v online hře i offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory`, a nikdy u hry označené jako hraná online - viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- každý nový klip a snímek: hra, soubor, druh, médium, délka (index, jinak hlavička MP4), okamžik z názvu souboru, ID a název highlightu, pokud je hra zaregistrovala, a místo hráče v tu chvíli z záznamu jiného adaptéru
- žádosti o highlight z GfeSDK (každé `Posted Request HL...` kromě konfiguračních volání) s jejich časem

**Uchováno surové**

- `UGC`: celý záznam klipu z rejstříku galerie UGCTracker.json, každé pole, které NVIDIA zapisuje
- `clip_file`: pro klip, který rejstřík neuvádí, cesta k souboru, velikost, čas a složka
- `highlights_config`: `Highlights\<hra>\config.json` hry tak, jak je zapsán (významnost, značky, názvy ve všech jazycích), jednou za relace
- `gfesdk_log`: každý řádek logů GfeSDK přečtených po prvním běhu, `used` pravda pro žádosti o highlight a nepravda pro ostatní (konfigurace, nastavení videa, vlastní zprávy SDK)

**Nedostupné**

- samotné klipy a snímky: video a obrázky zůstávají tam, kam je NVIDIA uložila; řádky uvádějí soubor
- co bylo před prvním během adaptéru: bere se jako již viděné, takže roky klipů se nepromění naráz v relace (`baseline`; False je zaznamená)
- `apps` a `info` v UGCTracker.json a GallerySettings.json: nastavení aplikace, ne okamžiky hry; používá se složka záznamů, kterou uvádějí
- pozice, kola, soupeři: GfeSDK pro ně nemá pole

**Velikost**: asi 1 KB na klip a několik KB definic a řádků logu na každé spuštění hry: výrazně méně než 1 MB za hodinu

## Ověřeno {#verified}

testováno na skutečném rejstříku galerie, nastavení, definicích highlightů a klipech z místní instalace; řádky žádostí o highlight z GfeSDK a ID highlightů v klipech zatím neotestovány

## Zdroj {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
