---
title: "VALORANT (posnetki)"
nav_order: 45
lang: "sl"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (posnetki) {#valorant-replays}

Po tekmi VALORANT watcher spremeni posnetek, ki ga je shranila igra, v datoteke, ki jih lahko pogledate kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `valorant-replays`, vrsta [`replay`](sources-and-rules.md); teče ves čas (ne čaka, da se igra zažene) in išče nove podatke vsakih 5 s.*

## Kaj se zapiše {#what-is-recorded}

- zemljevid, id tekme in izbrani agenti; informacijski blok posnetka (dolžina, različice, ime, čas snemanja, zastavice stiskanja in šifriranja)
- časovnica dogodkov strežnika: ubitja (ubijalec in žrtev kot id-ji omrežja), začetki krogov, nastavljene, razstavljene in eksplodirane bombe (spike), uporabljeni ultimati, menjava strani - vsak z id-jem in metapodatki
- vsak del datoteke cel v heat.raw.parquet; ni dekodirano: položaji, imena ali rezultati - ti so v zakritem toku

## Od kod prihaja {#where-it-comes-from}

posnetki, ki jih shrani VALORANT: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (samo deli, ki niso zakriti)

## Kako vklopiti {#how-to-switch-it-on}

shranite posnetek v VALORANT (kariera > tekma > prenesite posnetek)

## Kako deluje {#how-it-works}

League of Legends in VALORANT: kar se od njunih posnetkov da prebrati tako, kot je.

Obe igri shranita posnetke na igralčev disk in obe zaščitita vsebino: podatki igre minuto za minuto so zakriti in pri vsaki zakrpi drugače, da jih ni mogoče uporabiti za goljufanje. Da bi prišli do njih, bi bilo treba razstaviti igrino lastno kodo, kar Riotovi pogoji prepovedujejo (pogoji storitve 3.1 in 7.1) - zato tu ni narejeno. Prebere se, kar je v datoteki odprto, ostalo pa se ohrani tako, kot je: vsak del datoteke cel v `heat.raw.parquet` seje (pravilo pretvornika 3DHeat, docs/converters.md v repozitoriju pregledovalnikja), štet v `selfCheck.completeness` v meta.json.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, lokalni posnetek Unreal Engine (postavitev iz vrfkit, Apache-2.0, in ValorantReplayParser, MIT). Odprto: informacijski blok posnetka (dolžina, različica omrežja, changelist, ime, čas snemanja, ali je stisnjen ali šifriran), zemljevid, id tekme in izbrani agenti (v glavi) ter časovnica dogodkov strežnika - ubitja (ubijalec in žrtev kot id-ji omrežja, ne imena), začetki krogov, nastavljene, razstavljene in eksplodirane bombe, uporabljeni ultimati, menjava strani - vsak s svojim časom, id-jem in metapodatki. Položaji, imena, rezultati in vse drugo so v zakritem toku (kosi podatkov ponovitve in kontrolne točke), ki se shrani cel in ne bere.

Enaka modul služi tudi: [League of Legends (posnetki)](game-lol-replays.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | ne |
| Navpična os | `z` |
| Enote | enote sveta VALORANT |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `replay`: bere samo to, kar igra ali platforma ponudi (ponovitve in demo posnetki, ki jih igra shrani), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- informacijski blok, vsako polje (meta.json `vrf`): različica datoteke, prilagojene različice, dolžina, različica omrežja, changelist, ime, zastavica živega, čas snemanja, zastavici stisnjeno in šifrirano, ključ kot je shranjen
- glava: zemljevid, id tekme in izbrani agenti (poiščeni po svoji obliki)
- vsak kos dogodkov: id, skupina, metapodatki, začetni in končni čas, iz njegovih podatkov ime dogodka, njegov čas v sekundah in števila pred njim (id-ji omrežja ubijalca in žrtve) - vrstica za vsakega

**Shranjeno surovo**

- vsak kos cel, po vrstnem redu v datoteki (`offset`), tako da deli sestavljajo datoteko: `info`, `header`, `event <skupina>`, `replay_data`, `checkpoint`, `chunk <n>` za tip, ki ga postavitev ne poimenuje, `trailing` za bajte po zadnjem celem kosu

**Ni na voljo**

- položaji, imena, rezultati, sposobnosti, vsak okvir igre: kosi podatkov ponovitve in kontrolnih točk so zakriti; branje pomeni razstaviti odjemalca, kar Riotovi pogoji prepovedujejo. Shranjeno cel, neprebrano
- vsebina šifriranega posnetka: prehojen in shranjen cel, znotraj ničesar ni prebrano

**Velikost**: surovi zapis je približno enako velik kot sam posnetek: zakriti tok se ne stisne

## Preverjeno {#verified}

zgrajeno po postavitvi kontejnerja, dokumentirani v vrfkit (Apache-2.0); nepreizkušeno na pravem posnetku, ker ni bil na voljo - pred branjem preveri in preskoči, kar se ne ujema

## Vir {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
