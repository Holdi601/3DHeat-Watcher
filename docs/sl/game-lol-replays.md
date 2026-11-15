---
title: "League of Legends (posnetki)"
nav_order: 30
lang: "sl"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (posnetki) {#league-of-legends-replays}

Po tekmi League of Legends watcher spremeni posnetek, ki ga je shranil odjemalec, v datoteke, ki jih lahko pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `lol-replays`, vrsta [`replay`](sources-and-rules.md); teče ves čas (ne čaka, da se igra zažene) in išče nove podatke vsakih 5 s.*

## Kaj se zapiše {#what-is-recorded}

- prvak, vloga, ekipa, ubijanja, smrti, asistence, zlato, škoda prvakom in izid vsakega igralca ter vsako drugo število iz tabele na koncu igre
- vaša vrstica kot statistika, vaše vrstice pa označene kot vaše (meta.json `player`), z vašim Riot ID v nastavitvah
- z vašim lastnim ključem Riot API: položaj vsakega igralca vsako minuto s statistiko te minute, in vsak dogodek časovnice (ubijanja tam, kjer so se zgodila, stavbe, pošasti, straže, predmeti, spretnosti) ob stenskem času, ki ga da časovnica
- vsak del datoteke posnetka cel v heat.raw.parquet; ni dekodirano: potek igre minuto za minuto, ki je šifriran in zakrit proti goljufanju

## Od kod prihaja {#where-it-comes-from}

posnetki, ki jih shrani odjemalec League: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (samo navadni metapodatki ob koncu igre); z vašim lastnim ključem Riot API se uradna časovnica tekme pridobi iz Riotovega Match-V5 API-ja

## Kako vklopiti {#how-to-switch-it-on}

shranite posnetek v odjemalcu League (zgodovina tekem > prenesite); za položaje nastavite riot_api_key in riot_platform z `config --set`

## Kako deluje {#how-it-works}

League of Legends in VALORANT: kar se od njunih posnetkov da prebrati tako, kot je.

Obe igri shranita posnetke na igralčev disk in obe zaščitita vsebino: podatki igre minuto za minuto so zakriti in pri vsaki zakrpi drugače, da jih ni mogoče uporabiti za goljufanje. Da bi prišli do njih, bi bilo treba razstaviti igrino lastno kodo, kar Riotovi pogoji prepovedujejo (pogoji storitve 3.1 in 7.1) - zato tu ni narejeno. Prebere se, kar je v datoteki odprto, ostalo pa se ohrani tako, kot je: vsak del datoteke cel v `heat.raw.parquet` seje (pravilo pretvornika 3DHeat, docs/converters.md v repozitoriju pregledovalnikja), štet v `selfCheck.completeness` v meta.json.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Obe različici kontejnerja imata tabelo na koncu igre kot navaden JSON (`statsJson`): za vsakega od desetih igralcev prvaka, ubijanja, smrti, asistence, zlato, škodo prvakom, predmete, ekipo, vlogo, zmago, njegovo Riot ID in vsako drugo število, ki ga igra sešteje (čez sto na igralca); vse to postane vrstica `player_result` igralca. ROFL1 (zakrpa 14.9 in prej) jo ima po fiksni glavi (`RIOT\0\0`, 256-bajtni podpis, nato dolžine); ROFL2 (14.11 naprej, `RIOT\2\0`) na koncu datoteke, njena dolžina je v zadnjih štirih bajtih (navedel je Riotov inženir, ReplayBook issue 299). ROFL1-jeva glava podatkov (id igre, dolžina, števila kosov in ključnih sličic, dolžina ključa kosa) in njegova tabela kosov (id, tip, dolžina, naslednji kos, zamik) sta odprti in se preberejo; sami kosi so šifrirani in ostanejo cel, neprebrani. Postavitve iz roflxd.cs (MIT).

Položaji ne pridejo iz datoteke. S Riotovim razvijalskim ključem igralca samega (`riot_api_key` v nastavitvah; osebni ključ je namenjen prav temu, "prikazovanju (lastnih) statistik igralca"), se uradna časovnica tekme pridobi iz Riotovega Match-V5 API-ja: položaj vsakega igralca enkrat na minuto z vsem, kar okvir te minute pove o njem (zlato, izkušnje, nivo, minioni, statistika prvaka in škode), in vsak dogodek časovnice - ubijanja, stavbe, elitne pošasti, straže, predmeti, spretnosti, nivoji - vsak kot vrstica, tam, kjer se je zgodil, kadar ima mesto. Brez ključa se ne pridobi nič in ničesar se ne pošlje.

Enaka modul služi tudi: [VALORANT (posnetki)](game-valorant-replays.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | da |
| Navpična os | `y` |
| Enote | enote zemljevida Summoner's Rift (okoli 15000 čez) |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `replay`: bere samo to, kar igra ali platforma ponudi (ponovitve in demo posnetki, ki jih igra shrani), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- metapodatki JSON: dolžina igre, različica, id zadnjega kosa in ključnih sličic ter `statsJson` - vsako polje tabele vsakega igralca na njegovi vrstici `player_result` (števila, zapisana kot besedilo, se preberejo kot števila)
- ROFL1: blok dolžin, glava podatkov (id igre, dolžina igre, števila ključnih sličic in kosov, id-ji začetnega kosa in začetka igre, interval ključnih sličic, ključ kosa, kot je shranjen) in tabela kosov (id, tip, dolžina, naslednji kos, zamik) - v meta.json `rofl` in v `text` surovih vrstic
- ROFL2: niz z različico
- časovnica tekme Match-V5 (samo z lastnim ključem API): vsak okvir udeleženca v vrstici `position` (ali `participant_frame`, če nima mesta) z vsemi polji, sploščenimi (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp` ...); vsak dogodek kot vrstica, poimenovana po svojem tipu, tam, kjer ima `position`; CHAMPION_KILL kot ubijanje in smrt

**Shranjeno surovo**

- vsak del .rofl cel, po vrstnem redu v datoteki (`offset`), tako da deli sestavljajo datoteko: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); vsako področje, ki ga noben del ne pokrije, kot `unknown`
- časovnica cela: `timeline <type>` za vsak dogodek, `timeline participantFrame` za okvir vsakega igralca (`participant` je njegov id), `timeline` za ostalo

**Ni na voljo**

- sama igra (položaji, sposobnosti, vsaka enota, potek minuto za minuto): kosi ROFL1 in telo ROFL2 sta šifrirana, paketi znotraj pa zakriti in z vsako zakrpo drugačni; priti do njih pomeni razstaviti odjemalca, kar Riotovi pogoji prepovedujejo (3.1, 7.1). Shranjeno cel, neprebrano
- položaji brez vašega lastnega ključa Riot API: datoteka jih nima odprte

**Velikost**: surovi zapis je približno enako velik kot sam posnetek: šifrirani kosi se ne stisnejo

## Preverjeno {#verified}

bralnik metapodatkov preizkušen na datotekah, sestavljenih po postavitvah iz roflxd.cs (MIT); časovnica po dokumentiranem JSON-u Match-V5; pravega posnetka ni bilo na voljo za preverjanje

## Vir {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
