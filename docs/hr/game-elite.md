---
title: "Elite Dangerous (datoteke dnevnika)"
nav_order: 18
lang: "hr"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (datoteke dnevnika) {#elite-dangerous-log-files}

Dok igrate Elite Dangerous, watcher čita datoteke koje igra piše i sprema što se dogodilo, pa to kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `elite`, vrsta [`log`](sources-and-rules.md); radi dok je `EliteDangerous64.exe` pokrenut i traži nove podatke svakih 0,25 s.*

## Što se bilježi {#what-is-recorded}

- svaki događaj dnevnika igrača, pod nazivom iz dnevnika, s njegovim običnim poljima
- položaj u galaksiji (StarPos, svjetlosne godine) pri skokovima, lokacijama, pojavljivanjima, smrtima, pristajanju i sletanju
- pojavljivanje pri LoadGame/Resurrect, smrt pri Died, pristajanje/odlazak s pristaništa, dodir tla/polijetanje, skok, session_end
- ruta po površini planeta iz Status.json: geografska širina, dužina, visina, smjer, i metri u lokalnoj tangencijalnoj ravnini po tijelu (sesija = naziv tijela), uz ostala obična polja Status.json-a (Flags, Flags2, GuiFocus, LegalState, ...)
- svaki redak dnevnika igrača i svaka pomoćna datoteka cijela u heat.raw.parquet
- skokovi, prijeđena udaljenost skokovima, smrti, ubojstva, zarađeni krediti, dovršene misije, skenirana tijela, posjećeni sustavi, pristajanja, sletanja

## Odakle dolaze {#where-it-comes-from}

Dnevnik igrača %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (najnovija datoteka, prati se dok se piše), Status.json i ostale pomoćne datoteke \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) u istoj mapi

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Elite Dangerous: dnevnik igrača i Status.json koje igra piše dok radi.

Gdje: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - jedan JSON objekt po retku, jedna datoteka po pokretanju (duga sesija nastavlja u dijelu .02, .03 ...). Svaki redak ima `timestamp` (UTC, ISO 8601) i `event`. Položaji u galaksiji su `StarPos` [x, y, z] sustava, u svjetlosnim godinama od Sunca, pri `FSDJump`, `Location` i `CarrierJump`. Galaktički okvir Elite-a ima y gore (prema sjevernom galaktičkom polu), z prema galaktičkom središtu i x prema galaktičkoj dužini 270 - lijevorukan okvir, pa preglednik zrcali z kako bi se crtao ispravno.
* `Status.json` - cijel se ponovno piše pri svakoj promjeni stanja broda: `Flags`, a blizu planeta `Latitude`, `Longitude` (stupnjevi), `Altitude` (metri), `Heading`, `BodyName` i `PlanetRadius` (metri).
* Ostale pomoćne datoteke, svaka se cijela ponovno piše kad se odgovarajući događaj dnevnika zapiše: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Svaki `*.json` mape koji igra u ovoj sesiji napiše čuva se cijel pri svakoj promjeni, pod svojim nazivom datoteke (pravilo pretvarača 3DHeat: što izvor sadrži, to se čita ili čuva).

Svaki redak dnevnika čuva se cijel u sesijskoj sirovoj pomoćnoj datoteci pod svojim `event`, svaka pomoćna datoteka pod svojim nazivom; redak koji nije JSON ide pod `unparsed`.

Položaji na površini stavljaju se u lokalnu tangencijalnu ravninu po tijelu, u metrima: prva točka na tijelu je ishodište, x istok, z sjever, y gore (visina), ista orijentacija kao galaktički okvir, a retci nose naziv tijela kao svoj `session`, pa se vožnja ili hodanje po planetu crta kao zasebna ruta. Reci galaksije imaju sesiju "galaxy". Obje ljestvice su u jednoj tablici; sesiju birate u pregledniku.

Format: priručnik "Elite Dangerous Player Journal" tvrtke Frontier (objavljuje se uz svako ažuriranje na službenim forumima, <https://forums.frontier.co.uk/> - "Journal Manual", v4.x); događaji i polja kako su ondje dokumentirani; zastavice Status.json-a prema poglavlju "Status File" istog priručnika.

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os gore | `y` |
| Jedinice | svjetlosne godine (retci galaksije, sesija 'galaxy'); metri istok/gore/sjever od prve točke na tijelu (retci površine, sesija = naziv tijela) |
| Zrcaljenje za preglednik | `z` |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `log`: čita samo ono što igra ili platforma predaje (datoteke koje igra piše dok radi), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- svaki redak dnevnika kao redak pod svojim `event`, s njegovim običnim poljima (lokalizirani tekst tamo gdje ga igra daje; tekstovi duži od 300 znakova skraćuju se u retku)
- retci galaksije (StarPos) pri FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; retci površine iz Status.json i Touchdown/Liftoff
- obična polja Status.json-a (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) na retcima površine
- statistika: skokovi, udaljenost, smrti, ubojstva, zarađeni krediti, misije, skenirana tijela, posjećeni sustavi, pristajanja, sletanja

**Čuva se sirovo**

- svaki redak dnevnika cijel, `type` = njegov `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` true: popisi i objekti koje retci izostavljaju (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) nalaze se samo ovdje
- redak dnevnika koji nije JSON, `type` `unparsed`
- svaka pomoćna datoteka cijela svaki put kad je igra ponovno napiše, `type` = naziv datoteke: `Status.json` (`used` kad je stvorio redak površine), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, i svaki ostali `*.json` koji igra tamo piše

**Nije dostupno**

- položaj između skokova (u sustavu, u supercrusiseu ili normalnom prostoru): igra piše samo StarPos sustava i, blizu planeta, geografsku širinu, dužinu i visinu
- položaji drugih brodova i igrača: dnevnik je vlastiti račun zapovjednika
- brzina, gas i ostala podatka o letu: igra ih ne piše
- dnevnici i pomoćne datoteke ranijih sesija: čuvaju se kad su se igrale (watcher počinje na kraju datoteke starije od ovog pokretanja igre)
- Frontierovo web sučelje za pratnju (cAPI): traži prijavu igrača u Frontier; nije datoteka koju igra piše

**Veličina**: oko 1-5 MB sirovog teksta po satu: dnevnik 0,2-2 MB, Status.json (ispod 1 KB, ponovno se piše do svake sekunde) 1-2 MB, skup tržišta/opremanja/brodogradilišta 20-150 KB po postaji koju ste posjetili; zstd u heat.raw.parquet čini to oko desetinu

## Provjereno {#verified}

parser ponovno pušten nad stvarnim datotekama dnevnika s lokalne instalacije (broj događaja se slaže sa statistikom); prijelomne točke površine iz Status.json-a testirane samo na sintetičkim snimkama

## Izvor {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
