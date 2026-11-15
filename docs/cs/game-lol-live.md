---
title: "League of Legends (stav hry)"
nav_order: 29
lang: "cs"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (stav hry) {#league-of-legends-game-state}

Když hrajete League of Legends, Watcher uloží, co hra hlásí programům na vašem počítači, abyste se na to mohli později podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `lol-live`, druh [`gsi`](sources-and-rules.md); běží, dokud běží `League of Legends.exe`, a hledá nová data každých 0,5 s.*

## Co se zaznamenává {#what-is-recorded}

- žádné pozice: rozhraní API je nemá
- zápis zabití: zabití, smrti a asistence hráče, zabití ostatních šampionů s vrahem, obětí a asistujícími
- draci, heroldové, baroni, věže, inhibitory, vícenásobná zabití, esa, první krev, začátek a konec hry
- vlastní zabití, smrti, asistence, skóre creepů, skóre wardů, úroveň, zlato, šampion, herní čas, výsledek
- cíle, které vzal tým hráče

## Odkud to pochází {#where-it-comes-from}

Live Client Data API herního klienta, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), během zápasu

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

League of Legends: Live Client Data API, které herní klient poskytuje během zápasu.

Zatímco zápas běží (i v tréninkovém nástroji a ve sledování), `League of
Legends.exe` odpovídá na <https://127.0.0.1:2999> tím, co hráč vidí
v samotném rozhraní hry:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} od EventID N dál: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Žádné pozice nejsou: API je nemá, takže relace League jsou události a statistiky bez
tabulky pro teplotní mapu. Certifikát je self-signed, od kořenového certifikátu Riotu
(`riotgames.pem`, zveřejněný na
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Podmínky jeho
použití nejsou uvedeny, proto se nedodává: uložte ho do `<data>\riotgames.pem` a
spojení se ověří jím; bez něj je ověřování vypnuté - a jen
pro 127.0.0.1, jedinou adresu, se kterou tento adaptér mluví.

Pravidla Riotu povolují nástrojům zobrazovat to, co hráč může vědět z
samotné hry, a nic vypočítaného nad to (žádné časovače nepřátel): zde se zaznamenává
zápis zabití a skóre, které hráč vidí, a vlastní čísla hráče.

Každá odpověď se ukládá také celá (pravidlo převodníků 3DHeat, docs/converters.md v
repozitáři prohlížeče): `heat.raw.parquet`, `type` je endpoint
(„allgamedata“, „eventdata“), `text` je JSON, jak ho klient poslal, `status`
tam, kde nebyl 200. Odpověď, která je bajt po bajtu stejná jako předchozí odpověď
svého endpointu (seznam událostí, když se nic neděje), se uloží jednou a počítá se v
`unchanged_replies` v meta.json. allgamedata obsahuje vše, co ostatní endpointy
podávají (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells,
playermainrunes, gamestats), proto se ostatní nedotazují zvlášť. Odpovědi před
zápasem (načítací obrazovka) čekají v zásobníku a přejdou do relace zápasu;
po GameEnd relace zůstane otevřená, dokud klient neskončí, takže odpovědi z
obrazovky konce se uloží s ní.

Zdroj: <https://developer.riotgames.com/docs/lol#game-client-api>

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ne |
| Osa nahoru | `z` |
| Jednotky | žádné (bez pozic) |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapíší do `meta.json` (`axes`) každé relace a, pokud relace obsahuje pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků upravuje sám - viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `gsi`: čte jen to, co hra nebo platforma vydává (integraci stavu hry nebo místní API, které hra poskytuje), takže zaznamenává i v online hře i offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory`, a nikdy u hry označené jako hraná online - viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- zápis zabití z eventdata: každá událost jednou, její pojmenovaná pole dekódovaná (vrah, oběť a asistující s šampionem a týmem, budovy a jejich strana, typ draka, ukradení, vícenásobná zabití, esa, první krev, výsledek) a každé další pole události na jejím řádku pod svým vlastním názvem
- z allgamedata: vlastní zabití, smrti, asistence, skóre creepů, skóre wardů, úroveň, zlato, šampion, herní čas, herní režim a mapa

**Uchováno surové**

- `allgamedata`: každá odpověď celá (`text`), každé 2 s - activePlayer (schopnosti, každá statistika šampiona, celé runy, zlato, úroveň), allPlayers (předměty s sloty a cenami, runy, letecké kouzlo, skóre, úroveň, mrtvý a časovač oživení, skin, lane, bot), události, gameData (režim, čas, mapa, terén); `used` je pravda, dokud zápas běží, nepravda na obrazovce konce
- `eventdata`: každá odpověď celá, dotazováno každých 0,5 s od dalšího ID události; `used` je pravda, když přinesla nové události
- odpověď, která je bajt po bajtu stejná jako předchozí odpověď svého endpointu, se uloží jednou a počítá se (`unchanged_replies` v meta.json); chybové odpovědi (RESOURCE_NOT_FOUND z načítací obrazovky) se ukládají se svým `status`, před začátkem zápasu

**Nedostupné**

- pozice: API je nemá (žádná minimapa, žádné souřadnice)
- ostatní endpointy (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): každý podává část allgamedata, takže se nedotazují
- Replay API (`/replay/*` na stejném portu): přehrává replaye a sledované hry, když je v game.cfg zapnuto; není součástí hraného zápasu
- koncové body lockfile klienta League: není zveřejněné API (Zdroje a pravidla)
- hodnoty mezi dvěma čteními: API odpovídá, když se ho zeptáte, a nic nevysílá; skóre se dotazuje každé 2 s, události každých 0,5 s

**Velikost**: allgamedata má 15-40 KB (obsahuje celý seznam událostí, který roste) každé 2 s: asi 30-70 MB za hodinu v `raw.bin`; eventdata přidá málo, protože neměnné odpovědi se počítají, neukládají se; zstd zmenší opakující se JSON v `heat.raw.parquet` na několik MB za hodinu (odhad z dokumentovaného formátu)

## Ověřeno {#verified}

testováno proti falešnému místnímu serveru, který vrací odpovědi ve zdokumentovaném formátu; zatím neotestováno ve hře

## Zdroj {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
