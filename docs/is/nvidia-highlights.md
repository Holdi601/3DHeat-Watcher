---
title: "NVIDIA Highlights"
nav_order: 8
lang: "is"
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Sumir leikir biðja NVIDIA-skjákortsreklann þinn að vista stutt myndskeið þegar eitthvað gerist, eins og dráp.
Watcher skráir hvert þessara augnablika og, þegar það getur, setur það á kortið þar sem það gerðist.

Millistykkið `nvidia-highlights` skráir klippurnar, highlights og skjámyndirnar sem NVIDIA App (eða
GeForce Experience) vistar, og gefur hverju stað á kortinu þegar það getur. Þessi síða útskýrir hvað
NVIDIA Highlights getur skilað og hvað ekki, hvaða skrár watcher les, og hvernig highlight
fær staðsetningu. Sjálfvirka síða millistykkisins er [NVIDIA highlights (vettvangur)](game-nvidia-highlights.md).

## Hvað NVIDIA Highlights getur skilað og hvað ekki {#what-nvidia-highlights-can-and-cannot-deliver}

Leikur sem styður NVIDIA Highlights talar við NVIDIA App í gegnum GfeSDK frá NVIDIA. SDK-ið
ber aðeins tvær gerðir skilaboða:

1. **Einu sinni, í byrjun**: gerðir highlights sem leikurinn mun nota - auðkenni (eins og `kill`),
   mikilvægi, merki og birtingarheiti fyrir hvert tungumál. NVIDIA App geymir þetta fyrir hvern leik.
2. **Á augnabliki í spilun**: "highlight `<id>`, frá `<ms>` fyrir núna til `<ms>` eftir". Það er
   öll skilaboðin: auðkenni gerðar sem leikurinn skráði, og tvær tímafærslur sem segja NVIDIA App
   hvaða hluta af rúllandi upptöku sinni á að halda.

SDK-ið hefur **engan reit fyrir neitt annað**: enga staðsetningu, enga viðureign eða lotu, engan andstæðing, ekkert vopn, engin
stig, engin sérsniðin gögn af neinu tagi. Leikur getur ekki sett staðsetningu í highlight þótt hann vildi.
Þegar klippan er vistuð bætir NVIDIA App við skrá, leikheiti, lengd og tíma.

Allt sem highlight getur sagt er því "þessi gerð augnabliks, í þessum leik, á þessum tíma". Allt umfram það
verður að koma annars staðar frá.

## Hvað watcher les {#what-the-watcher-reads}

Allt er lesið úr skrám sem NVIDIA App skrifar fyrir sitt eigið gallerí. Ekkert talar við
rekilinn eða forritið. NVIDIA Overlay-mappan er
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Skrá | Hvað er tekið úr henni |
|---|---|
| `UGCTracker.json` | gallerívísirinn: hver klippa og skjámynd með slóð, gerð (video, image), undirgerð (`InstantReplay`, ...), dagsetningu, sniðsheiti leiksins, keyrsluskrá og stutt heiti, og lengd (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, upptökumappan, og `settings.tempDirectory`, þar sem highlights bíða (`<temp>\Highlights\<game>`) þar til þau eru vistuð |
| `Highlights\<game>\config.json` | gerðir highlights sem hver leikur skráði: auðkenni, og enska birtingarheitið (eða auðkennið þar sem leikurinn gaf ekkert) |
| upptökumappan (sjálfgefið `%USERPROFILE%\Videos\NVIDIA`) og `<temp>\Highlights` | klippu- og skjámyndaskrárnar sjálfar (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), ein mappa fyrir hvern leik |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | beiðnirnar sem GfeSDK-leikir skrá - `Posted Request HL...` línur - svo highlight sem leikurinn bað um er skráð jafnvel þótt engin klippa hafi verið geymd. Stillingarbeiðnum (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) er sleppt. |

Fyrir hvern nýjan hlut skrifar millistykkið eina röð: `highlight` fyrir myndskeið, `screenshot` fyrir mynd, eða
`highlight_request` fyrir GfeSDK-annálslínu. Reitir hennar:

| Reitur | Hvað það er |
|---|---|
| `ms` | augnablikið: tíminn í skráarheitinu (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, staðartíminn þegar klippan var vistuð), annars dagsetning vísisins, annars breytingartími skrárinnar |
| `game` | sniðsheiti NVIDIA, heiti möppunnar eða leikurinn í skráarheitinu |
| `clip`, `media` | slóð skrárinnar; `video`, `image` eða `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (úr tímabundnu highlights-möppunni) eða undirgerð vísisins |
| `duration_s`, `clip_start_ms` | lengdin, úr vísinum eða úr eigin haus myndskeiðsins (`moov/mvhd`, fundinn án þess að lesa myndskeiðið); augnablikið sem klippan byrjar |
| `highlight_id`, `highlight_name` | gerð highlight, þegar eitthvað nefnir hana (sjá hér á eftir) |
| `exe` | keyrsluskrá leiksins, úr vísinum |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | fengna staðsetningin, þegar hún fannst (sjá hér á eftir) |

Tölfræði lotunnar er `clips`, `screenshots`, `clip_seconds` og `placed` (hlutir sem fengu
staðsetningu).

**Auðkenni highlight** er ekki skrifað á neinn skjalfestan stað. Millistykkið reynir tvo óskjalfesta:
reit í gallerífærslunni sem heiti inniheldur "highlight", og - aðeins fyrir skrár í
tímabundnu highlights-möppunni - eitt af skráðum auðkennum leiksins (að minnsta kosti 4 stafir) sem
kemur fyrir í skráarheitinu. Vistuð klippa er nefnd eftir leiknum, sem gæti innihaldið auðkenni eins og "kill"
fyrir tilviljun, svo heiti hennar er ekki leitað. Ekki hefur sést að þessar tvær leiðir virki á raunverulegri vél
enn: engin klippa með highlight-auðkenni og engin GfeSDK-beiðnilína hefur komið fyrir þar sem millistykkið var
prófað. Gallerívísirinn, stillingar, highlight-skilgreiningar og klippur voru prófuð á raunverulegum skrám.

### Hvenær hlutir eru skráðir {#when-items-are-recorded}

- Klippa er enn skrifuð um stund eftir lyklaýtinguna. Millistykkið bíður þar til skrá hefur
  sömu stærð og tíma í tveimur skoðunum (á 10 s fresti) og er að minnsta kosti 5 s gömul.
- Í fyrsta skipti sem millistykkið keyrir er allt sem þegar er í galleríinu og annálunum aðeins skráð niður en ekki
  tekið upp, svo ára gamlar klippur flæði ekki yfir tölfræðina. Það sem það hefur séð er geymt í
  `<data>\state\nvidia-highlights.json`, svo endurræsing skráir ekkert tvisvar.
- Hlutir eru flokkaðir í eina lotu fyrir hvern leik. Lota leiks lokast eftir 30 mínútur án nýs
  hlutar, og endar á síðasta augnabliki sínu frekar en þegar hún lokaðist. Augnablik með meira en 30 mínútna millibili fara
  í aðskildar lotur.

## Hvernig highlight fær staðsetningu {#how-a-highlight-gets-a-position}

Highlight sjálft hefur engan stað. Millistykkið flettir augnablikinu upp í hinum upptökunum sem
watcher gerði af sama leik á sama tíma:

1. **Sami leikur**: lotumöppurnar undir `<data>\sessions\` þar sem leikheitið passar við
   leikheiti highlight. Heiti eru borin saman með litlum stöfum, aðeins bókstafir og tölustafir. Þau passa þegar þau eru
   eins, eða þegar það styttra hefur að minnsta kosti 5 stafi og er innihaldið í því lengra
   (`Counter-Strike 2` og `Counter-Strike-2`).
2. **Sami tími**: lotur þar sem upphaf og endir (úr `meta.json`, með sekúndu svigrúmi í báða
   enda) ná yfir augnablikið. Lotum sem enduðu án staðsetninga, og eigin lotum millistykkisins, er
   sleppt.
3. **Eigin röð spilarans**: í `events.jsonl` þeirra, nýjasta af eigin röðum spilarans með
   staðsetningu, á augnablikinu eða fyrir það og ekki meira en 5 sekúndum fyrir það. Röð er eigin röð spilarans
   þegar heimild hennar segir það: `"player": "me"`, eða `"own_car": 1` (kappakstursleikir sem skrá hvern bíl eftir
   ökumanni sínum), eða `player` sem er `player` lotunnar í `meta.json` (nafnið sem heimildin gefur
   spilaranum). Sjá [Eigin raðir spilarans](the-data.md#the-players-own-rows).

Ef röð finnst fær highlight sitt `x`, `y`, `z`, sitt `session` (eða heiti möppunnar),
`position_from` (möppuna sem það kom úr) og `position_lag_ms` (hve löngu fyrir augnablikið sú röð
var). Highlight-lotan tekur ása þeirrar upptöku, svo hún er teiknuð á sama veg. Ef engin röð
finnst er highlight áfram augnablik á tímalínunni án staðar.

Þetta þarf að vita um fengnu staðsetninguna:

- **Hún er þar sem þú varst þegar klippan var vistuð**, ekki þar sem aðgerðin hófst. Augnablikið er
  vistunartíminn í skráarheitinu, sem fyrir Instant Replay er endir þess. `clip_start_ms` segir hvenær
  klippan byrjar.
- **Annað millistykki þarf að hafa verið að taka upp sama leik á þeim tíma.** Þau sem merkja
  eigin raðir spilarans, og geta því staðsett highlight: Counter-Strike 2 og Dota 2 game-state integration,
  Forza, Assetto Corsa leikirnir, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive,
  Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War
  Thunder, Minecraft og minnissnið (sem `me`); F1 23/24/25, RaceRoom, Automobilista 2 og Project
  CARS 2 (raðir bílsins þíns bera `own_car` 1, eftir vísi bíls spilarans í leiknum, eigin sæti hans eða þátttakandanum sem er horft á);
  Elite Dangerous (nafn herforingjans, í `meta.json` sem `player`, þar sem dagbókin er
  alltaf spilarans).
- **Endursýning er umbreytt eftir viðureignina**, svo hún getur aðeins staðsett klippu sem er flett upp eftir
  umbreytinguna: klippan er staðsett þegar hún er tekin upp, og endursýning sem er vistuð seinna er ekki skoðuð aftur.
  Endursýningar League of Legends nefna raðir þínar eftir Riot ID í stillingunum og, með Riot API lykli, gefa
  þeim veggklukkutímann sem tímalína viðureignarinnar tilgreinir, svo þær finnast þá. CS2-demó getur ekki staðsett
  highlight yfirhöfuð: staðsetningar þess eru í eigin töflu umbreytisins, ekki í `events.jsonl`, og demó
  hefur ticks leiksins en engan veggklukkutíma til að bera augnablik klippu saman við.
- Í Rocket League eru einu raðirnar með stað boltaatburðir. Bolti sem þú slærð er röð frá þér,
  svo highlight getur verið staðsett þar sem þú sló boltann síðast.
- Leikir án nokkurrar staðsetningarheimildar (Overwatch 2, Call of Duty, Hunt: Showdown, ...) halda
  highlights sínum sem tímalínu augnablika.

## Hvers vegna minni getur ekki gefið staðsetningu í fjölspilun {#why-memory-cannot-give-a-position-in-multiplayer}

Hin leiðin til að fá staðsetningu væri að lesa hana úr minni. Hvorugt minnið gengur:

- **Minni NVIDIA hefur enga staðsetningu.** NVIDIA App fær það sem GfeSDK ber - auðkenni
  highlight og tvær tímafærslur - auk myndskeiðsins sem það tekur upp. Hvergi hjá NVIDIA er staðsetning til að lesa.
  (Watcher les ekki minni NVIDIA hvort sem er; það les skrárnar hér að ofan.)
- **Minni leiksins er bannað í fjölspilun.** Staðsetningin er í ferli leiksins, en
  watcher les aldrei minni fjölspilunarleiks: minnismillistykki fyrir leik sem er merktur spilaður á netinu
  er hafnað áður en nokkuð er opnað (sjá [Minnislestur](memory-reading.md)). Fjölspilunarleikir keyra
  undir svindlvörnum (Easy Anti-Cheat, BattlEye, Vanguard, ...) sem líta á það sem svindl þegar annað forrit opnar
  ferli leiksins, og það getur leitt til banns á aðganginum. Að lesa stöðu leiksins utan frá
  er einnig það sem skilmálar leikjanna banna. Highlight í fjölspilunarleik fær því stað aðeins
  úr því sem leikurinn birtir: game-state integration hans eða fjarmælingu, skráð af öðru millistykki á
  sama tíma.
