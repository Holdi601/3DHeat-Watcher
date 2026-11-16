---
title: "League of Legends (replaye)"
nav_order: 30
lang: "sk"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (replaye) {#league-of-legends-replays}

Po zápase League of Legends watcher prevedie replay, ktorý hra uložila, do súborov, ktoré si môžete pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `lol-replays`, typ [`replay`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- šampión každého hráča, rola, tím, zabitia, smrti, asistencie, zlato, poškodenie šampiónov a výsledok, a každé ďalšie číslo z tabuľky výsledkov na konci hry
- váš vlastný riadok ako štatistiky a vaše riadky označené ako vaše (`player` v meta.json), s vaším Riot ID v nastaveniach
- s vaším vlastným kľúčom Riot API: pozícia každého hráča každú minútu so štatistikami danej minúty a každá udalosť časovej osi (zabitia tam, kde sa stali, budovy, monštrá, strážne, predmety, schopnosti) v čase hodín, ktorý dáva časová os
- každá časť súboru replay celá v heat.raw.parquet; nedekódované: dianie hry od okamihu k okamihu, ktoré je zašifrované a zamaskované proti podvádzaniu

## Odkiaľ to berie {#where-it-comes-from}

replaye, ktoré ukladá klient League: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (len obyčajné metadáta z konca hry); s vaším vlastným kľúčom Riot API oficiálna časová os zápasu z Riot Match-V5 API

## Ako to zapnúť {#how-to-switch-it-on}

uložte replay v klientovi League (história zápasov > stiahnuť); pre polohy nastavte riot_api_key a riot_platform príkazom `config --set`

## Ako to funguje {#how-it-works}

Replaye League of Legends a VALORANT: čo sa z nich dá prečítať tak, ako sú.

Obe hry ukladajú replaye na disk hráča a obe chránia to, čo je vo vnútri: dáta hry od okamihu k okamihu sú zamaskované a pri každej záplate inak, aby sa nedali použiť na podvádzanie. Táto časť sa nikde v 3DHeat nedekóduje. Čo každý súbor nesie otvorene, sa načíta, a zvyšok sa uchová tak, ako je: každá časť súboru celá v `heat.raw.parquet` relácie (pravidlo konvertorov 3DHeat, docs/converters.md v repozitári prehliadača), počítaná v `selfCheck.completeness` v meta.json.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Obe verzie kontajnera nesú tabuľku výsledkov na konci hry ako obyčajný JSON (`statsJson`): pre každého z desiatich hráčov šampióna, zabitia, smrti, asistencie, zlato, poškodenie šampiónov, predmety, tím, rolu, výhru, ich Riot ID a každé ďalšie číslo, ktoré hra sčíta (viac ako sto na hráča); všetky sa stanú riadkom `player_result` hráča. ROFL1 (záplata 14.9 a staršie) ho má za pevnou hlavičkou (`RIOT\0\0`, 256-bajtový podpis, potom dĺžky); ROFL2 (14.11 a novšie, `RIOT\2\0`) na konci súboru, jeho dĺžka v posledných štyroch bajtoch (uvádza inžinier Riotu, ReplayBook issue 299). Hlavička užitočného obsahu ROFL1 (ID hry, dĺžka, počty blokov a kľúčových snímok, dĺžka kľúča bloku) a jeho tabuľka blokov (ID, typ, dĺžka, ďalší blok, posun) sú otvorené a čítajú sa; samotné bloky sú zašifrované a uchované celé, nečítané. Rozloženia z roflxd.cs (MIT).

Polohy nepochádzajú zo súboru. S vlastným vývojárskym kľúčom Riot hráča (`riot_api_key` v nastaveniach; osobný kľúč je určený presne na toto, „zobrazovanie (vlastných) štatistík hráča") sa oficiálna časová os zápasu sťahuje z Riot Match-V5 API: pozícia každého hráča raz za minútu so všetkým, čo rámec danej minúty o ňom hovorí (zlato, skúsenosti, úroveň, minióni, štatistiky šampióna a poškodenia), a každá udalosť časovej osi - zabitia, budovy, elitné monštrá, strážne, predmety, schopnosti, úrovne - každá ako riadok, tam, kde sa stala, ak má miesto. Bez kľúča sa nič nesťahuje a nič sa neposiela.

Ten istý modul slúži aj: [VALORANT (replaye)](game-valorant-replays.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Osa nahor | `y` |
| Jednotky | jednotky mapy Summoner's Rift (okolo 15000 napríč) |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)".
- Druh `replay`: číta len to, čo hra alebo platforma sprístupňuje (replaye a dema, ktoré hra uloží), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- metadáta v JSON: dĺžka hry, verzia, ID posledného bloku a kľúčovej snímky, a `statsJson` - každé pole tabuľky výsledkov každého hráča na jeho riadku `player_result` (čísla zapísané ako text sa čítajú ako čísla)
- ROFL1: blok dĺžok, hlavička užitočného obsahu (ID hry, dĺžka hry, počty kľúčových snímok a blokov, ID blokov štartu a začiatku hry, interval kľúčových snímok, kľúč bloku tak, ako je uložený) a tabuľka blokov (ID, typ, dĺžka, ďalší blok, posun) - v meta.json `rofl` a v `text` surových riadkov
- ROFL2: reťazec verzie
- časová os Match-V5 (len s vlastným kľúčom API): každý rámec účastníka na riadku `position` (alebo `participant_frame` bez miesta) so všetkými jeho poľami rozloženými na úroveň (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); každá udalosť ako riadok pomenovaný podľa typu, umiestnený tam, kde má `position`, CHAMPION_KILL ako zabitie a smrť

**Uchované surové**

- každá časť .rofl celá, v poradí v súbore (`offset`), takže časti sú súbor: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); každý úsek, ktorý nepokrýva žiadna časť, ako `unknown`
- časová os celá: `timeline <type>` pre každú udalosť, `timeline participantFrame` pre rámec každého hráča (`participant` je jeho ID), `timeline` pre zvyšok

**Nie je k dispozícii**

- samotná hra (polohy, schopnosti, každá jednotka, dianie od okamihu k okamihu): bloky ROFL1 a telo ROFL2 sú zašifrované a pakety vnútri sú zamaskované pri každej záplate. Uchované celé, nečítané
- polohy bez vášho vlastného kľúča Riot API: súbor ich otvorene nemá

**Veľkosť**: surový sprievodný súbor má približne veľkosť samotného replaye: zašifrované bloky sa nedajú skomprimovať

## Overené {#verified}

čítačka metadát overená na súboroch zostavených podľa rozložení z roflxd.cs (MIT); časová os podľa zdokumentovaného JSON Match-V5; žiadny skutočný replay nebol k dispozícii na porovnanie

## Zdroj {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
