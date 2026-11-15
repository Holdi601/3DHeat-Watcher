---
title: "Dota 2 (replaye)"
nav_order: 12
lang: "cs"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replaye) {#dota-2-replays}

Po zápase Dota 2 Watcher promění replay, který hra uložila, na soubory, na které se můžete podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `dota-replays`, druh [`replay`](sources-and-rules.md); běží pořád (nečeká, až začne hra) a hledá nová data každých 5 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice, výška, zdraví a úroveň každého hrdiny 7,5krát za sekundu, dokud žije
- zabití a smrti tam, kde se staly; věže, kasárny, Roshan a Tormentoři tam, kde padli; wardy tam, kde byly umístěny
- mapové pingy, kresby na mapě a příkazy každého hráče (pohyb, útok, kouzlo, nákup, ...) tam, kam ukazovaly
- skóre a řádek každého hráče; řádek přihlášeného hráče jako statistiky
- všechno ostatní, co replay obsahuje, uchované celé vedle tabulky: každý snímek a síťová zpráva, každá změna vlastnosti entity, každý záznam tabulky řetězců

## Odkud to pochází {#where-it-comes-from}

replaye, které Dota 2 ukládá: &lt;Dota>/game/dota/replays/&lt;match id>.dem (stažené v klientovi, nebo příkazem `dota-replay <match id>`)

## Jak to zapnout {#how-to-switch-it-on}

stáhněte replay zápasu v Dota 2, nebo stáhněte veřejný: `python -m heat3d_watch dota-replay <match id>`; potřebuje `pip install gem-dota`

Příkaz napište do terminálu otevřeného ve složce Watcheru (viz [Než začnete](before-you-start.md)). Pokud selže, poslední řádek vysvětlí proč; [Instalace a spuštění](installing-and-running.md) popisuje obvyklé příčiny.

## Jak to funguje {#how-it-works}

Replaye a dema: co hra uloží o zápase, převedeno jednou, když zápas skončí.

Replay obsahuje všechno, co živé rozhraní ve hrách pro více hráčů zadržuje – pozici každého hráče, každé zabití tam, kde se stalo – a je to soubor, který hra píše pro své hráče, takže jeho čtení se hry nijak nedotkne. Watcher sleduje složky, do kterých hry replaye ukládají, počká, až nový soubor přestane růst (jinak by ho hra ještě psala), a převádí ho ve vlákně na pozadí, takže dlouhý převod nezdrží zbytek Watcheru.

Poprvé, když se složka uvidí, replaye, které už v ní jsou, se jen zaznamenají, nepřevedou se: hráč s lety starými dema by jinak Watcher zavalil na celý den. `python -m heat3d_watch replays <adapter> [folder]` převede existující na vyžádání.

#### Dota 2 {#dota-2}

Dota 2 ukládá replaye, které si hráč stáhne (podrobnosti zápasu nebo Watch > Replays), do `<Dota>/game/dota/replays/<match id>.dem`; Valve drží replay každého veřejného zápasu na svých serverech několik týdnů a `python -m heat3d_watch dota-replay <match id>` ho stáhne podle id přes OpenDota. Každý se čte knihovnou gem (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) ve vlastním procesu (`heat3d_watch/decoders/dota_replay.py`): pozice, výška, zdraví, úroveň, natočení, mana, zkušenosti, atributy a předměty každého hrdiny 7,5krát za sekundu, dokud žije, zabití a smrti tam, kde se staly, věže, kasárny, Roshan a Tormentoři tam, kde padli, každý ward tam, kde byl umístěn a kde skončil, záznamy bojového logu o hrdinech (poškození, léčení, schopnosti, předměty, nákupy, runy, zlato, zkušenosti, modifikátory) a každý mapový ping, kresba a příkaz hráče – do `dota/<match>.parquet`; každá jiná jednotka (creepi, přivolaní, iluze, kurýři, budovy) jednou za sekundu do `<match>.units.parquet`; celý bojový log do `<match>.combatlog.parquet`; a zápas, chat, draft, všechno ostatní, co parser vytáhne, a herní záznam konce zápasu do `<match>.match.json` ve složce relace. Všechno ostatní, co replay obsahuje, se uchová celé vedle nich (pravidlo převodníků 3DHeat): každý snímek a síťová zpráva v `<match>.packets.parquet`, každá změna vlastnosti entity v `<match>.entities.parquet`, každý záznam tabulky řetězců v `<match>.strings.parquet`, počítáno v `selfCheck.completeness` dokumentu zápasu. Pozice jsou světové jednotky Dota, stejné, jaké hlásí game-state integration. Řádek skóre přihlášeného hráče se stane statistikami relace: zabití, smrti, asistence, poslední zásahy, odmítnutí, čistý zisk, GPM, XPM, poškození hrdinům, wardy a to, zda zápas vyhrál. Nový patch Dota může změnit entity replaye dřív, než je gem dožene; replay, který gem nedočte až do konce, se převede jen do místa, kam dojde, a v souhrnu se označí jako `incomplete`.

Stejný modul slouží také: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [osu! (replaye)](game-osu-replays.md), [Squad (replaye)](game-squad-demos.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Tanks (replaye)](game-wot-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `z` |
| Jednotky | světové jednotky Dota (jednotky Hammeru; mapa má přibližně 16400 napříč) |
| Zrcadleno pro prohlížeč | `y` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, když relace má pozice, do patičky `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítkuje řádky sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukáže jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `replay`: čte jen to, co hra nebo platforma vydává (replaye a dema, která hra ukládá), takže nahrává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda se smí číst paměť.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle jména (každé relace `stats` v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč na každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedené jménem.

## Úplnost {#completeness}

Převodník dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co replay obsahuje, se načte nebo uchová, nikdy se nezahodí. Kromě tabulky se všechno ostatní, co replay obsahuje, uchová celé ve vedlejších souborech vedle něj ve složce `dota/` relace – `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (sloupce `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, podle toho, co se na ně vztahuje) – a `selfCheck.completeness` dokumentu zápasu (`<match>.match.json`) počítá každý `type` – `lost` je 0.

**Načteno**

- tabulka (`dota/<match>.parquet`): pozice, výška, zdraví, úroveň, natočení, mana, zkušenosti, atributy, brnění, rychlost, poškození, předměty a kurzor hráče každého hrdiny 7,5krát za sekundu; zabití, smrti, cíle, wardy, záznamy bojového logu o hrdinech; mapové pingy (`ping`, DOTA_UM_LocationPing), kresby na mapě (`map_line`, DOTA_UM_MapLine) a každý příkaz jednotce (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` typ příkazu, `value` id schopnosti nebo předmětu, `text` třída cíle; v bodě příkazu, jinak u hrdiny)
- `<match>.units.parquet`: každá jiná jednotka jednou za sekundu; `<match>.combatlog.parquet`: celý bojový log, jak ho čte gem, každé pole
- dokument zápasu: všechno, co gem vytáhne, a celé záznamy replaye, které samo vede – `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: délka přehrávání, jméno, hrdina, steam id a tým každého hráče), `matchDetails` (DOTA_UM_MatchDetails: koncová tabulka herního koordinátora, čísla každého hráče, předměty, poškození podle typu, výběr a zákazy) a `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: zabití, smrti, asistence, úroveň, poslední zásahy a odmítnutí, jak se čtou ze streamu proti `matchDetails`, pro každého hráče

**Uchováno surové**

- `<match>.packets.parquet`: každý rámec, který není paket (`type` `frame <n>`), a každá síťová zpráva (`message <n>`, `name` podle Valve), celá v `payload`, v pořadí souboru (`seq`, `frame`), přičemž `decoded` je protobuf jako JSON (bajtové pole jako svá délka); dekódován každý typ zprávy: svc_PacketEntities (proud entit), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, zprávy bojového logu, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projektily, animace, krev), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; tabulky odesílání, seznam tříd a informace o serveru, které potřebuje pozdější dekodér entit, jsou mezi nimi
- `<match>.entities.parquet`: každá vlastnost každé entity pokaždé, když se změnila (`type` vlastnost, `name` třída, `entity` její index; `value`, `vector` nebo `decoded`), její celý stav při vzniku a každý vznik, vstup, odchod a smazání – miliony řádků za celý zápas
- `<match>.strings.parquet`: každý záznam tabulky řetězců z každé aktualizace a každého úplného snímku, hodnota celá; `userinfo`, `ActiveModifiers` a `EconItems` dekódované z protobufů
- `selfCheck.completeness` v dokumentu zápasu počítá rámce a zprávy podle názvů Valve, záznamy bojového logu (`combatlog <type>`), herní události (`gameevent <name>`), záznamy tabulky řetězců (`stringtable <name>`) a aktualizace entit (`entity <class>`); několik se uchovává jen surově (úplné snímky entit, které gem přeskočí, protože se staví z delt, a záznamy tabulek, jejichž hodnoty nic nečte), lost 0

**Nedostupné**

- hlas: replay má nastavení hlasu, ale ne hlasová data
- jména za hashi a id: zvuky a částice se jmenují podle hashů herních souborů, schopnosti podle id; replay jména nenese (předměty se pojmenují přes katalog gemu, kde ho má)
- cokoli, co věděl jen klient hráče (jeho kamera, jeho obrazovka) nad rámec toho, co server vysílal; kurzor a každý příkaz jsou uvnitř

**Velikost**: přílohy dohromady jsou o něco větší než samotný replay, nejvíc paketů a entit; celý zápas trvá v jednom procesu minutu nebo dvě

## Ověřeno {#verified}

ověřeno na veřejném replayi zápasu: zabití, smrti, asistence, úroveň, poslední zásahy a odmítnutí se shodují s koncovým záznamem hry pro všech deset hráčů; každá zpráva v příloze paketů se znovu serializuje bajt po bajtu; tabulka a statistiky testovány na syntetických datech

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
