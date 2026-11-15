---
title: "Star Citizen (skedarë regjistri)"
nav_order: 41
lang: "sq"
source: game-starcitizen.md
source_hash: "7b1ce51dc50a"
nav_exclude: true
search_exclude: true
---
# Star Citizen (skedarë regjistri) {#star-citizen-log-files}

Ndërsa luan Star Citizen, watcher lexon skedarët që shkruan loja dhe ruan çfarë ndodhi, që ta shohësh më vonë si statistika dhe vijë kohore.

*Detaje teknike: adaptori `starcitizen`, lloji [`log`](sources-and-rules.md); punon sa kohë `StarCitizen.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- vdekjet me viktimën, vrasësin, armën, llojin e dëmit dhe zonën (lojtarë dhe NPC)
- automjetet e çaktivizuara dhe të shkatërruara, me shoferin, shkakun dhe zonën
- objektivat e udhëtimit kuantik, ndryshimet e sistemit diellor, spawn-et, respawn-et, paaftësitë
- çdo rresht i Game.log i plotë te heat.raw.parquet
- vrasjet (lojtarë dhe NPC), vdekjet, vetëvrasjet, automjetet e shkatërruara e të humbura, kërcimet kuantike

## Nga vjen {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (dosja e build-it të StarCitizen.exe që punon), vetëm skedari i regjistrit që shkruan loja - një lojë Easy Anti-Cheat: asgjë nuk prek procesin e saj

## Si ta ndezësh {#how-to-switch-it-on}

Nuk ka asgjë për të ndezur: watcher e lexon burimin ashtu siç e ofron loja ose platforma.

## Si funksionon {#how-it-works}

Star Citizen: regjistri i vetë klientit, `<install>\StarCitizen\LIVE\Game.log`.

Loja e shkruan Game.log nga e para në çdo nisje (i mëparshmi shkon te
`logbackups\`). Lexohet vetëm ai skedar: Star Citizen përdor Easy Anti-Cheat, dhe
asgjë këtu nuk i afrohet procesit të lojës. Rreshtat nisin me një kohë UTC dhe
një nivel, pastaj një etiketë në kllapa këndore:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(i thyer këtu; nga një rresht secili në skedar). Zona e një vdekjeje është zakonisht
anija ku ndodhej viktima, jo një vend. Formati nuk është dokumentuar nga Cloud
Imperium dhe ndryshon mes patch-eve; modelet ndjekin rreshtat që i lexojnë gjurmuesit e
vrasjeve të komunitetit (p.sh. <https://github.com/DimmaDont/all-slain>, MIT - vetëm
fakte), dhe çdo gjë që nuk përputhet anashkalohet, nuk hamendësohet. `pos` i një automjeti
është relativ me zonën dhe ruhet vetëm si tekst: nuk vizatohen koordinata.

Çdo rresht ruhet i plotë te skedari anësor i papërpunuar i sesionit (rregulli i konvertuesit
të 3DHeat), përputhet ose jo: `type` është etiketa e rreshtit në kllapa këndore (`Actor
Death`, `Spawn Flow`, ...), përndryshe fjala e tij e parë në kllapa katrore (`Notice`,
`CSessionManager::OnClientSpawned`), përndryshe `untagged`; një rresht pa
kohë është `untimed`.

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | jo |
| Boshti lart | `y` |
| Njësitë | nuk regjistrohen pozicione |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `log`: lexon vetëm atë që loja ose platforma e jep vetë (skedarë që loja i shkruan sa kohë punon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- `<Actor Death>`: viktima, vrasësi, arma dhe klasa e saj, lloji i dëmit, zona; NPC ose lojtar
- `<Vehicle Destruction>`: automjeti, zona, pozicioni relativ me zonën si tekst, shoferi, shkaku, mënyra, niveli i shkatërrimit
- objektivat `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, respawn-et në spital, paaftësitë me shkaqet e tyre, `EndSession`
- emri i lojtarit nga `<AccountLoginCharacterStatus_Character>` ose rreshti i hyrjes

**Ruajtur të papërpunuara**

- çdo rresht i Game.log i plotë, `type` = etiketa e tij në kllapa këndore (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), përndryshe fjala e tij e parë në kllapa katrore (`Notice`, `CSessionManager::OnClientSpawned`, ...), përndryshe `untagged`; rreshtat pa kohë (header-i i regjistrit, teksti i thyer) si `untimed`; `used` ku rreshti u bë rresht

**Nuk ofrohet**

- pozicionet: regjistri nuk jep asnjë në një kuadër që mund të vizatohet (`pos` i një automjeti të shkatërruar është relativ me një zonë, vendi i së cilës nuk regjistrohet)
- çdo gjë nga procesi ose rrjeti i lojës: Star Citizen përdor Easy Anti-Cheat; lexohet vetëm skedari i regjistrit
- regjistrat e nisjeve të mëparshme (`logbackups`): Game.log i çdo nisjeje ruhet kur luhet
- rreshtat në një format që e ndryshon një patch: ruhen të papërpunuara, dekodohen sërish kur të njihet forma e re

**Madhësia**: Game.log rritet rreth 5-15 MB në orë loje (më shumë në zona të zëna dhe me gabime); zstd te heat.raw.parquet e bën afërsisht një të dhjetën

## Verifikuar {#verified}

i provuar me rreshta sintetikë Game.log në formatin që dokumentojnë gjurmuesit e komunitetit; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
