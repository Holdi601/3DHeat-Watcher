---
title: "Path of Exile (dnevniške datoteke)"
nav_order: 36
lang: "sl"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (dnevniške datoteke) {#path-of-exile-log-files}

Medtem ko igrate Path of Exile, watcher bere datoteke, ki jih igra zapisuje, in shrani, kaj se je zgodilo, da si to pozneje lahko ogledate kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `poe`, vrsta [`log`](sources-and-rules.md); teče, medtem ko se izvaja `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` ali `PathOfExile_x64_KG.exe`, in vsakih 0,5 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- območja, v katera vstopite, z ravnjo območja, ID-jem območja in njegovim semenom
- dvigi ravni z razredom in ravnjo
- smrti ("has been slain")
- igralci, ki vstopijo v območje in ga zapustijo, šepetanja noter in ven, zahteve za trgovanje, sprejete trgovine
- vsaka vrstica Client.txt te seje cela v heat.raw.parquet
- smrti, pridobljeni dvigi ravni, najvišja raven, obiskana območja, različna območja, šepetanja, zahteve za trgovanje, trgovine

## Od kod prihajajo {#where-it-comes-from}

&lt;namestitev&gt;\logs\Client.txt Path of Exile ali Path of Exile 2 (sledi se mu; mapa namestitve je mapa zagnane izvršljive datoteke)

## Kako vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklopiti: watcher bere vir tako, kot ga igra ali platforma ponuja.

## Kako deluje {#how-it-works}

Path of Exile in Path of Exile 2: dnevnik odjemalca, `<namestitev>\logs\Client.txt`.

Obe igri dopisujeta v eno datoteko Client.txt v svoji mapi namestitve, dokler sta nameščeni
(raste čez zagone). Vrstice so videti tako

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- lokalni čas, števec milisekund, zgoščena vrednost, raven in nit, nato tisto, kar prikazuje
  okno klepeta. Sporočila so iz angleške različice odjemalca; odjemalec v drugem jeziku jih zapiše
  prevedene in tukaj niso razumljena. Nič ne daje položaja. Format Grinding Gear Games ne dokumentira;
  to je navadni besedilni dnevnik igre, tako kot ga že leta berejo skupnostna orodja (pomočniki za trgovanje,
  vodniki po ravneh) - npr. <https://github.com/klayveR/poe-log-monitor> (MIT) za seznam dogodkov.

Mapa namestitve je mapa zagnane izvršljive datoteke; brez nje se iščejo knjižnice Steam in privzeta
mapa samostojnega odjemalca.

Vsaka vrstica te seje se shrani cela v surovo spremljevalno datoteko seje (pravilo pretvornikov 3DHeat), ne glede
na to, ali tukaj kaj pomeni: `type` je raven in beleževalec v njenih oklepajih (`INFO Client`, `DEBUG Client`,
`WARN Client`, ...), vrstica z oznako časa brez oklepajev je `untagged`, vrstica brez časa pa `untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- `You have entered <zone>`, z ravnjo območja, ID-jem območja in semenom iz vrstice `Generating level` tik pred njo
- `<name> (<class>) is now level <n>`, `<name> has been slain`, igralci, ki vstopijo v območje in ga zapustijo, šepetanja noter in ven (z oznako, ali gre za zahtevo za trgovanje), sprejete in preklicane trgovine

**Shranjeno surovo**

- vsaka vrstica te seje cela, `type` = raven in beleževalec v njenih oklepajih (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` tam, kjer je postala vrstica: globalni, trgovski, skupinski in ceh klepet, `Connecting to instance server`, obvestila AFK in DND, odgovori na klepetalne ukaze, kot sta `/played` in `/deaths`, nalagalne in motorne vrstice odjemalca - shranjeno, še ni pretvorjeno v vrstice
- vrstica z oznako časa brez oklepajev (`***** LOG FILE OPENING *****`) kot `untagged`, vrstica brez časa kot `untimed`

**Ni na voljo**

- položaji: noben zapis v dnevniku jih ne daje
- kaj zapiše odjemalec v drugem jeziku: vrstice se shranijo, a v vrstice se pretvorijo samo angleška sporočila
- prejšnji zagoni: Client.txt raste čez zagone; vrstice, zapisane pred tem zagonom igre, se pustijo (shranjene so bile, ko so bile igrane)
- ubijanja, poškodbe, plen in drevo veščin: igra jih ne beleži

**Velikost**: Client.txt na uro raste za približno 0,3-3 MB (večina iz vrstic DEBUG med nalaganjem območij, več pri živahnem trgovskem klepetu); zstd v heat.raw.parquet ga skrči na približno desetino

## Preverjeno {#verified}

preizkušeno na sintetičnih vrsticah Client.txt v obliki igre; nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
