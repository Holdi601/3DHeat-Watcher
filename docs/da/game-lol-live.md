---
title: "League of Legends (spiltilstand)"
nav_order: 29
lang: "da"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (spiltilstand) {#league-of-legends-game-state}

Mens du spiller League of Legends, gemmer watcheren det, spillet melder til programmer på din egen computer, så du senere kan se det som statistik og en tidslinje.

*Tekniske detaljer: adapter `lol-live`, type [`gsi`](sources-and-rules.md); den kører, mens `League of Legends.exe` kører, og leder efter nye data hver 0.5 s.*

## Hvad der registreres {#what-is-recorded}

- ingen positioner: API'et har ingen
- dræbfeedet: drab, dødsfald og assists for spilleren, andre championdrab med dræber, offer, assisterende
- drager, heraldere, baroner, tårne, hæmninger, multidrab, ess, first blood, spilstart og slut
- egne drab, dødsfald, assists, creep-score, ward-score, niveau, guld, champion, spiltid, resultat
- mål taget af spillerens hold

## Hvor data kommer fra {#where-it-comes-from}

Live Client Data API fra spilklienten, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), under en kamp

## Sådan slår du det til {#how-to-switch-it-on}

Der skal ikke slås noget til: watcheren læser kilden, som spillet eller platformen udleverer den.

## Sådan virker det {#how-it-works}

League of Legends: Live Client Data API'et, som spilklienten udbyder under en kamp.

Mens en kamp kører (også i øvetilstand og tilskuertilstand), svarer `League of
Legends.exe` på <https://127.0.0.1:2999> med det, spilleren kan se i
spillets egen grænseflade:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} fra EventID N og frem: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Der er ingen positioner: API'et har ingen, så en League-kørsel er hændelser og
statistik uden en varmetabel. Certifikatet er selvsigneret, af Riots egen
rodcertifikat (`riotgames.pem`, udgivet på
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Dets brugsvilkår
er ikke angivet, så det leveres ikke med; læg det i `<data>\riotgames.pem`, så
verificeres forbindelsen med det; uden det er verificeringen slået fra - og kun
nogensinde for 127.0.0.1, den ene adresse denne adapter taler til.

Riots politik tillader værktøjer at vise det, spilleren kan vide ud fra selve spillet,
og intet beregnet ud over det (ingen fjendtlige timere): dette registrerer dræbfeedet og
scoretavlen, som spilleren ser den, og spillerens egne tal.

Hvert svar gemmes også helt (3DHeats konverterregel, docs/converters.md i
viewerens repository): `heat.raw.parquet`, `type` er endepunktet
("allgamedata", "eventdata"), `text` er JSON'en, som klienten sendte den, `status`
når den ikke var 200. Et svar, der er byte for byte det forrige fra samme endepunkt (hændelseslisten, mens intet sker),
gemmes én gang og tælles i meta.json's `unchanged_replies`. allgamedata indeholder alt,
de andre endepunkter udbyder (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells,
playermainrunes, gamestats), så de spørges ikke særskilt. Svar før en kamp
(indlæsningsskærmen) venter i en kø og kommer med i kampens kørsel; efter GameEnd
forbliver kørslen åben, til klienten lukkes, så svarene på slutskærmen gemmes med den.

Kilde: <https://developer.riotgames.com/docs/lol#game-client-api>

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | nej |
| Op-akse | `z` |
| Enheder | ingen (ingen positioner) |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser det som "tilladt (læser kun det spillet udgiver)".
- Type `gsi`: den læser kun det spillet eller platformen udleverer (en game-state-integration eller lokal API spillet udbyder), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- dræbfeedet fra eventdata: hver hændelse én gang, med dens navngivne felter afkodet (dræber, offer og assisterende med champion og hold, bygninger og deres side, dragetype, stjæling, multidrab, ess, first blood, resultatet), og hvert andet felt i en hændelse på dens række under sit eget navn
- fra allgamedata: egne drab, dødsfald, assists, creep-score, ward-score, niveau, guld, champion, spiltid, spiltilstand og kort

**Gemt råt**

- `allgamedata`: hvert svar helt (`text`), hver 2. sekund - activePlayer (evner, hver championstat, fulde runer, guld, niveau), allPlayers (genstande med pladser og priser, runer, besvorgelser, scores, niveau, død og genopstandelsestimer, skin, bane, bot), hændelserne, gameData (tilstand, tid, kort, terræn); `used` er sand, mens kampen kører, falsk på slutskærmen
- `eventdata`: hvert svar helt, spurgt hver 0.5 sekund fra næste hændelses-id; `used` er sand, når det gav nye hændelser
- et svar, der er byte for byte det forrige fra samme endepunkt, gemmes én gang og tælles (`unchanged_replies` i meta.json); fejlsvar (indlæsningsskærmens RESOURCE_NOT_FOUND) gemmes med deres `status` før kampens start

**Ikke tilgængeligt**

- positioner: API'et har ingen (intet minikort, ingen koordinater)
- de andre endepunkter (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): hver udbyder en del af allgamedata, så de spørges ikke
- Replay-API'et (`/replay/*` på samme port): det afspiller replays og overvågede kampe, når det er slået til i game.cfg; det er ikke en del af en spillet kamp
- League-klientens lockfile-endepunkter: ikke et udgivet API (se Kilder og regler)
- værdier mellem to læsninger: API'et svarer, når der spørges, og skubber ikke; scoretavlen spørges hver 2. sekund, hændelserne hver 0.5 sekund

**Størrelse**: allgamedata er 15-40 KB (den indeholder hele hændelseslisten, som vokser) hver 2. sekund: cirka 30-70 MB i timen i `raw.bin`; eventdata lægger lidt til, da uændrede svar tælles, ikke gemmes; zstd skruer det gentagne JSON i `heat.raw.parquet` ned til nogle få MB i timen (estimeret ud fra det dokumenterede format)

## Verificeret {#verified}

testet mod en falsk lokal server, der svarer i det dokumenterede format; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
