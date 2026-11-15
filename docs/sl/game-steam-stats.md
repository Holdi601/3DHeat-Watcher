---
title: "Statistika Steam (platforma)"
nav_order: 43
lang: "sl"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Statistika Steam (platforma) {#steam-statistics-platform}

Watcher shrani, kar statistika Steam hrani o vaših igrah, da lahko kasneje pogledate svojo zgodovino kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `steam-stats`, vrsta [`platform`](sources-and-rules.md); deluje ves čas (ne čaka, da se igra začne) in išče nove podatke na vsakih 30 s.*

## Kaj se zapiše {#what-is-recorded}

- vsaka statistika, ki jo igra hrani v Steamu (njena lastna imena in vrednosti), za vsako igro, ob spremembi
- odklenjeni dosežki s prikaznim imenom, opisom in časom odklenitve
- spremembe statistik s staro vrednostjo, novo vrednostjo in razliko
- čas igranja (minute, zadnja dva tedna) in čas zadnjega igranja

## Od kod prihaja {#where-it-comes-from}

Steamov lokalni predpomnilnik statistik %STEAM%\appcache\stats\UserGameStats_&lt;account&gt;_&lt;appid&gt;.bin s UserGameStatsSchema_&lt;appid&gt;.bin; čas igranja iz %STEAM%\userdata\\&lt;account&gt;\config\localconfig.vdf (%STEAM% iz HKCU\Software\Valve\Steam SteamPath)

## Kako ga vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklopiti: watcher bere vir tako, kot ga igra ali platforma ponuja.

## Kako deluje {#how-it-works}

Kar zagonski program in grafični gonilnik hranita o igranju: Steamove statistike, dosežki, čas igranja in časovnice ter NVIDIA-ini posnetki in klipi.

Nobeden od teh virov ne potrebuje, da igra sodeluje ali teče, zato so trije adapterji tukaj vedno vklopljeni in vsakih nekaj sekund preberejo nekaj datotek.

#### Statistika Steam (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, ki ga Steam ponovno zapiše, kadar igra shrani svoje statistike, dekodiran s shemo `UserGameStatsSchema_<appid>.bin` poleg njega (binarni KeyValues, glej `_steam.py`). Statistike so cela ali decimalna števila, kot jih določi igra; dosežki imajo čas odklenitve v sekundah po Unixu. Čas igranja je v `<Steam>\userdata\<account>\config\localconfig.vdf` pod apps/&lt;appid&gt;: Playtime in Playtime2wks v minutah, LastPlayed v sekundah po Unixu. Steam se najde prek HKCU\Software\Valve\Steam SteamPath. API statistik: <https://partner.steamgames.com/doc/features/achievements>

Isti modul streže tudi: [NVIDIA highlights (platforma)](game-nvidia-highlights.md), [Steam Timeline (platforma)](game-steam-timeline.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zapisani | ne |
| Os navzgor | `y` |
| Enote | metri |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Ti podatki gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, tako da pregledovalnik 3DHeat vrstice sam obrne in prilagodi merilo - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **ne**. `games --markdown` to prikaže kot "enoigralska".
- Vrsta `platform`: bere samo, kar igra ali platforma izda (kar hrani Steam ali grafični gonilnik), zato zapisuje tudi v spletni igri, ne le brez povezave; zastavica odloča samo, ali sme pomnilnik sploh kdaj biti branjen.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji `memory` berejo pomnilnik, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Ključi statistike, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; zgoraj v »Kaj se zapiše« so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali ohrani, nikoli ni izpuščeno. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, ohrani celoten v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, ohranjeno po imenu; `used` označuje, kar je postalo tudi vrstica), `meta.json` pa v `selfCheck.completeness` šteje vsak `type` - `lost` je 0.

**Prebrano**

- vsaka statistika iz datoteke statistik po imenu API (int, float, avgrate), vsak bit dosežka s časom odklenitve, poimenovan in opisan po shemi
- spremembe glede na zadnje branje (staro, novo, razlika), novi odklepi; čas igranja, dvotedenski čas igranja in zadnje igranje iz localconfig.vdf

**Ohranjeno surovo**

- `UserGameStats`: bajti datoteke statistik, celi, vsakič ko se zapiše (`crc`, `PendingChanges`, biti dosežkov, ki jih shema ne določa več, in vsak ključ, ki ga dekoder preskoči, so v njej)
- `UserGameStatsSchema`: bajti datoteke sheme poleg nje, da se statistike lahko dekodirajo iz same seje (imena vseh statistik in dosežkov v vseh jezikih, ikone, zastavice)
- `localconfig_app`: celoten blok igre iz localconfig.vdf kot JSON (stanje sinhronizacije v oblaku, možnosti zagona, značke in vsak drug ključ, ki ga Steam hrani za igro), kadar je zabeležen njen čas igranja
- datoteka statistik, ki je dekoder ne more prebrati (odrezana sredi zapisovanja ali nova postavitev): njeni bajti in shema v seji brez vrstic (`used` false; `unreadable` v meta.json)

**Ni na voljo**

- preostanek localconfig.vdf (prijatelji, klepet, nastavitve Steama): ni igrin in je zasebno
- vrednosti statistik med dvema zapisoma: Steam ponovno zapiše datoteko, ko igra shrani svoje statistike, navadno ob zaprtju
- globalni odstotki dosežkov in statistike drugih igralcev: so na Steamovih strežnikih, ne tukaj

**Velikost**: nekaj KB na zabeleženo sejo igranja, plus shema (do nekaj sto KB za igro z veliko dosežki) - daleč pod 1 MB na uro igranja; zstd zmanjša besedilo sheme za polovico ali več

## Preverjeno {#verified}

Preizkušeno na pravih datotekah statistik in shemah iz lokalne namestitve; zaznavanje sprememb preizkušeno na datotekah, zgrajenih v binarnem formatu KeyValues.

## Vir {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
