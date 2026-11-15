---
title: "Forza Horizon 5 (živi podatki)"
nav_order: 22
lang: "sl"
source: game-forza-horizon-5.md
source_hash: "0083724478e7"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 5 (živi podatki) {#forza-horizon-5-live-data}

Medtem ko igrate Forza Horizon 5, watcher shrani podatke, ki jih igra sama pošilja, da jih lahko kasneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `forza-horizon-5`, vrsta [`telemetry`](sources-and-rules.md); teče, ko je `ForzaHorizon5.exe` zagnan, in išče nove podatke vsakih 0,1 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj lastnega avtomobila (svetovni XYZ, m) na 10 Hz, s hitrostjo, prestavo, plinom, zavoro in krogom
- začetek in konec vožnje (session_start/session_end), krogi s časom kroga, po igri
- začetek in cilj dirke s položajem na dirki
- teleportacije (previjanje, hitro potovanje): `teleport`, kjer je bil avto, `spawn`, kjer je zdaj
- krogi, najboljši krog, razdalja, najvišja hitrost, dirke

## Od kod prihaja {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (format Dash); vsak paket se nespremenjen posreduje na 127.0.0.1:5301

## Kako vklopiti {#how-to-switch-it-on}

V igri: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, vrata 5300 (Motorsport: format Dash). FH Companion ali druga aplikacija Data Out: nastavite njena vrata na 5301 - watcher posreduje vsak paket; dokler druga aplikacija posluša na 5300, watcher vrata prepusti njej in ne zapiše ničesar.

## Kako deluje {#how-it-works}

Lastna telemetrija dirkaških iger: Forza, igre Assetto Corsa, reli igre in BeamNG, zapisana kot poti, krogi in etape.

Vsaka igra tu objavlja svojo telemetrijo namenoma, za nadzorne plošče in gibalne naprave; ničesar se ne vbrizga in ne bere se nič, kar igra ne ponudi. Dekodiranje ni napisano dvakrat: to so snemalniki krogov iz GameCapture-ja 3DHeat, `heat3d_capture/telemetry`, kopirani v `heat3d_watch/decoders` (tam preizkušeni na paketih, sestavljenih iz objavljenih postavitev). Ta modul njihove okvirje pretvori v vrstice watcherja: položaj avtomobila nekajkrat na sekundo s hitrostjo, prestavo in pedali, dogodek za vsak krog ali etapo ter števila, ki jih voznik zanima: krogi, najboljši krog, razdalja, najvišja hitrost.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, vklopljen v nastavitvah igre HUD and Gameplay, na 127.0.0.1, vrata 5300, format Dash. En paket na simulacijski takt; odmik bloka nadzorne plošče se najde iz paketov (`forza.detect_layout`). Svetovni metri, Y navzgor; svet je levosučen in se riše tako, kot pride, kot ga riše snemalnik krogov (dokumentacija Forza Motorsport in Forza Horizon "Data Out").
Igra pošilja na ena vrata, FH Companion in druge aplikacije Data Out pa poslušajo na istih. Dva programa ne moreta deliti vrat: v Windows dobi pakete vtičnica, vezana na 127.0.0.1, vtičnica, vezana na vse naslove na istih vratih, pa nobenega, ne glede na to, katera je bila prva. Zato watcher malo počaka, potem ko se igra zažene, preden zasede vrata, nikoli ne vzame vrat aplikaciji, ki jih drži, in jih izpusti takoj, ko druga aplikacija začne poslušati tam. Medtem ko drži vrata, vsak paket nespremenjen posreduje na 127.0.0.1:5301 - nastavite polje za vrata v FH Companion (zavihek telemetry) na 5301, in oba zapisujeta.

#### Vse shranjeno {#everything-kept}

Vrstic je nekaj na sekundo; igre jih pošljejo veliko več. Vsak UDP paket, ki pride - v menijih, med krogi, tudi tisti, ki jih noben dekoder ne bere - se shrani cel v `heat.raw.parquet` seje pod svojo obliko (`dash-horizon`, `session_update`, `extradata3`, `H3D1` ...), vsaka stran skupnega pomnilnika (celotna preslikava, ne samo dekodirani bajti) pa ob vsaki spremembi, pod imenom svoje preslikave (`acpmf_physics` ...). `used` označi, kaj je postalo tudi vrstica; `selfCheck.completeness` v `meta.json` šteje vsako vrsto (pravilo pretvornika 3DHeat).

Istemu modulu pripadajo tudi: [Assetto Corsa (živi podatki)](game-assetto-corsa.md), [Assetto Corsa Competizione (živi podatki)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živi podatki)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živi podatki)](game-assetto-corsa-rally.md), [BeamNG.drive (živi podatki)](game-beamng.md), [DiRT Rally 2.0 (živi podatki)](game-dirt-rally-2.md), [EA SPORTS WRC (živi podatki)](game-ea-wrc.md), [Forza Horizon 4 (živi podatki)](game-forza-horizon-4.md), [Forza Horizon 6 (živi podatki)](game-forza-horizon-6.md), [Forza Motorsport (živi podatki)](game-forza-motorsport.md), [Richard Burns Rally (živi podatki)](game-richard-burns-rally.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | da |
| Navpična os | `y` |
| Enote | metri; Forzin svet je levosučen, riše se tako, kot pride, kot ga riše snemalnik krogov |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo to, kar igra ali platforma ponudi (vrata UDP ali skupni pomnilnik, ki ga igra objavi), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- vrstice pri 10 Hz: položaj, hitrost, prestava, plin, zavora, krog, zasuk/nagib/zvitje (rad), vrtljaji, krmiljenje (-1..1); session_start z zaporedno številko avtomobila, razredom, PI in pogonom; krogi z igrinim časom kroga; položaj na dirki

**Shranjeno surovo**

- vsak paket, ki doseže vrata, cel, z igrinim taktom (en na simulacijski takt), pod svojo obliko: `dash-horizon` (324 bajtov, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: obraba pnevmatik in id proge), `sled` (232, brez položaja), `<n>-byte` za vse drugo - vključno z menijskimi paketi (isRaceOn 0), paketi, zadržanimi, dokler postavitev nadzorne plošče ni dokazana, in približno 13 bajti paketa Horizon, ki jih nobena objavljena postavitev ne poimenuje
- blok Sled: vsak kanal kolesa (zdrs, kot zdrsa, skupni zdrs, vzmetenje, hitrost kolesa, rumble, puddle), pospeški, kotna hitrost, moč, navor, turbo, gorivo, temperature pnevmatik, sklopka, ročna zavora, vožnjena linija, razlika zavor AI: vse je v paketih, dekodirano z `decoders/fulllap.decode_full`

**Ni na voljo**

- drugi avtomobili: Data Out opiše samo avto igralca
- ime proge ali poti: Forza Horizon je nikoli ne pošlje; Motorsport 2023 pošlje samo številko proge
- paketi, medtem ko drug program (FH Companion) drži UDP 5300: watcher vrata prepusti njemu

**Velikost**: približno 85 MB na uro pred stiskanjem (60 paketov na sekundo po 324 bajtov plus 70-bajtna glava elementa); zaporedni paketi se malo razlikujejo, zato zstd ohrani delček

## Preverjeno {#verified}

dekodiranje je od snemalnika krogov iz gamecapture (preizkušeno na paketih, sestavljenih iz postavitve Data Out); adapter preizkušen na sintetičnih paketih in na posnetih trajektorijah krogov, predvajanih kot paketi; še nepreizkušeno na sami igri

## Vir {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
