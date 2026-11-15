---
title: "Elite Dangerous (skedarë regjistri)"
nav_order: 18
lang: "sq"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (skedarë regjistri) {#elite-dangerous-log-files}

Ndërsa luan Elite Dangerous, watcher i lexon skedarët që loja i shkruan dhe ruan çfarë ndodhi, që t'i shohësh më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `elite`, lloji [`log`](sources-and-rules.md); punon sa kohë `EliteDangerous64.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.25 s.*

## Çfarë regjistrohet {#what-is-recorded}

- çdo ngjarje e ditarit (journal), nën emrin e saj në ditar, me fushat e saj të thjeshta
- pozicioni në galaktikë (StarPos, vite dritë) te kërcimet, vendndodhjet (locations), spawn-et, vdekjet, ankorimi, uljet
- spawn te LoadGame/Resurrect, vdekja te Died, docked/undocked, touchdown/liftoff, jump, session_end
- rruga në sipërfaqen e planetit nga Status.json: gjerësia, gjatësia, lartësia, drejtimi (heading), dhe metra në një plan tangjent për çdo trup (sesioni = emri i trupit), me fushat e tjera të thjeshta të Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- çdo rresht i ditarit dhe çdo skedar shoqërues i plotë te heat.raw.parquet
- kërcimet, distanca e kërcyer, vdekjet, vrasjet, kreditet e fituara, misionet e përfunduara, trupat e skanuar, sistemet e vizituara, ankorimet, uljet

## Nga vjen {#where-it-comes-from}

Player Journal %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (skedari më i ri, ndiqet ndërsa shkruhet), Status.json dhe skedarët e tjerë shoqërues \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) në të njëjtën dosje

## Si ta ndezësh {#how-to-switch-it-on}

Nuk ka asgjë për të ndezur: watcher e lexon burimin ashtu siç e ofron loja ose platforma.

## Si funksionon {#how-it-works}

Elite Dangerous: Player Journal dhe Status.json që loja i shkruan sa kohë punon.

Ku: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - një objekt JSON për rresht, një
  skedar për çdo nisje (një sesion i gjatë vazhdon në pjesën .02, .03 ...). Çdo rresht
  ka `timestamp` (UTC, ISO 8601) dhe `event`. Pozicionet në galaktikë janë
  `StarPos` [x, y, z] i sistemit, në vite dritë nga Dielli (Sol), te `FSDJump`,
  `Location` dhe `CarrierJump`. Kuadri galaktik i Elite ka y lart (drejt veriut
  galaktik), z drejt bërthamës galaktike dhe x drejt gjatësisë galaktike
  270 - një kuadër i majtë, prandaj shikuesi e pasqyron z-në për ta vizatuar drejt.
* `Status.json` - rishkruhet i plotë sa herë ndryshon gjendja e anijes: `Flags`,
  dhe pranë një planeti `Latitude`, `Longitude` (gradë), `Altitude` (metra),
  `Heading`, `BodyName` dhe `PlanetRadius` (metra).
* Skedarët e tjerë shoqërues, secili rishkruhet i plotë kur shkruhet ngjarja
  përkatëse e ditarit: `Market.json`, `Outfitting.json`, `Shipyard.json`,
  `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`,
  `Backpack.json`, `FCMaterials.json`. Çdo `*.json` i dosjes që
  loja e shkruan në këtë seancë ruhet i plotë sa herë ndryshon (rregulli i
  konvertuesit të 3DHeat: çfarë mban burimi lexohet ose ruhet), nën emrin e skedarit.

Çdo rresht i ditarit ruhet i plotë te skedari anësor i papërpunuar i sesionit nën
`event` të vet, çdo skedar shoqërues nën emrin e skedarit; një rresht që nuk është JSON
nën `unparsed`.

Pozicionet në sipërfaqe vendosen në një plan tangjent lokal për çdo trup, në metra: pika e
parë e fiksuar mbi një trup është origjina e tij, x lindje, z veri, y lart (lartësia), me të
njëjtën orientim si kuadri i galaktikës, dhe rreshtat e mbajnë emrin e trupit si `session`,
kështu që një makinë ose një ecje në një planet vizatohet si rrugë më vete. Rreshtat e
galaktikës kanë sesionin "galaxy". Dy shkallët jetojnë në një tabelë; zgjidh sesionin
në shikues.

Formati: manuali "Elite Dangerous Player Journal" i Frontier (publikuar me çdo
përditësim në forumet zyrtare, <https://forums.frontier.co.uk/> - "Journal Manual",
v4.x), ngjarjet dhe fushat siç dokumentohen aty; flamujt e Status.json sipas kapitullit
"Status File" të të njëjtit manual.

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | vite dritë (rreshtat e galaktikës, sesioni 'galaxy'); metra lindje/lart/veri nga pika e parë e fiksuar mbi një trup (rreshtat e sipërfaqes, sesioni = emri i trupit) |
| Pasqyruar për shikuesin | `z` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `log`: lexon vetëm atë që loja ose platforma e jep vetë (skedarë që loja i shkruan teksa punon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- çdo rresht i ditarit si rresht nën `event` të vet, me fushat e tij të thjeshta (teksti i lokalizuar ku loja jep një; tekstet më të gjata se 300 shkronja priten në rresht)
- rreshtat e galaktikës (StarPos) te FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; rreshtat e sipërfaqes nga Status.json dhe Touchdown/Liftoff
- fushat e thjeshta të Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) te rreshtat e sipërfaqes
- statistikat: kërcimet, distanca, vdekjet, vrasjet, kreditet e fituara, misionet, trupat e skanuar, sistemet e vizituara, ankorimet, uljet

**Ruajtur të papërpunuara**

- çdo rresht i ditarit i plotë, `type` = `event` i tij (FSDJump, Scan, Music, ReceiveText, ...), `used` true: listat dhe objektet që rreshtat i lënë jashtë (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) janë vetëm këtu
- një rresht i ditarit që nuk është JSON, `type` `unparsed`
- çdo skedar shoqërues i plotë sa herë e rishkruan loja, `type` = emri i skedarit: `Status.json` (`used` kur bëri një rresht sipërfaqeje), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, dhe çdo `*.json` tjetër që loja e shkruan aty

**Nuk ofrohet**

- pozicioni mes kërcimeve (brenda një sistemi, në supercruise ose në hapësirë normale): loja shkruan vetëm StarPos të sistemit dhe, pranë një planeti, gjerësinë, gjatësinë dhe lartësinë
- pozicionet e anijeve dhe lojtarëve të tjerë: ditari është rrëfimi i vetë komandantit
- shpejtësia, gazi dhe telemetria tjetër e fluturimit: loja nuk i shkruan
- ditarët dhe skedarët shoqërues të seancave të mëparshme: ruhen kur janë luajtur (ndjekësi fillon në fund të një skedari më të vjetër se kjo nisje e lojës)
- API-ja e uebit shoqërues e Frontier (cAPI): kërkon hyrjen e lojtarit te Frontier; nuk është skedar që e shkruan loja

**Madhësia**: rreth 1-5 MB tekst i papërpunuar në orë: ditari 0.2-2 MB, Status.json (nën 1 KB, rishkruhet deri në çdo sekondë) 1-2 MB, një set market/outfitting/shipyard 20-150 KB për çdo stacion të vizituar; zstd te heat.raw.parquet e bën rreth një të dhjetën

## Verifikuar {#verified}

parser-i u riluajt mbi skedarë të vërtetë ditari nga një instalim lokal (numrat e ngjarjeve përputhen me statistikat); pikat e fiksuara të sipërfaqes nga Status.json u provuan vetëm me pamje sintetike

## Burimi {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
