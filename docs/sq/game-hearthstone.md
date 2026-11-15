---
title: "Hearthstone (skedarë regjistri)"
nav_order: 25
lang: "sq"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (skedarë regjistri) {#hearthstone-log-files}

Ndërsa luan Hearthstone, watcher lexon skedarët që shkruan loja dhe ruan çfarë ndodhi, që ta shohësh më vonë si statistika dhe vijë kohore.

*Detaje teknike: adaptori `hearthstone`, lloji [`log`](sources-and-rules.md); punon sa kohë `Hearthstone.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- fillimi dhe fundi i lojës, me rezultatin (fitoi, humbi, barazim), kthesat dhe emrin e kundërshtarit
- çdo kthesë
- çdo rresht i Power.log dhe i regjistrave të tjerë i plotë te heat.raw.parquet
- lojërat, fitoret, humbjet, barazimet, kthesat, loja më e gjatë

## Nga vjen {#where-it-comes-from}

&lt;install>\Logs\Power.log (ose Logs\Hearthstone_\*\Power.log), shkruar sapo %LOCALAPPDATA%\Blizzard\Hearthstone\log.config ka një seksion [Power], dhe çdo \*.log tjetër që loja e shkruan aty

## Si ta ndezësh {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` shton regjistrimin [Power] te %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (ruhet kopje rezervë); rinise lojën

Shkruaje komandën në një terminal të hapur në dosjen e watcher-it (shih [Para se të nisësh](before-you-start.md)). Nëse dështon, rreshti i fundit tregon pse; [Instalimi dhe nisja](installing-and-running.md) mbulon shkaqet e zakonshme.

`python -m heat3d_watch setup hearthstone` liston skedarët që do t'i ndryshonte; `python -m heat3d_watch setup hearthstone --apply` i ndryshon, duke e ruajtur origjinalin si `<file>.heat3d-backup` (shih [Komandat](commands.md#setup)). Printon `hearthstone: changed: ...` për çdo ndryshim, ose `hearthstone: nothing to change` kur është tashmë i ndezur.

## Si funksionon {#how-it-works}

Hearthstone: Power.log i lojës, që e shkruan sapo `log.config` e kërkon.

Hearthstone e lexon `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` gjatë nisjes;
një seksion `[Power]` me `LogLevel=1` dhe `FilePrinting=true` e bën të shkruajë
ndryshimet e gjendjes së çdo loje te `<install>\Logs\Power.log` (klientët më të rinj e vendosin
regjistrat e çdo nisjeje në një dosje të vetën, `Logs\Hearthstone_<date>\`). Ky
është regjistrimi i dokumentuar për debug që deck tracker-ët e kanë ndezur që nga 2014
(setup-i i Hearthstone Deck Tracker e shkruan të njëjtin seksion). `setup()` e shton
seksionin, me një kopje rezervë të skedarit siç ishte; loja ka nevojë për rinisje që ta lexojë.

Rreshtat e përdorur, të gjithë nga `GameState.DebugPrintPower()` (rreshtat `PowerTaskList`
i përsërisin dhe anashkalohen):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Ana e vetë lojtarit është ajo që ka kartat e dorës së nisjes të emërtuara
(të kundërshtarit janë të fshehura), përndryshe ana që nuk është AI (llogaria 0) ose
"UNKNOWN HUMAN PLAYER". Rreshtat mbajnë vetëm orën e ditës; data është e sotmja.
Pa pozicione.

Çdo rresht i Power.log ruhet i plotë te skedari anësor i papërpunuar i sesionit (rregulli i
konvertuesit të 3DHeat), përfshirë përsëritjet `PowerTaskList`, opsionet, zgjedhjet dhe
përditësimet e entiteteve: `type` është metoda që e shkroi (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Çdo
regjistër tjetër që loja e shkruan pranë tij - `LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ..., secili aty kur log.config e kërkon (deck tracker-ët shpesh
e bëjnë) - ndiqet njësoj dhe ruhet me emrin e vet te `log`.

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

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- `CREATE_GAME`, lojtarët (entiteti, id e lojtarit, llogaria; llogaria 0 është AI) dhe emrat e tyre (`DebugPrintGame`)
- e kujt është ana e lojtarit, nga kartat e emërtuara të dorës së nisjes
- `TAG_CHANGE` i TURN, PLAYSTATE (fitoi, humbi, barazim) dhe STATE COMPLETE: kthesat, rezultati, kundërshtari

**Ruajtur të papërpunuara**

- çdo rresht i Power.log i plotë, `type` = metoda që e shkroi (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` ku u bë rresht: çdo kartë e luajtur, e tërhequr dhe e zbuluar, çdo ndryshim etikete, sulm, opsion dhe zgjedhje është këtu, ende jo në rreshta
- çdo rresht i regjistrave të tjerë në të njëjtën dosje (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - çfarëdo që log.config ndez), të njëjtat `type`, me emrin e regjistrit te `log`
- një rresht pa nivel dhe orë dite si `untimed`, një pa metodë si `untagged`

**Nuk ofrohet**

- pozicionet: një lojë me karta nuk ka
- kartat e fshehura të kundërshtarit: regjistri e emërton një kartë vetëm pasi zbulohet
- regjistrat që log.config nuk i ndez: `setup` kërkon vetëm [Power]; regjistrat e tjerë vijnë kur një mjet tjetër (një deck tracker) i ka ndezur
- regjistrat e nisjeve të mëparshme: çdo nisje shkruan një dosje të re; ata më të vjetër se ky punim i lojës nuk lexohen sërish

**Madhësia**: Power.log me Verbose është rreth 1-5 MB për lojë, 10-40 MB në orë loje; regjistrat e tjerë shtojnë pak; zstd te heat.raw.parquet e bën afërsisht një të dhjetën ose më pak (rreshtat përsëriten shumë)

## Verifikuar {#verified}

i provuar me rreshta sintetikë Power.log në formatin e lojës; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
