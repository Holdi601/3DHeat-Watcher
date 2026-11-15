---
title: "War Thunder (leikjastaða)"
nav_order: 46
lang: "is"
source: game-warthunder-webmap.md
source_hash: "34a876e38f09"
nav_exclude: true
search_exclude: true
---
# War Thunder (leikjastaða) {#war-thunder-game-state}

Meðan þú spilar War Thunder vistar watcher það sem leikurinn tilkynnir til forrita á þinni eigin tölvu, svo þú getir skoðað það síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `warthunder-webmap`, gerð [`gsi`](sources-and-rules.md); það keyrir meðan `aces.exe` er í gangi og leitar að nýjum gögnum á 0,5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- eigin staða (kort austur/norður í metrum; hæð úr /state í loftfari, annars 0) tvisvar á sekúndu, stefna, hraði
- endurfæðingar og það að eigið farartæki yfirgefur kortið (eyðilagt, lent, aftur í hangar), ein sortie hver
- önnur loftför og landeiningar á smákortinu sem staðsetningar með rakin auðkenni og hlið (engin hæð)
- flugvellir, hertökusvæði og bækistöðvar einu sinni, og svæði sem skipta um hlið
- línur í dráps- og skaðastraumnum (hver, farartæki, sögn); dráp og dauðsföll spilarans þegar nafnið þitt er stillt (`config --set player_names.warthunder-webmap=<name>`)
- endurfæðingar, vegalengd, mesta hæð, mesti sanni lofthraði, farartæki; dráp og dauðsföll þegar nafnið þitt er stillt
- hvert svar vefkortsins geymt í heild í heat.raw.parquet - allt /state og /indicators, spjallið, markmið bardagans og mynd kortsins með; milli bardaga í lotu út af fyrir sig

## Hvaðan það kemur {#where-it-comes-from}

staðbundið vefkort leiksins, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Hvernig á að kveikja á því {#how-to-switch-it-on}

Engu þarf að kveikja á: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

## Hvernig það virkar {#how-it-works}

War Thunder: eigið staðbundið vefkort leiksins á <http://127.0.0.1:8111>.

Leikurinn þjónar síðunni sem annar skjár eða sími getur sýnt ("vefkortið"),
og JSON-gögnunum á bak við hana, meðan hann keyrir - í öllum hömum, líka fjölspilun:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: the map's extent in metres; valid false in the hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: what the minimap shows, the player's own
                  vehicle with icon "Player"; no ids, no heights
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: flight values,
                  valid only in an aircraft
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} newer than the ids given, each
                  {"id", "msg", "sender", "enemy", "mode", "time"}; damage lines read like
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  the chat newer than the id given, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    the battle's objectives and their status
/map.img         the map's picture the page draws the objects on
```

Hvert svar er geymt í heild í hráu hliðarskrá lotunnar undir endapunkti sínum
(map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img);
milli bardaga fara svörin í lotu út af fyrir sig.

Kortastaða verður að metrum með útbreiðslunni: u = min_x + x \* (max_x - min_x)
austur, v = max_y - y \* (max_y - min_y) norður (y myndarinnar liggur niður). Raðirnar eru
x = u, y = hæð ("H, m" eigin loftfars; 0 fyrir allt annað), z = v, svo
Y er upp; z er speglað fyrir skoðarann svo norður sé ekki teiknað í suður.

Litirnir segja til um hliðarnar eins og spilarinn sér þær: eigin gulur (#faC81E sjálfgefið),
sveit græn, bandamenn bláir (#174DFF), óvinir rauðir (#f40C00); litblindupallettur
breyta þeim, svo blærinn ræður, ekki nákvæmt gildi. Leikurinn nefnir engan á
kortinu og gefur hlutum engin auðkenni: aðrir hlutir fá auðkenni hér með því að fylgja þeim
frá könnun til könnunar (næsti af sömu gerð og tákni), sem getur víxlað tveimur
loftförum af sömu gerð sem fara nálægt hvort öðru. Eigið nafn spilarans er heldur ekki í
API-inu: gefðu það upp í stillingunum (`config --set
player_names.warthunder-webmap=<your name>`) og línur í drápsstraumnum um
spilarann verða að drápum og dauðsföllum; án þess eru þær skráðar sem drápsstraumurinn.

Heimildir: eigin síða leiksins á <http://127.0.0.1:8111> og JSON hennar; staðreyndir um reiti
eins og JoyPro 2 verkefnið skjalfestir þær (docs/telemetry-recording.md; GPL, notað aðeins fyrir
staðreyndir).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar (kort austur/norður; hæð aðeins fyrir eigið loftfar) |
| Speglað fyrir skoðarann | `z` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `gsi`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (game-state integration eða staðbundið API sem leikurinn þjónar), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er hver pakki, síða, lína eða svar sem millistykkið fær geymt í heild í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, svo hver reitur sem geymdur er með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hvert `type` - `lost` er 0.

**Lesið**

- /map_info.json: útbreiðsla kortsins og hnitanet (metrar, auðkenni kortsins) í meta.json; ógilt svar lýkur bardaganum
- /map_obj.json (tvisvar á sekúndu): eigið farartæki, önnur loftför og landeiningar (rakin auðkenni, hlið úr litnum, tákn, stefna, litur) og flugvellir, svæði og bækistöðvar sem raðir
- /state (tvisvar á sekúndu, í loftfari): hæð, TAS, IAS, Mach og Vy á eigin röðum
- /indicators (á 2 s fresti): gerð hers (army) og farartækis
- /hudmsg (einu sinni á sekúndu): línur í dráps- og skaðastraumnum sem dráp, dauðsföll, skot og straumraðir; aðrir HUD-atburðir sem raðir

**Geymt óunnið**

- hvert svar í heild, `text` er JSON eins og leikurinn sendi það, undir endapunkti sínum: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` bæti kortamyndarinnar sem `payload`, einu sinni í bardaga
- það sem aðeins hráa hliðarskráin geymir: hver reitur í /state umfram þá fimm sem eru lesnir (AoA, AoS, Ny, Wx, inngjöf, RPM, eldsneyti, ... - mengi eins loftfars er ólíkt öðru), hver reitur í /indicators (mælar í stjórnklefa loftfara, hraði, gír, áhöfn og stöðugleikabúnaður skriðdreka), aðrir lyklar kortahlutanna (color[], blink, icon_bg, flugvallarendar), sender, enemy og mode í hudmsg, spjallið (/gamechat, einu sinni á sekúndu), markmið bardagans og staða þeirra (/mission.json, á 10 s fresti í bardaga), línur sem sagðar voru áður en watcher ræsti
- milli bardaga (hangar, hleðsla) fara svörin í lotu út af fyrir sig, merkta `between_battles` í meta.json, sem hefur engar raðir

**Ekki tiltækt**

- nöfn, auðkenni og hæðir farartækja annarra spilara: vefkortið hefur ekkert af þessu (auðkenni eru gefin hér með því að fylgja hlutum frá könnun til könnunar); drápsstraumurinn nefnir spilara án staðsetninga
- allt utan vefkortsins: endursýningar leiksins eru lesnar af warthunder-endursýningabreytinum, og minni leiksins er aldrei lesið (netleikur)
- /map_obj.json oftar en tvisvar á sekúndu: könnunartíðnin er höfð lág svo vefþjónn leiksins sjálfs verði ekki fyrir álagi

**Stærð**: um 50-120 MB á klukkustund af JSON fyrir zstd í bardaga (map_obj 5-15 KB tvisvar á sekúndu, state um 1,5 KB tvisvar á sekúndu, indicators á 2 s fresti, spjall og HUD-línur litlar) auk kortamyndarinnar einu sinni í bardaga (undir 2 MB); 1-2 MB á klukkustund milli bardaga (kortið tvisvar á sekúndu, HUD og spjall einu sinni, hvert stutt svar); zstd minnkar endurtekið JSON vel yfir tífalt

## Staðfest {#verified}

prófað gegn gervi-staðbundnum þjóni sem svarar á sniði vefkorts leiksins; óprófað gegn leiknum í keyrslu

## Heimild {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
