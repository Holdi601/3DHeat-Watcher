---
title: "Counter-Strike 2 (herný stav)"
nav_order: 9
lang: "sk"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (herný stav) {#counter-strike-2-game-state}

Keď hráte Counter-Strike 2, watcher ukladá to, čo hra hlási programom vo vašom počítači, aby ste si to neskôr mohli pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `cs2-gsi`, druh [`gsi`](sources-and-rules.md); beží, kým beží `cs2.exe`, a hľadá nové dáta každých 0,05 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- vlastná pozícia (svetové XYZ, palce) a smer pohľadu až 10-krát za sekundu, kým žijete
- oživenia (prvé zistenie v každom kole, znovuoživenia) a smrti (zdravie na 0, alebo počet smrtí)
- zabitia s aktívnou zbraňou zo štatistík zápasu
- kolá (začiatok, koniec, víťaz), bomba položená, zneškodnená alebo vybuchnutá, fázy zápasu a výsledok
- zabitia, asistencie, smrti, MVP, skóre, peniaze, poškodenie, zabitia hlavou, vyhrané a prehrané kolá

## Odkiaľ to pochádza {#where-it-comes-from}

Game State Integration: HTTP POST na 127.0.0.1:3311, nastavené v &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Ako to zapnúť {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, potom spustite CS2 (hra súbor číta pri štarte)

Príkaz zadajte v termináli otvorenom v priečinku watchera (pozrite [Pred začiatkom](before-you-start.md)). Ak zlyhá, posledný riadok povie prečo; [Inštalácia a spustenie](installing-and-running.md) popisuje najčastejšie príčiny.

`python -m heat3d_watch setup cs2-gsi` vypíše, ktoré súbory by zmenil; `python -m heat3d_watch setup cs2-gsi --apply` ich zmení a pôvodný súbor uloží ako `<file>.heat3d-backup` (pozrite [Príkazy](commands.md#setup)). Pre každú zmenu vypíše `cs2-gsi: changed: ...`, alebo `cs2-gsi: nothing to change`, keď je to už zapnuté.

Nastavenia z premenných prostredia:

- `HEAT3D_CS2_GSI_PORT`: port, na ktorý hra posiela (predvolene 3311); cfg súbor hry musí uvádzať ten istý port

## Ako to funguje {#how-it-works}

Valve Game State Integration: Counter-Strike 2 a Dota 2 hlásia, čo sa deje, lokálnemu webovému serveru.

Obe hry pri štarte prečítajú každý súbor `gamestate_integration_*.cfg` vo svojom priečinku cfg a odvtedy pošlú dokument JSON na `uri` každého súboru vždy, keď sa stav zmení (najviac každých `throttle` sekúnd a každých `heartbeat` sekúnd, keď sa nič nemení). Watcher je tento webový server: počúva len na 127.0.0.1, na každý POST hneď odpovie 200 a prácu robí vo svojom vlastnom vlákne.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Čo sa hráčovi pošle – a teda čo sa dá zaznamenať – rozhoduje hra, čo hráč smie vidieť:

- CS2: `provider` (vlastné steamid), `map` (názov, režim, fáza warmup/live/intermission/gameover, kolo, skóre team_ct/team_t), `round` (fáza freezetime/live/over, bomba planted/exploded/defused, win_team), `player` (hráč, ktorého *sledujete*: seba, kým žijete, spoluhráča po smrti) s `state` (zdravie, vesta, peniaze, round_kills, round_killhs, round_totaldmg), `match_stats` (kills, assists, deaths, mvps, score), `position` a `forward` ako reťazce „x, y, z“ vo svetových jednotkách (palce, Z smeruje nahor), `weapons`; `bomb` len pre divákov. Pozície ostatných hráčov (`allplayers_*`) sa posielajú len divákom a GOTV, preto sa nevyžadujú.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos vo svetových jednotkách, level, alive, respawn_seconds), `buildings` (zdravie každej veže, kasární a ancient), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Výšku nemá: z je 0. Vyžiadané a uchované celé sú aj `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (hra posiela to, čo má klient hráča; či niečo z toho obsahuje počas hry, a nie počas sledovania, nie je overené).

Každý dokument sa uchová aj celý (pravidlo konvertorov 3DHeat, docs/converters.md v repozitári vieweru): `heat.raw.parquet`, `type` "gsi", `text` je JSON tak, ako bol poslaný – iba token z cfg súboru je vymazaný, lebo je to tajomstvo watchera, nie herné dáta. Dokumenty poslané, keď nie je otvorený žiadny zápas (menu, načítavanie, medzi zápasmi), čakajú v `Backlog` a idú do relácie ďalšieho zápasu, pred jeho začiatkom; čo zostane, keď sa hra zavrie, dostane vlastnú reláciu, ktorá obsahuje len ich. Nečitateľné posty a posty so zlým tokenom sa tiež uchovajú ("gsi-unreadable", "gsi-bad-auth").

Zdroje: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (formát, ktorý CS2 zachovalo), <https://github.com/antonpup/CounterStrike2GSI> a <https://github.com/antonpup/Dota2GSI> (zoznamy polí; MIT, čítané len kvôli faktom).

Rovnaký modul slúži aj: [Dota 2 (herný stav)](game-dota2-gsi.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `z` |
| Jednotky | palce (Hammer jednotky) |
| Zrkadlené pre viewer | `y` |
| Mierka (`scale`: viewer pozície násobí týmto číslom) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat riadky otáča a mení mierku sám – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hraná online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Druh `gsi`: číta len to, čo hra alebo platforma vydáva (game-state integration alebo lokálne API, ktoré hra poskytuje), takže zaznamenáva aj online hru, aj offline; príznak rozhoduje len o tom, či sa smie čítať pamäť.
- Pamäť: tento adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online – pozrite [Pravidlá a zdroje](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Štatistické kľúče, ktoré kód tohto adaptéra nastavuje podľa názvu (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Kľúč v zložených zátvorkách sa doplní až za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z vlastných názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich uvádza.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: čo zdroj obsahuje, sa prečíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celý v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a potom každé pole, ktoré sa podľa názvu ponechalo; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Prečítané**

- pozícia, smer pohľadu, zdravie, vesta, peniaze, aktívna zbraň, prilba, sada na zneškodnenie, hodnoty dymu/záblesku/ohňa a hodnota výstroja hráča, ktorého sledujete, na každom riadku pozície, kým ide o vlastného hráča (steamid providera = steamid hráča)
- oživenia, smrti (zdravie na 0, alebo počet smrtí zo štatistík zápasu), zabitia (rast počtu zabití)
- fázy zápasu, kolá (čas na nákup, živé, ukončené, víťaz), bomba položená, zneškodnená, vybuchnutá, výsledok
- zabitia, asistencie, smrti, MVP, skóre, peniaze, poškodenie, zabitia hlavou, vyhrané a prehrané kolá ako štatistiky

**Uchované surové**

- `gsi`: každý dokument, ktorý hra pošle, celý, tak ako bol poslaný (`text`); `used` je pravda, keď sa čítal počas zápasu – provider (verzia, časová pečiatka), map (režim, názvy tímov, po sebe idúce prehry kola, časové odpočty, výhry v sérii, `round_wins` s podmienkou výhry každého kola), round, sledovaný hráč (klan, slot diváka, aktivita, každá zbraň so skinom, muníciou a zásobou), bomb, odpočty fáz a `previously`/`added` – rozdiel hry oproti predchádzajúcemu postu
- dokumenty z menu, načítavania a medzi zápasmi: uchované rovnako, v ich vlastnom čase pred začiatkom ďalšieho zápasu; po poslednom zápase v ich vlastnej relácii (`raw_only` v meta.json)
- `gsi-unreadable`: post, ktorý nie je objektom JSON, jeho bajty ako `payload` a `length`
- `gsi-bad-auth`: post s iným tokenom, než má cfg súbor

**Nie je k dispozícii**

- ostatní hráči (`allplayers_*`) a granáty (`allgrenades`): hra ich posiela len divákom a GOTV a watcher ich nevyžaduje (pozrite Pravidlá a zdroje); demo má všetkých hráčov – pozrite [Counter-Strike 2 (replaye)](game-cs2-demos.md)
- stavy medzi postami: hra posiela najviac každých 0,1 s (`throttle`) a len pri zmene, inak každých 10 s (`heartbeat`)
- token z cfg súboru, vymazaný v každom uchovanom dokumente: tajomstvo watchera, nie herné dáta
- posty nad 10 000 čakajúcich (watcher sa zasekol) sa počítajú ako `dropped_packets`, neuchovajú sa; post väčší ako 4 MB sa uchová ako `gsi-unreadable` s dĺžkou, ale bez bajtov

**Veľkosť**: dokument hráča má 2–4 KB a posiela sa až 10-krát za sekundu, keď sa niečo mení: asi 30–150 MB za hodinu v `raw.bin`, keď zápas beží, a desatina alebo menej v komprimovanom `heat.raw.parquet` (odhad podľa zverejneného formátu, nie meranie na hre)

## Overené {#verified}

testované na dokumentoch vo zverejnenom formáte GSI, odoslaných bežiacemu adaptéru; inštalácia a vyhľadanie priečinka cfg testované na lokálnej inštalácii; netestované s bežiacou hrou

## Zdroj {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
