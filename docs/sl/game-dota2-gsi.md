---
title: "Dota 2 (stanje igre)"
nav_order: 13
lang: "sl"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (stanje igre) {#dota-2-game-state}

Medtem ko igrate Dota 2, watcher shrani, kaj igra sporoča programom na vašem računalniku, da lahko to pozneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `dota2-gsi`, vrsta [`gsi`](sources-and-rules.md); teče, dokler je `dota2.exe` zagnan, in novih podatkov išče vsakih 0,05 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj lastnega heroja (svetovni X/Y, enote Dote; brez višine), dokler je živ
- pojavitev, smrti (s časom ponovnega pojava) in ponovne pojavitve lastnega heroja
- pobitja, iz rasti števila pobitij
- zgradbe, uničene ob Roshanu, dogodki igre (roshan_killed, aegis_picked_up, ...), stanja igre, rezultat
- pobitja, smrti, asistence, zadnji udarci, zanikanja, zlato, GPM, XPM, raven, heroj

## Od kod prihaja {#where-it-comes-from}

Game State Integration: HTTP POST-i na 127.0.0.1:3312, nastavljeni v datoteki &lt;Dota&gt;\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## Kako ga vklopiti {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, nato zaženite Dota 2 (datoteko prebere ob zagonu)

Ukaz vpišite v terminal, odprt v mapi watcherja (glej [Preden začnete](before-you-start.md)). Če ne uspe, zadnja vrstica pove, zakaj; [Namestitev in zagon](installing-and-running.md) pokrije pogoste vzroke.

`python -m heat3d_watch setup dota2-gsi` izpiše, katere datoteke bi spremenil; `python -m heat3d_watch setup dota2-gsi --apply` jih spremeni, izvirnik pa ohrani kot `<file>.heat3d-backup` (glej [Ukazi](commands.md#setup)). Za vsako spremembo izpiše `dota2-gsi: changed: ...`, ali `dota2-gsi: nothing to change`, kadar je že vklopljeno.

Nastavitve iz okoljskih spremenljivk:

- `HEAT3D_DOTA_GSI_PORT`: vrata, na katera igra pošilja (privzeto 3312); cfg datoteka igre mora navesti ista vrata

## Kako deluje {#how-it-works}

Valve Game State Integration: Counter-Strike 2 in Dota 2 sporočata lokalnemu spletnemu strežniku, kaj se dogaja.

Obe igri ob zagonu prebereta vsako datoteko `gamestate_integration_*.cfg` v svoji cfg mapi in od takrat pošiljata JSON dokument na `uri` vsake datoteke, kadarkoli se stanje spremeni (največ vsakih `throttle` sekund, in vsakih `heartbeat` sekund, kadar se nič ne spremeni). Watcher je tisti spletni strežnik: posluša samo na 127.0.0.1, na vsak POST takoj odgovori s 200 in delo opravi v svoji niti za branje.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Kaj igralec dobi - in s tem, kaj se lahko zapiše - določi igra, ki odloči, kaj igralec sme videti:

- CS2: `provider` (lastni steamid), `map` (ime, način, faza warmup/live/intermission/gameover, krog, rezultat team_ct/team_t), `round` (faza freezetime/live/over, bomba postavljena/eksplodirala/razstavljena, win_team), `player` (igralec, ki ga *gledate*: sebe, dokler ste živi, soigralca po smrti) s `state` (zdravje, oklep, denar, round_kills, round_killhs, round_totaldmg), `match_stats` (pobitja, asistence, smrti, mvps, rezultat), `position` in `forward` kot nizi "x, y, z" v svetovnih enotah (palci, Z navzgor), `weapons`; `bomb` samo za gledalce. Položaje drugih igralcev (`allplayers_*`) pošiljajo samo gledalcem in GOTV, zato jih watcher ne zahteva.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos v svetovnih enotah, level, alive, respawn_seconds), `buildings` (zdravje po stolpih, barakah in prastarem), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Višine ni: z je 0. Prav tako zahtevano in v celoti ohranjeno: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (igra pošlje, kar ima igralčev lastni odjemalec; kateri od njih kaj vsebujejo med igranjem, ne med gledanjem, ni preizkušeno).

Vsak dokument je prav tako ohranjen v celoti (pravilo pretvornikov 3DHeat, docs/converters.md v repozitoriju pregledovalnika): `heat.raw.parquet`, `type` "gsi", `text` pa JSON, kakor je bil poslan - le žeton iz cfg datoteke je izbrisan, ker je to skrivnost watcherja, ne podatek igre. Dokumenti, poslani, ko ni odprte tekme (meniji, nalaganje, med tekmami), čakajo v `Backlog` in gredo v sejo naslednje tekme, pred njen začetek; kar ostane, ko se igra zapre, dobi svojo sejo, ki vsebuje samo njih. Nepravilne objave in objave z napačnim žetonom so prav tako ohranjene ("gsi-unreadable", "gsi-bad-auth").

Viri: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(format, ki ga je ohranil CS2), <https://github.com/antonpup/CounterStrike2GSI> in <https://github.com/antonpup/Dota2GSI> (seznami polj; MIT, prebrano samo zaradi dejstev).

Isti modul služi tudi: [Counter-Strike 2 (stanje igre)](game-cs2-gsi.md).

## Osi položajev {#positions-and-axes}

| | |
|---|---|
| Zapisani položaji | da |
| Os navzgor | `z` |
| Enote | svetovne enote Dote (z je vedno 0) |
| Zrcaljeno za pregledovalnik | `y` |
| Merilo enot (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

Ti gredo v `meta.json` vsake seje (`axes`) in, kadar ima seja položaje, v nogo `heat.parquet`, tako pregledovalnik sam obrača in meri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `gsi`: bere samo to, kar igra ali platforma objavi (game-state integration ali lokalni API, ki ga igra streže), zato zapisuje tudi pri igri na spletu, tako kot offline; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali ohrani, nikoli ne izpusti. Poleg vrstic je vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, ohranjen v celoti v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text`, nato vsako polje, ohranjeno po imenu; `used` označi, kar je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- položaj lastnega heroja (x/y), živ, raven, zdravje, največ zdravja, mana, največ mane; pojavitev, smrti s časom ponovnega pojava, ponovne pojavitve
- pobitja (rast števila pobitij); pobitja, smrti, asistence, zadnji udarci, zanikanja, zlato, GPM, XPM, neto vrednost, raven in heroj kot statistika
- uničene zgradbe, Roshan dol in nazaj, vsak vnos v `events` enkrat, stanja igre, zmagovalec

**Ohranjeno surovo**

- `gsi`: vsak dokument, ki ga igra pošlje, v celoti, kakor je bil poslan (`text`), `used` true, kadar je bil prebran med tekmo - vseh petnajst komponent, ki jih zahteva cfg datoteka: ponudnik, map (dan/noč, pavza, časovne omejitve žetonov, rezultati), player (zanesljivo in nezanesljivo zlato, serije, seznam pobitij, izdani ukazi, ...), hero (bonusi, talenti, Aghanim, lastnosti), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league in igrin diff `previously`/`added`
- dokumenti iz menijev, nalaganja in med tekmami: ohranjeni na enak način, ob svojem času pred začetkom naslednje tekme; po zadnji tekmi v lastni seji (`raw_only` v meta.json)
- `gsi-unreadable`: objava, ki ni JSON objekt, njeni bajti kot `payload` in `length`
- `gsi-bad-auth`: objava z drugačnim žetonom, kot ga ima cfg datoteka

**Ni na voljo**

- višina: igra pošilja samo x in y
- drugi heroji med igranjem: igra pošilja lastnega heroja, vsakega igralca pa samo gledalcem (takrat se ohrani surovo, ne riše se); več komponent (draft, minimap, couriers) nosi samo to, kar ima igralčev lastni odjemalec - med igranjem to ni preizkušeno
- stanja med objavami: največ eno na 0,1 s (`throttle`), vsakih 10 s, kadar se nič ne spremeni
- žeton iz cfg datoteke, izbrisan v vsakem ohranjenem dokumentu: skrivnost watcherja, ne podatek igre
- objave preko 10.000 čakajočih (watcher je obstal) se štejejo kot `dropped_packets` in se ne ohranijo; objava nad 4 MB se ohrani kot `gsi-unreadable` z dolžino, vendar brez bajtov

**Velikost**: z vsemi komponentami je dokument igralca velik okoli 5-15 KB in se objavi do 10-krat na sekundo (ura se spremeni vsako objavo): okoli 100-500 MB na uro v `raw.bin` med tekmo, približno desetino tega v zstd `heat.raw.parquet`; gledalčev dokument, z vsemi igralci in mini zemljevidom, je nekajkrat večji (ocenjeno iz objavljenega formata, ne izmerjeno na igri)

## Preverjeno {#verified}

preizkušeno na dokumentih v objavljenem GSI formatu, poslanih tekočemu adapterju; nepreizkušeno na tekoči igri

## Vir {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
