---
title: "Path of Exile (annálsskrár)"
nav_order: 35
lang: "is"
source: game-poe.md
source_hash: "b5783b5a5690"
nav_exclude: true
search_exclude: true
---
# Path of Exile (annálsskrár) {#path-of-exile-log-files}

Meðan þú spilar Path of Exile les watcher skrárnar sem leikurinn skrifar og vistar það sem gerðist, svo þú getir skoðað það síðar sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `poe`, gerð [`log`](sources-and-rules.md); það keyrir meðan `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` eða `PathOfExile_x64_KG.exe` er í gangi og leitar að nýjum gögnum á 0,5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- svæði sem farið er inn á með svæðisstigi, svæðisauðkenni og fræi þess
- stigahækkanir með flokki og stigi
- dauðsföll („has been slain“)
- leikmenn sem koma inn á svæðið og fara af því, hvísl inn og út, viðskiptabeiðnir, viðskipti samþykkt
- sérhver lína úr Client.txt frá þessari setu heil í heat.raw.parquet
- dauðsföll, stig unnin, hæsta stig, svæði sem farið er inn á, ólík svæði, hvísl, viðskiptabeiðnir, viðskipti

## Hvaðan það kemur {#where-it-comes-from}

&lt;install>\logs\Client.txt í Path of Exile eða Path of Exile 2 (fylgst með; uppsetningarmappan er mappa keyrsluskrárinnar sem er í gangi)

## Hvernig kveikt er á því {#how-to-switch-it-on}

Ekki þarf að kveikja á neinu: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

## Hvernig það virkar {#how-it-works}

Path of Exile og Path of Exile 2: biðlaraannállinn, `<install>\logs\Client.txt`.

Báðir leikirnir bæta við eina Client.txt í uppsetningarmöppu sinni svo lengi sem
þeir eru uppsettir (hún stækkar milli ræsinga). Línurnar líta svona út

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- staðartími, millisekúndutalning, kjötkássa (hash), stig og þráður, svo það sem
  spjallglugginn sýnir. Skilaboðin eru þau sem enski biðlarinn skrifar; biðlari á öðru tungumáli
  skrifar þau þýdd og er ekki skilinn hér. Ekkert gefur
  staðsetningu. Sniðið er ekki skjalað af Grinding Gear Games; það er
  látlaus textaannáll leiksins, eins og samfélagsverkfæri (viðskiptahjálp, borðaleiðbeiningar) hafa
  lesið hann í mörg ár - t.d. <https://github.com/klayveR/poe-log-monitor> (MIT) fyrir
  atburðalistann.

Uppsetningarmappan er mappa keyrsluskrárinnar sem er í gangi; án hennar er leitað í Steam-
söfnunum og sjálfgefinni möppu sjálfstæða biðlarans.

Sérhver lína úr þessari setu er geymd heil í hráu hliðarskrá lotunnar (umbreytingarregla
3DHeat), hvort sem hún þýðir eitthvað hér eða ekki: `type` er stigið og
skráningaraðilinn í hornklofum hennar (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), tímastimpluð
lína án hornklofa er `untagged`, lína án tímastimpils
`untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- `You have entered <zone>`, með svæðisstigi, svæðisauðkenni og fræi úr `Generating level`-línunni á undan
- `<name> (<class>) is now level <n>`, `<name> has been slain`, leikmenn sem koma inn á svæðið og fara af því, hvísl inn og út (með því hvort þau eru viðskiptabeiðni), viðskipti samþykkt og afturkölluð

**Geymt hrátt**

- sérhver lína úr þessari setu heil, `type` = stigið og skráningaraðilinn í hornklofum hennar (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` þar sem hún varð að röð: almennt spjall, viðskiptaspjall, hópspjall og gildisspjall, `Connecting to instance server`, AFK- og DND-tilkynningar, svör við spjallskipunum eins og `/played` og `/deaths`, hleðslu- og vélarlínur biðlarans - geymt, ekki enn gert að röðum
- tímastimpluð lína án hornklofa (`***** LOG FILE OPENING *****`) sem `untagged`, lína án tímastimpils sem `untimed`

**Ekki fáanlegt**

- staðsetningar: ekkert í annálnum gefur þær
- það sem biðlari á öðru tungumáli skrifar: línurnar eru geymdar, en aðeins ensku skilaboðin eru gerð að röðum
- línur fyrri ræsinga: Client.txt stækkar milli ræsinga; línur með tímastimpli fyrir þessa keyrslu leiksins eru látnar vera (þær voru geymdar þegar þær voru spilaðar)
- dráp, skaði, herfang og hæfileikatréð: leikurinn skráir þetta ekki í annál

**Stærð**: Client.txt stækkar um 0,3-3 MB á klukkustund (mest vegna DEBUG-lína þegar svæði eru hlaðin, meira með annasömu viðskiptaspjalli); zstd í heat.raw.parquet gerir þetta um tíunda hluta

## Staðfest {#verified}

prófað á tilbúnum línum úr Client.txt á sniði leiksins; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
