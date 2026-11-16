---
title: NVIDIA Highlights
nav_order: 8
lang: "cs"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Některé hry požádají ovladač vaší grafické karty NVIDIA, aby uložil krátké video, když se něco stane, třeba zabití.
Watcher si každý takový okamžik poznamená a, když to jde, ho zobrazí na mapě v místě, kde se stal.

Adaptér `nvidia-highlights` zaznamenává klipy, highlighty a snímky obrazovky, které ukládá aplikace NVIDIA App (nebo GeForce Experience), a každému dá místo na mapě, když to jde. Tato stránka vysvětluje, co NVIDIA Highlights umí doručit a co ne, které soubory Watcher čte a jak highlight dostane pozici. Generovaná stránka adaptéru je [NVIDIA highlights (platforma)](game-nvidia-highlights.md).

## Co NVIDIA Highlights umí doručit a co ne {#what-nvidia-highlights-can-and-cannot-deliver}

Hra, která podporuje NVIDIA Highlights, mluví s aplikací NVIDIA App přes GfeSDK NVIDIA. SDK nese jen dva druhy zpráv:

1. **Jednou, na začátku**: druhy highlightů, které hra použije – id (například `kill`), významnost, značky a zobrazované jméno v každém jazyce. Aplikace NVIDIA App je ukládá pro každou hru.
2. **V okamžiku hry**: „highlight `<id>`, od `<ms>` před teď do `<ms>` po teď“. To je celá zpráva: id druhu, který hra zaregistrovala, a dva časové posuny, které řeknou aplikaci NVIDIA App, jakou část jejího průběžného záznamu si má ponechat.

SDK nemá **žádné pole pro nic dalšího**: žádnou pozici, žádný zápas ani kolo, žádného soupeře, žádnou zbraň, žádné skóre, žádná vlastní data jakéhokoli druhu. Hra nemůže do highlightu dát pozici, ani kdyby chtěla. Když se klip uloží, aplikace NVIDIA App přidá soubor, název hry, délku a čas.

Highlight tedy může říct jen „tento druh okamžiku, v této hře, v tomto čase“. Všechno ostatní musí přijít odjinud.

## Co Watcher čte {#what-the-watcher-reads}

Všechno se čte ze souborů, které aplikace NVIDIA App zapisuje pro svou vlastní galerii. Nic nemluví s ovladačem ani s aplikací. Složka překryvu NVIDIA je
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Soubor | Co se z něj bere |
|---|---|
| `UGCTracker.json` | index galerie: každý klip a snímek s cestou, typem (video, obrázek), podtypem (`InstantReplay`, ...), datem, jménem profilu hry, spustitelným souborem a krátkým názvem hry, a délkou (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, složka záznamů, a `settings.tempDirectory`, kde čekají highlighty (`<temp>\Highlights\<game>`), dokud se neuloží |
| `Highlights\<game>\config.json` | druhy highlightů, které každá hra zaregistrovala: id a anglické zobrazované jméno (nebo id, když hra žádné nedala) |
| složka záznamů (výchozí `%USERPROFILE%\Videos\NVIDIA`) a `<temp>\Highlights` | samotné soubory klipů a snímků (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), jedna složka na hru |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | žádosti, které hry s GfeSDK zapisují do logu – řádky `Posted Request HL...` – takže se zaznamená highlight, o který hra požádala, i když se nezachoval žádný klip. Konfigurační žádosti (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) se přeskakují. |

Pro každou novou položku adaptér zapíše jeden řádek: `highlight` pro video, `screenshot` pro obrázek, nebo `highlight_request` pro řádek logu GfeSDK. Jeho pole:

| Pole | Co to je |
|---|---|
| `ms` | okamžik: čas v názvu souboru (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, místní čas uložení klipu), jinak datum z indexu, jinak čas změny souboru |
| `game` | jméno profilu NVIDIA, jméno složky nebo hra z názvu souboru |
| `clip`, `media` | cesta k souboru; `video`, `image` nebo `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (z dočasné složky highlightů) nebo podtyp z indexu |
| `duration_s`, `clip_start_ms` | délka, z indexu nebo z vlastní hlavičky videa (`moov/mvhd`, najde se bez čtení videa); okamžik, kdy klip začíná |
| `highlight_id`, `highlight_name` | druh highlightu, když ho něco pojmenuje (viz níže) |
| `exe` | spustitelný soubor hry, z indexu |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | vypůjčená pozice, když se nějaká našla (viz níže) |

Statistiky relace jsou `clips`, `screenshots`, `clip_seconds` a `placed` (položky, které dostaly pozici).

**Id highlightu** není zapsané v žádném dokumentovaném místě. Adaptér zkusí dva nedokumentované: pole záznamu galerie, jehož název obsahuje „highlight“, a – jen pro soubory v dočasné složce highlightů – jedno z id, která hra zaregistrovala (délka alespoň 4 znaky), které se objeví v názvu souboru. Uložený klip je pojmenovaný podle hry, která by mohla náhodou obsahovat id jako „kill“, proto se v jeho názvu nehledá. Tyto dva způsoby zatím na skutečném počítači nefungovaly: nebyl pozorován žádný klip s id highlightu ani žádný řádek žádosti GfeSDK tam, kde se adaptér testoval. Index galerie, nastavení, definice highlightů a klipy se testovaly na skutečných souborech.

### Kdy se položky zaznamenají {#when-items-are-recorded}

- Klip se ještě nějakou dobu zapisuje i po stisknutí klávesy. Adaptér počká, až má soubor při dvou pohledech stejnou velikost a čas (každých 10 s) a je starý alespoň 5 s.
- Když adaptér běží poprvé, všechno, co už je v galerii a logách, se jen zaznamená, ne nahraje, aby roky starých klipů nezaplavily statistiky. Co viděl, se uchovává v `<data>\state\nvidia-highlights.json`, takže restart nezaznamená nic dvakrát.
- Položky se seskupují do jedné relace na hru. Relace hry se uzavře po 30 minutách bez nové položky a skončí u svého posledního okamžiku, ne když se hra zavřela. Okamžiky vzdálené od sebe více než 30 minut jdou do oddělených relace.

## Jak highlight dostane pozici {#how-a-highlight-gets-a-position}

Highlight sám žádné místo nemá. Adaptér vyhledá okamžik v jiných záznamech, které Watcher pořídil ze stejné hry ve stejnou dobu:

1. **Stejná hra**: složky relace pod `<data>\sessions\`, jejichž jméno hry odpovídá jménu highlightu. Jména se porovnávají malými písmeny, jen písmena a číslice. Shodují se, když jsou stejná, nebo když kratší má alespoň 5 znaků a je obsažena v delším (`Counter-Strike 2` a `Counter-Strike-2`).
2. **Stejný čas**: relace, jejichž začátek a konec (z `meta.json`, s jednou sekundou rezervy na obou koncích) okamžik pokrývají. Relace, které skončily bez pozic, a vlastní relaci adaptéru se přeskakují.
3. **Vlastní řádek hráče**: v jeho `events.jsonl` nejnovější vlastní řádek hráče s pozicí, v okamžiku nebo nejvýš 5 sekund před ním. Řádek je vlastní, když to jeho zdroj říká: `"player": "me"`, nebo `"own_car": 1` (závodní hry, které zaznamenávají každé auto podle jezdce), nebo `player`, který je `player` relace v `meta.json` (jméno, které zdroj dává hráči). Viz [Vlastní řádky hráče](the-data.md#the-players-own-rows).

Když se řádek najde, highlight dostane svá `x`, `y`, `z`, svou `session` (nebo jméno složky), `position_from` (složku, odkud pochází) a `position_lag_ms` (jak dlouho před okamžikem byl ten řádek). Relace highlightu převezme osy toho záznamu, takže se kreslí stejným směrem. Když se žádný řádek nenajde, highlight zůstane okamžikem na časové ose bez místa.

Věci, které je dobré vědět o vypůjčené pozici:

- **Je to místo, kde jste byli, když se klip ukládal**, ne kde akce začala. Okamžik je čas uložení v názvu souboru, což je u Instant Replay jeho konec. `clip_start_ms` říká, kdy klip začíná.
- **Jiný adaptér musel ve stejnou dobu nahrávat tutéž hru.** Ty, které označují vlastní řádky hráče, a tak mohou highlight umístit: game-state integration Counter-Strike 2 a Dota 2, Forza, hry Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft a profily paměti (jako `me`); F1 23/24/25, RaceRoom, Automobilista 2 a Project CARS 2 (řádky vašeho auta nesou `own_car` 1 podle indexu hráčova auta hry, jeho vlastního slotu nebo sledovaného účastníka); Elite Dangerous (jméno velitele v `meta.json` jako `player`, protože deník je vždy hráčův).
- **Replay se převede až po zápase**, takže může umístit jen klip, který se hledá až po převodu: klip se umístí, když se nahraje, a replay uložený později se znovu nekontroluje. Replaye League of Legends pojmenovávají své řádky podle Riot ID v nastavení a s klíčem Riot API jim dávají čas nástěnných hodin, který uvádí časová osa zápasu, takže se tehdy najdou. Demo CS2 nemůže highlight umístit vůbec: jeho pozice jsou v tabulce převodníku, ne v `events.jsonl`, a demo má herní ticky, ale ne čas nástěnných hodin, se kterým by se dal okamžik klipu porovnat.
- V Rocket League jsou jediné řádky s místem události s míčem. Váš zásah do míče je váš řádek, takže se highlight dá umístit tam, kde jste naposledy zasáhli míč.
- Hry bez jakéhokoli pozičního zdroje (Overwatch 2, Call of Duty, Hunt: Showdown, ...) si své highlighty drží jako časovou osu okamžiků.

## Proč paměť nedá pozici ve hře pro více hráčů {#why-memory-cannot-give-a-position-in-multiplayer}

Druhým způsobem, jak získat pozici, by bylo číst ji z paměti. Ani jedna paměť to neumožní:

- **Paměť NVIDIA žádnou pozici neobsahuje.** Aplikace NVIDIA App dostane to, co nese GfeSDK – id highlightu a dva časové posuny – plus video, které nahraje. Na straně NVIDIA není nikde žádná pozice, kterou by bylo možné přečíst. (Watcher stejně paměť NVIDIA nečte; čte výše uvedené soubory.)
- **Paměť hry je v hrách pro více hráčů mimo dosah.** Pozice je v procesu hry, ale Watcher paměť hry pro více hráčů nikdy nečte: adaptér paměti pro hru označenou jako hraná online se odmítne ještě předtím, než se cokoli otevře (viz [Čtení paměti](memory-reading.md)). Hry pro více hráčů běží pod anti-cheaty (Easy Anti-Cheat, BattlEye, Vanguard, ...), které považují otevření procesu hry jiným programem za podvádění, což může vést k zablokování účtu. Highlight ve hře pro více hráčů tedy dostane místo jen z toho, co hra zveřejňuje: z její game-state integration nebo telemetrie, zaznamenané jiným adaptérem ve stejnou dobu.
