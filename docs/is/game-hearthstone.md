---
title: "Hearthstone (annálsskrár)"
nav_order: 25
lang: "is"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (annálsskrár) {#hearthstone-log-files}

Meðan þú spilar Hearthstone les watcher skrárnar sem leikurinn skrifar og vistar það sem gerðist, svo þú getir skoðað það síðar sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `hearthstone`, gerð [`log`](sources-and-rules.md); það keyrir meðan `Hearthstone.exe` er í gangi og leitar að nýjum gögnum á 0,5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- upphaf og endir leiks, með niðurstöðunni (sigur, tap, jafntefli), umferðum og nafni andstæðingsins
- hver umferð
- hver lína úr Power.log og hinum annálunum heil í heat.raw.parquet
- leikir, sigrar, töp, jafntefli, umferðir, lengsti leikur

## Hvaðan það kemur {#where-it-comes-from}

&lt;install>\Logs\Power.log (eða Logs\Hearthstone_\*\Power.log), skrifað þegar %LOCALAPPDATA%\Blizzard\Hearthstone\log.config hefur [Power]-hluta, og sérhver önnur \*.log sem leikurinn skrifar þar

## Hvernig kveikt er á því {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` bætir [Power]-skráningu við %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (afrit er geymt); endurræstu leikinn

Sláðu skipunina inn í terminal sem er opnaður í möppu watcher (sjá [Áður en þú byrjar](before-you-start.md)). Ef hún mistekst segir síðasta línan hvers vegna; [Uppsetning og keyrsla](installing-and-running.md) fer yfir algengustu orsakirnar.

`python -m heat3d_watch setup hearthstone` telur upp skrárnar sem það myndi breyta; `python -m heat3d_watch setup hearthstone --apply` breytir þeim og geymir upprunalegu skrána sem `<file>.heat3d-backup` (sjá [Skipanir](commands.md#setup)). Það prentar `hearthstone: changed: ...` fyrir hverja breytingu, eða `hearthstone: nothing to change` þegar kveikt er þegar á þessu.

## Hvernig það virkar {#how-it-works}

Hearthstone: Power.log leiksins, sem hann skrifar þegar `log.config` biður um það.

Hearthstone les `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` við ræsingu;
`[Power]`-hluti með `LogLevel=1` og `FilePrinting=true` lætur hann skrifa
allar stöðubreytingar hvers leiks í `<install>\Logs\Power.log` (nýrri biðlarar setja
annála hverrar ræsingar í sína eigin möppu, `Logs\Hearthstone_<date>\`). Þetta
er skjalaða villuleitarskráningin sem spilaþjálfarar (deck trackers) hafa kveikt á síðan 2014
(uppsetning Hearthstone Deck Tracker skrifar sama hlutann). `setup()` bætir
hlutanum við, með afriti af skránni eins og hún var; leikurinn þarf að endurræsa til að lesa hann.

Línurnar sem eru notaðar, allar úr `GameState.DebugPrintPower()` (`PowerTaskList`-línurnar
endurtaka þær og eru sleppt):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Hlið spilarans sjálfs er sú þar sem spilin í upphafshöndinni eru nefnd
(spil andstæðingsins eru falin), annars hliðin sem er ekki gervigreindin (aðgangur 0) eða
„UNKNOWN HUMAN PLAYER“. Línurnar bera aðeins tíma dagsins; dagsetningin er dagurinn í dag.
Engar staðsetningar.

Sérhver lína úr Power.log er geymd heil í hráu hliðarskrá lotunnar (umbreytingarregla
3DHeat), þar með taldar endurtekningar `PowerTaskList`, valkostir, val og uppfærslur
eininga: `type` er aðferðin sem skrifaði hana (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Sérhver annar
annáll sem leikurinn skrifar við hliðina - `LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ..., hver þar þegar log.config biður um hann (spilaþjálfarar gera það oft) -
er fylgt á sama hátt og geymdur með heiti sínu í `log`.

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | nei |
| Upp-ás | `y` |
| Einingar | engar staðsetningar skráðar |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `log`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (skrár sem leikurinn skrifar meðan hann keyrir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- `CREATE_GAME`, leikmennirnir (eining, leikmannsnúmer, aðgangur; aðgangur 0 er gervigreindin) og nöfn þeirra (`DebugPrintGame`)
- hvaða hlið er spilarans, út frá nefndum spilum upphafshandarinnar
- `TAG_CHANGE` á TURN, PLAYSTATE (sigur, tap, jafntefli) og STATE COMPLETE: umferðir, niðurstaða, andstæðingur

**Geymt hrátt**

- sérhver lína úr Power.log heil, `type` = aðferðin sem skrifaði hana (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` þar sem hún varð að röð: hvert spil sem er spilað, dregið og afhjúpað, hver breyting á merki (tag), árás, valkostur og val er hér, ekki enn í röðum
- sérhver lína úr hinum annálunum í sömu möppu (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - það sem log.config kveikir á), sömu `type`, með heiti annálsins í `log`
- lína án stigs og tíma dagsins sem `untimed`, lína án aðferðar sem `untagged`

**Ekki fáanlegt**

- staðsetningar: kortaleikur hefur engar
- falin spil andstæðingsins: annállinn nefnir spil aðeins þegar það er afhjúpað
- annálar sem log.config kveikir ekki á: `setup` biður aðeins um [Power]; hinir annálarnir koma þegar annað verkfæri (spilaþjálfari) hefur kveikt á þeim
- annálar fyrri ræsinga: hver ræsing skrifar nýja möppu; þær sem eru eldri en þessi keyrsla leiksins eru ekki lesnar aftur

**Stærð**: Power.log með Verbose er um 1-5 MB á leik, 10-40 MB á klukkustund af spilun; hinir annálarnir bæta litlu við; zstd í heat.raw.parquet gerir þetta um tíunda hluta eða minna (línurnar endurtaka sig mikið)

## Staðfest {#verified}

prófað á tilbúnum línum úr Power.log á sniði leiksins; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
