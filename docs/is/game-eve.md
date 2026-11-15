---
title: "EVE Online (annálsskrár)"
nav_order: 20
lang: "is"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (annálsskrár) {#eve-online-log-files}

Meðan þú spilar EVE Online les watcher skrárnar sem leikurinn skrifar og vistar það sem gerðist, svo þú getir skoðað það síðar sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `eve`, gerð [`log`](sources-and-rules.md); það keyrir meðan `exefile.exe` er í gangi og leitar að nýjum gögnum á 0,5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- skaði veittur og hlotinn með hinu skipinu, flugmanninum, kenniskammstöfun fyrirtækis (corporation ticker), vopni og gæðum höggs
- misheppnuð skot veitt og hlotin
- verðlaun greidd (NPC-dráp) með ISK
- stökk milli kerfa
- hver lína úr gamelog og spjallskrám heil í heat.raw.parquet
- skaði veittur og hlotinn, högg, misheppnuð skot, verðlaunadráp og ISK, stökk

## Hvaðan það kemur {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt og Chatlogs\\\*.txt við hliðina (sérhver skrá sem hefur verið skrifuð frá því biðlarinn ræsti)

## Hvernig kveikt er á því {#how-to-switch-it-on}

Ekki þarf að kveikja á neinu: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

## Hvernig það virkar {#how-it-works}

EVE Online: leikjaannálar biðlarans, `Documents\EVE\logs\Gamelogs\*.txt`.

Biðlarinn skrifar eina skrá fyrir hverja persónu við hverja innskráningu,
`<yyyymmdd>_<hhmmss>[_<character id>].txt`; skráning í skrá er sjálfgefið á. Margir biðlarar sem keyra
hlið við hlið skrifa hver sína, svo sérhverri skrá sem hefur verið skrifuð síðan leikurinn ræsti er
fylgt. Haus og línur (EVE-tími er UTC):

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

(combat-línan er ein lína í skránni). Sniðmerki eru fjarlægð áður en
leitað er að samsvörun. Skráin hefur verið UTF-8 og UTF-16 í gegnum árin; báðar eru lesnar.
Sniðið er ekki skjalað af CCP; það er látlaus textaannáll biðlarans, lesinn eins og
samfélagsverkfæri fyrir bardagaannála lesa hann (t.d. <https://docs.rs/crate/eve-log-parser>).
Engar staðsetningar.

Við hliðina, `Documents\EVE\logs\Chatlogs\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
ein skrá fyrir hverja spjallrás við hverja innskráningu (þegar spjallskráning er á, sem er sjálfgefið í
biðlaranum), UTF-16, haus sem nefnir rásina og hlustandann, svo
`[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Sérhver lína úr báðum er geymd heil í hráu hliðarskrá lotunnar (umbreytingarregla
3DHeat): lína úr gamelog undir rás sinni í hornklofum (`combat`,
`notify`, `bounty`, `None`, ...), spjalllína sem `chat` með rás sinni, og
hauslínurnar sem `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- `(combat)` í gamelog: högg veitt og hlotin (magn, hinn flugmaðurinn, kenniskammstöfun fyrirtækis, skip, vopn, gæði höggs) og misheppnuð skot í báðar áttir
- `(bounty)` í gamelog: greiðslur með ISK, og línurnar `Jumping from A to B`
- Listener í haus gamelog: hver á annálinn

**Geymt hrátt**

- sérhver lína úr gamelog heil, `type` = rás hennar í hornklofum (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), með `file` og `listener`; `used` þar sem hún varð að röð; hauslínurnar sem `gamelog header`
- sérhver lína úr spjallskrá heil (Local, fyrirtæki, floti, einkarásir, tilkynningar `EVE System` eins og breyting á Local-rás við stökk), `type` `chat`, með `channel`, `listener` og `file`; hauslínurnar sem `chatlog header`. Ekki enn gerðar að röðum
- sniðmerkin (`<color>`, `<b>`, `<font>`) haldast í hráa textanum; raðirnar hafa þau fjarlægð

**Ekki fáanlegt**

- staðsetningar: biðlarinn skrifar engar í annála sína
- bardagar annarra flugmanna: gamelog er alltaf hlustandans sjálfs
- annálar fyrri innskráninga: hver innskráning skrifar nýjar skrár; þær sem eru eldri en þessi keyrsla biðlarans eru ekki lesnar aftur
- spjall þegar spilarinn hefur slökkt á spjallskráningu í stillingum biðlarans
- eigin skyndiminni- og stillingaskrár biðlarans: ekki annálar, og ekki skjalaðar

**Stærð**: gamelog er 0,1-2 MB á klukkustund (mest í bardaga); spjallskrár fara eftir opnum rásum - upptekin Local- eða flotarás 0,5-3 MB á klukkustund; zstd í heat.raw.parquet gerir þetta um tíunda hluta

## Staðfest {#verified}

prófað á tilbúnum línum úr gamelog á sniðinu sem samfélagsþáttarar birta; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
