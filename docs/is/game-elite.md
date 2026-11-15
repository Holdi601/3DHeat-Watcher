---
title: "Elite Dangerous (logskrár)"
nav_order: 18
lang: "is"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (logskrár) {#elite-dangerous-log-files}

Meðan þú spilar Elite Dangerous les watcher skrárnar sem leikurinn skrifar og vistar það sem gerðist, svo þú getir skoðað það síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `elite`, gerð [`log`](sources-and-rules.md); það keyrir meðan `EliteDangerous64.exe` er í gangi og leitar að nýjum gögnum á 0,25 s fresti.*

## Hvað er skráð {#what-is-recorded}

- sérhver atburður dagbókarinnar, undir dagbókarnafni sínu, með einföldu reitina sína
- vetrarbrautarstaða (StarPos, ljósár) við stökk, staðsetningar, upphaf, dauðsföll, tengingu við stöð, lendingu
- spawn við LoadGame/Resurrect, death við Died, docked/undocked, touchdown/liftoff, jump, session_end
- leið á yfirborði reikistjörnu úr Status.json: breiddargráða, lengdargráða, hæð, stefna, og metrar í snertiplani fyrir hvern hnött (lota = nafn hnattarins), með öðrum einföldum reitum Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- sérhver dagbókarlína og sérhver fylgiskrá heil í heat.raw.parquet
- stökk, vegalengd stökka, dauðsföll, dráp, inneignir sem aflað var, verkefni lokið, hnettir skannaðir, kerfi heimsótt, tengingar við stöð, lendingar

## Hvaðan það kemur {#where-it-comes-from}

Player Journal %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (nýjasta skráin, fylgt eftir meðan hún er skrifuð), Status.json og hinar fylgiskrárnar \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) í sömu möppu

## Hvernig kveikt er á því {#how-to-switch-it-on}

Ekki þarf að kveikja á neinu: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

## Hvernig það virkar {#how-it-works}

Elite Dangerous: Player Journal og Status.json sem leikurinn skrifar meðan hann keyrir.

Hvar: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - einn JSON-hlutur í hverri línu, ein
  skrá fyrir hverja ræsingu (löng seta heldur áfram í part .02, .03 ...). Sérhver lína
  hefur `timestamp` (UTC, ISO 8601) og `event`. Vetrarbrautarstöður eru
  `StarPos` [x, y, z] kerfisins, í ljósárum frá Sol, við `FSDJump`,
  `Location` og `CarrierJump`. Vetrarbrautarkerfi Elite er y upp (í átt að
  norðri vetrarbrautarinnar), z í átt að kjarna vetrarbrautarinnar og x í átt að
  lengdargráðu vetrarbrautar 270 - vinstrihandarkerfi, svo skoðarinn speglar z til að teikna það
  rétt.
* `Status.json` - endurskrifuð í heild í hvert sinn sem ástand skipsins breytist: `Flags`,
  og nálægt reikistjörnu `Latitude`, `Longitude` (gráður), `Altitude` (metrar),
  `Heading`, `BodyName` og `PlanetRadius` (metrar).
* Hinar fylgiskrárnar, hver endurskrifuð í heild þegar samsvarandi dagbókaratburður
  er skrifaður: `Market.json`, `Outfitting.json`, `Shipyard.json`,
  `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`,
  `Backpack.json`, `FCMaterials.json`. Sérhver `*.json` í möppunni sem
  leikurinn skrifar í þessari setu er geymd heil í hvert sinn sem hún breytist (umbreytingarregla
  3DHeat: það sem heimildin geymir er lesið eða varðveitt), undir skráarheiti sínu.

Sérhver dagbókarlína er geymd heil í hráu hliðarskrá lotunnar undir `event` sínu,
sérhver fylgiskrá undir skráarheiti sínu; lína sem er ekki JSON undir
`unparsed`.

Yfirborðsstöður eru settar í staðbundið snertiplan fyrir hvern hnött, í metrum: fyrsta
staðsetning á hnetti er upphafspunktur hans, x austur, z norður, y upp (hæð), sama
handrétta og í vetrarbrautarkerfinu, og raðirnar bera nafn hnattarins sem
`session`, svo akstur eða ganga á reikistjörnu teiknast sem sérstök leið. Raðir
vetrarbrautarinnar hafa lotuna „galaxy“. Kvarðarnir tveir eru í einni töflu; veldu lotuna
í skoðaranum.

Snið: handbók Frontier „Elite Dangerous Player Journal“ (birt með hverri
uppfærslu á opinberu spjallborðunum, <https://forums.frontier.co.uk/> - „Journal Manual“,
v4.x), atburðir og reitir eins og þar er skjalað; fánar Status.json samkvæmt kaflanum „Status File“
í sömu handbók.

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | ljósár (raðir vetrarbrautarinnar, lota 'galaxy'); metrar austur/upp/norður frá fyrstu staðsetningu á hnetti (yfirborðsraðir, lota = nafn hnattar) |
| Speglað fyrir skoðarann | `z` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `log`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (skrár sem leikurinn skrifar meðan hann keyrir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- sérhver dagbókarlína sem röð undir `event` sínu, með einföldu reitina sína (staðfærði textinn þar sem leikurinn gefur einn; textar lengri en 300 stafir styttir í röðinni)
- raðir vetrarbrautarinnar (StarPos) við FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; yfirborðsraðir úr Status.json og Touchdown/Liftoff
- einfaldir reitir Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) á yfirborðsröðunum
- tölfræðin: stökk, vegalengd, dauðsföll, dráp, inneignir sem aflað var, verkefni, hnettir skannaðir, kerfi heimsótt, tengingar við stöð, lendingar

**Geymt hrátt**

- sérhver dagbókarlína heil, `type` = `event` hennar (FSDJump, Scan, Music, ReceiveText, ...), `used` satt: listarnir og hlutirnir sem raðirnar sleppa (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) eru aðeins hér
- dagbókarlína sem er ekki JSON, `type` `unparsed`
- sérhver fylgiskrá heil í hvert sinn sem leikurinn endurskrifar hana, `type` = skráarheiti hennar: `Status.json` (`used` þegar hún bjó til yfirborðsröð), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, og sérhver önnur `*.json` sem leikurinn skrifar þar

**Ekki fáanlegt**

- staða milli stökka (innan kerfis, í supercruise eða venjulegu rými): leikurinn skrifar aðeins StarPos kerfisins og, nálægt reikistjörnu, breiddargráðu, lengdargráðu og hæð
- staða annarra skipa og spilara: dagbókin er frásögn foringjans sjálfs
- hraði, inngjöf og önnur flugfjarmæling: leikurinn skrifar hana ekki
- dagbækur og fylgiskrár fyrri setna: geymt þegar þær voru spilaðar (fylgjandinn byrjar í lok skrár sem er eldri en þessi keyrsla leiksins)
- vef-API Frontier fyrir fylgiforrit (cAPI): krefst innskráningar spilarans hjá Frontier; ekki skrá sem leikurinn skrifar

**Stærð**: um 1-5 MB af hráum texta á klukkustund: dagbókin 0,2-2 MB, Status.json (undir 1 KB, endurskrifuð allt að á hverri sekúndu) 1-2 MB, sett af markaði/útbúnaði/skipasmíði 20-150 KB fyrir hverja stöð sem er heimsótt; zstd í heat.raw.parquet gerir það um tíunda hluta

## Staðfest {#verified}

þáttarinn (parser) endurspilaður yfir raunverulegar dagbókarskrár úr staðbundinni uppsetningu (fjöldi atburða stemmir við tölfræðina); yfirborðsstaðsetningar Status.json prófaðar aðeins á tilbúnum skyndimyndum

## Heimild {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
