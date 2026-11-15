---
title: "EA SPORTS F1 25 (podatki v živo)"
nav_order: 16
lang: "sl"
source: game-f1-25.md
source_hash: "7476dbb3b308"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 25 (podatki v živo) {#ea-sports-f1-25-live-data}

Medtem ko igrate EA SPORTS F1 25, watcher shrani podatke, ki jih igra sama pošilja ven, da jih lahko pozneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `f1-25`, vrsta [`telemetry`](sources-and-rules.md); teče, dokler je `F1_25.exe` zagnan, in novih podatkov išče vsakih 0,1 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj vsakega avtomobila (svetovni XYZ, m) 10-krat na sekundo, po imenu voznika, ekipi, lastni avto označen (`own_car` 1, iz indeksa igralčevega avtomobila), s hitrostjo, prestavo, plinom, zavoro, zavijanjem, vrtljaji, DRS, zasukom, nagibom, valjanjem (stopinje) in g-silami
- kroge za vsak avtomobil s časom kroga in položajem na dirki; cilji in odstopi
- dogodki dirke v igri: začetek in konec seje, najhitrejši krog, kazni, prehitevanja, trki, varnostni avto, rdeča zastava, luči na startu, karirana zastava, zmagovalec, povratki (`teleport`, kje je bil avto, in `spawn`, kam se je vrnil)
- proga, vrsta seje, kroge in vozniki vsake seje
- lastni krogi, najboljši krog, položaj na dirki in štartnem položaju, postanki v boksih, kazni, prehitevanja, trki, razdalja, najvišja hitrost
- vsak paket, ki ga igra pošlje, v celoti, v `heat.raw.parquet` - tudi tisti, ki niso prebrani v vrstice

## Od kod prihaja {#where-it-comes-from}

UDP telemetrija 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## Kako ga vklopiti {#how-to-switch-it-on}

V igri: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, vrata 20777 - ali `python -m heat3d_watch setup f1-25 --apply` (popravi hardware_settings_config.xml, najprej se naredi varnostna kopija; igra mora biti zaprta). Dokler drug program drži 20777, watcher vrata prepusti njemu.

Ukaz vpišite v terminal, odprt v mapi watcherja (glej [Preden začnete](before-you-start.md)). Če ne uspe, zadnja vrstica pove, zakaj; [Namestitev in zagon](installing-and-running.md) pokrije pogoste vzroke.

`python -m heat3d_watch setup f1-25` izpiše, katere datoteke bi spremenil; `python -m heat3d_watch setup f1-25 --apply` jih spremeni, izvirnik pa ohrani kot `<file>.heat3d-backup` (glej [Ukazi](commands.md#setup)). Za vsako spremembo izpiše `f1-25: changed: ...`, ali `f1-25: nothing to change`, kadar je že vklopljeno.

## Kako deluje {#how-it-works}

EA SPORTS F1 23, F1 24 in F1 25: uradna UDP telemetrija, vsak avtomobil na progi.

Igre jo pošiljajo same (Settings > Telemetry Settings, ali
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, zgoščeno, glava dolga 29 bajtov na vsakem paketu (enaka v formatih 2023,
2024 in 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Kaj se bere, po id-ju paketa:

```text
0 Motion        CarMotionData[22], 60 bajtov vsak: svetovni položaj x y z
                (metri; Y je navzgor), svetovna hitrost, vektorji naprej in
                desno (int16 / 32767), g-sile, yaw pitch roll
1 Session       vreme, temperature, skupno število krogov, dolžina proge, vrsta
                seje, id proge, ... omrežna igra
2 Lap Data      LapData[22]: zadnji čas kroga, razdalja kroga, položaj na dirki,
                trenutna številka kroga, postanki v boksih, kazni, štartni položaj,
                stanje voznika in rezultata. 50 bajtov na avto v 2023; 57 v
                2024 in 2025, ki sta dodala minutne dele razlik in hitrostno past.
3 Event         štiričrkovna koda in unija podrobnosti: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI ali človek, voznik, ekipa, startna
                številka, ime (48 bajtov v 2023 in 2024, 32 v 2025; 58,
                60 in 57 bajtov na avto)
6 Car Telemetry CarTelemetryData[22], 60 bajtov: hitrost km/h, plin,
                zavijanje, zavora, sklopka, prestava, vrtljaji, DRS ...
```

Vsak paket je prav tako ohranjen v celoti, kakor je prišel, v surovi spremljevalni datoteki seje (`heat.raw.parquet`, `type` je ime paketa - `motion`, `car_status` ... -
s `format`, `packet_id`, `frame` in `session_uid`) - tako tisti, ki so prebrani zgoraj, kot tisti, ki jih nič ne bere: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, katerikoli kasnejši id in paketi v formatu, ki ga ta ne bere. Tako poznejši dekoder potrebuje samo spremljevalno datoteko.

Vsak položaj avtomobila je v paketu Motion - tudi na spletu, kjer ga igra sama izroča (samo podatki o gorivu, ERS, poškodbah in setih gum so zadržani za igralce, katerih "Your Telemetry" je omejena). Vsak avto se zapisuje približno 10-krat na sekundo pod imenom udeleženca ("car N", dokler imena ne pridejo), ekipa po imenu, lastni avto igralca pa označen z `own`.

Viri: EA-jeva "F1 25 UDP Specification" (forums.ea.com, središče informacij o igrah F1), specifikaciji za F1 23 in F1 24; iste tabele so zrcaljene v MacManley/f1-25-udp (MIT). Paketi v testih so zgrajeni iz teh postavitev.

Isti modul služi tudi: [EA SPORTS F1 23 (podatki v živo)](game-f1-23.md), [EA SPORTS F1 24 (podatki v živo)](game-f1-24.md).

## Osi položajev {#positions-and-axes}

| | |
|---|---|
| Zapisani položaji | da |
| Os navzgor | `y` |
| Enote | metri |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enot (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

Ti gredo v `meta.json` vsake seje (`axes`) in, kadar ima seja položaje, v nogo `heat.parquet`, tako pregledovalnik sam obrača in meri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo to, kar igra ali platforma objavi (vrata UDP ali deljeni pomnilnik, ki ju igra objavlja), zato zapisuje tudi pri igri na spletu, tako kot offline; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali ohrani, nikoli ne izpusti. Poleg vrstic je vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, ohranjen v celoti v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text`, nato vsako polje, ohranjeno po imenu; `used` označi, kar je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- 0 Motion: svetovni položaj in hitrost vsakega avtomobila ter zdaj tudi zasuk, nagib, valjanje (stopinje, iz radianov specifikacije) in bočna, vzdolžna ter navpična g-sila, na vsaki vrstici položaja avtomobila
- 1 Session: proga, vrsta seje, skupno število krogov, dolžina proge, na spletu ali ne (`sessions` v meta.json)
- 2 Lap Data: zadnji čas kroga, številka kroga, položaj na dirki in štartni položaj, postanki v boksih, kazni, stanje rezultata (krogi, cilji, odstopi, statistika)
- 3 Event: vsaka koda razen BUTN kot lastna vrstica, s podrobnostmi
- 4 Participants: imena voznikov, ekipe, število aktivnih avtomobilov (`player` in `team` vrstic, `drivers` v meta.json)
- 6 Car Telemetry: hitrost, prestava, plin, zavora, zdaj tudi zavijanje (-1..1), vrtljaji in DRS na vsaki vrstici položaja avtomobila
- preverjeno z objavljenimi specifikacijami UDP podjetja EA za formate 2023, 2024 in 2025 (velikosti paketov potrjene v testih); še ni preverjeno na igri

**Ohranjeno surovo**

- vsak paket v celoti v `heat.raw.parquet`, `payload` je datagram, `type` je ime id-ja: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` za id, ki ga specifikacije še ne navajajo); stolpci `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` je true za pakete, prebrane zgoraj (Motion, Session, Lap Data, Participants, Car Telemetry in kode Event razen BUTN); ostali - nastavitve avtomobilov, stanje avtomobila (gorivo, ERS, spojina in starost gum, zastavice), končna uvrstitev, predsoba, poškodbe avtomobila, zgodovina seje (vsak čas kroga in sektorja za vsak avto), setovi gum, motion ex (vzmetenje lastnega avtomobila, hitrosti koles, lokalna hitrost, kotna hitrost in pospešek), time trial, položaji krogov, dogodki gumbov BUTN - so ohranjeni za poznejši dekoder
- `format <year>`: paket v formatu pred letom 2023 (drugačna postavitev glave), v celoti; `short`: datagram krajši od 29-bajtne glave, v celoti

**Ni na voljo**

- gorivo, ERS, poškodbe in seti gum drugih igralcev na spletu, kadar je njihov "Your Telemetry" omejena: igra zanje pošilja ničle
- paketi, poslani, medtem ko watcher ni zagnan, ali medtem ko drug program drži vrata 20777: igra UDP ne shranjuje

**Velikost**: pri hitrosti pošiljanja 60 Hz je vsak paket okoli 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status in Motion Ex pri 60 Hz, Session History in Tyre Sets 20/s, Car Damage 10/s, Session in Car Setups 2/s) plus okoli 0,03 MB/s glav predmetov: okoli 1,5 GB na uro vožnje pred stiskanjem, okoli 0,55 GB pri privzetih 20 Hz; zstd to zmanjša na delček (prazne reže avtomobilov in ponovljene vrednosti se dobro stisnejo; še ni izmerjeno na pravi seji)

## Preverjeno {#verified}

preizkušeno na paketih v formatih 2023, 2024 in 2025, zgrajenih iz EA-jeve objavljene specifikacije, poslanih prek UDP; nepreizkušeno na igri

## Vir {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
