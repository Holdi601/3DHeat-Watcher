---
title: "League of Legends (herný stav)"
nav_order: 29
lang: "sk"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (herný stav) {#league-of-legends-game-state}

Počas hry League of Legends watcher ukladá to, čo hra hlási programom na vašom počítači, aby ste sa na to neskôr mohli pozrieť ako na štatistiky a časovú os.

*Technické údaje: adaptér `lol-live`, typ [`gsi`](sources-and-rules.md); beží, kým beží `League of Legends.exe`, a hľadá nové dáta každých 0,5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- žiadne polohy: API ich nemá
- zoznam udalostí o zabitiach: zabitia, smrti a asistencie hráča, zabitia iných šampiónov s vrahom, obeťou, asistujúcimi
- draci, heraldi, baróni, veže, inhibítory, multikily, esá, prvá krv, začiatok a koniec hry
- vlastné zabitia, smrti, asistencie, skóre creepov, skóre wardov, úroveň, zlato, šampión, herný čas, výsledok
- ciele, ktoré získal tím hráča

## Odkiaľ to berie {#where-it-comes-from}

Live Client Data API klienta hry, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), počas zápasu

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

League of Legends: Live Client Data API, ktoré klient hry počas zápasu poskytuje.

Počas zápasu (aj v tréningovom nástroji a v režime diváka) `League of
Legends.exe` odpovedá na <https://127.0.0.1:2999> tým, čo hráč vidí v
rozhraní hry:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} od EventID N ďalej: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Žiadne polohy nie sú: API ich nemá, takže relácia z League je udalosti a štatistiky, bez tabuľky polôh. Certifikát je self-signed od koreňového certifikátu samotného Riotu (`riotgames.pem`, zverejnený na
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Podmienky jeho použitia nie sú uvedené, preto sa nedodáva: uložte ho do `<data>\riotgames.pem` a spojenie sa overí oním; bez neho sa overovanie vypne – a to len pre 127.0.0.1, jedinú adresu, s ktorou tento adaptér hovorí.

Pravidlá Riotu dovoľujú nástrojom zobrazovať to, čo hráč vie z hry samotnej, a nič vypočítané nad to (žiadne časovače nepriateľov): toto zaznamenáva zoznam udalostí a tabuľku skóre, ktorú vidí hráč, a vlastné čísla hráča.

Každá odpoveď sa uchová aj celá (pravidlo konvertorov 3DHeat, docs/converters.md v repozitári prehliadača): `heat.raw.parquet`, `type` je koncový bod („allgamedata“, „eventdata“), `text` je JSON tak, ako ho klient poslal, `status`, keď nebolo 200. Odpoveď bajt po bajte rovnaká ako predchádzajúca toho istého koncového bodu (zoznam udalostí, kým sa nič nedeje) sa uchová raz a počíta sa v `unchanged_replies` v meta.json. allgamedata obsahuje všetko, čo ostatné koncové body ponúkajú (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), takže sa tieto nepýtajú osobitne. Odpovede pred zápasom (obrazovka načítania) čakajú v zásobníku a idú do relácie zápasu; po GameEnd relácia zostane otvorená, kým klient neskončí, takže odpovede koncovej obrazovky sa uchovajú s ňou.

Zdroj: <https://developer.riotgames.com/docs/lol#game-client-api>

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | nie |
| Os nahor | `z` |
| Jednotky | žiadne (žiadne polohy) |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Typ `gsi`: číta len to, čo hra alebo platforma vydáva (integrácia herného stavu alebo lokálne API, ktoré hra poskytuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- zoznam udalostí o zabitiach z eventdata: každá udalosť raz, jej pomenované polia dekódované (vrah, obeť a asistujúci s šampiónom a tímom, stavby a ich strana, typ draka, ukradnutie, multikily, esá, prvá krv, výsledok) a každé iné pole udalosti na jej riadku pod vlastným menom
- z allgamedata: vlastné zabitia, smrti, asistencie, skóre creepov, skóre wardov, úroveň, zlato, šampión, herný čas, herný režim a mapa

**Uchované surové**

- `allgamedata`: každá odpoveď celá (`text`), každé 2 s – activePlayer (schopnosti, každá štatistika šampióna, úplné runy, zlato, úroveň), allPlayers (predmety so slotmi a cenami, runy, zaklínadlá prizývateľa, skóre, úroveň, mŕtvy a čas do oživenia, skin, líniu, bot), udalosti, gameData (režim, čas, mapa, terén); `used` je pravda, kým zápas beží, nepravda na koncovej obrazovke
- `eventdata`: každá odpoveď celá, pýtané každých 0,5 s od ďalšieho ID udalosti; `used` je pravda, keď priniesla nové udalosti
- odpoveď bajt po bajte rovnaká ako predchádzajúca toho istého koncového bodu sa uchová raz a počíta sa (`unchanged_replies` v meta.json); chybové odpovede (RESOURCE_NOT_FOUND na obrazovke načítania) sa uchovajú s ich `status`, pred začiatkom zápasu

**Nedostupné**

- polohy: API ich nemá (žiadna minimapa, žiadne súradnice)
- ostatné koncové body (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): každý poskytuje časť allgamedata, preto sa nepýtajú
- Replay API (`/replay/*` na tom istom porte): prehráva replaye a sledované hry, keď sa zapne v game.cfg; nie je súčasťou hranej hry
- koncové body lockfile klienta League: nie sú zdokumentované ako verejné API (Zdroje a pravidlá)
- hodnoty medzi dvoma čítaniami: API odpovedá, keď sa ho spýtate, a nič neposiela; tabuľka skóre sa pýta každé 2 s, udalosti každých 0,5 s

**Veľkosť**: allgamedata má 15 až 40 KB (nesie celý zoznam udalostí, ktorý rastie) každé 2 s: približne 30 až 70 MB za hodinu v `raw.bin`; eventdata pridá málo, lebo nezmenené odpovede sa počítajú, neukladajú; zstd zmenší opakujúci sa JSON v `heat.raw.parquet` na niekoľko MB za hodinu (odhad z dokumentovaného formátu)

## Overené {#verified}

testované proti falošnému lokálnemu serveru, ktorý podáva odpovede v zdokumentovanom formáte; neotestované proti hre

## Zdroj {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
