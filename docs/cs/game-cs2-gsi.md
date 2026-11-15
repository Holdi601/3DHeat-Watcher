---
title: "Counter-Strike 2 (stav hry)"
nav_order: 9
lang: "cs"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (stav hry) {#counter-strike-2-game-state}

Když hrajete Counter-Strike 2, Watcher ukládá to, co hra hlásí programům na vašem počítači, abyste se na to mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `cs2-gsi`, druh [`gsi`](sources-and-rules.md); běží, dokud běží `cs2.exe`, a hledá nová data každých 0,05 s.*

## Co se zaznamenává {#what-is-recorded}

- vlastní pozice (světové XYZ, palce) a směr pohledu až 10krát za sekundu, dokud žijete
- oživení (první spatření v každém kole, znovuoživení) a smrti (zdraví na 0, nebo počet smrtí)
- zabití s aktivní zbraní, ze statistik zápasu
- kola (začátek, konec, vítěz), bomba položena, zneškodněna nebo vybuchla, fáze zápasu a výsledek
- zabití, asistence, smrti, MVP, skóre, peníze, poškození, zabití headshotem, vyhraná a prohraná kola

## Odkud to pochází {#where-it-comes-from}

Game State Integration: HTTP POSTy na 127.0.0.1:3311, nastavené souborem &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Jak to zapnout {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, potom spusťte CS2 (soubor načítá při startu)

Příkaz napište do terminálu otevřeného ve složce Watcheru (viz [Než začnete](before-you-start.md)). Pokud selže, poslední řádek vysvětlí proč; [Instalace a spuštění](installing-and-running.md) popisuje obvyklé příčiny.

`python -m heat3d_watch setup cs2-gsi` vypíše soubory, které by změnil; `python -m heat3d_watch setup cs2-gsi --apply` je změní a původní soubor ponechá jako `<file>.heat3d-backup` (viz [Příkazy](commands.md#setup)). Pro každou změnu vypíše `cs2-gsi: changed: ...`, nebo `cs2-gsi: nothing to change`, když je to už zapnuté.

Nastavení z proměnných prostředí:

- `HEAT3D_CS2_GSI_PORT`: port, na který hra posílá (výchozí 3311); soubor cfg ve hře musí uvádět stejný port

## Jak to funguje {#how-it-works}

Valve Game State Integration: Counter-Strike 2 a Dota 2 říkají místnímu webovému serveru, co se děje.

Obě hry při startu načtou každý soubor `gamestate_integration_*.cfg` ve své složce cfg a od té chvíle při každé změně stavu pošlou JSON dokument na `uri` daného souboru (nejvýše každých `throttle` sekund a každých `heartbeat` sekund, když se nic nemění). Watcher je tím webovým serverem: poslouchá jen na 127.0.0.1, na každý POST hned odpoví 200 a práci dělá ve svém vlastním vlákně.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Co hráč dostane, a tedy co se dá zaznamenat, určuje hra podle toho, co hráči smí vidět:

- CS2: `provider` (vlastní steamid), `map` (název, režim, fáze warmup/live/intermission/gameover, kolo, skóre team_ct/team_t), `round` (fáze freezetime/live/over, bomba položena/vybuchla/zneškodněna, win_team), `player` (sledovaný hráč: vy, dokud žijete, spoluhráč po smrti) s `state` (zdraví, vesta, peníze, round_kills, round_killhs, round_totaldmg), `match_stats` (zabití, asistence, smrti, mvps, skóre), `position` a `forward` jako řetězce „x, y, z“ ve světových jednotkách (palce, Z nahoru), `weapons`; `bomb` jen pro diváky. Pozice ostatních hráčů (`allplayers_*`) se posílají jen divákům a GOTV, proto se o ně nežádá.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos ve světových jednotkách, level, alive, respawn_seconds), `buildings` (zdraví každé věže, kasárny a ancient), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Výška se nesleduje: z je 0. Žádají se také a uchovávají celé: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (hra posílá to, co má klient daného hráče; které z nich něco obsahují během hraní, a ne při sledování, se neověřilo).

Každý dokument se také uchovává celý (pravidlo převodníků 3DHeat, docs/converters.md v repozitáři prohlížeče): `heat.raw.parquet`, `type` „gsi“, `text` je JSON tak, jak byl poslán – jen token ze souboru cfg je vymazaný, je to tajemství Watcheru, ne herní data. Dokumenty poslané, když není otevřený žádný zápas (menu, načítání, mezi zápasy), čekají ve `Backlog` a jdou do relace dalšího zápasu, před jeho začátkem; co zbude, když se hra zavře, dostane vlastní relaci, která obsahuje jen ně. Nečitelné posty a posty se špatným tokenem se také uchovají („gsi-unreadable“, „gsi-bad-auth“).

Zdroje: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(formát, který CS2 zachovalo), <https://github.com/antonpup/CounterStrike2GSI> a
<https://github.com/antonpup/Dota2GSI> (seznamy polí; licence MIT, čteno jen kvůli faktům).

Stejný modul slouží také: [Dota 2 (stav hry)](game-dota2-gsi.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `z` |
| Jednotky | palce (jednotky Hammeru) |
| Zrcadleno pro prohlížeč | `y` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, když relace má pozice, do patičky `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítkuje řádky sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukáže jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `gsi`: čte jen to, co hra nebo platforma vydává (game-state integration nebo místní API, které hra poskytuje), takže nahrává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda se smí číst paměť.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle jména (každé relace `stats` v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč na každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedené jménem.

## Úplnost {#completeness}

Watcher dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se načte nebo uchová, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér dostane, uchovává celý v `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uchovaná podle jména; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- sledovaný hráč: pozice, směr pohledu, zdraví, vesta, peníze, aktivní zbraň, helma, sada na zneškodnění, množství záblesku/kouře/ohně a hodnota výbavy, u každého řádku pozice, když je to vlastní hráč (steamid poskytovatele = steamid hráče)
- oživení, smrti (zdraví na 0, nebo počet smrtí ze statistik zápasu), zabití (počet zabití roste)
- fáze zápasu, kola (freeze time, live, over, vítěz), bomba položena/zneškodněna/vybuchla, výsledek
- zabití, asistence, smrti, MVP, skóre, peníze, poškození, zabití headshotem, vyhraná a prohraná kola jako statistiky

**Uchováno surové**

- `gsi`: každý dokument, který hra pošle, celý, tak jak byl poslán (`text`), `used` true, když byl načten v zápase – provider (verze, časové razítko), map (režim, názvy týmů, po sobě jdoucí prohry kol, timeouty, výhry v sérii, `round_wins` s podmínkou výhry každého kola), round, sledovaný hráč (klan, slot diváka, aktivita, každá zbraň se skinem, municí a zásobou), bomb, odpočty fází a vlastní rozdíl hry `previously`/`added` proti předchozímu postu
- dokumenty z menu, načítání a mezi zápasy: uchovávají se stejně, v čase, kdy přišly, před začátkem dalšího zápasu; po posledním zápase v relaci vlastní (`raw_only` v meta.json)
- `gsi-unreadable`: post, který není JSON objekt, jeho bajty jako `payload` a `length`
- `gsi-bad-auth`: post s jiným tokenem, než má soubor cfg

**Nedostupné**

- další hráči (`allplayers_*`) a granáty (`allgrenades`): hra je posílá jen divákům a GOTV a Watcher o ně nežádá (viz Zdroje a pravidla); demo má všechny hráče – viz [Counter-Strike 2 (replaye)](game-cs2-demos.md)
- stavy mezi posty: hra posílá nejvýše každých 0,1 s (`throttle`) a jen při změně, jinak každých 10 s (`heartbeat`)
- token ze souboru cfg, vymazaný v každém uchovaném dokumentu: tajemství Watcheru, ne herní data
- posty nad 10 000 čekajících (Watcher se zasekl) se počítají jako `dropped_packets` a neuchovají se; post nad 4 MB se uchová jako `gsi-unreadable` s délkou, ale bez bajtů

**Velikost**: dokument jednoho hráče má 2–4 KB a posílá se až 10krát za sekundu, když se něco mění: asi 30–150 MB za hodinu v `raw.bin` během zápasu, desetina nebo méně v zstd `heat.raw.parquet` (odhad podle zveřejněného formátu, neměřeno na hře)

## Ověřeno {#verified}

testováno na dokumentech ve zveřejněném formátu GSI poslaných běžícímu adaptéru; instalace a vyhledání složky cfg otestované na místní instalaci; neotestováno proti běžící hře

## Zdroj {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
