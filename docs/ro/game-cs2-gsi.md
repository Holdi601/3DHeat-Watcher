---
title: "Counter-Strike 2 (starea jocului)"
nav_order: 9
lang: "ro"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (starea jocului) {#counter-strike-2-game-state}

Cât joci Counter-Strike 2, watcher-ul salvează ce raportează jocul către programe de pe calculatorul tău, ca să te poți uita mai târziu la ele pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `cs2-gsi`, tip [`gsi`](sources-and-rules.md); rulează cât timp `cs2.exe` este pornit și caută date noi la fiecare 0,05 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția ta (XYZ în lume, în țoli) și direcția în care privești, de până la 10 ori pe secundă cât ești în viață
- apariții (prima vedere a fiecărei runde, reapariții) și morți (viața ajunge la 0, sau numărul de morți crește)
- eliminările, cu arma activă, din statisticile meciului
- runde (început, sfârșit, câștigător), bomba plantată, dezamorsată sau explodată, fazele meciului și rezultatul
- eliminări, asistențe, morți, MVP-uri, scor, bani, daune, eliminări cu lovitură în cap, runde câștigate și pierdute

## De unde vine {#where-it-comes-from}

Game State Integration: cereri HTTP POST către 127.0.0.1:3311, configurate de &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Cum îl pornești {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, apoi pornești CS2 (jocul citește fișierul la pornire)

Scrie comanda într-un terminal deschis în folderul watcher-ului (vezi [Înainte de a începe](before-you-start.md)). Dacă eșuează, ultima linie spune de ce; [Instalarea și rularea](installing-and-running.md) acoperă cauzele obișnuite.

`python -m heat3d_watch setup cs2-gsi` arată ce fișiere ar schimba; `python -m heat3d_watch setup cs2-gsi --apply` le schimbă, păstrând originalul ca `<file>.heat3d-backup` (vezi [Comenzi](commands.md#setup)). Afișează `cs2-gsi: changed: ...` pentru fiecare modificare, sau `cs2-gsi: nothing to change` dacă este deja pornit.

Setări din variabile de mediu:

- `HEAT3D_CS2_GSI_PORT`: portul la care trimite jocul (implicit 3311); fișierul cfg al jocului trebuie să indice același port

## Cum funcționează {#how-it-works}

Valve Game State Integration: Counter-Strike 2 și Dota 2 spun unui server web local ce se întâmplă.

Ambele jocuri citesc fiecare `gamestate_integration_*.cfg` din folderul lor cfg la pornire și, de atunci încolo, trimit un document JSON la `uri`-ul fiecărui fișier ori de câte ori se schimbă starea (cel mult la fiecare `throttle` secunde, și la fiecare `heartbeat` secunde când nu se schimbă nimic). Watcher-ul este chiar acel server web: ascultă doar pe 127.0.0.1, răspunde imediat cu 200 la fiecare cerere POST și face munca în propriul său fir de sondare.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Ce i se trimite unui jucător - și deci ce poate fi înregistrat - este ce decide jocul că jucătorul are voie să vadă:

- CS2: `provider` (propriul steamid), `map` (nume, mod, faza warmup/live/intermission/gameover, runda, scorul team_ct/team_t), `round` (faza freezetime/live/over, bomba plantată/explodată/dezamorsată, win_team), `player` (jucătorul *urmărit*: tu, cât ești în viață, sau un coleg după moarte), cu `state` (viață, armură, bani, round_kills, round_killhs, round_totaldmg), `match_stats` (eliminări, asistențe, morți, mvps, scor), `position` și `forward` ca șiruri „x, y, z” în unități din lume (țoli, Z în sus), `weapons`; `bomb` doar pentru spectatori. Pozițiile celorlalți jucători (`allplayers_*`) se trimit doar spectatorilor și GOTV, deci nu sunt cerute.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos în unități din lume, nivel, alive, respawn_seconds), `buildings` (viață per turn, cazarmă, ancient), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Nu există înălțime: z este 0. Mai sunt cerute și păstrate integral: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (jocul trimite ce are clientul propriu al jucătorului; dacă vreuna dintre ele conține ceva în timpul jocului, nu în timpul urmăririi, nu este testat).

Fiecare document este păstrat și integral (regula de convertor a 3DHeat, docs/converters.md din depozitul vizualizatorului): `heat.raw.parquet`, `type` „gsi”, `text` este JSON-ul trimis - doar tokenul din fișierul cfg este șters, fiindcă este secretul watcher-ului, nu date de joc. Documentele trimise cât nu este deschis niciun meci (meniuri, încărcare, între meciuri) așteaptă într-un `Backlog` și intră în sesiunea următorului meci, înainte de începutul lui; ce rămâne când se închide jocul primește o sesiune proprie, care conține doar ele. Cererile ilizibile și cele cu token greșit sunt păstrate și ele („gsi-unreadable”, „gsi-bad-auth”).

Surse: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (formatul pe care CS2 l-a păstrat) și <https://github.com/antonpup/CounterStrike2GSI> și <https://github.com/antonpup/Dota2GSI> (liste de câmpuri; licență MIT, citite doar pentru fapte).

Același modul servește și: [Dota 2 (starea jocului)](game-dota2-gsi.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `z` |
| Unități | țoli (unități Hammer) |
| Oglindită pentru vizualizator | `y` |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, așa că vizualizatorul 3DHeat rotește și scalează singur rândurile - vezi [Datele](the-data.md).

## Joc online {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tip `gsi`: citește doar ce scoate jocul sau platforma (o integrare a stării jocului sau o API locală pe care o servește jocul), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria are voie să fie citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistică pe care codul acestui adaptor le setează după nume (`stats` din `meta.json` al fiecărei sesiuni și tabelul `stats` din `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor jocului nu sunt în această listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce are sursa este citit sau păstrat, niciodată aruncat. În afară de rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat integral în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat după nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type` - `lost` este 0.

**Citit**

- poziția jucătorului urmărit, direcția privirii, viața, armura, banii, arma activă, casca, kitul de dezamorsare, cantitățile de flash/fum/foc și valoarea echipamentului, la fiecare rând de poziție cât este al jucătorului propriu (steamid-ul furnizorului = steamid-ul jucătorului)
- apariții, morți (viața ajunge la 0, sau numărul de morți din statisticile meciului), eliminări (numărul de eliminări crește)
- fazele meciului, runde (timpul de îngheț, live, încheiată, câștigătorul), bomba plantată/dezamorsată/explodată, rezultatul
- eliminări, asistențe, morți, MVP-uri, scor, bani, daune, eliminări cu lovitură în cap, runde câștigate și pierdute, ca statistici

**Păstrat brut**

- `gsi`: fiecare document trimis de joc, integral, așa cum a fost trimis (`text`), `used` adevărat când a fost citit într-un meci - furnizorul (versiune, marcaj de timp), harta (mod, nume de echipe, pierderi consecutive de runde, timeout-uri, victorii în serie, `round_wins` cu condiția de victorie a fiecărei runde), runda, jucătorul urmărit (clan, slotul de spectator, activitate, fiecare armă cu skin, muniție și rezervă), bomba, cronometrele fazelor, și diferența `previously`/`added` a jocului față de postarea dinainte
- documentele din meniuri, încărcare și între meciuri: păstrate la fel, la timpul lor, înainte de începutul următorului meci; după ultimul meci, într-o sesiune proprie (`raw_only` în meta.json)
- `gsi-unreadable`: o postare care nu este un obiect JSON, cu octeții ei ca `payload` și `length`
- `gsi-bad-auth`: o postare cu alt token decât cel din fișierul cfg

**Nedisponibil**

- ceilalți jucători (`allplayers_*`) și granatele (`allgrenades`): jocul le trimite doar spectatorilor și GOTV, iar watcher-ul nu le cere (Surse și reguli); un demo are toți jucătorii - vezi [Counter-Strike 2 (reluări)](game-cs2-demos.md)
- stările dintre postări: jocul postează cel mult la fiecare 0,1 s (`throttle`) și doar la o schimbare, la fiecare 10 s (`heartbeat`) în rest
- tokenul din fișierul cfg, șters din fiecare document păstrat: secretul watcher-ului, nu date de joc
- postările peste 10.000 de așteptare (când watcher-ul s-a blocat) se numără ca `dropped_packets`, nu se păstrează; o postare de peste 4 MB se păstrează ca `gsi-unreadable` cu lungimea ei, dar fără octeți

**Dimensiune**: documentul unui jucător are 2-4 KB și se postează de până la 10 ori pe secundă cât se schimbă ceva: aproximativ 30-150 MB pe oră în `raw.bin` cât rulează meciul, o zecime sau mai puțin în `heat.raw.parquet` comprimat cu zstd (estimat din formatul publicat, nemăsurat pe joc)

## Verificat {#verified}

testat pe documente în formatul GSI publicat, trimise adaptorului care rulează; instalarea și căutarea folderului cfg testate pe o instalare locală; netestat cu jocul care rulează

## Sursă {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
