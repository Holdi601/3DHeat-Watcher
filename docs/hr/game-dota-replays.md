---
title: "Dota 2 (replay-i)"
nav_order: 12
lang: "hr"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replay-i) {#dota-2-replays}

Nakon utakmice Dota 2, watcher pretvara replay koji je igra spremila u datoteke koje možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `dota-replays`, vrsta [`replay`](sources-and-rules.md); radi cijelo vrijeme (ne čeka da igra počne) i traži nove podatke svakih 5 s.*

## Što se bilježi {#what-is-recorded}

- pozicija, visina, zdravlje i razina svakog heroja, 7,5 puta u sekundi dok je živ
- ubojstva i smrti tamo gdje su se dogodili; tornjevi, vojarne, Roshan i Tormentori tamo gdje su pali; čuvari tamo gdje su postavljeni
- sve oznake na karti, crteži na karti i naredbe (kretanje, napad, čaranje, kupnja, ...) svakog igrača tamo gdje su pokazivale
- rezultat i red svakog igrača; red prijavljenog igrača kao statistika
- sve ostalo što replay sadrži, čuvano cjelovito uz tablicu: svaki okvir i mrežna poruka, svaka promjena svojstva entiteta, svaki unos tablice nizova

## Odakle dolazi {#where-it-comes-from}

replayi koje sprema Dota 2: &lt;Dota>/game/dota/replays/&lt;match id>.dem (preuzeti u klijentu, ili naredbom `dota-replay <match id>`)

## Kako ga uključiti {#how-to-switch-it-on}

preuzmite replay utakmice u Dota 2, ili dohvatite javni: `python -m heat3d_watch dota-replay <match id>`; treba `pip install gem-dota`

Upišite naredbu u terminal otvoren u mapi watchera (vidi [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje najčešće uzroke.

## Kako radi {#how-it-works}

Replayi i demo snimke: što igra spremi o utakmici, pretvoreno kad utakmica završi.

Replay sadrži sve što živo sučelje u igrama za više igrača skriva - položaj svakog igrača, svako ubojstvo gdje se dogodilo - i datoteka je koju igra piše za svoje igrače, pa čitanje ne dira ništa u igri. Watcher gleda mape u koje igre spremaju replaye, čeka da novoj datoteci prestane rasti (inače igra još piše u nju), i pretvara je u niti radnika, pa dugo pretvaranje ne zaustavlja ostatak watchera.

Kad se mapa prvi put vidi, replayi koji su već u njoj samo se zabilježe, ne pretvaraju se: igrač s višegodišnjim demo snimkama inače bi čekao watcher cijeli dan. `python -m heat3d_watch replays <adapter> [folder]` pretvara postojeće na zahtjev.

#### Dota 2 {#dota-2}

Dota 2 sprema replaye koje igrač preuzme (detalji utakmice ili Watch > Replays) u `<Dota>/game/dota/replays/<match id>.dem`; Valve čuva replay svake javne utakmice na svojim poslužiteljima nekoliko tjedana, a `python -m heat3d_watch dota-replay <match id>` dohvaća jedan po njegovu ID-u preko OpenDota. Svaki se čita pomoću gem-a (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) u vlastitom procesu (`heat3d_watch/decoders/dota_replay.py`): pozicija, visina, zdravlje, razina, smjer, mana, iskustvo, atributi i predmeti svakog heroja 7,5 puta u sekundi dok je živ, ubojstva i smrti tamo gdje su se dogodili, tornjevi, vojarne, Roshan i Tormentori tamo gdje su pali, svaki čuvar tamo gdje je postavljen i gdje je nestao, unosi borbenog dnevnika o herojima (šteta, liječenje, sposobnosti, predmeti, kupnje, runa, zlato, iskustvo, modifikatori), i sve oznake na karti, crteži i naredbe svakog igrača - u `dota/<match>.parquet`; sve ostale jedinice (kreature, prizvanja, iluzije, kuriri, građevine) jednom u sekundi u `<match>.units.parquet`; cijeli borbeni dnevnik u `<match>.combatlog.parquet`; a utakmica, chat, draft, sve ostalo što parser izvuče i završni zapis igre o utakmici u `<match>.match.json`, u mapi sesije. Sve ostalo što replay sadrži čuva se cjelovito uz njih (pravilo pretvarača 3DHeata): svaki okvir i mrežna poruka u `<match>.packets.parquet`, svaka promjena svojstva entiteta u `<match>.entities.parquet`, svaki unos tablice nizova u `<match>.strings.parquet`, prebrojano u `selfCheck.completeness` dokumenta utakmice. Pozicije su Dota svjetske jedinice, iste koje javlja game-state integracija. Red prijavljenog igrača na ljestvici postaje statistika sesije: ubojstva, smrti, asistencije, zadnji udarci, odbijanja, neto vrijednost, GPM, XPM, šteta herojima, čuvari, i je li utakmica pobijeđena. Novi Dota patch može promijeniti entitete replaya prije nego ih gem prati; replay koji gem ne može pročitati do kraja pretvori se dokle može i u sažetku se označi kao `incomplete`.

Isti modul služi i za: [Counter-Strike 2 (replay-i)](game-cs2-demos.md), [osu! (replay-i)](game-osu-replays.md), [Squad (replay-i)](game-squad-demos.md), [War Thunder (replay-i)](game-warthunder-replays.md), [World of Tanks (replay-i)](game-wot-replays.md), [World of Warships (replay-i)](game-wows-replays.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Pozicije se bilježe | da |
| Os prema gore | `z` |
| Jedinice | Dota svjetske jedinice (Hammer jedinice; karta je široka oko 16400) |
| Zrcaljeno za preglednik | `y` |
| Mjerilo jedinice (`scale`: preglednik pozicije množi njime) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igra na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (replayi i demo snimke koje igra sprema), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igra na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika koja se bilježi {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Pretvarač slijedi [pravilo pretvarača 3DHeata](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što replay sadrži se čita ili čuva, nikad se ne odbacuje. Osim tablice, sve ostalo što replay sadrži čuva se cjelovito u pomoćnim datotekama uz nju, u mapi `dota/` sesije - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (stupci `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, kako se koji primjenjuje) - a `selfCheck.completeness` u dokumentu utakmice (`<match>.match.json`) broji svaki `type` - `lost` je 0.

**Čita se**

- tablica (`dota/<match>.parquet`): pozicija, visina, zdravlje, razina, smjer, mana, iskustvo, atributi, oklop, brzina, šteta, predmeti i pokazivač igrača svakog heroja 7,5 puta u sekundi; ubojstva, smrti, ciljevi, čuvari, unosi borbenog dnevnika o herojima; oznake na karti (`ping`, DOTA_UM_LocationPing), crteži na karti (`map_line`, DOTA_UM_MapLine) i svaka naredba jedinici (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` vrsta naredbe, `value` ID sposobnosti ili predmeta, `text` klasa cilja; na zadanoj točki, inače kod heroja)
- `<match>.units.parquet`: sve ostale jedinice jednom u sekundi; `<match>.combatlog.parquet`: cijeli borbeni dnevnik kako ga gem čita, svako polje
- dokument utakmice: sve što gem izvuče, i cjelovito zapise replaya - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: trajanje reprodukcije, ime, heroj, Steam ID i tim svakog igrača), `matchDetails` (DOTA_UM_MatchDetails: završna ljestvica utakmice iz game coordinatora, brojke svakog igrača, predmeti, šteta po vrsti, odabiri i zabrane) i `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: ubojstva, smrti, asistencije, razina, zadnji udarci i odbijanja kako su pročitani iz toka u odnosu na `matchDetails`, po igraču

**Čuva se u izvornom obliku**

- `<match>.packets.parquet`: svaki okvir koji nije paket (`type` `frame <n>`) i svaka mrežna poruka (`message <n>`, `name` Valveov), cjelovito u `payload`, redom iz datoteke (`seq`, `frame`), s `decoded` kao protobuf u JSON-u (polje bajtova kao svoja duljina), svaka vrsta poruke dekodirana: svc_PacketEntities (tok entiteta), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, poruke borbenog dnevnika, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projektili, animacije, krv), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; tablice poslanih podataka, popis klasa i informacije o poslužitelju koje kasniji dekoder entiteta treba među njima su
- `<match>.entities.parquet`: svako svojstvo svakog entiteta svaki put kad se promijenilo (`type` svojstvo, `name` klasa, `entity` njegov indeks; `value`, `vector` ili `decoded`), njegovo cjelovito stanje pri stvaranju, i svako stvaranje, ulazak, odlazak i brisanje - za cijelu utakmicu milijuni redaka
- `<match>.strings.parquet`: svaki unos tablice nizova iz svakog ažuriranja i svake potpune snimke, vrijednost cjelovito; `userinfo`, `ActiveModifiers` i `EconItems` dekodirani iz svojih protobuf-ova
- `selfCheck.completeness` u dokumentu utakmice broji okvire i poruke po Valveovu imenu, unose borbenog dnevnika (`combatlog <type>`), događaje igre (`gameevent <name>`), unose tablice nizova (`stringtable <name>`) i ažuriranja entiteta (`entity <class>`); nekoliko ih se čuva samo sirovo (potpune snimke entiteta koje gem preskače jer ih rekonstruira iz promjena, i unosi tablica čije vrijednosti ništa ne čita), izgubljeno 0

**Nije dostupno**

- glas: replay ima postavke glasa, ali nema glasovnih podataka
- imena iza hashova i ID-ova: zvukovi i čestice imenovani su hashovima iz datoteka igre, sposobnosti ID-ovima; replay ne nosi imena (predmeti se imenuju kroz gemov katalog gdje ga ima)
- sve što su znali samo klijenti igrača (njihova kamera, njihov ekran) izvan onoga što je poslužitelj emitirao; pokazivač i svaka naredba su unutra

**Veličina**: pomoćne datoteke zajedno su nešto veće od samog replaya, najveće su paketi i entiteti; cijela utakmica traje minutu-dvije u jednom procesu

## Provjereno {#verified}

provjereno na javnom replayu utakmice: ubojstva, smrti, asistencije, razina, zadnji udarci i odbijanja odgovaraju završnoj ljestvici igre za svih deset igrača; svaka poruka u datoteci paketa ponovno se serijalizira bajt po bajt; tablica i statistika testirani sintetičkim podacima

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
