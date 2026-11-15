---
title: "League of Legends (starea jocului)"
nav_order: 29
lang: "ro"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (starea jocului) {#league-of-legends-game-state}

Cât timp jucați League of Legends, watcher-ul salvează ce raportează jocul către programe de pe propriul computer, ca să le puteți vedea mai târziu ca statistici și ca o cronologie.

*Detalii tehnice: adaptorul `lol-live`, tipul [`gsi`](sources-and-rules.md); rulează cât timp `League of Legends.exe` rulează și caută date noi la fiecare 0,5 s.*

## Ce se înregistrează {#what-is-recorded}

- fără poziții: API-ul nu are
- feed-ul de eliminări: eliminările, morțile și asistențele jucătorului, eliminările altor campioni cu ucigașul, victima și asistenții
- dragoni, heralzi, baroni, turnuri, inhibitori, multikill-uri, aces, primul sânge, începutul și sfârșitul jocului
- eliminările, morțile, asistențele, scorul de creep, scorul de ward, nivelul, aurul, campionul, timpul de joc, rezultatul proprii
- obiectivele luate de echipa jucătorului

## De unde vine {#where-it-comes-from}

API-ul Live Client Data al clientului de joc, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), în timpul unui meci

## Cum se activează {#how-to-switch-it-on}

Nu trebuie activat nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

League of Legends: API-ul Live Client Data pe care îl servește clientul jocului în timpul unui meci.

Cât timp rulează un meci (și în modul de antrenament și de spectator), `League of Legends.exe` răspunde la <https://127.0.0.1:2999> cu ce poate vedea jucătorul în interfața jocului însuși:

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

Nu există poziții: API-ul nu are, deci o sesiune de League este formată din evenimente și statistici, fără tabel de heat. Certificatul este autosemnat, de la rădăcina proprie a Riot (`riotgames.pem`, publicat la <https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Condițiile lui de utilizare nu sunt precizate, deci nu este livrat: puneți-l la `<data>\riotgames.pem` și conexiunea este verificată cu el; fără el verificarea este dezactivată - și doar pentru 127.0.0.1, singura adresă cu care vorbește acest adaptor.

Politica Riot permite uneltelor să arate ce ar putea ști jucătorul din jocul însuși, și nimic calculat dincolo de el (fără cronometre ale inamicilor): aceasta înregistrează feed-ul de eliminări și tabelul de scor pe care le vede jucătorul și propriile lui cifre.

Fiecare răspuns este păstrat și întreg (regula convertorului 3DHeat, docs/converters.md din depozitul vizualizatorului): `heat.raw.parquet`, cu `type` endpoint-ul („allgamedata”, „eventdata”), `text` JSON-ul așa cum l-a trimis clientul, `status` când nu a fost 200. Un răspuns identic octet cu cel dinaintea lui din același endpoint (lista de evenimente cât timp nu se întâmplă nimic) este păstrat o dată și numărat în `unchanged_replies` din meta.json. allgamedata conține tot ce servesc celelalte endpoint-uri (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), deci acestea nu sunt cerute separat. Răspunsurile dinainte de meci (ecranul de încărcare) așteaptă într-un backlog și intră în sesiunea meciului; după GameEnd sesiunea rămâne deschisă până pleacă clientul, deci răspunsurile ecranului de final sunt păstrate cu ea.

Sursa: <https://developer.riotgames.com/docs/lol#game-client-api>

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | nu |
| Axa verticală | `z` |
| Unități | niciuna (fără poziții) |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tipul `gsi`: citește doar ce oferă jocul sau platforma (o integrare de stare a jocului sau un API local pe care îl servește jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- feed-ul de eliminări din eventdata: fiecare eveniment o dată, cu câmpurile lui numite decodate (ucigașul, victima și asistenții cu campion și echipă, structurile și partea lor, tipul dragonului, furturile, multikill-urile, aces, primul sânge, rezultatul) și fiecare alt câmp al unui eveniment pe rândul lui, sub numele lui
- din allgamedata: eliminările, morțile, asistențele, scorul de creep, scorul de ward, nivelul, aurul, campionul, timpul de joc, modul de joc și harta proprii

**Păstrat brut**

- `allgamedata`: fiecare răspuns întreg (`text`), la fiecare 2 s - activePlayer (abilități, fiecare statistică a campionului, rune complete, aur, nivel), allPlayers (obiecte cu sloturi și prețuri, rune, vrăji de invocator, scoruri, nivel, mort și cronometrul de reapariție, skin, bandă, bot), evenimentele, gameData (mod, timp, hartă, teren); `used` adevărat cât timp rulează meciul, fals pe ecranul de final
- `eventdata`: fiecare răspuns întreg, cerut la fiecare 0,5 s de la următorul id de eveniment; `used` adevărat când a adus evenimente noi
- un răspuns identic octet cu cel dinaintea lui din același endpoint este păstrat o dată și numărat (`unchanged_replies` în meta.json); răspunsurile de eroare (RESOURCE_NOT_FOUND de pe ecranul de încărcare) sunt păstrate cu `status` lor, înainte de începutul meciului

**Nu este disponibil**

- poziții: API-ul nu are (nicio hartă minimă, nicio coordonată)
- celelalte endpoint-uri (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): fiecare servește o parte din allgamedata, deci nu sunt cerute
- API-ul de reluare (`/replay/*` pe același port): redă reluări și jocuri urmărite odată ce este activat în game.cfg; nu face parte dintr-un meci jucat
- endpoint-urile lockfile ale clientului League: nu este un API publicat (Surse și reguli)
- valorile între două citiri: API-ul răspunde când este întrebat și nu trimite singur; scorul este cerut la fiecare 2 s, evenimentele la fiecare 0,5 s

**Dimensiune**: allgamedata are 15-40 KB (conține toată lista de evenimente, care crește) la fiecare 2 s: aproximativ 30-70 MB pe oră în `raw.bin`; eventdata adaugă puțin, pentru că răspunsurile identice sunt numărate, nu stocate; zstd micșorează JSON-ul repetat din `heat.raw.parquet` la câțiva MB pe oră (estimat după formatul documentat)

## Verificat {#verified}

testat pe un server local fals, care servește răspunsuri în formatul documentat; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
