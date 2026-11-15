---
title: "League of Legends (spilltilstand)"
nav_order: 29
lang: "no"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (spilltilstand) {#league-of-legends-game-state}

Mens du spiller League of Legends, lagrer watcheren det spillet rapporterer til programmer på din egen datamaskin, slik at du senere kan se på det som statistikk og en tidslinje.

*Tekniske detaljer: adapter `lol-live`, type [`gsi`](sources-and-rules.md); den kjører mens `League of Legends.exe` går og ser etter nye data hvert 0,5 s.*

## Hva som tas opp {#what-is-recorded}

- ingen posisjoner: API-et har ingen
- drapsloggen: drap, dødsfall og assists for spilleren, andre champion-drap med drapsmann, offer og assisterende
- drager, heraldene, baroner, tårn, hemmere, multikills, aces, first blood, spillstart og -slutt
- egne drap, dødsfall, assists, creep-poeng, ward-poeng, nivå, gull, champion, spilletid, resultat
- mål tatt av spillerens lag

## Hvor det kommer fra {#where-it-comes-from}

Live Client Data API til spillklienten, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), under en kamp

## Slik slår du det på {#how-to-switch-it-on}

Ingenting må slås på: watcheren leser kilden slik spillet eller plattformen gir den.

## Slik fungerer det {#how-it-works}

League of Legends: Live Client Data API-et som spillklienten serverer under en kamp.

Mens en kamp kjører (også i øvingsverktøyet og tilskuermodus), svarer `League of Legends.exe` på <https://127.0.0.1:2999> med det spilleren kan se i spillets eget grensesnitt:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Det finnes ingen posisjoner: API-et har ingen, så en League-økt er hendelser og statistikk, uten en varmetabell. Sertifikatet er selvsignert, av Riots egen rotsertifikat (`riotgames.pem`, publisert på <https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Vilkårene for bruk er ikke oppgitt, så det er ikke levert med: legg det i `<data>\riotgames.pem`, så verifiseres forbindelsen med det; uten det er verifiseringen av - og bare for 127.0.0.1, den ene adressen denne adapteren snakker med.

Riots retningslinjer tillater verktøy å vise det spilleren kunne vite fra selve spillet, og ikke noe beregnet utover det (ingen fiendetimere): dette tar opp drapsloggen og scoreboardet spilleren ser, og spillerens egne tall.

Hvert svar tas også vare på hel (3DHeats konverteringsregel, docs/converters.md i viewerens repositorium): `heat.raw.parquet`, `type` endepunktet ("allgamedata", "eventdata"), `text` JSON-en slik klienten sendte den, `status` når den ikke var 200. Et svar byte for byte likt det før fra samme endepunkt (hendelseslisten mens ingenting skjer) tas vare på én gang og telles i meta.jsons `unchanged_replies`. allgamedata inneholder alt de andre endepunktene leverer (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), så de spørres ikke separat. Svar før en kamp (lastingsskjermen) venter i en kø og går inn i kampens økt; etter GameEnd forblir økten åpen til klienten lukkes, så sluttskjermens svar tas vare på med den.

Kilde: <https://developer.riotgames.com/docs/lol#game-client-api>

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | nei |
| Opp-akse | `z` |
| Enheter | ingen (ingen posisjoner) |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `gsi`: den leser bare det spillet eller plattformen gir ut (en spilltilstandsintegrasjon eller et lokalt API spillet serverer), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- drapsloggen fra eventdata: hver hendelse én gang, dens navngitte felt dekodet (drapsmann, offer og assisterende med champion og lag, bygninger og deres side, dragetype, stjelinger, multikills, aces, first blood, resultatet), og hvert annet felt i en hendelse på sin rad under sitt eget navn
- fra allgamedata: egne drap, dødsfall, assists, creep-poeng, ward-poeng, nivå, gull, champion, spilletid, spillmodus og kart

**Tatt vare på rått**

- `allgamedata`: hvert svar hele (`text`), hvert 2. sekund - activePlayer (evner, hver champion-statistikk, hele runes, gull, nivå), allPlayers (gjenstander med plasser og priser, runes, summoner spells, poeng, nivå, død og gjenoppstandingstimer, skin, bane, bot), hendelsene, gameData (modus, tid, kart, terreng); `used` sann mens kampen går, usann på sluttskjermen
- `eventdata`: hvert svar hele, spurt hvert 0,5 s fra neste hendelses-id; `used` sann når det kom nye hendelser
- et svar byte for byte likt det før fra samme endepunkt tas vare på én gang og telles (`unchanged_replies` i meta.json); feilsvar (lastingsskjermens RESOURCE_NOT_FOUND) tas vare på med sin `status`, før kampens start

**Ikke tilgjengelig**

- posisjoner: API-et har ingen (ingen minikart, ingen koordinater)
- de andre endepunktene (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): hver gir en del av allgamedata, så de spørres ikke
- Replay-API-et (`/replay/*` på samme port): det spiller av repriser og overvåkede spill når det er slått på i game.cfg; det er ikke en del av en spilt kamp
- League-klientens lockfile-endepunkter: ikke et publisert API (Kilder og regler)
- verdier mellom to lesinger: API-et svarer når det spørres og sender ikke selv; scoreboardet spørres hvert 2. sekund, hendelsene hvert 0,5 s

**Størrelse**: allgamedata er 15-40 KB (den har hele hendelseslisten, som vokser) hvert 2. sekund: omtrent 30-70 MB i timen i `raw.bin`; eventdata legger lite til, siden uendrede svar telles, ikke lagres; zstd krymper den gjentatte JSON-en i `heat.raw.parquet` til noen få MB i timen (anslått fra det dokumenterte formatet)

## Verifisert {#verified}

testet mot en falsk lokal server som sender svar i det dokumenterte formatet; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
