---
title: "League of Legends (spelets tillstånd)"
nav_order: 29
lang: "sv"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (spelets tillstånd) {#league-of-legends-game-state}

När du spelar League of Legends sparar watchern det som spelet rapporterar till program på din egen dator, så att du senare kan titta på det som statistik och en tidslinje.

*Tekniska detaljer: adapter `lol-live`, slag [`gsi`](sources-and-rules.md); den körs medan `League of Legends.exe` är igång och letar efter ny data var 0,5 s.*

## Vad som spelas in {#what-is-recorded}

- inga positioner: API:et har inga
- dödsflödet: spelarens dödanden, dödsfall och assist, andra mästares dödanden med mördare, offer och assistenter
- drakar, heroldar, baroner, torn, hämmare, multikills, aces, first blood, spelets start och slut
- egna dödanden, dödsfall, assist, creep score, vaktpoäng, nivå, guld, mästare, speltid, resultat
- mål som spelarens lag tagit

## Var datan kommer ifrån {#where-it-comes-from}

Live Client Data API i spelklienten, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), under en match

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

League of Legends: Live Client Data API som spelklienten erbjuder under en match.

Medan en match pågår (även i träningsverktyget och åskådarläget) svarar `League of Legends.exe` på <https://127.0.0.1:2999> med det spelaren kan se i spelets eget gränssnitt:

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

Det finns inga positioner: API:et har inga, så en League-session är händelser och statistik, utan värmetabell. Certifikatet är självsignerat, av Riots egen rot (`riotgames.pem`, publicerat på <https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Användarvillkoren för det anges inte, så det levereras inte: lägg det i `<data>\riotgames.pem` så verifieras anslutningen med det; utan det är verifieringen av - och bara någonsin för 127.0.0.1, den enda adress som adaptern pratar med.

Riots policy tillåter verktyg att visa det spelaren kan veta ur spelet självt, och inget beräknat utöver det (inga fiendetimers): den här sparar dödsflödet och resultattavlan som spelaren ser, och spelarens egna siffror.

Varje svar sparas också helt (3DHeats konverterarregel, docs/converters.md i visarens förråd): `heat.raw.parquet`, `type` är slutpunkten ("allgamedata", "eventdata"), `text` är JSON:en så som klienten skickade den, `status` när den inte var 200. Ett svar som är byte för byte samma som det föregående från dess slutpunkt (händelselistan när inget händer) sparas en gång och räknas i meta.json:s `unchanged_replies`. allgamedata innehåller allt de andra slutpunkterna levererar (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), så de frågas inte separat. Svar före en match (laddningsskärmen) väntar i en kö och hamnar i matchens session; efter GameEnd är sessionen öppen tills klienten stängs, så slutskärmens svar sparas med den.

Källa: <https://developer.riotgames.com/docs/lol#game-client-api>

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | nej |
| Upp-axel | `z` |
| Enheter | ingen (inga positioner) |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Slag `gsi`: den läser bara det spelet eller plattformen lämnar ut (en spelstatusintegration eller lokalt API som spelet erbjuder), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- dödsflödet ur eventdata: varje händelse en gång, dess namngivna fält avkodade (mördare, offer och assistenter med mästare och lag, byggnader och deras sida, drakens typ, stjälningar, multidödanden, aces, first blood, resultatet) och varje annat fält i en händelse på sin rad under sitt eget namn
- ur allgamedata: egna dödanden, dödsfall, assist, creep score, vaktpoäng, nivå, guld, mästare, speltid, spelläge och karta

**Sparas råa**

- `allgamedata`: varje svar helt (`text`), var 2:a s - activePlayer (förmågor, varje mästarstatistik, alla runor, guld, nivå), allPlayers (föremål med platser och priser, runor, besvärjelser, poäng, nivå, död och återuppståndelsetimer, skin, bana, bot), händelserna, gameData (läge, tid, karta, terräng); `used` sann medan matchen pågår, falsk på slutskärmen
- `eventdata`: varje svar helt, efterfrågat var 0,5 s från nästa händelse-id och framåt; `used` sann när det gav nya händelser
- ett svar byte för byte likadant som det föregående från dess slutpunkt sparas en gång och räknas (`unchanged_replies` i meta.json); felsvar (laddningsskärmens RESOURCE_NOT_FOUND) sparas med sin `status`, före matchens start

**Finns inte**

- positioner: API:et har inga (ingen minikarta, inga koordinater)
- de andra slutpunkterna (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): var och en levererar en del av allgamedata, så de frågas inte
- Replay-API:et (`/replay/*` på samma port): det spelar upp repriser och åskådade spel när det slagits på i game.cfg, det ingår inte i en spelad match
- League-klientens lockfile-slutpunkter: inte ett publicerat API (Källor och regler)
- värden mellan två läsningar: API:et svarar när det frågas och skickar inte själv; resultattavlan frågas var 2 s, händelserna var 0,5 s

**Storlek**: allgamedata är 15-40 KB (den bär hela händelselistan, som växer) var 2:a s: ungefär 30-70 MB per timme i `raw.bin`; eventdata tillför lite, eftersom oförändrade svar räknas, inte sparas; zstd krymper den upprepade JSON:en i `heat.parquet` till några MB per timme (uppskattat ur det dokumenterade formatet)

## Verifierat {#verified}

testad mot en falsk lokal server som levererar svar i det dokumenterade formatet; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
