---
title: "EA SPORTS WRC (živi podatki)"
nav_order: 17
lang: "sl"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (živi podatki) {#ea-sports-wrc-live-data}

Medtem ko igrate EA SPORTS WRC, watcher shrani podatke, ki jih igra sama pošilja, da jih lahko kasneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `ea-wrc`, vrsta [`telemetry`](sources-and-rules.md); teče, ko je `WRC.exe` zagnan, in išče nove podatke vsakih 0,1 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj lastnega avtomobila (svetovni XYZ, m) na 10 Hz, s hitrostjo, prestavo, plinom, zavoro in razdaljo na etapi
- začetek etape (ura etape se zažene), cilj s časom etape, ponovni zagoni
- teleportacije (vrnitev na cesto): `teleport`, kjer je bil avto, `spawn`, kjer je zdaj
- etape, najboljši čas etape, razdalja, najvišja hitrost

## Od kod prihaja {#where-it-comes-from}

UDP 127.0.0.1:20777, paket session_update privzete strukture `wrc` (Documents\My Games\WRC\telemetry\config.json); dokler drug program drži 20777, watcher vrata prepusti njemu

## Kako vklopiti {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` vklopi paket session_update v config.json (prej naredite varnostno kopijo)

Ukaz vtipkajte v terminalu, odprtem v mapi watcherja (glej [Preden začneš](before-you-start.md)). Če ne uspe, zadnja vrstica pove, zakaj; [Namestitev in zagon](installing-and-running.md) pokriva običajne vzroke.

`python -m heat3d_watch setup ea-wrc` našteje datoteke, ki bi se spremenile; `python -m heat3d_watch setup ea-wrc --apply` jih spremeni, original pa ohrani kot `<file>.heat3d-backup` (glej [Ukazi](commands.md#setup)). Izpiše `ea-wrc: changed: ...` za vsako spremembo ali `ea-wrc: nothing to change`, če je že vklopljeno.

## Kako deluje {#how-it-works}

Lastna telemetrija dirkaških iger: Forza, igre Assetto Corsa, reli igre in BeamNG, zapisana kot poti, krogi in etape.

Vsaka igra tu objavlja svojo telemetrijo namenoma, za nadzorne plošče in gibalne naprave; ničesar se ne vbrizga in ne bere se nič, kar igra ne ponudi. Dekodiranje ni napisano dvakrat: to so snemalniki krogov iz GameCapture-ja 3DHeat, `heat3d_capture/telemetry`, kopirani v `heat3d_watch/decoders` (tam preizkušeni na paketih, sestavljenih iz objavljenih postavitev). Ta modul njihove okvirje pretvori v vrstice watcherja: položaj avtomobila nekajkrat na sekundo s hitrostjo, prestavo in pedali, dogodek za vsak krog ali etapo ter števila, ki jih voznik zanima: krogi, najboljši krog, razdalja, najvišja hitrost.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, vklopljen v nastavitvah igre HUD and Gameplay, na 127.0.0.1, vrata 5300, format Dash. En paket na simulacijski takt; odmik bloka nadzorne plošče se najde iz paketov (`forza.detect_layout`). Svetovni metri, Y navzgor; svet je levosučen in se riše tako, kot pride, kot ga riše snemalnik krogov (dokumentacija Forza Motorsport in Forza Horizon "Data Out").
Igra pošilja na ena vrata, FH Companion in druge aplikacije Data Out pa poslušajo na istih. Dva programa ne moreta deliti vrat: v Windows dobi pakete vtičnica, vezana na 127.0.0.1, vtičnica, vezana na vse naslove na istih vratih, pa nobenega, ne glede na to, katera je bila prva. Zato watcher malo počaka, potem ko se igra zažene, preden zasede vrata, nikoli ne vzame vrat aplikaciji, ki jih drži, in jih izpusti takoj, ko druga aplikacija začne poslušati tam. Medtem ko drži vrata, vsak paket nespremenjen posreduje na 127.0.0.1:5301 - nastavite polje za vrata v FH Companion (zavihek telemetry) na 5301, in oba zapisujeta.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC-jev `Documents/My Games/WRC/telemetry/config.json` (paket `session_update` strukture `wrc`), DiRT-ov `hardware_settings_config.xml` (`<udp enabled="true" extradata="3" port="20777">`), RBR-jev NGP vtičnik (`udpTelemetry=1`, vrata 6776). Etape po uri etape igre (`rally.StageSplitter`). RBR ne dokumentira svojih osi: navpična os je tista, ki se vzdolž etape najmanj spreminja, odloči se, ko se seja zaključi.

#### Vse shranjeno {#everything-kept}

Vrstic je nekaj na sekundo; igre jih pošljejo veliko več. Vsak UDP paket, ki pride - v menijih, med krogi, tudi tisti, ki jih noben dekoder ne bere - se shrani cel v `heat.raw.parquet` seje pod svojo obliko (`dash-horizon`, `session_update`, `extradata3`, `H3D1` ...), vsaka stran skupnega pomnilnika (celotna preslikava, ne samo dekodirani bajti) pa ob vsaki spremembi, pod imenom svoje preslikave (`acpmf_physics` ...). `used` označi, kaj je postalo tudi vrstica; `selfCheck.completeness` v `meta.json` šteje vsako vrsto (pravilo pretvornika 3DHeat).

Istemu modulu pripadajo tudi: [Assetto Corsa (živi podatki)](game-assetto-corsa.md), [Assetto Corsa Competizione (živi podatki)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živi podatki)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živi podatki)](game-assetto-corsa-rally.md), [BeamNG.drive (živi podatki)](game-beamng.md), [DiRT Rally 2.0 (živi podatki)](game-dirt-rally-2.md), [Forza Horizon 4 (živi podatki)](game-forza-horizon-4.md), [Forza Horizon 5 (živi podatki)](game-forza-horizon-5.md), [Forza Horizon 6 (živi podatki)](game-forza-horizon-6.md), [Forza Motorsport (živi podatki)](game-forza-motorsport.md), [Richard Burns Rally (živi podatki)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- vrstice pri 10 Hz: položaj, hitrost, prestava, plin, zavora, razdalja na etapi, zasuk, vrtljaji, krmiljenje; začetek etape, cilj s časom etape, ponovni zagoni

**Shranjeno surovo**

- vsak paket, ki doseže vrata, cel, s hitrostjo igre, pod svojo obliko: `session_update` (privzeta struktura `wrc`, 237 bajtov), `wrc <n>-byte` za vsak drug paket, ki ga konfiguracija pošilja
- v paketu poleg vrstic: svetovna hitrost in pospešek, osi avtomobila, za vsako kolo položaj in hitrost vodila, hitrost stične ploskve, temperatura zavor, sklopka, ročna zavora, igrin čas; 22 bajtov (zamiki 16-36 in 40), ki jih noben objavljen seznam kanalov ne poimenuje

**Ni na voljo**

- drugi avtomobili: igre pošljejo samo avto igralca
- druge strukture in paketi, ki jih lahko definira konfiguracija telemetrije (session_start, session_end, pause): `setup` vklopi samo `session_update`; vsak drug paket, poslan na vrata, se shrani

**Velikost**: približno 65 MB na uro pri 60 paketih na sekundo (237 bajtov plus 70-bajtna glava elementa; stopnja -1 v konfiguraciji pošlje enega na okvir, zato pri višji hitrosti sličic več); zstd ohrani delček

## Preverjeno {#verified}

dekodiranje je od snemalnika krogov iz gamecapture (preizkušeno na paketih, sestavljenih iz dokumentiranih postavitev); adapter preizkušen na paketih, sestavljenih v testu in poslanih preko UDP; še nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
