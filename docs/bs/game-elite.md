---
title: "Elite Dangerous (log datoteke)"
nav_order: 18
lang: "bs"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (log datoteke) {#elite-dangerous-log-files}

Dok igrate Elite Dangerous, watcher čita datoteke koje igra piše i sprema šta se desilo, da to kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `elite`, vrsta [`log`](sources-and-rules.md); radi dok je pokrenut `EliteDangerous64.exe` i svakih 0,25 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- svaki događaj iz dnevnika (journal), pod svojim imenom iz dnevnika, s njegovim običnim poljima
- galaktički položaj (StarPos, svjetlosne godine) pri skokovima, lokacijama, spawnovima, smrtima, pristajanju, slijetanju
- spawn pri LoadGame/Resurrect, smrt pri Died, docked/undocked, touchdown/liftoff, jump, session_end
- ruta po površini planeta iz Status.json: geografska širina, dužina, visina, kurs, i metri u tangencijalnoj ravni po tijelu (sesija = ime tijela), s ostalim običnim poljima iz Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- svaka linija dnevnika i svaka prateća datoteka cijela u heat.raw.parquet
- skokovi, preskočena udaljenost, smrti, kills, zarađeni krediti, završene misije, skenirana tijela, posjećeni sistemi, pristajanja, slijetanja

## Odakle dolazi {#where-it-comes-from}

Player Journal %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (najnovija datoteka, prati se dok se piše), Status.json i druge prateće \*.json datoteke (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) u istom folderu

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Elite Dangerous: Player Journal i Status.json koje igra piše dok radi.

Gdje: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - jedan JSON objekt po liniji, jedna
  datoteka po pokretanju (duga sesija nastavlja u dijelu .02, .03 ...). Svaka linija
  ima `timestamp` (UTC, ISO 8601) i `event`. Galaktički položaji su
  `StarPos` [x, y, z] sistema, u svjetlosnim godinama od Sola, pri `FSDJump`,
  `Location` i `CarrierJump`. Elite-ov galaktički okvir ima y gore (prema
  galaktičkom sjeveru), z prema galaktičkom jezgru i x prema galaktičkoj dužini
  270 - lijevoruki okvir, pa preglednik zrcali z da ga nacrta ispravno
  okrenutog.
* `Status.json` - prepisuje se cijel kad god se promijeni stanje broda: `Flags`,
  a blizu planete `Latitude`, `Longitude` (stepeni), `Altitude` (metri),
  `Heading`, `BodyName` i `PlanetRadius` (metri).
* Ostale prateće datoteke, svaka se prepisuje cijela kad se napiše odgovarajući
  događaj dnevnika: `Market.json`, `Outfitting.json`, `Shipyard.json`,
  `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`,
  `Backpack.json`, `FCMaterials.json`. Svaki `*.json` iz foldera koji
  igra napiše u ovom igranju čuva se cijel pri svakoj promjeni
  (3DHeat-ovo pravilo konvertera: ono što izvor sadrži se čita ili čuva), pod svojim imenom datoteke.

Svaka linija dnevnika čuva se cijela u sirovom sidecar-u sesije pod svojim
`event`, svaka prateća datoteka pod svojim imenom datoteke; linija koja nije JSON
pod `unparsed`.

Položaji na površini stavljaju se u lokalnu tangencijalnu ravan po tijelu, u metrima: prvi
fiks na tijelu je njegovo ishodište, x istok, z sjever, y gore (visina), ista
orijentacija kao u galaktičkom okviru, a redovi nose ime tijela kao svoj
`session`, pa se vožnja ili hodanje po planeti crta kao vlastita ruta. Galaktički
redovi imaju sesiju "galaxy". Obje skale žive u jednoj tabeli; sesiju birate
u preglednik-u.

Format: Frontierov priručnik "Elite Dangerous Player Journal" (objavljuje se uz svako
ažuriranje na službenim forumima, <https://forums.frontier.co.uk/> - "Journal Manual",
v4.x), događaji i polja kako su tamo dokumentirani; zastavice Status.json prema poglavlju
"Status File" istog priručnika.

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | svjetlosne godine (galaktički redovi, sesija 'galaxy'); metri istok/gore/sjever od prvog fiksa na tijelu (redovi površine, sesija = ime tijela) |
| Zrcaljeno za preglednik | `z` |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `log`: čita samo ono što igra ili platforma daje (datoteke koje igra piše dok radi), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- svaka linija dnevnika kao red pod svojim `event`, s običnim poljima (lokalizirani tekst gdje ga igra daje; tekstovi duži od 300 znakova skraćeni u redu)
- galaktički redovi (StarPos) pri FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; redovi površine iz Status.json i Touchdown/Liftoff
- obična polja Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) na redovima površine
- statistika: skokovi, distanca, smrti, kills, zarađeni krediti, misije, skenirana tijela, posjećeni sistemi, pristajanja, slijetanja

**Čuva se sirovo**

- svaka linija dnevnika cijela, `type` = njen `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` true: liste i objekti koje redovi izostavljaju (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) nalaze se samo ovdje
- linija dnevnika koja nije JSON, `type` `unparsed`
- svaka prateća datoteka cijela svaki put kad je igra prepiše, `type` = njeno ime datoteke: `Status.json` (`used` kad je dala red površine), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, i svaki drugi `*.json` koji igra tamo piše

**Nije dostupno**

- položaj između skokova (unutar sistema, u supercruise ili normalnom prostoru): igra piše samo StarPos sistema i, blizu planete, geografsku širinu, dužinu i visinu
- položaji tuđih brodova i igrača: dnevnik je komandantov vlastiti izvještaj
- brzina, gas i druga telemetrija leta: igra ih ne piše
- dnevnici i prateće datoteke ranijih igranja: čuvaju se kad su se igrali (pratilac počinje na kraju datoteke starije od ovog pokretanja igre)
- Frontierov prateći web API (cAPI): traži igračevu Frontier prijavu; nije datoteka koju igra piše

**Veličina**: oko 1-5 MB sirovog teksta na sat: dnevnik 0,2-2 MB, Status.json (ispod 1 KB, prepisuje se do svake sekunde) 1-2 MB, komplet market/outfitting/shipyard 20-150 KB po posjećenoj stanici; zstd u heat.raw.parquet to svodi na otprilike desetinu

## Provjereno {#verified}

parser puštan preko pravih datoteka dnevnika s lokalne instalacije (brojevi događaja se poklapaju sa statistikom); fiksevi površine iz Status.json testirani samo na sintetičkim snimcima stanja

## Izvor {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
