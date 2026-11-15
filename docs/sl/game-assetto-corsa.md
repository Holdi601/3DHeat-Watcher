---
title: "Assetto Corsa (živi podatki)"
nav_order: 2
lang: "sl"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (živi podatki) {#assetto-corsa-live-data}

Medtem ko igrate Assetto Corsa, watcher shrani podatke, ki jih igra sama pošilja, da jih lahko kasneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `assetto-corsa`, vrsta [`telemetry`](sources-and-rules.md); teče, ko sta `acs.exe` ali `acs_x86.exe` zagnana, in išče nove podatke vsakih 0,1 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj lastnega avtomobila (svetovni XYZ, m: povprečje stičnih točk pnevmatik) na 10 Hz, s hitrostjo, prestavo, plinom in zavoro
- začetek in konec seje s progo in avtomobilom, ki ju navede igra
- krogi po števcu krogov v igri, s časom kroga
- teleportacije (nazaj v boks, ponovni zagon): `teleport`, kjer je bil avto, `spawn`, kjer je zdaj
- krogi, najboljši krog, razdalja, najvišja hitrost

## Od kod prihaja {#where-it-comes-from}

skupni pomnilnik Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Kako vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklopiti: watcher bere vir tako, kot ga igra ali platforma ponuja.

## Kako deluje {#how-it-works}

Lastna telemetrija dirkaških iger: Forza, igre Assetto Corsa, reli igre in BeamNG, zapisana kot poti, krogi in etape.

Vsaka igra tu objavlja svojo telemetrijo namenoma, za nadzorne plošče in gibalne naprave; ničesar se ne vbrizga in ne bere se nič, kar igra ne ponudi. Dekodiranje ni napisano dvakrat: to so snemalniki krogov iz GameCapture-ja 3DHeat, `heat3d_capture/telemetry`, kopirani v `heat3d_watch/decoders` (tam preizkušeni na paketih, sestavljenih iz objavljenih postavitev). Ta modul njihove okvirje pretvori v vrstice watcherja: položaj avtomobila nekajkrat na sekundo s hitrostjo, prestavo in pedali, dogodek za vsak krog ali etapo ter števila, ki jih voznik zanima: krogi, najboljši krog, razdalja, najvišja hitrost.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, vklopljen v nastavitvah igre HUD and Gameplay, na 127.0.0.1, vrata 5300, format Dash. En paket na simulacijski takt; odmik bloka nadzorne plošče se najde iz paketov (`forza.detect_layout`). Svetovni metri, Y navzgor; svet je levosučen in se riše tako, kot pride, kot ga riše snemalnik krogov (dokumentacija Forza Motorsport in Forza Horizon "Data Out").
Igra pošilja na ta vrata, FH Companion in druge aplikacije Data Out pa poslušajo na istih vratih. Dva programa ne moreta deliti vrat: v Windows dobi pakete vtičnica, vezana na 127.0.0.1, vtičnica, vezana na vse naslove na istih vratih, pa nobenega, ne glede na to, katera je bila prva. Zato watcher malo počaka, potem ko se igra zažene, preden zasede vrata, nikoli ne vzame vrat aplikaciji, ki jih drži, in jih izpusti takoj, ko druga aplikacija začne poslušati tam. Medtem ko drži vrata, vsak paket nespremenjen posreduje na 127.0.0.1:5301 - nastavite polje za vrata v FH Companion (zavihek telemetry) na 5301, in oba zapisujeta.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Skupni pomnilnik, ki ga igra piše za aplikacije: `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`). Odprt samo za branje in šele, ko ga igra ustvari (`simracing_shm`). Položaj je povprečje štirih stičnih točk pnevmatik, svetovni metri, Y navzgor. Krogi po števcu igre (AC, ACC) ali s ponovnim prehodom začetne točke (AC EVO, AC Rally), kot to za snemalnik krogov naredi `kunos.py`.

#### Vse shranjeno {#everything-kept}

Vrstic je nekaj na sekundo; igre jih pošljejo veliko več. Vsak UDP paket, ki pride - v menijih, med krogi, tudi tisti, ki jih noben dekoder ne bere - se shrani cel v `heat.raw.parquet` pod svojo obliko (`dash-horizon`, `session_update`, `extradata3`, `H3D1` ...), vsaka stran skupnega pomnilnika (celotna preslikava, ne samo dekodirani bajti) pa ob vsaki spremembi, pod imenom svoje preslikave (`acpmf_physics` ...). `used` označi, kaj je postalo tudi vrstica; `selfCheck.completeness` v `meta.json` šteje vsako vrsto (pravilo pretvornika 3DHeat).

Istemu modulu pripadajo tudi: [Assetto Corsa Competizione (živi podatki)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živi podatki)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živi podatki)](game-assetto-corsa-rally.md), [BeamNG.drive (živi podatki)](game-beamng.md), [DiRT Rally 2.0 (živi podatki)](game-dirt-rally-2.md), [EA SPORTS WRC (živi podatki)](game-ea-wrc.md), [Forza Horizon 4 (živi podatki)](game-forza-horizon-4.md), [Forza Horizon 5 (živi podatki)](game-forza-horizon-5.md), [Forza Horizon 6 (živi podatki)](game-forza-horizon-6.md), [Forza Motorsport (živi podatki)](game-forza-motorsport.md), [Richard Burns Rally (živi podatki)](game-richard-burns-rally.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | da |
| Navpična os | `y` |
| Enote | metri |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo to, kar igra ali platforma ponudi (vrata UDP ali skupni pomnilnik, ki ga igra objavi), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- vrstice pri 10 Hz iz strani fizike: položaj (povprečje stičnih točk pnevmatik), hitrost, prestava, plin, zavora, zasuk, nagib in zvitje (rad), vrtljaji, krmiljenje (kot ga stran ima); začetek seje s progo in avtomobilom iz statične strani; krogi, položaj na dirki

**Shranjeno surovo**

- vsaka stran cela - celotna preslikava, ne samo dekodirani bajti - ob vsaki spremembi bajtov, ob branju watcherja na 10 Hz: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; ponovno branje, ki je bajt za bajtom enako zadnjemu, se šteje v `unchanged_reads` v meta.json in ni shranjeno znova
- vse, dekodirano samo za datoteke krogov (`decoders/kunos.py`: po kolesu zdrs, obremenitev, tlak, temperature, nagib koles, vzmetenje, stične točke, temperature zavor, zdrs in kot zdrsa; hitrost sveta in lokalna hitrost, kotna hitrost, pomočniki), je v teh straneh

**Ni na voljo**

- položaji drugih avtomobilov: strani opisujejo samo avto igralca (graphics stran ACC ima v nekaterih različicah id-je avtomobilov in koordinate drugih - shranjeni so v surovi strani, niso dekodirani)
- fizikalni takti med branji watcherja: igra prepisuje stran s svojo fizikalno hitrostjo (do 333 Hz), watcher pa bere 10-krat na sekundo

**Velikost**: približno 150-300 MB na uro pred stiskanjem (4 KB področje na stran pri največ 10 spremembah na sekundo); strani so večinoma ničle, zstd ohrani majhen delež

## Preverjeno {#verified}

dekodiranje je od snemalnika krogov iz gamecapture (preizkušeno na sintetičnih straneh); adapter preizkušen na skupnem pomnilniku, zgrajenem v testu po dokumentirani postavitvi; še nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
