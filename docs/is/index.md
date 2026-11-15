---
title: "Heim"
nav_order: 1
lang: "is"
source: index.md
source_hash: "d74a4eae2685"
nav_exclude: true
search_exclude: true
permalink: /is/
---
# 3DHeat Watcher {#dheat-watcher}

**Hvað er þetta?** Þú spilar leik. Þetta forrit skrifar hljóðlega niður hvert þú fórst og hvað gerðist.
Seinna geturðu skoðað það sem litað kort í 3DHeat-skoðaranum.

**Hvers vegna ætti ég að nota það?** Til að eiga þína eigin skrá yfir hverja lotu - hvar þú ókst, flaugst eða barðist,
og samtölur fyrir hvern leik - án nokkurrar vefsíðu og án þess að breyta leiknum.

**Dæmi:** þú ekur hring í kappakstursleik meðan watcher er í gangi; á eftir geymir skrá í
`sessions\<game>\` línuna sem þú ókst, og skoðarinn teiknar hana.

Nánar: 3DHeat Watcher er bakgrunnsforrit sem skráir það sem leikir birta um spilun þína - hvert þú
fórst, hvað gerðist hvar og tölurnar á bak við það - í skrár á þinni eigin vél. Skrárnar eru
fyrir þína eigin tölfræði og fyrir hitakortin og leiðarlínurnar í 3DHeat-skoðaranum.

Það keyrir hljóðlega, tekur eftir hvaða leik þú ræstir og les eigið úttak leiksins: fjarmælingagátt
eða samnýtt minni sem leikurinn birtir fyrir mælaborð, game-state integration, dagbókina eða logginn sem
leikurinn skrifar, endursýninguna sem hann vistar eftir leik, tölfræðina sem Steam heldur, klippurnar sem NVIDIA App
vistar. Upptökur haldast á þinni vél. Forritið hefur aðeins samband við tvær þjónustur utan vélarinnar, og aðeins í
þessum tilvikum: GitHub, til að leita að nýrri útgáfu (sjá [Uppfærslur](updates.md)), og Match-V5 API frá Riot,
og aðeins ef þú slærð inn þinn eigin Riot API-lykil (sjá [League of Legends endursýningar](game-lol-replays.md)).

![watcher: það sem leikir birta, yfir í skrár á þinni vél](../assets/img/is/overview.svg)

## Hvað það skráir {#what-it-records}

- **Staðsetningar**: bíllinn, flugvélin, hetjan eða leikmaðurinn, nokkrum sinnum á sekúndu þar sem leikurinn birtir
  þær, með hraða, stefnu og öllu öðru sem leikurinn sendir með.
- **Atburðir**: endurfæðingar, dauðsföll, dráp, hringir, leiðir, lotur, mörk, verkefni, flugtök og lendingar, svæðisskipti,
  afrek, hápunktar. Hver atburður er geymdur með tíma sínum, og með stað sínum þegar
  leikurinn gefur hann upp.
- **Tölfræði fyrir hverja lotu**: dráp, dauðsföll, hringir, besti hringur, vegalengd, hámarkshraði, spilatími og
  eigin tölfræði leiksins þar sem hann heldur hana.

Hvað hver leikur gefur, og hvaðan, er á síðu hans undir [Leikir](games.md). Ein heimild getur ekki
skráð allt: fjölspilunarleikir eru aðeins skráðir í gegnum það sem þeir birta, og watcher
les aldrei minni þeirra (sjá [Heimildir og reglur](sources-and-rules.md)).

## Uppsetning {#install}

Ertu ný/r í skipanalínunni? Lestu fyrst [Áður en þú byrjar](before-you-start.md).

Watcher er Python-forrit fyrir Windows (Python 3.10 eða nýrra). Margar heimildir þess eru aðeins til á Windows: samnýtt
minni, nýskráningin (registry), Windows-tilkynningar.

```bash
git clone https://github.com/Holdi601/3DHeat-Watcher.git
cd 3DHeat-Watcher
pip install -r requirements.txt
```

Útgáfuskjalasafn sem þú sækir virkar eins: pakkaðu því upp og keyrðu svo `pip install -r requirements.txt`
inni í möppunni. Nánar, og aukahlutirnir sem sumir leikir þurfa, er í
[Uppsetning og keyrsla](installing-and-running.md).

## Fljótleg byrjun {#quick-start}

```bash
python -m heat3d_watch games            # what each game gives, and from where
python -m heat3d_watch setup all        # what would have to be switched on (nothing is changed)
python -m heat3d_watch setup f1-25 --apply   # switch one game's output on (the original file is backed up)
python -m heat3d_watch run              # watch; leave it running while you play
python -m heat3d_watch stats            # totals per game
python -m heat3d_watch stats --csv out  # sessions, events and stats as CSV files
```

Þú ættir að sjá: eftir `games` töflu með einni línu fyrir hvern leik; `run` heldur áfram þar til þú ýtir á
Ctrl+C eða lokar glugganum.

Allt er skrifað í `%LOCALAPPDATA%\3DHeat\Watcher`. Til að nota aðra möppu skaltu stilla umhverfisbreytuna
`HEAT3D_WATCH_HOME` eða keyra `python -m heat3d_watch config --set data=D:\somewhere`.

- `sessions\<game>\<date>_<adapter>\` - ein mappa fyrir hverja lotu, með `events.jsonl` (hver atburður
  um leið og hann gerist), `heat.parquet` (raðirnar með staðsetningu, tilbúnar fyrir 3DHeat-skoðarann) og
  `meta.json` (leikur, heimild, ásar, talningar, tölfræði)
- `watcher.sqlite` - tölfræði hverrar lotu, í þremur einföldum töflum
- `watcher.log` - það sem watcher gerði

Skoðarinn opnar `heat.parquet` lotu beint, án þess að stilla neitt (ásar hennar og einingar eru í
skránni). Umbreyttar endursýningar eru skrifaðar sem töflur og leikjaskjöl við hliðina; eigið
eins-skrár-fyrir-leik snið skoðarans er lýst á síðunni [`.3dheat` ílát](https://holdi601.github.io/3DHeat/container.html),
og dálkar hverrar töflu í [Gögnin](the-data.md).

## Skjölunin {#the-documentation}

| Síða | Hvað hún fjallar um |
|---|---|
| [Áður en þú byrjar](before-you-start.md) | Python, skipanalína, staðgenglar, hvernig árangur og algengar villur líta út |
| [Uppsetning og keyrsla](installing-and-running.md) | kröfur, keyrsla í bakgrunni, ræsing með Windows, læsingarskráin, loggurinn, allar stillingar og umhverfisbreytur |
| [Leikir](games.md) | ein síða fyrir hvern leik: hvað er skráð, hvaðan, hvernig á að kveikja á því, hvernig það virkar, ásar, tölfræði, hvað var staðfest |
| [Gögnin](the-data.md) | lotumöppur, `events.jsonl`, `heat.parquet` og fótur hennar, `meta.json`, `watcher.sqlite`, endurheimt eftir hrun, CSV-útflutningur, að opna lotu í 3DHeat-skoðaranum |
| [Skipanir](commands.md) | allar skipanir og valkostir `python -m heat3d_watch` |
| [Heimildir og reglur](sources-and-rules.md) | heimildirnar sex, fjölspilunarreglurnar, hvaða leikir eru undanskildir og hvers vegna |
| [NVIDIA Highlights](nvidia-highlights.md) | hvað NVIDIA Highlights getur og getur ekki skilað, og hvernig hápunktur fær staðsetningu |
| [Netþjónamódd fyrir upptöku](server-mods.md) | Arma 3 og Arma Reforger netþjónamódd sem skrá heil verkefni fyrir skoðarann |
| [Minnislestur](memory-reading.md) | minnissnið fyrir einspilunarleiki: sniðið, athuganirnar, hvernig á að skrifa eitt og staðfesta það |
| [Uppfærslur](updates.md) | hvernig watcher leitar að nýjum útgáfum og uppfærir sig sjálfur |
| [Þróun](development.md) | að skrifa millistykki: API, prófanir, heiðarlegt `verified`, endurgerð leikjasíðna |
| [Allir leikir í einni töflu](watcher.md) | hver leikur í einni töflu, eins og `games --markdown` prentar hana, auk leikja sem hafa verið rannsakaðir en ekki smíðaðir enn |
| [Skipanayfirlit](../cli-reference.md) | `--help` hverrar skipunar, búið til úr kóðanum |
| [Viðhald](maintaining.md) | útgáfulistinn fyrir þessar síður |

## Hluti af 3DHeat {#part-of-3dheat}

3DHeat Watcher er eitt af ókeypis verkfærunum í kringum 3DHeat-skoðarann (watcher notar 3DHeat CS2
til að umbreyta CS2 demóum). Hvert er sérstakt verkefni, með eigin útgáfur og leyfi:

| Verkfæri | Hvað það gerir | Skjöl |
|---|---|---|
| [3DHeat](https://github.com/Holdi601/3DHeat) | skoðarinn: hitakort, kappakstursgreining og leikjayfirferð í þrívídd | [vefsíða](https://holdi601.github.io/3DHeat/) |
| [GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) | brautir og borð úr skrám sem leikir fylgja með, sem þrívíddarlíkön | [vefsíða](https://holdi601.github.io/3DHeat-GameFiles/) |
| [GameCapture](https://github.com/Holdi601/3DHeat-GameCapture) | hringjafjarmæling úr kappakstursleikjum; borð endurbyggð úr leikjamyndbandi | [vefsíða](https://holdi601.github.io/3DHeat-GameCapture/) |
| [Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter) | viðbót fyrir Unreal Editor sem flytur borð út sem eitt þrívíddarlíkan | [vefsíða](https://holdi601.github.io/3DHeat-UnrealExporter/) |
| [CS2](https://github.com/Holdi601/3DHeat-CS2) | Counter-Strike 2 demó í töflur og leikjaskjöl; kort í þrívíddarlíkön | [vefsíða](https://holdi601.github.io/3DHeat-CS2/) |
| [Watcher](https://github.com/Holdi601/3DHeat-Watcher) | skráir í bakgrunni það sem leikir birta um spilun þína | [vefsíða](https://holdi601.github.io/3DHeat-Watcher/) |
| [Ext-WarThunder](https://github.com/Holdi601/3DHeat-Ext-WarThunder) | War Thunder endursýningar í töflur og leikjaskjöl | [vefsíða](https://holdi601.github.io/3DHeat-Ext-WarThunder/) |
| [Ext-WoT](https://github.com/Holdi601/3DHeat-Ext-WoT) | World of Tanks endursýningar í töflur og leikjaskjöl | [vefsíða](https://holdi601.github.io/3DHeat-Ext-WoT/) |
| [Ext-WoWs](https://github.com/Holdi601/3DHeat-Ext-WoWs) | World of Warships endursýningar í töflur og leikjaskjöl | [vefsíða](https://holdi601.github.io/3DHeat-Ext-WoWs/) |
| [Ext-Squad](https://github.com/Holdi601/3DHeat-Ext-Squad) | Squad netþjónademó í töflur og leikjaskjöl | [vefsíða](https://holdi601.github.io/3DHeat-Ext-Squad/) |
| [Ext-DCS](https://github.com/Holdi601/3DHeat-Ext-DCS) | DCS World kort í þrívíddarlíkön | [vefsíða](https://holdi601.github.io/3DHeat-Ext-DCS/) |
| [Ext-IL2](https://github.com/Holdi601/3DHeat-Ext-IL2) | IL-2 Sturmovik kort í þrívíddarlíkön | [vefsíða](https://holdi601.github.io/3DHeat-Ext-IL2/) |
| [Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota) | Dota 2 kortið úr þinni eigin uppsetningu sem þrívíddarborð | [vefsíða](https://holdi601.github.io/3DHeat-Ext-Dota/) |
| [Ext-DotaReplay](https://github.com/Holdi601/3DHeat-Ext-DotaReplay) | Dota 2 endursýningar | [vefsíða](https://holdi601.github.io/3DHeat-Ext-DotaReplay/) |
| [Ext-Riot](https://github.com/Holdi601/3DHeat-Ext-Riot) | League of Legends og VALORANT endursýningar (það sem þær geyma ódulkóðað) | [vefsíða](https://holdi601.github.io/3DHeat-Ext-Riot/) |
| [Ext-Forza](https://github.com/Holdi601/3DHeat-Ext-Forza) | Forza brautir, keppnir og bílar úr þinni eigin uppsetningu | [vefsíða](https://holdi601.github.io/3DHeat-Ext-Forza/) |
| [Ext-Battlefield](https://github.com/Holdi601/3DHeat-Ext-Battlefield) | Battlefield borð (Frostbite) sem þrívíddarborð | [vefsíða](https://holdi601.github.io/3DHeat-Ext-Battlefield/) |
| [Ext-BeamNG](https://github.com/Holdi601/3DHeat-Ext-BeamNG) | BeamNG.drive brautir | [vefsíða](https://holdi601.github.io/3DHeat-Ext-BeamNG/) |
| [Ext-ACRally](https://github.com/Holdi601/3DHeat-Ext-ACRally) | Assetto Corsa Rally leiðir sem brautir | [vefsíða](https://holdi601.github.io/3DHeat-Ext-ACRally/) |
| [Ext-Reforger](https://github.com/Holdi601/3DHeat-Ext-Reforger) | Arma Reforger heimar (Enfusion) sem þrívíddarborð | [vefsíða](https://holdi601.github.io/3DHeat-Ext-Reforger/) |
| [Ext-R6](https://github.com/Holdi601/3DHeat-Ext-R6) | Rainbow Six Siege leikjaendursýningar | [vefsíða](https://holdi601.github.io/3DHeat-Ext-R6/) |

Leyfi: MIT ([LICENSE](https://github.com/Holdi601/3DHeat-Watcher/blob/main/LICENSE)). Leyfi
þriðju aðila pakka sem það notar, og það sem leikirnir sem það les krefjast, eru talin upp í
[LICENSES.md](https://github.com/Holdi601/3DHeat-Watcher/blob/main/LICENSES.md).
