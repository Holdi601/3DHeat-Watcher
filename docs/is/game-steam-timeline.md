---
title: "Steam Timeline (vettvangur)"
nav_order: 43
lang: "is"
source: game-steam-timeline.md
source_hash: "3a502e4ad09e"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (vettvangur) {#steam-timeline-platform}

Watcher vistar það sem Steam Timeline geymir um leikina þína, svo þú getir skoðað söguna síðar sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `steam-timeline`, gerð [`platform`](sources-and-rules.md); það keyrir alltaf (það bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 10 s fresti.*

## Hvað er skráð {#what-is-recorded}

- ein lota fyrir hverja tímalínuskrá: upphaf hennar og endir (session_start, session_end)
- afrek sem opnast meðan á spilun stendur, með tíma
- breytingar á leikham (spilun, staging, valmyndir, hleðsluskjár)
- atburðir sem leikir bæta við í gegnum ISteamTimeline, með titli og lýsingu, undir nafni tákns þeirra
- leikfasar (viðureign, verkefni) með merkjum sínum; atburðir innan eins bera auðkenni hans sem session
- stöðulýsingar sem leikurinn sýnir á tímalínunni ("Round 3")
- eigin upptökuvillur Steam

## Hvaðan það kemur {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Hvernig á að kveikja á því {#how-to-switch-it-on}

Steam > Settings > Game Recording: taktu upp í bakgrunni eða eftir þörfum (þá skrifar Steam tímalínur)

## Hvernig það virkar {#how-it-works}

Það sem ræsiforritið og skjákortsreklarinn geyma um spilun: tölfræði, afrek,
spilatími og tímalínur Steam, og hápunktar og klippur NVIDIA.

Engin þessara heimilda þarf að leikurinn vinni með eða sé í gangi, svo
millistykkin þrjú hér eru alltaf kveikt og líta á nokkrar skrár á nokkurra sekúndna fresti.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
skrifuð meðan Steam Game Recording er kveikt. Skráin er JSON með tölur sem strengi:
"daterecorded" (Unix-sekúndur), "starttime"/"endtime" (ms) og
"entries", hver {"id", "time" (ms frá daterecorded), "type", ...}. Gerðir
sem sáust í raunverulegum skrám:
```text
achievement        achievement_name - Steam adds these for every game
gamemode           mode, an ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - Steam's own ("#GameRecording_RecordingFailed")
event              a game's AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              a StartGamePhase..EndGamePhase span: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
Skráarsniðið er Steam og óskjalfest; reitirnir eru færibreytur API-sins.
Allar aðrar gerðir eru skráðar undir eigin nafni með reitum sínum.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Sama eining þjónar líka: [NVIDIA hápunktar (vettvangur)](game-nvidia-highlights.md), [Steam tölfræði (vettvangur)](game-steam-stats.md).

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

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er hver pakki, síða, lína eða svar sem millistykkið fær geymt í heild í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, svo hver reitur sem geymdur er með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hvert `type` - `lost` er 0.

**Lesið**

- hver færsla einu sinni, sem röð á tíma sínum: gerð hennar, hver einfaldur reitur (title, description, icon, priority, duration, possible_clip, nafn afreks, mode, ...), merki fasa eftir hópum, birtingarnafn afreksins úr tölfræðiskeminu; upphaf og endir skrárinnar

**Geymt óunnið**

- hver færsla í heild sem JSON undir eigin `type` Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, hver önnur): hreiðraðir reitir - tákn og forgangur merkis, allt sem síðari Steam bætir við - eru aðeins hér
- `timeline`: eigin reitir skrárinnar (daterecorded, starttime, endtime, hver annar), þegar lotan opnast og aftur þegar þeir breytast

**Ekki tiltækt**

- upptakan sjálf (myndband): Steam geymir hana í eigin möppum; lotan vísar á tímalínuskrána með nafni
- lestur á skrá sem Steam er að skrifa og er ekki hægt að þátta jafnvel þótt endi hennar sé lokað: talinn (`bad` í stöðu millistykkisins) og lesinn aftur við næstu breytingu, þar sem færslur hennar eru teknar

**Stærð**: nokkur hundruð færslur af 100-300 bætum fyrir hverja klukkustund af spilun: langt undir 1 MB fyrir hverja klukkustund

## Staðfest {#verified}

prófað á raunverulegum tímalínuskrám úr staðbundinni uppsetningu: færslur achievement, gamemode, error og eigin event, state_description og phase færslur leikja; skráarsniðið sjálft er óskjalfest

## Heimild {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
