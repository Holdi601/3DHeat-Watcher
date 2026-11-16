---
title: NVIDIA Highlights
nav_order: 8
lang: "sk"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Niektoré hry žiadajú váš grafický ovládač NVIDIA, aby uložil krátke video, keď sa niečo stane, napríklad zabitie.
Watcher si každý taký okamih poznačí a, keď to ide, ho umiestni na mape, kde sa stal.

Adaptér `nvidia-highlights` zaznamenáva klipy, highlighty a snímky obrazovky, ktoré ukladá aplikácia NVIDIA App (alebo GeForce Experience), a každému z nich dá miesto na mape, ak sa dá. Táto stránka vysvetľuje, čo môžu NVIDIA Highlights doručiť a čo nie, ktoré súbory watcher číta a ako highlight získa pozíciu. Generovaná stránka adaptéra je [NVIDIA highlights (platforma)](game-nvidia-highlights.md).

## Čo môžu NVIDIA Highlights doručiť a čo nie {#what-nvidia-highlights-can-and-cannot-deliver}

Hra, ktorá podporuje NVIDIA Highlights, hovorí s aplikáciou NVIDIA App cez GfeSDK od NVIDIA. SDK prenáša len dva druhy správ:

1. **Raz, na začiatku**: druhy highlightov, ktoré hra použije – id (napríklad `kill`), dôležitosť, značky a zobrazované meno v každom jazyku. NVIDIA App ich ukladá pre každú hru.
2. **V okamihu hry**: „highlight `<id>`, od `<ms>` pred teraz po `<ms>` po teraz“. To je celá správa: id druhu, ktorý hra zaregistrovala, a dva časové posuny, ktoré hovoria aplikácii NVIDIA App, ktorý úsek jej priebežného záznamu sa má zachovať.

SDK **nemá pole pre nič iné**: žiadna pozícia, zápas ani kolo, žiadny protivník, zbraň, skóre ani vlastné dáta akéhokoľvek druhu. Hra nemôže do highlightu dostať pozíciu, ani keby chcela. Keď sa klip uloží, NVIDIA App pridá súbor, názov hry, dĺžku a čas.

Highlight teda dokáže povedať len „tento druh okamihu, v tejto hre, v tomto čase“. Všetko ostatné musí prísť odinde.

## Čo watcher číta {#what-the-watcher-reads}

Všetko sa číta zo súborov, ktoré NVIDIA App zapisuje pre svoju vlastnú galériu. Nič sa nebaví s ovládačom ani s aplikáciou. Priečinok NVIDIA Overlay je
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Súbor | Čo sa z neho berie |
|---|---|
| `UGCTracker.json` | index galérie: každý klip a snímok s jeho cestou, typom (video, obrázok), podtypom (`InstantReplay`, ...), dátumom, menom profilu hry, spustiteľným súborom a krátkym názvom hry a dĺžkou (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, priečinok záznamov, a `settings.tempDirectory`, kde čakajú highlighty (`<temp>\Highlights\<game>`), kým sa uložia |
| `Highlights\<game>\config.json` | druhy highlightov, ktoré si každá hra zaregistrovala: id a anglické zobrazované meno (alebo id, ak ho hra nedala) |
| priečinok záznamov (predvolene `%USERPROFILE%\Videos\NVIDIA`) a `<temp>\Highlights` | samotné súbory klipov a snímkov (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), jeden priečinok na hru |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | žiadosti, ktoré zapisujú hry s GfeSDK – riadky `Posted Request HL...` – takže highlight, o ktorý hra žiadala, sa zaznamená aj vtedy, keď sa žiadny klip neuchoval. Konfiguračné žiadosti (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) sa preskočia. |

Pre každú novú položku adaptér zapíše jeden riadok: `highlight` pre video, `screenshot` pre obrázok alebo `highlight_request` pre riadok logu GfeSDK. Jeho polia:

| Pole | Čo je |
|---|---|
| `ms` | okamih: čas v názve súboru (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, miestny čas uloženia klipu), inak dátum z indexu, inak čas zmeny súboru |
| `game` | meno profilu NVIDIA, názov priečinka alebo názov hry z názvu súboru |
| `clip`, `media` | cesta k súboru; `video`, `image` alebo `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (z dočasného priečinka highlightov) alebo podtyp z indexu |
| `duration_s`, `clip_start_ms` | dĺžka, z indexu alebo z hlavičky videa (`moov/mvhd`, nájdená bez čítania videa); okamih, kedy klip začína |
| `highlight_id`, `highlight_name` | druh highlightu, keď ho niečo pomenuje (pozrite nižšie) |
| `exe` | spustiteľný súbor hry, z indexu |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | prevzatá pozícia, keď sa našla (pozrite nižšie) |

Štatistiky relácie sú `clips`, `screenshots`, `clip_seconds` a `placed` (položky, ktoré dostali pozíciu).

**Id highlightu** nie je zapísané v žiadnom zdokumentovanom mieste. Adaptér skúša dva nezdokumentované spôsoby: pole záznamu galérie, ktorého názov obsahuje „highlight“, a – len pre súbory v dočasnom priečinku highlightov – jedno z id, ktoré hra zaregistrovala (aspoň 4 znaky dlhé), a objaví sa v názve súboru. Názov uloženého klipu nesie názov hry, ktorý by mohol náhodou obsahovať id ako „kill“, preto sa podľa názvu nehľadá. Zatiaľ sa nevidelo, že by tieto dva spôsoby fungovali na skutočnom počítači: nevznikol klip s id highlightu a nevznikol ani riadok žiadosti GfeSDK, na ktorom bol adaptér testovaný. Index galérie, nastavenia, definície highlightov a klipy boli testované na skutočných súboroch.

### Kedy sa položky zaznamenajú {#when-items-are-recorded}

- Klip sa ešte chvíľu zapisuje po stlačení klávesu. Adaptér počká, kým súbor pri dvoch pohľadoch (každých 10 s) nemá rovnakú veľkosť a čas, a je aspoň 5 s starý.
- Keď adaptér beží prvý raz, všetko, čo už je v galérii a logoch, sa len zaznamená, nie zapíše, aby sa roky starých klipov nenahrnuli do štatistík. Čo už videl, sa uchová v `<data>\state\nvidia-highlights.json`, takže reštart nezapíše nič dvakrát.
- Položky sa zoskupujú do jednej relácie na hru. Relácia hry sa zavrie po 30 minútach bez novej položky a končí v svojom poslednom okamihu, nie vtedy, keď sa hra zavrela. Okamihy, ktoré sú od seba viac ako 30 minút, idú do samostatných relácií.

## Ako highlight získa pozíciu {#how-a-highlight-gets-a-position}

Samotný highlight nemá miesto. Adaptér vyhľadá okamih v ďalších záznamoch, ktoré watcher urobil z tej istej hry v tom istom čase:

1. **Tá istá hra**: priečinky relácií pod `<data>\sessions\`, ktorých názov hry sa zhoduje s názvom hry highlightu. Názvy sa porovnávajú malými písmenami, len písmená a číslice. Zhodujú sa, keď sú rovnaké, alebo keď je kratší z nich dlhý aspoň 5 znakov a je obsiahnutý v dlhšom (`Counter-Strike 2` a `Counter-Strike-2`).
2. **Ten istý čas**: relácie, ktorých začiatok a koniec (z `meta.json`, s jednou sekundou rezervy na oboch koncoch) pokrývajú okamih. Relácie, ktoré skončili bez pozícií, a vlastné relácie adaptéra sa preskočia.
3. **Vlastný riadok hráča**: v jeho `events.jsonl` najnovší vlastný riadok hráča s pozíciou, v čase okamihu alebo pred ním a najviac 5 sekúnd pred ním. Riadok je vlastný hráča, keď to jeho zdroj hovorí: `"player": "me"`, alebo `"own_car": 1` (pretekárske hry, ktoré zaznamenávajú každé auto podľa jazdca), alebo `player`, ktoré je `player` relácie v `meta.json` (meno, ktoré zdroj dáva hráčovi). Pozrite [Riadky hráča](the-data.md#the-players-own-rows).

Ak sa riadok nájde, highlight dostane svoje `x`, `y`, `z`, svoju `session` (alebo názov priečinka), `position_from` (priečinok, odkiaľ pochádza) a `position_lag_ms` (koľko pred okamihom bol ten riadok). Relácia highlightu prevezme osi tohto záznamu, takže sa kreslí rovnako otočená. Ak sa riadok nenájde, highlight zostane okamihom na časovej osi bez miesta.

Veci, ktoré treba vedieť o prevzatej pozícii:

- **Je to miesto, kde ste boli, keď sa klip uložil**, nie miesto, kde sa akcia začala. Okamih je čas uloženia v názve súboru, čo pri Instant Replay je jeho koniec. `clip_start_ms` hovorí, kedy klip začína.
- **Iný adaptér musel v tom čase nahrávať tú istú hru.** Tie, ktoré označujú vlastné riadky hráča, a teda môžu highlight umiestniť: game-state integration Counter-Strike 2 a Dota 2, Forza, hry Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft a profily pamäte (ako `me`); F1 23/24/25, RaceRoom, Automobilista 2 a Project CARS 2 (riadky vášho auta nesú `own_car` 1, podľa indexu hráčovho auta hry, jeho vlastného slotu alebo sledovaného účastníka); Elite Dangerous (meno veliteľa, v `meta.json` ako `player`, lebo denník je vždy hráčov).
- **Replay sa prevedie po zápase**, takže môže umiestniť len klip, ktorý sa hľadá až po konverzii: klip sa umiestni, keď sa zaznamená, a replay uložený neskôr sa znovu nepozerá. Replaye League of Legends pomenúvajú vaše riadky podľa Riot ID v nastaveniach a, s kľúčom Riot API, dajú im čas nástennych hodín, ktorý uvádza časová os zápasu, takže sa nájdu vtedy. Demo CS2 nemôže umiestniť highlight vôbec: jeho pozície sú v tabuľke konvertora, nie v `events.jsonl`, a demo má herné takty, ale nie čas nástennych hodín, s ktorým by sa dal porovnať okamih klipu.
- V Rocket League sú jediné riadky s miestom udalosti s loptou. Váš zásah do lopty je váš riadok, takže highlight sa dá umiestniť tam, kde ste naposledy loptu zasiahli.
- Hry bez akéhokoľvek pozičného zdroja (Overwatch 2, Call of Duty, Hunt: Showdown, ...) si svoje highlighty uchovávajú ako časovú os okamihov.

## Prečo pamäť nedá pozíciu vo viachráčovej hre {#why-memory-cannot-give-a-position-in-multiplayer}

Druhý spôsob, ako získať pozíciu, by bol čítať ju z pamäte. Ani jedna pamäť nepomôže:

- **Pamäť NVIDIA nemá pozíciu.** NVIDIA App dostane to, čo prenáša GfeSDK – id highlightu a dva časové posuny – plus video, ktoré nahrá. Na strane NVIDIA nie je nikde pozícia, ktorú by sa dalo čítať. (Watcher aj tak pamäť NVIDIA nečíta; číta súbory uvedené vyššie.)
- **Pamäť hry je vo viachráčových hrách mimo dosahu.** Pozícia je v procese hry, ale watcher pamäť viachráčovej hry nikdy nečíta: adaptér pamäte pre hru označenú ako hranú online sa odmietne ešte predtým, než sa čokoľvek otvorí (pozrite [Čítanie pamäte](memory-reading.md)). Viachráčové hry bežia pod anti-cheatmi (Easy Anti-Cheat, BattlEye, Vanguard, ...), ktoré považujú otvorenie procesu hry iným programom za podvádzanie, čo môže účet zablokovať. Highlight vo viachráčovej hre preto dostane miesto len z toho, čo hra zverejňuje: jej game-state integration alebo telemetrie, zaznamenanej iným adaptérom v tom istom čase.
