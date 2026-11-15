---
title: "Counter-Strike 2 (gjendja e lojës)"
nav_order: 9
lang: "sq"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (gjendja e lojës) {#counter-strike-2-game-state}

Ndërsa luan Counter-Strike 2, watcher-i ruan çfarë i raporton loja programeve në kompjuterin tënd, që më vonë ta shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `cs2-gsi`, lloji [`gsi`](sources-and-rules.md); ekzekutohet sa kohë `cs2.exe` është në punë dhe kërkon të dhëna të reja çdo 0.05 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni i vetë lojtarit (XYZ botërore, inç) dhe drejtimi i shikimit deri në 10 Hz, ndërsa je gjallë
- shfaqjet (pamja e parë e çdo raundi, ringjalljet) dhe vdekjet (jeta në 0, ose numri i vdekjeve)
- vrasjet me armën aktive, nga statistikat e ndeshjes
- raundet (fillimi, mbarimi, fituesi), bomba e vendosur/çaktivizuar/shpërthyer, fazat e ndeshjes dhe rezultati
- vrasjet, asistet, vdekjet, MVP-të, pikët, paratë, dëmi, vrasjet me goditje në kokë, raundet e fituara dhe të humbura

## Nga vjen {#where-it-comes-from}

Game State Integration: POST-e HTTP te 127.0.0.1:3311, të konfiguruara nga &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Si aktivizohet {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, pastaj nise CS2 (e lexon skedarin kur niset)

Shkruaje komandën në një terminal të hapur në dosjen e watcher-it (shih [Para se të fillosh](before-you-start.md)). Nëse dështon, rreshti i fundit tregon pse; [Instalimi dhe ekzekutimi](installing-and-running.md) përmban shkaqet më të zakonshme.

`python -m heat3d_watch setup cs2-gsi` liston skedarët që do të ndryshonte; `python -m heat3d_watch setup cs2-gsi --apply` i ndryshon, duke e ruajtur origjinalin si `<file>.heat3d-backup` (shih [Komandat](commands.md#setup)). Shfaq `cs2-gsi: changed: ...` për çdo ndryshim, ose `cs2-gsi: nothing to change` kur është tashmë i aktivizuar.

Cilësime nga variablat e mjedisit:

- `HEAT3D_CS2_GSI_PORT`: porta ku poston loja (parazgjedhja 3311); skedari cfg i lojës duhet të emërtojë të njëjtën portë

## Si funksionon {#how-it-works}

Valve Game State Integration: Counter-Strike 2 dhe Dota 2 i tregojnë një serveri web lokal çfarë ndodh.

Të dyja lojërat lexojnë çdo `gamestate_integration_*.cfg` në dosjen e tyre cfg kur
niset loja, dhe që nga ai çast dërgojnë me POST një dokument JSON te `uri` e çdo skedari sa herë
ndryshon gjendja (më së shumti çdo `throttle` sekonda, dhe çdo `heartbeat` sekonda
kur nuk ndryshon asgjë). Watcher-i është ai server web: dëgjon vetëm te 127.0.0.1,
i përgjigjet çdo POST-i me 200 menjëherë dhe e bën punën në thread-in e vet të pyetjes.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Çfarë i dërgohet një lojtari - dhe pra çfarë mund të regjistrohet - është ajo që loja
vendos që një lojtar mund ta shohë:

- CS2: `provider` (steamid i vetë lojtarit), `map` (emri, mënyra, faza warmup/live/
  intermission/gameover, raundi, rezultati team_ct/team_t), `round` (faza
  freezetime/live/over, bomba e vendosur/shpërthyer/çaktivizuar, win_team), `player` (lojtari
  që po *shikohet*: vetja ndërsa je gjallë, një shok skuadre pas vdekjes) me
  `state` (jeta, forca mbrojtëse, paratë, round_kills, round_killhs, round_totaldmg),
  `match_stats` (kills, assists, deaths, mvps, score), `position` dhe `forward`
  si vargje "x, y, z" në njësi botërore (inç, Z lart), `weapons`; `bomb` vetëm për
  spektatorët. Pozicionet e lojtarëve të tjerë (`allplayers_*`) dërgohen vetëm te
  spektatorët dhe GOTV, ndaj nuk kërkohen.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player`
  (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero`
  (xpos/ypos në njësi botërore, level, alive, respawn_seconds), `buildings`
  (jeta për çdo kullë/barrakë/ancient), `roshan`, `events` (roshan_killed,
  aegis_picked_up, ...). Nuk ka lartësi: z është 0. Kërkohen gjithashtu, dhe ruhen
  të plota: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`,
  `neutralitems`, `league` (loja dërgon çfarë ka klienti i vetë lojtarit;
  cilat prej tyre mbajnë diçka kur luan, jo kur shikon, nuk është provuar).

Çdo dokument ruhet edhe i plotë (rregulli i konvertuesve të 3DHeat,
docs/converters.md në repon e shikuesit): `heat.raw.parquet`, `type`
"gsi", `text` JSON-i siç u postua - vetëm token-i i skedarit cfg është fshirë, sepse është
sekreti i vetë watcher-it, jo e dhënë loje. Dokumentet e postuara ndërsa nuk ka ndeshje të hapur
(menytë, ngarkimi, mes ndeshjeve) presin në një `Backlog` dhe hyjnë në seancën e
ndeshjes tjetër, para fillimit të saj; ato që mbeten kur mbyllet loja marrin
një seancë të vetën që mban vetëm ato. Edhe POST-et e palexueshme dhe ato me
token të gabuar ruhen ("gsi-unreadable", "gsi-bad-auth").

Burimet: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(formati që CS2 e mbajti), <https://github.com/antonpup/CounterStrike2GSI> dhe
<https://github.com/antonpup/Dota2GSI> (listat e fushave; MIT, lexuar vetëm për fakte).

I njëjti modul shërben edhe: [Dota 2 (gjendja e lojës)](game-dota2-gsi.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet regjistrohen | po |
| Boshti lart | `z` |
| Njësitë | inç (njësi Hammer) |
| Pasqyruar për shikuesin | `y` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto shkojnë në `meta.json` të çdo seance (`axes`) dhe, kur seanca ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si luajtur online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `gsi`: lexon vetëm çfarë jep loja ose platforma (një integrim i gjendjes së lojës ose API lokale që e shërben loja), ndaj regjistron edhe në lojë online edhe offline; flamuri vendos vetëm nëse mund të lexohet ndonjëherë memoria.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterat `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri i vendos me emër (`stats` e çdo seance në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Një çelës në kllapa gjarpëruese plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë fushash të lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher-i ndjek [rregullin e konvertuesve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, nuk hidhet kurrë. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që merr adapteri ruhet e plotë në `heat.raw.parquet` të seancës (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e mbajtur me emër; `used` shënon çfarë u bë edhe rresht), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexohet**

- pozicioni, drejtimi i shikimit, jeta, forca mbrojtëse, paratë, arma aktive, helmeta, kiti i çaktivizimit, sasitë e flash/tymit/zjarrit dhe vlera e pajisjes së lojtarit të shikuar, në çdo rresht pozicioni kur është i vetë lojtarit (steamid i provider = steamid i lojtarit)
- shfaqjet, vdekjet (jeta në 0, ose numri i vdekjeve në statistikat e ndeshjes), vrasjet (numri i vrasjeve që rritet)
- fazat e ndeshjes, raundet (freeze time, live, over, fituesi), bomba e vendosur/çaktivizuar/shpërthyer, rezultati
- vrasjet, asistet, vdekjet, MVP-të, pikët, paratë, dëmi, vrasjet me goditje në kokë, raundet e fituara dhe të humbura si statistika

**Ruhet i papërpunuar**

- `gsi`: çdo dokument që poston loja, i plotë, siç u postua (`text`), `used` e vërtetë kur u lexua në një ndeshje - provider (version, timestamp), map (mode, emrat e ekipeve, humbjet radhazi të raundeve, timeout-et, fitoret e serisë, `round_wins` me kushtin e fitores së çdo raundi), round, lojtari i shikuar (clan, observer slot, activity, çdo armë me skin, municion dhe rezervë), bomb, numërimet mbrapsht të fazave, dhe diferenca `previously`/`added` e vetë lojës me POST-in e mëparshëm
- dokumentet nga menytë, ngarkimi dhe mes ndeshjeve: ruhen njësoj, në kohën e tyre përpara fillimit të ndeshjes tjetër; pas ndeshjes së fundit, në një seancë të vetën (`raw_only` në meta.json)
- `gsi-unreadable`: një POST që nuk është objekt JSON, bajtet e tij si `payload` dhe `length`
- `gsi-bad-auth`: një POST me token tjetër nga ai i skedarit cfg

**Nuk disponohet**

- lojtarët e tjerë (`allplayers_*`) dhe granatat (`allgrenades`): loja i dërgon vetëm te spektatorët dhe GOTV, dhe watcher-i nuk i kërkon (Burimet dhe rregullat); një demo ka çdo lojtar - shih [Counter-Strike 2 (riluajtjet)](game-cs2-demos.md)
- gjendjet mes POST-eve: loja poston më së shumti çdo 0.1 s (`throttle`) dhe vetëm kur ndryshon diçka, përndryshe çdo 10 s (`heartbeat`)
- token-i i skedarit cfg, i fshirë në çdo dokument të ruajtur: sekreti i vetë watcher-it, jo e dhënë loje
- POST-et përtej 10,000 në pritje (watcher-i u bllokua) numërohen si `dropped_packets`, nuk ruhen; një POST mbi 4 MB ruhet si `gsi-unreadable` me gjatësinë e tij por pa bajtet

**Madhësia**: dokumenti i një lojtari është 2-4 KB, i postuar deri në 10 herë në sekondë ndërsa ndryshon diçka: rreth 30-150 MB në orë në `raw.bin` ndërsa ndeshja është në punë, një e dhjeta e kësaj ose më pak në `heat.raw.parquet` me zstd (vlerësuar nga formati i publikuar, jo i matur në lojë)

## Verifikuar {#verified}

provuar me dokumente në formatin e publikuar GSI të postuara te adapteri në punë; instalimi dhe gjetja e dosjes cfg të provuara në një instalim lokal; i paprovuar me lojën në punë

## Burimi {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Gjeneruar nga adapteri me tools/gen_game_pages.py; ndrysho adapterin dhe ekzekuto përsëri, mos e redakto këtë faqe. -->
