---
title: "RaceRoom Racing Experience (živi podatki)"
nav_order: 38
lang: "sl"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (živi podatki) {#raceroom-racing-experience-live-data}

Medtem ko igrate RaceRoom Racing Experience, watcher shrani podatke, ki jih igra sama pošilja ven, da si jih lahko pozneje ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `raceroom`, vrsta [`telemetry`](sources-and-rules.md); teče, medtem ko se izvaja `RRRE64.exe` ali `RRRE.exe`, in vsakih 0,1 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- položaj (svetovne koordinate XYZ, m) vsakega avtomobila desetkrat na sekundo, po imenu voznika, lastni avto označen, s hitrostjo in uvrstitvijo; lastna prestava, plin, zavora
- začetek seje s progo, ki jo poimenuje igra; krogi po avtomobilih s časom kroga; cilji; lastni postanki v boksih
- teleporti (vrnitev v bokse, ponovni zagon): `teleport`, kje je bil avtomobil, `spawn`, kje je zdaj
- lastni krogi, najboljši krog, uvrstitev, razdalja, najvišja hitrost
- celotna stran skupnega pomnilnika igre v `heat.raw.parquet`, ob vsaki spremembi
- lastne točke incidentov

## Od kod prihajajo {#where-it-comes-from}

skupni pomnilnik $R3E (r3e.h Sector3, različica 3)

## Kako vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklopiti: watcher bere vir tako, kot ga igra ali platforma ponuja.

## Kako deluje {#how-it-works}

Skupni pomnilnik, ki ga dirkalne simulacije objavljajo za nadzorne plošče, odprt samo za branje - in
nikoli ustvarjen.

Več simulacij svojo telemetrijo objavlja kot imenovano preslikavo datoteke v Windows, ki jo igra
ustvari in jo lahko vsak prebere: Kunosove strani `Local\acpmf_*` (Assetto Corsa,
ACC, AC Rally, AC EVO-jeve `Local\acevo_pmf_*`), iRacingova
`Local\IRSDKMemMapFileName`, RaceRoomova `$R3E`, Automobilista 2 / Project CARS 2 `$pcars2$`.

Zakaj ne `mmap.mmap(-1, size, tagname=...)`, ki je sicer običajen način v Pythonu: ko preslikava
še ne obstaja, jo *ustvari* - tu samo za branje. Igra, zagnana kasneje, odpre watcherjevo preslikavo
namesto svoje in potem vanjo ne more pisati, zato je njena telemetrija mrtva, dokler watcher ne izpusti.
Watcher adapter zažene takoj, ko se pojavi proces igre, in to je ravno trenutek, ko igra še ni
ustvarila svoje preslikave. Zato to odpre z `OpenFileMappingW`, ki res najde samo obstoječo
preslikavo, jo preslika z `FILE_MAP_READ` in sicer javi "še ni tu"; adapterji poskusijo
čez trenutek znova.

Nič tukaj ne more pisati: pogled je preslikan samo za branje in se iz njega kopira samo z
`ctypes.string_at`.

Tu se berejo tudi dve igri; vsi avtomobili na progi so na njunih straneh.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3-ov `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
različica 3.6), `#pragma pack(1)`. Glava pove, kje se začnejo vozniki in kako veliki so
(`all_drivers_offset`, `driver_data_size`), zato se del za vsakega voznika - ime, reža, mesto,
svetovni položaj (float x y z, m), opravljeni krogi, čas trenutnega kroga, stanje cilja, pas
boksov, hitrost - bere po teh. Lastna polja igralca (najboljši in prejšnji krog, uvrstitev,
točke incidentov, prestava, pedali, imeni proge in postavitve) se berejo na odmikih 3.6 samo,
kadar je `all_drivers_offset` tisti 2008, na katerem jo postavi ta postavitev. Y je vzet kot navzgor;
glava tega ne pove.

Isti modul streže tudi: [Automobilista 2 (živi podatki)](game-automobilista-2.md), [Project CARS 2 (živi podatki)](game-project-cars-2.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | da |
| Navpična os | `y` |
| Enote | metri; predpostavljen y navzgor (r3e.h tega ne pove) |
| Zrcaljenje za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo, kar igra ali platforma ponudi (UDP vrata ali skupni pomnilnik, ki ga igra objavlja), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- za vsak slot voznika (po lastnem odmiku in velikosti glave): ime, reža, stanje cilja, mesto, svetovni položaj, opravljeni krogi, čas trenutnega kroga, pas boksov, hitrost
- lastna polja igralca, samo kadar je stran postavitve r3e.h 3.6: imeni proge in postavitve, vrsta seje, uvrstitev, najboljši in prejšnji krog, točke incidentov, prestava, plin, zavora, reža igralca
- odmiki, določeni iz r3e.h 3.6 Sector3 in preverjeni na strani, zgrajeni iz nje v testih; še ne na igri

**Shranjeno surovo**

- `r3e`: celotna preslikava $R3E, ob vsakem branju, katerega bajti se razlikujejo od zadnje shranjene kopije - vsako polje r3e.h: fizika igralca (usmerjenost, hitrosti, pospeški, g-sile), motor, gorivo, pnevmatike, zavore, poškodbe, zastavice, meni boksov, časi sektorjev, vsaka reža voznika s celimi podatki voznika (razred, model, ekipa, časi sektorjev, zaostanki, kazni, pnevmatike)
- `used` je resničen za stran, prebrano v vrstice; false za stran v menijih, med pavzo, v ponovitvi, drugačne postavitve ali ujeto med pisanjem (`torn` 1); `unchanged_reads` v meta.json šteje branja, ki so bajt za bajtom enaka prej shranjeni kopiji

**Ni na voljo**

- vnosi in fizika drugih voznikov: stran daje samo igralčev lastni
- krogi drugih avtomobilov, natančno: reža ima samo tekoči čas kroga, zato je krog zadnji videni tekoči čas (na približno 0,1 s)
- lastna polja igralca na postavitvi, ki ni 3.6: shranjena surovo, ne prebrana, dokler ni preverjena

**Velikost**: stran meri 44 KB (r3e.h 3.6; preslikava je zaokrožena na cele strani po 4 KB), do 10-krat na sekundo med vožnjo: približno 1,6 GB na uro pred stiskanjem; prazne reže voznikov in polja, ki se ne spreminjajo, se z zstd zelo dobro stisnejo (še ni izmerjeno na pravi seji)

## Preverjeno {#verified}

preizkušeno na strani, zgrajeni v testu iz r3e.h 3.6 (odmiki določeni iz uradne glave); nepreizkušeno z igro; krogi drugih avtomobilov so zadnji videni tekoči čas kroga (na približno 0,1 s)

## Vir {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
