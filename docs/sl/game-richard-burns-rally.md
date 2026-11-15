---
title: "Richard Burns Rally (živi podatki)"
nav_order: 39
lang: "sl"
source: game-richard-burns-rally.md
source_hash: "1b9866f5a1f6"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (živi podatki) {#richard-burns-rally-live-data}

Medtem ko igrate Richard Burns Rally, watcher shrani podatke, ki jih igra sama pošilja ven, da si jih lahko pozneje ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `richard-burns-rally`, vrsta [`telemetry`](sources-and-rules.md); teče, medtem ko se izvaja `RichardBurnsRally_SSE.exe` ali `RichardBurnsRally.exe`, in vsakih 0,1 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- položaj lastnega avtomobila (svetovne koordinate XYZ, m) desetkrat na sekundo s hitrostjo, prestavo, plinom, zavoro in razdaljo etape
- začetek etape (začne se štoparica etape), cilj s časom etape, ponovni zagoni
- teleporti (ponastavitev na cesto): `teleport`, kje je bil avtomobil, `spawn`, kje je zdaj
- etape, najboljši čas etape, razdalja, najvišja hitrost

## Od kod prihajajo {#where-it-comes-from}

UDP telemetrija vtičnika NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Kako vklopiti {#how-to-switch-it-on}

RSF/NGP: v RichardBurnsRally.ini, v oddelku [NGP] nastavite udpTelemetry=1 in naslov 127.0.0.1:6776

## Kako deluje {#how-it-works}

Lastna telemetrija dirkalnih iger: Forza, igre Assetto Corsa, rally igre in BeamNG, zapisana kot poti, krogi in etape.

Vsaka tukaj navedena igra objavlja svojo telemetrijo namensko, za nadzorne plošče in gibalne naprave; nič se ne vbrizgava in ničesar, kar igra ne ponuja, se ne bere. Dekodiranje ni napisano dvakrat: to so snemalniki krogov gamecapture v `heat3d_capture/telemetry` v 3DHeat GameCapture, kopirani v `heat3d_watch/decoders` (tam preizkušeni na paketih, sestavljenih iz objavljenih postavitev), ta modul pa njihove okvirje pretvori v vrstice watcherja - položaj avtomobila nekajkrat na sekundo s hitrostjo, prestavo in pedali, dogodek za vsak krog ali etapo ter števila, ki jih voznik zanima: krogi, najboljši krog, razdalja, najvišja hitrost.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP "Data Out", vklopljen v igri v nastavitvah HUD and Gameplay, na 127.0.0.1, vrata 5300, format Dash. En paket na vsak simulacijski takt; odmik bloka nadzorne plošče se najde iz paketov (`forza.detect_layout`). Svetovni metri, os Y navzgor; svet je levosučen in se riše tako, kot ga igra pošlje, kot to počne snemalnik krogov (dokumentacija Forza Motorsport in Forza Horizon "Data Out").
Igra pošilja na ta vrata, FH Companion in druge aplikacije Data Out poslušajo na istih vratih. Dva programa ne moreta deliti vrat: v Windows vtičnica, vezana na 127.0.0.1, dobi pakete, vtičnica, vezana na vse naslove na istih vratih, pa nobenega, ne glede na to, katera je prva. Zato watcher malo počaka, potem ko se igra zažene, preden zavzame vrata, jih nikoli ne vzame aplikaciji, ki jih drži, in jih izpusti takoj, ko druga aplikacija začne poslušati tam. Medtem ko drži vrata, vsak paket nespremenjen posreduje na 127.0.0.1:5301 - nastavite polje za vrata v FH Companion (zavihek telemetry) na 5301, in snemata oba.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC-jeva `Documents/My Games/WRC/telemetry/config.json` (paket `session_update` strukture `wrc`),
DiRT-ova `hardware_settings_config.xml` (`<udp enabled="true" extradata="3" port="20777">`), RBR-jev
vtičnik NGP (`udpTelemetry=1`, vrata 6776). Etape po štoparici etape igre (`rally.StageSplitter`).
RBR ne dokumentira svojih osi: navpična os je tista, vzdolž katere se etapa najmanj spreminja, določena
ob zaprtju seje.

#### Vse shranjeno {#everything-kept}

Vrstic je nekaj na sekundo; igre pošiljajo veliko več. Vsak UDP paket, ki pride - v menijih, med krogi, tudi tisti, ki jih noben dekoder ne bere - se shrani nedotaknjen v `heat.raw.parquet` seje pod svojo obliko (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), vsaka stran skupnega pomnilnika (celotno preslikavo, ne le dekodiranih bajtov) pa ob vsaki spremembi, pod imenom svoje preslikave (`acpmf_physics`, ...). `used` označuje, kaj je postalo tudi vrstica; `selfCheck.completeness` v `meta.json` šteje vsako vrsto (pravilo pretvornikov 3DHeat).

Isti modul streže tudi: [Assetto Corsa (živi podatki)](game-assetto-corsa.md), [Assetto Corsa Competizione (živi podatki)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živi podatki)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živi podatki)](game-assetto-corsa-rally.md), [BeamNG.drive (živi podatki)](game-beamng.md), [DiRT Rally 2.0 (živi podatki)](game-dirt-rally-2.md), [EA SPORTS WRC (živi podatki)](game-ea-wrc.md), [Forza Horizon 4 (živi podatki)](game-forza-horizon-4.md), [Forza Horizon 5 (živi podatki)](game-forza-horizon-5.md), [Forza Horizon 6 (živi podatki)](game-forza-horizon-6.md), [Forza Motorsport (živi podatki)](game-forza-motorsport.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | da |
| Navpična os | `y` |
| Enote | metri; navpična os določena iz vožnje (RBR svojih osi ne dokumentira) |
| Zrcaljenje za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **ne**. `games --markdown` to prikaže kot "enoigralska".
- Vrsta `telemetry`: bere samo, kar igra ali platforma ponudi (UDP vrata ali skupni pomnilnik, ki ga igra objavlja), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- vrstice na 10 Hz: položaj, hitrost, prestava, plin, zavora, razdalja etape, yaw, vrtljaji, krmiljenje; začetek etape, cilj s časom etape, ponovni zagoni

**Shranjeno surovo**

- vsak paket, ki pride do vrat, cel, pri taktu igre: pod svojo obliko `telemetry` (30-bajtni TelemetryData vtičnika NGP z 664 bajti), `rbr <n>-byte` za vse drugo
- v paketu poleg vrstic: odnos avtomobila, lastne hitrosti in pospeški avtomobila, za vsako kolo odklon vzmeti in sila, napredek etape in razdalja do konca; ostalih 664 bajtov (motor, bloki pnevmatik in zavor za vsako kolo) še nikjer ni dekodiranih

**Ni na voljo**

- drugi avtomobili: igre pošiljajo samo avto igralca
- njegova enota hitrosti in osi: niso dokumentirane - hitrost se vzame iz položajev, navzgor iz vožnje

**Velikost**: približno 160 MB na uro pri 60 paketih na sekundo (664 bajtov plus 70-bajtna glava vnosa); zstd ohrani delček

## Preverjeno {#verified}

dekodiranje je snemalnika krogov gamecapture (preizkušeno na paketih, sestavljenih iz dokumentiranih postavitev); adapter preizkušen na paketih, sestavljenih v testu in poslanih čez UDP; nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
