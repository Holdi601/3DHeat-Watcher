---
title: "Steam tölfræði (vettvangur)"
nav_order: 42
lang: "is"
source: game-steam-stats.md
source_hash: "09ecf3611c02"
nav_exclude: true
search_exclude: true
---
# Steam tölfræði (vettvangur) {#steam-statistics-platform}

Watcher vistar það sem Steam tölfræði geymir um leikina þína, svo þú getir skoðað söguna síðar sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `steam-stats`, gerð [`platform`](sources-and-rules.md); það keyrir alltaf (það bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 30 s fresti.*

## Hvað er skráð {#what-is-recorded}

- hver tölfræði sem leikur geymir í Steam (eigin nöfn og gildi), fyrir hvern leik, þegar hún breytist
- afrek sem opnast með birtingarnafni, lýsingu og opnunartíma
- breytingar á tölfræði með gömlu gildi, nýju gildi og mismun
- spilatími (mínútur, síðustu tvær vikur) og tími síðasta leiks

## Hvaðan það kemur {#where-it-comes-from}

staðbundin tölfræðigeymsla Steam %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin með UserGameStatsSchema_&lt;appid>.bin; spilatími úr %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% úr HKCU\Software\Valve\Steam SteamPath)

## Hvernig á að kveikja á því {#how-to-switch-it-on}

Ekki þarf að kveikja á neinu: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

## Hvernig það virkar {#how-it-works}

Það sem ræsiforritið og skjákortsreklarinn geyma um spilun: tölfræði, afrek,
spilatími og tímalínur Steam, og hápunktar og klippur NVIDIA.

Engin þessara heimilda þarf að leikurinn vinni með eða sé í gangi, svo
millistykkin þrjú hér eru alltaf kveikt og líta á nokkrar skrár á nokkurra sekúndna fresti.

#### Steam tölfræði (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, endurskrifuð af
Steam-biðlaranum í hvert sinn sem leikur geymir tölfræði sína, afkóðuð með skeminu
`UserGameStatsSchema_<appid>.bin` við hlið hennar (tvíundar KeyValues, sjá `_steam.py`).
Tölfræði eru heiltölur eða fleytitölur eins og leikurinn skilgreinir þær; afrek eru bitar
með opnunartíma í Unix-sekúndum. Spilatími er í
`<Steam>\userdata\<account>\config\localconfig.vdf` undir apps/&lt;appid>:
Playtime og Playtime2wks í mínútum, LastPlayed í Unix-sekúndum.
Steam finnst í gegnum HKCU\Software\Valve\Steam SteamPath.
Stats API: <https://partner.steamgames.com/doc/features/achievements>

Sama eining þjónar líka: [NVIDIA hápunktar (vettvangur)](game-nvidia-highlights.md), [Steam Timeline (vettvangur)](game-steam-timeline.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | nei |
| Upp-ás | `y` |
| Einingar | metrar |
| Speglað fyrir skoðarann | engin |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **nei**. `games --markdown` sýnir þetta sem "single-player".
- Gerð `platform`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (það sem Steam eða skjákortsreklarinn geymir), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er hver pakki, síða, lína eða svar sem millistykkið fær geymt í heild í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, svo hver reitur sem geymdur er með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hvert `type` - `lost` er 0.

**Lesið**

- hver tölfræði í tölfræðiskránni eftir API-nafni sínu (int, float, avgrate), hver afreksbiti með opnunartíma, nefndur og lýstur af skeminu
- breytingar miðað við síðasta lestur (gamalt, nýtt, mismunur), ný afrek; spilatími, spilatími síðustu tveggja vikna og síðasti leikur úr localconfig.vdf

**Geymt óunnið**

- `UserGameStats`: bæti tölfræðiskrárinnar, í heild, í hvert sinn sem hún er skráð (`crc`, `PendingChanges`, afreksbitar sem skemað skilgreinir ekki lengur og hver lykill sem afkóðarinn sleppir eru í henni)
- `UserGameStatsSchema`: bæti skemaskrárinnar við hlið hennar, svo hægt sé að afkóða tölfræðina úr lotunni einni (nöfn hverrar tölfræði og hvers afreks á öllum tungumálum, tákn, flögg)
- `localconfig_app`: allur blokk leiksins í localconfig.vdf sem JSON (staða skýjasamstillingar, ræsivalkostir, merki og hver annar lykill sem Steam geymir fyrir hvern leik) þegar spilatími hans er skráður
- tölfræðiskrá sem afkóðarinn getur ekki lesið (skorin í miðri skrift, eða nýtt snið): bæti hennar og skemað í lotu án raða (`used` false; `unreadable` í meta.json)

**Ekki tiltækt**

- afgangurinn af localconfig.vdf (vinir, spjall, stillingar Steam): ekki leiksins, og einkamál
- tölfræðigildi milli tveggja skrifta: Steam endurskrifar skrána þegar leikurinn geymir tölfræði sína, venjulega þegar hann lokast
- alþjóðleg afrekshlutföll og tölfræði annarra spilara: þau eru á netþjónum Steam, ekki hér

**Stærð**: nokkur KB fyrir hverja skráða setu, auk skemans (allt að nokkur hundruð KB fyrir leik með mörg afrek) - langt undir 1 MB fyrir hverja klukkustund af spilun; zstd minnkar texta skemans um helming eða meira

## Staðfest {#verified}

prófað á raunverulegum tölfræðiskrám og skemum úr staðbundinni uppsetningu; greining breytinga prófuð á skrám sem eru búnar til á tvíundar KeyValues sniði

## Heimild {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
