---
title: "NVIDIA highlights (platforma)"
nav_order: 34
lang: "sl"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platforma) {#nvidia-highlights-platform}

Watcher shrani, kar NVIDIA highlights hrani o vaših igrah, da si svojo zgodovino pozneje lahko ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `nvidia-highlights`, vrsta [`platform`](sources-and-rules.md); teče ves čas (ne čaka, da se igra zažene) in vsakih 10 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- vsak nov posnetek, poudarek ali posnetek zaslona: igra, datoteka, vrsta, dolžina in trenutek (ura, ms)
- ID in ime poudarka, kadar ga je igra prijavila pri NVIDIA
- kje je bil igralec v tistem trenutku, kadar je drug adapter takrat zapisal isto igro
- zahteve za poudarke, ki jih beležijo igre GfeSDK, tudi kadar se nobeden posnetek ne shrani

## Od kod prihajajo {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;igra&gt;\config.json; posnetki v mapi zajemanja (%USERPROFILE%\Videos\NVIDIA\\&lt;Igra&gt;\\\*.mp4) in &lt;temp&gt;\Highlights\\&lt;igra&gt;; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe&gt;_&lt;pid&gt;.log

## Kako vklopiti {#how-to-switch-it-on}

NVIDIA App: vklopljen Instant Replay ali Highlights, posnetki shranjeni s tipko ali z igro

## Kako deluje {#how-it-works}

Kar zaganjalnik in grafični gonilnik hranita o igranju: Steamova statistika,
dosežki, čas igranja in časovnice ter poudarki in posnetki NVIDIA.

Nobeden od teh virov ne potrebuje, da bi igra sodelovala ali da teče, zato so trije adapterji tukaj
vedno vklopljeni in vsakih nekaj sekund preberejo nekaj datotek.

#### Poudarki in posnetki NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Kar hrani NVIDIA App / GeForce Experience, vse pod
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      kazalo galerije: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, ko je bila datoteka zapisana), profileName, drsName
                     (exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (kam se shranjujejo posnetki),
                     settings.tempDirectory (poudarki čakajo v
                     <temp>\Highlights\<igra>, dokler se ne shranijo)
Highlights\<igra>\config.json  vrste poudarkov, ki jih je igra prijavila:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
in sami posnetki, `<mapa zajemanja>\<Igra>\<Igra> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (posnetki zaslona: `<Igra> Screenshot yyyy.mm.dd - ...png`), čas v imenu je
lokalni čas, ko je bil posnetek shranjen. Igre GfeSDK svoje klice poudarkov beležijo tudi v
`%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Kaj to lahko in česa ne more dati: igra, ki podpira NVIDIA Highlights (GfeSDK), enkrat prijavi vrste
poudarkov - ID kot "kill", pomembnost, oznake, prikazno ime - kasneje pa pove samo "highlight <id>,
from <ms> before now to <ms> after". Ni položajev, ni tekme ali kroga, ni nasprotnika, ni
poljubnih podatkov: SDK zanje nima polja. Shranjen posnetek doda datoteko, ime igre, dolžino in
čas. Zabeleži se torej "tak trenutek, v tej igri, ob tem času" - kraj pa samo tako, da čas poiščemo
v zapisu drugega adapterja za isto igro (`position_at`), kar ta adapter stori za vsak zapisani posnetek.
<https://developer.nvidia.com/highlights>

Vsak adapter hrani, kar je že videl, v `<podatki>\state\<id>.json`, zato ponovni zagon ne zapiše ničesar dvakrat.

Vsaka seja hrani tudi, iz česa so nastale njene vrstice, cele (pravilo pretvornikov 3DHeat, docs/converters.md
v repozitoriju pregledovalnika), v `heat.raw.parquet`: bajti datoteke statistike in njene sheme ter blok localconfig
igre (steam-stats; datoteka statistike, ki je dekoder ne more prebrati, dobi sejo, ki hrani samo njene bajte),
glava datoteke časovnice in vsak vnos kot JSON (steam-timeline), vsak vnos kazala posnetkov, definicije
poudarkov igre in vsaka vrstica dnevnikov GfeSDK (nvidia-highlights).

Isti modul streže tudi: [Steam statistika (platforma)](game-steam-stats.md), [Steam Timeline (platforma)](game-steam-timeline.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | samo posojeni: mesto, ki ga za ta trenutek ima drug zapis iste igre |
| Navpična os | `y` |
| Enote | metri |
| Zrcaljenje za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **ne**. `games --markdown` to prikaže kot "enoigralska".
- Vrsta `platform`: bere samo, kar igra ali platforma ponudi (kar hranita Steam ali grafični gonilnik), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- vsak nov posnetek in posnetek zaslona: igra, datoteka, vrsta, medij, dolžina (iz kazala, sicer iz glave MP4), trenutek iz imena datoteke, ID in ime poudarka, kjer ga je igra prijavila, in igralčevo mesto takrat iz zapisa drugega adapterja
- zahteve za poudarke GfeSDK (vsak `Posted Request HL...`, razen klicev nastavitev) s svojim časom

**Shranjeno surovo**

- `UGC`: celoten vnos posnetka iz kazala galerije UGCTracker.json, vsako polje, ki ga zapiše NVIDIA
- `clip_file`: za posnetek, ki ga kazalo ne navaja, pot datoteke, velikost, čas in mapa
- `highlights_config`: `Highlights\<igra>\config.json` igre, kakor je zapisan (pomembnost, oznake, imena v vseh jezikih), enkrat na sejo
- `gfesdk_log`: vsaka vrstica dnevnikov GfeSDK, prebrana po prvem zagonu, `used` resničen za zahteve za poudarke in false za ostalo (nastavitve, video nastavitve, sporočila samega SDK)

**Ni na voljo**

- sami posnetki in posnetki zaslona: video in slike ostanejo, kjer jih je shranil NVIDIA; vrstice imenujejo datoteko
- kar je bilo tam pred prvim zagonom adapterja: vzeto kot že videno, da se leta posnetkov ne spremenijo v seje naenkrat (`baseline`; False jih zapiše)
- `apps` in `info` v UGCTracker.json ter GallerySettings.json: nastavitve aplikacije, ne trenutki igranja; uporabi se mapa zajemanja, ki jo navajata
- položaji, krogi, nasprotniki: GfeSDK zanje nima polja

**Velikost**: približno 1 KB na posnetek in nekaj KB definicij ter vrstic dnevnika na zagon igre: daleč pod 1 MB na uro

## Preverjeno {#verified}

preizkušeno na pravem kazalu galerije, nastavitvah, definicijah poudarkov in posnetkih iz lokalne namestitve; vrstice zahtev za poudarke GfeSDK in ID-ji poudarkov v posnetkih še niso preizkušeni

## Vir {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
