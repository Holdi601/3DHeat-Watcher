---
title: "EVE Online (dnevniške datoteke)"
nav_order: 20
lang: "sl"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (dnevniške datoteke) {#eve-online-log-files}

Medtem ko igrate EVE Online, watcher bere datoteke, ki jih igra zapisuje, in shrani, kaj se je zgodilo, da si to pozneje lahko ogledate kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `eve`, vrsta [`log`](sources-and-rules.md); teče, medtem ko se izvaja `exefile.exe`, in vsakih 0,5 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- škoda, storjena in prejeta z drugo ladjo, pilotom, oznako korporacije, orožjem in kakovostjo zadetka
- zgrešeni streli, storjeni in prejeti
- izplačila nagrad (ubijanje NPC) z ISK
- skoki med sistemi
- vsaka vrstica dnevnika igre in klepeta cela v heat.raw.parquet
- škoda, storjena in prejeta, zadetki, zgrešitve, ubijanja za nagrado in ISK, skoki

## Od kod prihajajo {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt in Chatlogs\\\*.txt zraven (vsaka datoteka, zapisana od zagona odjemalca)

## Kako vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklopiti: watcher bere vir tako, kot ga igra ali platforma ponuja.

## Kako deluje {#how-it-works}

EVE Online: dnevniki odjemalca igre, `Documents\EVE\logs\Gamelogs\*.txt`.

Odjemalec zapiše eno datoteko na lik in prijavo,
`<yyyymmdd>_<hhmmss>[_<id lika>].txt`; beleženje v datoteko je privzeto vklopljeno. Če teče več
odjemalcev hkrati, vsak zapiše svojo, zato se sledi vsaki datoteki, zapisani od zagona igre.
Glava in vrstice (čas EVE je UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(vrstica combat je v datoteki ena sama vrstica). Oznake oblikovanja se pred ujemanjem odstranijo.
Datoteka je bila skozi leta UTF-8 in UTF-16; prebrani sta obe.
Format CCP ne dokumentira; to je navadni besedilni dnevnik odjemalca, prebran tako, kot ga berejo
skupnostna orodja za bojni dnevnik (npr. <https://docs.rs/crate/eve-log-parser>).
Brez položajev.

Poleg njega `Documents\EVE\logs\Chatlogs\<kanal>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
ena datoteka na kanal klepeta na prijavo (kadar je beleženje klepeta vklopljeno, kar je privzeto v odjemalcu),
UTF-16, glava z imenom kanala in poslušalca, nato
`[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Vsaka vrstica obeh se shrani cela v surovo spremljevalno datoteko seje (pravilo pretvornikov 3DHeat): vrstica dnevnika
igre pod svojim kanalom v oklepajih (`combat`, `notify`, `bounty`, `None` ...), vrstica klepeta kot `chat` s svojim
kanalom, glave kot `gamelog header` / `chatlog header`.

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | ne |
| Navpična os | `y` |
| Enote | položaji niso zabeleženi |
| Zrcaljenje za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `log`: bere samo, kar igra ali platforma ponudi (datoteke, ki jih igra zapisuje med delovanjem), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- zadetki `(combat)` iz dnevnika igre, storjeni in prejeti (znesek, drugi pilot, oznaka korporacije, ladja, orožje, kakovost zadetka) ter zgrešitve v obe smeri
- izplačila `(bounty)` z ISK in vrstice `Jumping from A to B`
- `Listener` v glavi dnevnika igre: čigav dnevnik je

**Shranjeno surovo**

- vsaka vrstica dnevnika igre cela, `type` = njen kanal v oklepajih (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None` ...), z `file` in `listener`; `used` tam, kjer je postala vrstica; glave kot `gamelog header`
- vsaka vrstica dnevnika klepeta cela (Local, korporacija, flota, zasebni kanali, obvestila `EVE System`, na primer sprememba kanala Local ob skoku), `type` `chat`, z `channel`, `listener` in `file`; glave kot `chatlog header`. Še niso pretvorjene v vrstice
- oznake oblikovanja (`<color>`, `<b>`, `<font>`) ostanejo v surovem besedilu; vrstice jih imajo odstranjene

**Ni na voljo**

- položaji: odjemalec jih v svoje dnevnike ne zapisuje
- boji drugih pilotov: dnevnik igre je samo poslušalčev
- dnevniki prejšnjih prijav: vsaka prijava zapiše nove datoteke; tiste, starejše od tega zagona odjemalca, se ne berejo znova
- klepet, kadar je igralec v nastavitvah odjemalca izklopil beleženje klepeta
- predpomnilnik odjemalca in datoteke nastavitev: niso dnevniki in niso dokumentirani

**Velikost**: dnevnik igre meri 0,1-2 MB na uro (večina v boju); dnevniki klepeta so odvisni od odprtih kanalov - zaseden kanal Local ali flota 0,5-3 MB na uro; zstd v heat.raw.parquet jih skrči približno na desetino

## Preverjeno {#verified}

preizkušeno na sintetičnih vrsticah dnevnika igre v obliki, ki jo objavljajo skupnostni razčlenjevalniki; nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
