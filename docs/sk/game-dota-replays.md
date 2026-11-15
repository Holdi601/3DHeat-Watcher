---
title: "Dota 2 (replaye)"
nav_order: 12
lang: "sk"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replaye) {#dota-2-replays}

Po zápase Dota 2 watcher premení replay, ktorý hra uložila, na súbory, ktoré si môžete pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `dota-replays`, druh [`replay`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- pozícia, výška, zdravie a úroveň každého hrdinu 7,5-krát za sekundu, kým žije
- zabitia a smrti tam, kde sa stali; veže, kasárne, Roshan a Tormentori tam, kde padli; wardy tam, kde boli položené
- mapové pingy, kresby na mape a príkazy (pohyb, útok, kúzlo, nákup, ...) každého hráča tam, kam mierili
- skóre a riadok každého hráča; riadok prihláseného hráča ako štatistiky
- všetko ostatné, čo replay obsahuje, uchované celé vedľa tabuľky: každý rámec a sieťová správa, každá zmena vlastnosti entity, každý záznam reťazcovej tabuľky

## Odkiaľ to pochádza {#where-it-comes-from}

replaye, ktoré Dota 2 ukladá: &lt;Dota>/game/dota/replays/&lt;match id>.dem (stiahnuté v klientovi, alebo príkazom `dota-replay <match id>`)

## Ako to zapnúť {#how-to-switch-it-on}

stiahnite replay zápasu v Dota 2, alebo si stiahnite verejný: `python -m heat3d_watch dota-replay <match id>`; potrebuje `pip install gem-dota`

Príkaz zadajte v termináli otvorenom v priečinku watchera (pozrite [Pred začiatkom](before-you-start.md)). Ak zlyhá, posledný riadok povie prečo; [Inštalácia a spustenie](installing-and-running.md) popisuje najčastejšie príčiny.

## Ako to funguje {#how-it-works}

Replaye a dema: to, čo hra uloží o zápase, prevedené po skončení zápasu.

Replay obsahuje všetko, čo živé rozhranie v hrách pre viacerých hráčov zadržiava – pozíciu každého hráča, každé zabitie tam, kde sa stalo – a je to súbor, ktorý hra zapisuje pre svojich hráčov, takže jeho čítanie nič v hre nezasiahne. Watcher sleduje priečinky, do ktorých hry ukladajú replaye, počká, kým sa nový súbor prestane zväčšovať (inak by hra stále zapisovala), a prevedie ho vo vlákne na pozadí, takže dlhá konverzia nezdrží zvyšok watchera.

Keď sa priečinok prvýkrát uvidí, replaye, ktoré v ňom už sú, sa len zaevidujú, nie prevedú; hráč s rokmi dem by inak čakal, že watcher bude zaneprázdnený celý deň. `python -m heat3d_watch replays <adapter> [folder]` prevedie existujúce na požiadanie.

#### Dota 2 {#dota-2}

Dota 2 ukladá replaye, ktoré si hráč stiahne (podrobnosti zápasu alebo Watch > Replays), do `<Dota>/game/dota/replays/<match id>.dem`; Valve drží replay každého verejného zápasu na svojich serveroch niekoľko týždňov, a `python -m heat3d_watch dota-replay <match id>` ho stiahne podľa jeho id cez OpenDota. Každý sa číta knižnicou gem (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) vo vlastnom procese (`heat3d_watch/decoders/dota_replay.py`): pozícia, výška, zdravie, úroveň, smer, mana, skúsenosti, atribúty a predmety každého hrdinu 7,5-krát za sekundu, kým žije; zabitia a smrti tam, kde sa stali; veže, kasárne, Roshan a Tormentori tam, kde padli; každý ward tam, kde bol položený, a kde skončil; záznamy bojového protokolu o hrdinoch (poškodenie, lieči, schopnosti, predmety, nákupy, runy, zlato, skúsenosti, modifikátory) a mapové pingy a kresby a príkazy každého hráča – do `dota/<match>.parquet`; každá iná jednotka (creepy, prizvané, ilúzie, kuriéri, budovy) raz za sekundu do `<match>.units.parquet`; celý bojový protokol do `<match>.combatlog.parquet`; a zápas, chat, draft, všetko ostatné, čo parser vytiahne, a koncový záznam zápasu od hry do `<match>.match.json`, v priečinku relácie. Všetko ostatné, čo replay obsahuje, sa uchová celé vedľa nich (pravidlo konvertorov 3DHeat): každý rámec a sieťová správa v `<match>.packets.parquet`, každá zmena vlastnosti entity v `<match>.entities.parquet`, každý záznam reťazcovej tabuľky v `<match>.strings.parquet`, započítané v `selfCheck.completeness` dokumentu zápasu. Pozície sú svetové jednotky Dota, tie isté, aké hlási herná game-state integration. Riadok skóre prihláseného hráča sa stane štatistikami relácie: zabitia, smrti, asistencie, posledné zásahy, odmietnutia, čistý zisk, GPM, XPM, poškodenie hrdinom, wardy a to, či zápas vyhral. Nová záplata Dota môže zmeniť entity replaye skôr, než gem nasleduje; replay, ktorý gem nedokáže prečítať až do konca, sa prevedie, až kam sa dá, a v súhrne sa označí `incomplete`.

Rovnaký modul slúži aj: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [osu! (replaye)](game-osu-replays.md), [Squad (replaye)](game-squad-demos.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Tanks (replaye)](game-wot-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `z` |
| Jednotky | svetové jednotky Dota (Hammer jednotky; mapa má asi 16400 naprieč) |
| Zrkadlené pre viewer | `y` |
| Mierka (`scale`: viewer pozície násobí týmto číslom) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat riadky otáča a mení mierku sám – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hraná online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Druh `replay`: číta len replaye a dema, ktoré hra uloží; takže zaznamenáva aj online hru, aj offline; príznak rozhoduje len o tom, či sa smie čítať pamäť.
- Pamäť: tento adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online – pozrite [Pravidlá a zdroje](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Štatistické kľúče, ktoré kód tohto adaptéra nastavuje podľa názvu (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Kľúč v zložených zátvorkách sa doplní až za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z vlastných názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich uvádza.

## Úplnosť {#completeness}

Konvertor sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: čo replay obsahuje, sa prečíta alebo uchová, nikdy sa nezahodí. Okrem tabuľky sa všetko ostatné, čo replay obsahuje, uchová celé vo sprievodných súboroch vedľa nej, v priečinku `dota/` relácie – `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (stĺpce `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, podľa toho, čo sa uplatní) – a `selfCheck.completeness` dokumentu zápasu (`<match>.match.json`) počíta každý `type` – `lost` je 0.

**Prečítané**

- tabuľka (`dota/<match>.parquet`): pozícia, výška, zdravie, úroveň, smer, mana, skúsenosti, atribúty, brnenie, rýchlosť, poškodenie, predmety a kurzor hráča každého hrdinu 7,5-krát za sekundu; zabitia, smrti, ciele, wardy, záznamy bojového protokolu o hrdinoch; mapové pingy (`ping`, DOTA_UM_LocationPing), kresby na mape (`map_line`, DOTA_UM_MapLine) a každý príkaz jednotke (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` typ príkazu, `value` id schopnosti alebo predmetu, `text` trieda cieľa; v bode príkazu, inak pri hrdinovi)
- `<match>.units.parquet`: každá iná jednotka raz za sekundu; `<match>.combatlog.parquet`: celý bojový protokol tak, ako ho číta gem, každé pole
- dokument zápasu: všetko, čo gem vytiahne, a celé záznamy replaye od samotnej hry – `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: dĺžka prehrávania, meno každého hráča, hrdina, Steam id, tím), `matchDetails` (DOTA_UM_MatchDetails: koncové skóre zápasu z herného koordinátora, čísla každého hráča, predmety, poškodenie podľa typu, výbery a zákazy) a `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: zabitia, smrti, asistencie, úroveň, posledné zásahy a odmietnutia, ako sa čítajú z prúdu, oproti `matchDetails`, pre každého hráča

**Uchované surové**

- `<match>.packets.parquet`: každý rámec, ktorý nie je paketom (`type` `frame <n>`), a každá sieťová správa (`message <n>`, `name` podľa Valve), celá v `payload`, v poradí v súbore (`seq`, `frame`), s `decoded` ako protobuf v JSON (bajtové pole ako svoja dĺžka); dekódovaný každý typ správy: svc_PacketEntities (prúd entít), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, správy bojového protokolu, GE_SosStartSoundEvent, DOTA_UM_TE_\* (strely, animácie, krv), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; medzi nimi sú tabuľky odoslania, zoznam tried a informácie o serveri, ktoré neskorší dekodér entít potrebuje
- `<match>.entities.parquet`: každá vlastnosť každej entity zakaždým, keď sa zmenila (`type` vlastnosť, `name` trieda, `entity` jej index; `value`, `vector` alebo `decoded`), jej celý stav pri vytvorení a každé vytvorenie, vstup, odchod a zmazanie – pre celý zápas milióny riadkov
- `<match>.strings.parquet`: každý záznam reťazcovej tabuľky z každej aktualizácie a každého úplného snímku, hodnota celá; `userinfo`, `ActiveModifiers` a `EconItems` dekódované z ich protobufov
- `selfCheck.completeness` v dokumente zápasu počíta rámce a správy podľa názvu Valve, záznamy bojového protokolu (`combatlog <type>`), herné udalosti (`gameevent <name>`), záznamy reťazcovej tabuľky (`stringtable <name>`) a aktualizácie entít (`entity <class>`); niektoré sú uchované len surovo (úplné snímky entít, ktoré gem preskočí, lebo obnovuje z delt, a záznamy tabuliek, ktorých hodnoty nič nečíta), strata 0

**Nie je k dispozícii**

- hlasová komunikácia: replay má nastavenie hlasu, ale nie hlasové dáta
- názvy skryté za hashmi a id: zvuky a častice majú názvy z hashov súborov hry, schopnosti z id; replay názvy nenesie (predmety sa pomenúvajú podľa katalógu gem, kde ho má)
- čokoľvek, čo poznali len klienti hráčov (ich kamera, ich obrazovka) nad rámec toho, čo vysielal server; kurzor a každý príkaz sú v tom zahrnuté

**Veľkosť**: sprievodné súbory spolu sú o niečo väčšie ako samotný replay, najväčšie sú pakety a entity; celý zápas trvá jednu alebo dve minúty v jednom procese

## Overené {#verified}

overené na replaye verejného zápasu: zabitia, smrti, asistencie, úroveň, posledné zásahy a odmietnutia sa zhodujú s koncovým záznamom hry pre všetkých desiatich hráčov; každá správa v sprievodnom súbore paketov sa znovu serializuje bajt po bajte; tabuľka a štatistiky testované na syntetických dátach

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
