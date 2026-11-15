---
title: "EVE Online (logy)"
nav_order: 20
lang: "sk"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (logy) {#eve-online-log-files}

Počas hry EVE Online watcher číta súbory, ktoré hra zapisuje, a ukladá, čo sa stalo, aby ste sa na to neskôr mohli pozrieť ako na štatistiky a časovú os.

*Technické údaje: adaptér `eve`, typ [`log`](sources-and-rules.md); beží, kým beží `exefile.exe`, a hľadá nové dáta každých 0,5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- uštedrené a prijaté poškodenie voči inej lodi, pilotovi, tickeru korporácie, zbrani a kvalite zásahu
- netrafenia uštedrené a prijaté
- vyplatené odmeny (zabitia NPC) s ISK
- skoky medzi systémami
- každý riadok gamelogu a chatu celý v heat.raw.parquet
- uštedrené a prijaté poškodenie, zásahy, netrafenia, zabitia za odmenu a ISK, skoky

## Odkiaľ to berie {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt a Chatlogs\\\*.txt vedľa nich (každý súbor zapísaný od spustenia klienta)

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

EVE Online: herné logy klienta, `Documents\EVE\logs\Gamelogs\*.txt`.

Klient zapisuje jeden súbor na postavu a na prihlásenie,
`<yyyymmdd>_<hhmmss>[_<id postavy>].txt`; zápis do súboru je zapnutý predvolene. Ak beží viacero klientov naraz, každý zapisuje svoj súbor, takže sa sledujú všetky súbory zapísané od spustenia hry. Hlavička a riadky (čas EVE je UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(riadok combat je v súbore jeden riadok). Značky formátovania sa pred porovnávaním odstránia. Súbor bol v priebehu rokov UTF-8 aj UTF-16; čítajú sa oba.
Formát CCP nedokumentuje; je to obyčajný textový log klienta, čítaný tak, ako ho čítajú komunitné nástroje na boj (napr. <https://docs.rs/crate/eve-log-parser>).
Žiadne polohy.

Vedľa je `Documents\EVE\logs\Chatlogs\<kanál>_<yyyymmdd>_<hhmmss>[_<id>].txt`: jeden súbor na chatový kanál a na prihlásenie (keď je zapnuté logovanie chatu, čo je predvolené v klientovi), UTF-16, hlavička s názvom kanála a poslucháčom, potom `[ yyyy.mm.dd hh:mm:ss ] Odosielateľ > správa`.

Každý riadok oboch sa uchová celý v surovom sprievodnom súbore relácie (pravidlo konvertorov 3DHeat): riadok gamelogu pod svojím kanálom v hranatých zátvorkách (`combat`, `notify`, `bounty`, `None`, ...), riadok chatu ako `chat` s kanálom, hlavičkové riadky ako `gamelog header` / `chatlog header`.

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | nie |
| Os nahor | `y` |
| Jednotky | polohy sa nezaznamenávajú |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Typ `log`: číta len to, čo hra alebo platforma vydáva (súbory, ktoré hra zapisuje počas behu), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- gamelog `(combat)`: uštedrené a prijaté zásahy (množstvo, iný pilot, ticker korporácie, loď, zbraň, kvalita zásahu) a netrafenia oboma smermi
- gamelog `(bounty)`: vyplatenia s ISK a riadky `Jumping from A to B`
- `Listener` z hlavičky gamelogu: čí log to je

**Uchované surové**

- každý riadok gamelogu celý, `type` = jeho kanál v hranatých zátvorkách (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), s `file` a `listener`; `used` tam, kde sa stal riadkom; hlavičkové riadky ako `gamelog header`
- každý riadok chat logu celý (Local, korporácia, flotila, súkromné kanály, oznámenia `EVE System`, napr. zmena kanála Local pri skoku), `type` `chat`, s `channel`, `listener` a `file`; hlavičkové riadky ako `chatlog header`. Zatiaľ sa nepremieňajú na riadky
- značky formátovania (`<color>`, `<b>`, `<font>`) zostávajú v surovom texte; riadky ich majú odstránené

**Nedostupné**

- polohy: klient ich do svojich logov nezapisuje
- boje iných pilotov: gamelog je len vlastný log poslucháča
- logy skorších prihlásení: každé prihlásenie zapisuje nové súbory; tie staršie ako toto spustenie klienta sa znova nečítajú
- chat, keď hráč vypne logovanie chatu v nastaveniach klienta
- vyrovnávacia pamäť klienta a súbory nastavení: nie sú to logy a nie sú zdokumentované

**Veľkosť**: gamelog je 0,1 až 2 MB za hodinu (väčšinou v boji); chat logy závisia od otvorených kanálov – rušný Local alebo flotila 0,5 až 3 MB za hodinu; zstd v heat.raw.parquet ich zmenší zhruba na desatinu

## Overené {#verified}

testované na syntetických riadkoch gamelogu v formáte, ktorý zverejňujú komunitné parsery; neotestované proti hre

## Zdroj {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
