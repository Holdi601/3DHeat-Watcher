---
title: "Minecraft (logskrár)"
nav_order: 33
lang: "is"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (logskrár) {#minecraft-log-files}

Meðan þú spilar Minecraft les watcher skrárnar sem leikurinn skrifar og vistar það sem gerðist, svo þú getir skoðað það síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `minecraft`, gerð [`log`](sources-and-rules.md); það keyrir meðan `javaw.exe` eða `java.exe` er í gangi og leitar að nýjum gögnum á 0,5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða þín og annarra spilara (kubbar = m, y upp) í hvert sinn sem heimurinn vistast, vídd (dimension) sem lota
- spawn með stöðu þegar spilari skráir sig inn á (innbyggða) þjóninn
- innskráningar, útskráningar, dauðsföll með dánarskilaboðunum, afrek (advancements), spjalllínur
- dauðsföll, afrek, spjallskilaboð; úr tölfræðiskránni: spilunartími, vegalengd, dráp á skrímslum og spilurum, stökk, skaði, kubbar sem eru unnir, hlutir sem eru smíðaðir (hlutur þessarar lotu)
- sérhver logglína og sérhver vistuð tölfræði-, afreka- og spilaraskrá heil í heat.raw.parquet

## Hvaðan það kemur {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (fylgt eftir), saves\\&lt;world>\stats\\&lt;uuid>.json og saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), lesið þegar leikurinn vistar þær

## Hvernig kveikt er á því {#how-to-switch-it-on}

Ekki þarf að kveikja á neinu: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

## Hvernig það virkar {#how-it-works}

Minecraft (Java Edition): logg-, tölfræði- og spilaraskrárnar sem leikurinn skrifar.

Hvar (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - logg leiksins, nýtt við hverja ræsingu (það gamla er
  pakkað í dagsett .log.gz). Línur `[hh:mm:ss] [thread/LEVEL]: message`
  (viðbótarhleðslur skrifa `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`).
  Það sem spilarar sjá í spjallinu er þar: innskráningar og útskráningar, dánarskilaboð,
  afrek, spjall - innbyggði þjónninn í einspilunarheimi skrifar
  sömu línurnar aftur, svo lína sem endurtekur sig innan sömu sekúndu telst
  einu sinni. „Setting user: &lt;name>“ nefnir spilarann; hjá þjóninum
  „&lt;name>[...] logged in with entity id N at (x, y, z)“ gefur hvar þeir
  birtust.
* `saves\<world>\stats\<uuid>.json` - tölfræðiskjárinn, skrifaður þegar
  heimurinn vistast (sjálfvirk vistun á nokkurra mínútna fresti, og við brottför): `stats` ->
  `minecraft:custom` (play_time í tikkum, mob_kills, \*_one_cm vegalengdir, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Heildartölur heimsins; tölur
  lotunnar eru mismunurinn á því sem skráin sagði þegar leikurinn
  ræstist. Snið: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (og `level.dat` -> Data -> Player
  fyrir einspilunarhýsil) - gzip-þjappað NBT, skrifað við sömu vistanir:
  `Pos` [x, y, z] tvöfaldar tölur, `Rotation` [yaw, pitch], `Dimension`
  („minecraft:overworld“; heiltala 0/-1/1 fyrir 1.16). NBT samkvæmt
  <https://minecraft.wiki/w/NBT_format> - lesið hér með lítilli lesara af okkar eigin.
* `saves\<world>\advancements\<uuid>.json` - framvinda afreksskjásins,
  skrifuð við sömu vistanir.

Hnit eru kubbar, einn kubbur er einn metri, y upp; x austur, z suður - hægrihandarkerfi,
teiknað eins og það er. Stöður koma aðeins þegar heimurinn vistast, svo
leið er fáeinir punktar við hverja sjálfvirka vistun, ekki slóð; víddin er
`session`, svo Nether er ekki teiknað yfir Overworld.

Allt sem er lesið er geymt heilt í hráu hliðarskrá lotunnar (umbreytingarregla
3DHeat): sérhver logglína undir stigi sínu (`INFO`, `WARN`, `ERROR`, ...; lína
án hornklofahaussins, eins og stack trace, sem `untagged`), og sérhver
vistuð skrá undir gerð sinni (`stats`, `advancements`, `playerdata`,
`level.dat`) - JSON sem texti, NBT sem bæti. Tölur tölfræðiskrár skiljast aðeins
miðað við það sem hún sagði þegar leikurinn ræstist, svo það fyrsta afrit
er líka geymt (`baseline`), í fyrsta sinn sem skráin breytist.

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | kubbar (1 kubbur = 1 m) |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `log`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (skrár sem leikurinn skrifar meðan hann keyrir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- latest.log: nafn spilarans (`Setting user`), innskráningar með stöðu, innskráningar, útskráningar, dauðsföll með dánarskilaboðunum, afrek, spjalllínur, þjónninn stöðvast
- stats/&lt;uuid>.json: spilunartími, vegalengd, dráp á skrímslum og spilurum, stökk, skaði veittur og tekinn, kubbar unnir, hlutir smíðaðir - hlutur þessarar setu
- playerdata/&lt;uuid>.dat og level.dat (NBT): staða, vídd, yaw, pitch, heilsa, XP-stig

**Geymt hrátt**

- sérhver latest.log-lína heil, `type` = stig hennar (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) með þræði loggarans í `thread`, `used` þar sem hún varð að röð; lína án hornklofahaussins (stack trace, borði viðbótar) sem `untagged`
- sérhver stats/&lt;uuid>.json heil sem texti, `type` `stats` (`used`: tölur hennar eru í tölfræðinni), með fyrsta afrit hennar frá ræsingu leiksins sem `baseline`
- sérhver advancements/&lt;uuid>.json heil sem texti, `type` `advancements` (sérhver viðmiðun og hvenær hún var uppfyllt; ekki enn gerð að röðum)
- sérhver playerdata/&lt;uuid>.dat og level.dat heil sem bæti (gzip NBT), `type` `playerdata` / `level.dat`, `used` þar sem hún gaf stöðu: farangur, ender-kista, áhrif, upphafspunktur, leikreglur, fræ heimsins og tími eru aðeins hér
- sérhver vistuð skrá hefur `world` og `file` (slóð hennar undir `saves`)

**Ekki fáanlegt**

- staðarslóð: leikurinn skrifar stöðu spilarans aðeins þegar heimurinn vistast (á nokkurra mínútna fresti og við brottför)
- stöður á þjóni sem einhver annar hýsir: heimsskrár hans eru á þjóninum, ekki hér; þá er aðeins loggið lesið
- heimurinn sjálfur (region .mca-skrár, einingar, data/\*.dat kort og árásir): stórt, og landslagið, ekki spilunin
- logg fyrri setna (logs/\*.log.gz): geymt þegar þær voru spilaðar
- Bedrock Edition: hún skrifar engin slík logg eða skrár

**Stærð**: latest.log 0,1-2 MB á klukkustund (meira með viðbótum); tölfræðiskrá 5-50 KB og spilaraskrá 5-100 KB við hverja sjálfvirka vistun, level.dat 1-20 KB - um 1-5 MB á klukkustund alls; zstd í heat.raw.parquet gerir textann um tíunda hluta (NBT-skrárnar eru þegar gzip)

## Staðfest {#verified}

prófað á tilbúnum logglínum, tölfræði-JSON og NBT-skrám sem eru smíðaðar eftir birtum sniðum; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
