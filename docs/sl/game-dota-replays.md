---
title: "Dota 2 (replays)"
nav_order: 12
lang: "sl"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replays) {#dota-2-replays}

Po tekmi Dota 2 watcher replay, ki ga je shranila igra, pretvori v datoteke, ki jih lahko pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `dota-replays`, vrsta [`replay`](sources-and-rules.md); teče ves čas (ne čaka, da se igra zažene) in novih podatkov išče vsakih 5 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj, višina, zdravje in raven vsakega heroja 7,5-krat na sekundo, dokler je živ
- pobitja in smrti tam, kjer sta se zgodila; stolpi, barake, Roshan in Tormentorji tam, kjer so padli; čuvaji tam, kjer so bili postavljeni
- vsi pingi na zemljevid, risbe na zemljevidu in ukazi vsakega igralca (premik, napad, uporaba, nakup, ...) tam, kamor so kazali
- rezultat in vrstica vsakega igralca; vrstica prijavljenega igralca kot statistika
- vse drugo, kar replay vsebuje, ohranjeno v celoti ob tabeli: vsak okvir in omrežno sporočilo, vsaka sprememba lastnosti entitete, vsak vnos tabele nizov

## Od kod prihaja {#where-it-comes-from}

replayi, ki jih shrani Dota 2: &lt;Dota&gt;/game/dota/replays/&lt;match id&gt;.dem (preneseni v odjemalcu ali z `dota-replay <match id>`)

## Kako ga vklopiti {#how-to-switch-it-on}

prenesite replay tekme v Dota 2 ali pridobite javnega: `python -m heat3d_watch dota-replay <match id>`; potrebuje `pip install gem-dota`

Ukaz vpišite v terminal, odprt v mapi watcherja (glej [Preden začnete](before-you-start.md)). Če ne uspe, zadnja vrstica pove, zakaj; [Namestitev in zagon](installing-and-running.md) pokrije pogoste vzroke.

## Kako deluje {#how-it-works}

Replayi in demo posnetki: kar igra shrani o tekmi, pretvorjeno, ko je tekma končana.

Replay vsebuje vse, kar vmesnik v živo zadrži pri igrah z več igralci - položaj vsakega igralca, vsako pobitje tam, kjer se je zgodilo - in je datoteka, ki jo igra zapiše za svoje igralce, zato branje ničesar v igri ne prizadene. Watcher gleda mape, kamor igre shranjujejo, počaka, da nova datoteka neha rasti (sicer igra še piše vanjo), in jo pretvori v delovni niti, da dolga pretvorba nikoli ne zadrži preostalega watcherja.

Prvič, ko watcher vidi mapo, se replayi, ki so že v njej, samo zabeležijo, ne pretvorijo: igralec z leti demo posnetkov bi sicer dobil watcher, zaposlen cel dan. `python -m heat3d_watch replays <adapter> [folder]` na zahtevo pretvori obstoječe.

#### Dota 2 {#dota-2}

Dota 2 shrani replayi, ki jih igralec prenese (podrobnosti tekme ali Watch > Replays), v `<Dota>/game/dota/replays/<match id>.dem`; Valve hrani replay vsake javne tekme na svojih strežnikih nekaj tednov, `python -m heat3d_watch dota-replay <match id>` pa ga prenese po njegovem ID-ju prek OpenDota. Vsakega bere gem (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) v svojem procesu (`heat3d_watch/decoders/dota_replay.py`): položaj, višina, zdravje, raven, obrat, mana, izkušnje, lastnosti in predmeti vsakega heroja 7,5-krat na sekundo, dokler je živ; pobitja in smrti tam, kjer sta se zgodila; stolpi, barake, Roshan in Tormentorji tam, kjer so padli; vsak čuvaj tam, kjer je bil postavljen, in kjer se je končal; vnosi bojnega dnevnika o herojih (škoda, zdravljenje, sposobnosti, predmeti, nakupi, runi, zlato, izkušnje, modifikatorji); ter vsak ping, risba na zemljevidu in ukaz vsakega igralca - v `dota/<match>.parquet`; vsaka druga enota (kreature, prizvanja, iluzije, kurirji, zgradbe) enkrat na sekundo v `<match>.units.parquet`; ves bojni dnevnik v `<match>.combatlog.parquet`; in tekma, klepet, izbor herojev, vse drugo, kar izlušči razčlenjevalnik, ter uradni zapis igre ob koncu tekme v `<match>.match.json` v mapi seje. Vse drugo, kar replay vsebuje, je ohranjeno ob njih v celoti (pravilo pretvornikov 3DHeat): vsak okvir in omrežno sporočilo v `<match>.packets.parquet`, vsaka sprememba lastnosti entitete v `<match>.entities.parquet`, vsak vnos tabele nizov v `<match>.strings.parquet`, šteto v `selfCheck.completeness` dokumenta tekme. Položaji so v svetovnih enotah Dote, iste kot jih poroča game-state integration. Vrstica rezultata prijavljenega igralca postane statistika seje: pobitja, smrti, asistence, zadnji udarci, zanikanja, neto vrednost, GPM, XPM, škoda heroju, čuvaji in ali je bila tekma zmagana. Nova zaplata Dote lahko spremeni entitete replaya, preden gem sledi; replay, ki ga gem ne more prebrati do konca, se pretvori, kolikor gre, in je v povzetku označen kot `incomplete`.

Isti modul služi tudi: [Counter-Strike 2 (replays)](game-cs2-demos.md), [osu! (replays)](game-osu-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Osi položajev {#positions-and-axes}

| | |
|---|---|
| Zapisani položaji | da |
| Os navzgor | `z` |
| Enote | svetovne enote Dote (enote Hammer; zemljevid je širok okoli 16400) |
| Zrcaljeno za pregledovalnik | `y` |
| Merilo enot (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

Ti gredo v `meta.json` vsake seje (`axes`) in, kadar ima seja položaje, v nogo `heat.parquet`, tako pregledovalnik sam obrača in meri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `replay`: bere samo replaye in demo posnetke, ki jih igra ali platforma shrani, zato zapisuje tudi pri igri na spletu, tako kot offline; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Pretvornik sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar replay vsebuje, se prebere ali ohrani, nikoli ne izpusti. Poleg tabele je vse drugo, kar replay vsebuje, ohranjeno v celoti v spremljevalnih datotekah ob njej v mapi `dota/` seje - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (stolpci `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, kakor se uporabijo) - in `selfCheck.completeness` dokumenta tekme (`<match>.match.json`) šteje vsak `type` - `lost` je 0.

**Prebrano**

- tabela (`dota/<match>.parquet`): položaj, višina, zdravje, raven, obrat, mana, izkušnje, lastnosti, oklep, hitrost, škoda, predmeti in kazalec igralca vsakega heroja 7,5-krat na sekundo; pobitja, smrti, cilji, čuvaji, vnosi bojnega dnevnika o herojih; pingi na zemljevid (`ping`, DOTA_UM_LocationPing), risbe na zemljevidu (`map_line`, DOTA_UM_MapLine) in vsak ukaz enote (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` vrsta ukaza, `value` id sposobnosti ali predmeta, `text` razred cilja; na točki ukaza, sicer na heroju)
- `<match>.units.parquet`: vsaka druga enota enkrat na sekundo; `<match>.combatlog.parquet`: ves bojni dnevnik, kakor ga bere gem, vsako polje
- dokument tekme: vse, kar izlušči gem, in v celoti zapisi replaya samo - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: dolžina predvajanja, ime vsakega igralca, heroj, Steam id, ekipa), `matchDetails` (DOTA_UM_MatchDetails: uradni rezultat ob koncu tekme z vsakim igralcem, predmeti, škoda po vrsti, izbori in prepovedi) in `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: pobitja, smrti, asistence, raven, zadnji udarci in zanikanja, prebrani iz toka, primerjani z `matchDetails`, za vsakega igralca

**Ohranjeno surovo**

- `<match>.packets.parquet`: vsak okvir, ki ni paket (`type` `frame <n>`), in vsako omrežno sporočilo (`message <n>`, ime `name` po Valvu), v celoti v `payload`, v vrstnem redu datoteke (`seq`, `frame`), z `decoded` protobufom kot JSON (polje bajtov kot njegova dolžina); dekodirana je vsaka vrsta sporočila: svc_PacketEntities (tok entitet), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, sporočila bojnega dnevnika, GE_SosStartSoundEvent, DOTA_UM_TE_\* (izstrelki, animacije, kri), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; tabele pošiljanja, seznam razredov in podatki o strežniku, ki jih potrebuje poznejši dekoder entitet, so med njimi
- `<match>.entities.parquet`: vsaka lastnost vsake entitete vsakič, ko se spremeni (`type` lastnost, `name` razred, `entity` njen indeks; `value`, `vector` ali `decoded`), njeno celotno stanje ob nastanku ter vsak nastanek, vstop, odhod in izbris - milijoni vrstic za celo tekmo
- `<match>.strings.parquet`: vsak vnos tabele nizov iz vsake posodobitve in vsakega polnega posnetka, vrednost v celoti; `userinfo`, `ActiveModifiers` in `EconItems` dekodirani iz svojih protobufov
- `selfCheck.completeness` dokumenta tekme šteje okvirje in sporočila po Valvovem imenu, vnose bojnega dnevnika (`combatlog <type>`), dogodke igre (`gameevent <name>`), vnose tabele nizov (`stringtable <name>`) in posodobitve entitet (`entity <class>`); nekateri so ohranjeni samo surovo (celotni posnetki entitet, ki jih gem preskoči, ker jih rekonstruira iz sprememb, in vnosi tabel, katerih vrednosti nič ne bere), lost 0

**Ni na voljo**

- glas: replay ima nastavitev glasu, nima pa glasovnih podatkov
- imena za zgoščenimi vrednostmi in ID-ji: zvoki in delci so poimenovani z zgoščenimi vrednostmi igrinih datotek, sposobnosti z ID-ji; replay imen ne nosi (predmeti so poimenovani prek kataloga gem, kjer ga ima)
- vse, kar so vedeli samo odjemalci igralcev (njihova kamera, njihov zaslon), razen tega, kar je strežnik oddajal; kazalec in vsak ukaz sta vključena

**Velikost**: spremljevalne datoteke skupaj so nekoliko večje od samega replaya, največja sta paketi in entitete; cela tekma se pretvori v minuto ali dve v enem procesu

## Preverjeno {#verified}

preizkušeno na replayu javne tekme: pobitja, smrti, asistence, raven, zadnji udarci in zanikanja se ujemajo z uradnim zapisom igre ob koncu za vseh deset igralcev; vsako sporočilo v spremljevalni datoteki paketov se ponovno serializira bajt za bajtom; tabela in statistike s testi na sintetičnih podatkih

## Vir {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
