---
title: "League of Legends (stanje igre)"
nav_order: 29
lang: "sl"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (stanje igre) {#league-of-legends-game-state}

Medtem ko igrate League of Legends, watcher shrani, kar igra poroča programom na vašem računalniku, da si to pozneje lahko ogledate kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `lol-live`, vrsta [`gsi`](sources-and-rules.md); teče, medtem ko se izvaja `League of Legends.exe`, in vsakih 0,5 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- brez položajev: API jih nima
- potek ubijanj: ubijanja, smrti in asistence igralca, ubijanja drugih prvakov z ubijalcem, žrtvijo, asistenti
- zmaji, heraldi, baroni, stolpi, inhibitorji, večkratna ubijanja, asi, prva krvava kri, začetek in konec igre
- lastna ubijanja, smrti, asistence, rezultat na kreposti, rezultat varovanja, raven, zlato, prvak, čas igre, izid
- cilji, ki jih je vzela igralčeva ekipa

## Od kod prihajajo {#where-it-comes-from}

API živih podatkov odjemalca igre, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), med tekmo

## Kako vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklopiti: watcher bere vir tako, kot ga igra ali platforma ponuja.

## Kako deluje {#how-it-works}

League of Legends: API živih podatkov, ki ga odjemalec igre streže med tekmo.

Med tekmo (tudi v orodju za vadbo in v načinu gledalca) `League of
Legends.exe` odgovarja na <https://127.0.0.1:2999> s tem, kar igralec vidi
v vmesniku igre:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} od EventID N naprej: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Položajev ni: API jih nima, zato je seja League dogodki in statistika, brez tabele
položajev. Potrdilo je samoizdano, Riotovo lastno korensko (`riotgames.pem`, objavljeno na
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Pogoji njegove uporabe niso navedeni,
zato ga ne priložimo: postavite ga v `<podatki>\riotgames.pem`, in povezava se preveri z njim; brez njega
preverjanje ni vklopljeno - in to samo za 127.0.0.1, edini naslov, s katerim adapter govori.

Riotova politika dovoljuje orodjem prikazati, kar lahko igralec ve iz same igre, in nič, kar bi bilo
izračunano preko tega (brez sovražnikovih časovnikov): to zapiše potek ubijanj in lestvico, ki jo vidi
igralec, ter igralčeva lastna števila.

Vsak odgovor se shrani tudi cel (pravilo pretvornikov 3DHeat, docs/converters.md v repozitoriju
pregledovalnika): `heat.raw.parquet`, `type` je krajišče ("allgamedata", "eventdata"), `text` je JSON, kot
ga je poslal odjemalec, `status`, kadar ni bil 200. Odgovor, ki je bajt za bajtom enak prejšnjemu
istega krajišča (seznam dogodkov, medtem ko se nič ne dogaja), se shrani enkrat in šteje v `unchanged_replies`
v meta.json. allgamedata vsebuje vse, kar strežejo druga krajišča (activeplayer\*, playerlist, playerscores,
playeritems, playersummonerspells, playermainrunes, gamestats), zato se ne sprašujejo ločeno. Odgovori pred
tekmo (nalagalni zaslon) čakajo v zaostanku in gredo v sejo tekme; po GameEnd seja ostane odprta, dokler ne
odide odjemalec, zato se odgovori zaključnega zaslona shranijo z njo.

Vir: <https://developer.riotgames.com/docs/lol#game-client-api>

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | ne |
| Navpična os | `z` |
| Enote | nobene (brez položajev) |
| Zrcaljenje za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `gsi`: bere samo, kar igra ali platforma ponudi (vmesnik integracije stanja igre ali lokalni API, ki ga igra streže), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- potek ubijanj iz eventdata: vsak dogodek enkrat, z dekodiranimi poimenovanimi polji (ubijalec, žrtev in asistenti z prvakom in ekipo, konstrukcije in njihova stran, vrsta zmaja, ukradeni cilji, večkratna ubijanja, asi, prva krvava kri, izid), in vsako drugo polje dogodka na svoji vrstici pod svojim imenom
- iz allgamedata: lastna ubijanja, smrti, asistence, rezultat na kreposti, rezultat varovanja, raven, zlato, prvak, čas igre, način igre in zemljevid

**Shranjeno surovo**

- `allgamedata`: vsak odgovor cel (`text`), na vsaki 2 s - activePlayer (sposobnosti, vsaka statistika prvaka, cele rune, zlato, raven), allPlayers (predmeti z režami in cenami, rune, prizivanja, rezultati, raven, mrtev in čas do ponovnega rojstva, izgled, pas, bot), dogodki, gameData (način, čas, zemljevid, teren); `used` je resničen, medtem ko tekma teče, false na zaključnem zaslonu
- `eventdata`: vsak odgovor cel, zahtevan na vsakih 0,5 s od naslednjega ID-ja dogodka naprej; `used` je resničen, kadar je prinesel nove dogodke
- odgovor, ki je bajt za bajtom enak prejšnjemu istega krajišča, se shrani enkrat in šteje (`unchanged_replies` v meta.json); odgovori z napako (RESOURCE_NOT_FOUND na nalagalnem zaslonu) se shranijo s svojim `status`, pred začetkom tekme

**Ni na voljo**

- položaji: API jih nima (brez minimape, brez koordinat)
- druga krajišča (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): vsako streže del allgamedata, zato se ne sprašujejo
- API ponovitev (`/replay/*` na istih vratih): predvaja ponovitve in gledane igre, ko je vklopljen v game.cfg; ni del odigrane tekme
- krajišča datoteke zaklepanja odjemalca League: niso javno dokumentiran API (Viri in pravila)
- vrednosti med dvema branjema: API odgovarja, ko ga vprašamo, in ne potiska; lestvica se sprašuje na vsaki 2 s, dogodki na vsakih 0,5 s

**Velikost**: allgamedata meri 15-40 KB (vsebuje celoten seznam dogodkov, ki raste) na vsaki 2 s: približno 30-70 MB na uro v `raw.bin`; eventdata doda malo, ker se nespremenjeni odgovori štejejo, ne shranjujejo; zstd skrči ponovljeni JSON v `heat.parquet` na nekaj MB na uro (ocenjeno iz dokumentiranega formata)

## Preverjeno {#verified}

preizkušeno na lažnem lokalnem strežniku, ki streže odgovore v dokumentirani obliki; nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
