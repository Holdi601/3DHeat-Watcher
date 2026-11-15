---
title: "Dota 2 (snimci)"
nav_order: 12
lang: "bs"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (snimci) {#dota-2-replays}

Poslije meča Dota 2, watcher pretvara snimak koji je igra spremila u datoteke koje možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `dota-replays`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da igra krene) i svakih 5 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- pozicija, visina, zdravlje i nivo svakog heroja, 7,5 puta u sekundi dok je živ
- ubistva i smrti gdje su se desile; tornjevi, barake, Roshan i Tormentori gdje su pali; wardovi gdje su postavljeni
- pingovi na mapi, crteži na mapi i komande svakog igrača (kretanje, napad, čaranje, kupovina, ...) gdje su pokazali
- rezultat i linija svakog igrača; prijavljenog igrača kao statistike
- sve ostalo što snimak drži, sačuvano cijelo pored tabele: svaki frame i mrežna poruka, svaka promjena svojstva entiteta, svaki unos tabele stringova

## Odakle dolazi {#where-it-comes-from}

snimci koje Dota 2 sprema: &lt;Dota>/game/dota/replays/&lt;match id>.dem (preuzeti u klijentu, ili s `dota-replay <match id>`)

## Kako to uključiti {#how-to-switch-it-on}

preuzmite snimak meča u Dota 2, ili dohvatite javni: `python -m heat3d_watch dota-replay <match id>`; treba `pip install gem-dota`

Komandu upišite u terminal otvoren u folderu watchera (vidite [Prije nego počnete](before-you-start.md)). Ako ne uspije, zadnja linija kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje uobičajene uzroke.

## Kako radi {#how-it-works}

Snimci i demoi: ono što igra spremi o meču, pretvoreno kad meč završi.

Snimak drži sve što živi interfejs u multiplayer igrama zadržava za sebe -
poziciju svakog igrača, svako ubistvo gdje se desilo - a to je datoteka koju
igra piše za svoje igrače, pa čitanje ništa ne dira u igri. Watcher
gleda foldere u koje igre spremaju snimke, čeka da nova datoteka prestane
rasti (inače je igra još piše) i pretvara je u
radnoj niti, pa duga konverzija nikad ne zadržava ostatak watchera.

Kad se folder prvi put vidi, snimci koji su već u njemu samo se zabilježe, ne
pretvaraju: igrač s godinama demoa inače bi našao watcher zauzet
cijeli dan. `python -m heat3d_watch replays <adapter> [folder]` pretvara
postojeće na zahtjev.

#### Dota 2 {#dota-2}

Dota 2 sprema snimke koje igrač preuzme (detalji meča, ili Watch >
Replays) u `<Dota>/game/dota/replays/<match id>.dem`; Valve čuva snimak svakog javnog
meča na svojim serverima nekoliko sedmica, a `python -m heat3d_watch
dota-replay <match id>` dohvaća jedan po njegovom id-u preko OpenDote. Svaki se čita s
gem (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) u vlastitom
procesu (`heat3d_watch/decoders/dota_replay.py`): pozicija, visina,
zdravlje, nivo, smjer, mana, iskustvo, atributi i predmeti svakog heroja 7,5
puta u sekundi dok je živ, ubistva i smrti gdje su se desile, tornjevi,
barake, Roshan i Tormentori gdje su pali, svaki ward gdje je
postavljen i gdje je završio, unosi combat loga o herojima
(šteta, liječenje, sposobnosti, predmeti, kupovine, rune, zlato, iskustvo,
modifikatori), te pingovi na mapi, crteži na mapi i komande svakog igrača - u
`dota/<match>.parquet`; svaka druga jedinica (creepovi, prizvana bića, iluzije,
kuriri, zgrade) jednom u sekundi u `<match>.units.parquet`; cijeli
combat log u `<match>.combatlog.parquet`; a meč, chat,
draft, sve ostalo što parser izvuče i igrin vlastiti zapis kraja meča
u `<match>.match.json`, u folderu sesije. Sve ostalo
što snimak drži čuva se cijelo pored njih (pravilo konvertera programa 3DHeat):
svaki frame i mrežna poruka u `<match>.packets.parquet`, svaka promjena
svojstva entiteta u `<match>.entities.parquet`, svaki unos tabele stringova u
`<match>.strings.parquet`, što se broji u `selfCheck.completeness` dokumenta
meča. Pozicije su Dotine svjetske
jedinice, iste koje prijavljuje game-state integracija. Linija igrača
koji je prijavljen s tabele rezultata postaje statistika sesije: ubistva, smrti, asistencije,
last hitovi, denyji, net worth, GPM, XPM, šteta herojima, wardovi i je li
meč dobiven. Novi Dota patch može promijeniti entitete snimka prije nego što ga gem
slijedi; snimak koji gem ne može pročitati do kraja pretvara se
dokle ide i u svom sažetku se označi kao `incomplete`.

Isti modul služi i: [Counter-Strike 2 (snimci)](game-cs2-demos.md), [osu! (snimci)](game-osu-replays.md), [Squad (snimci)](game-squad-demos.md), [War Thunder (snimci)](game-warthunder-replays.md), [World of Tanks (snimci)](game-wot-replays.md), [World of Warships (snimci)](game-wows-replays.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `z` |
| Jedinice | Dotine svjetske jedinice (Hammer jedinice; mapa je široka oko 16400) |
| Zrcaljeno za preglednik | `y` |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (snimke i demoe koje igra sprema), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Konverter slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što snimak drži čita se ili čuva, nikad ne odbacuje. Osim tabele, sve ostalo što snimak drži čuva se cijelo u sidecar datotekama pored nje u folderu `dota/` sesije - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (kolone `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, već prema slučaju) - a `selfCheck.completeness` dokumenta meča (`<match>.match.json`) broji svaki `type` - `lost` je 0.

**Čita se**

- tabela (`dota/<match>.parquet`): pozicija, visina, zdravlje, nivo, smjer, mana, iskustvo, atributi, armor, brzina, šteta, predmeti svakog heroja i igračev kursor 7,5 puta u sekundi; ubistva, smrti, ciljevi, wardovi, unosi combat loga o herojima; pingovi na mapi (`ping`, DOTA_UM_LocationPing), crteži na mapi (`map_line`, DOTA_UM_MapLine) i svaka komanda jedinici (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` je tip komande, `value` id sposobnosti ili predmeta, `text` klasa cilja; na naređenoj tački, inače na heroju)
- `<match>.units.parquet`: svaka druga jedinica jednom u sekundi; `<match>.combatlog.parquet`: cijeli combat log kako ga gem čita, svako polje
- dokument meča: sve što gem izvuče, i, cijeli, vlastiti zapisi snimka - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: dužina reprodukcije, ime, heroj, Steam id i tim svakog igrača), `matchDetails` (DOTA_UM_MatchDetails: tabela rezultata kraja meča iz koordinatora igre, brojevi svakog igrača, predmeti, šteta po tipu, pickovi i banovi) i `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: ubistva, smrti, asistencije, nivo, last hitovi i denyji kako su pročitani iz toka naspram `matchDetails`, po igraču

**Čuva se sirovo**

- `<match>.packets.parquet`: svaki frame koji nije paket (`type` `frame <n>`) i svaka mrežna poruka (`message <n>`, `name` je Valveovo), cijela u `payload`, redom iz datoteke (`seq`, `frame`), a `decoded` je protobuf kao JSON (bytes polje dato kao njegova dužina), svaki tip poruke dekodiran: svc_PacketEntities (tok entiteta), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, poruke combat loga, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projektili, animacije, krv), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; među njima su send tabele, lista klasa i informacije o serveru koje treba kasniji dekoder entiteta
- `<match>.entities.parquet`: svako svojstvo svakog entiteta svaki put kad se promijenilo (`type` je svojstvo, `name` klasa, `entity` njegov indeks; `value`, `vector` ili `decoded`), njegovo cijelo stanje pri nastanku, te svako stvaranje, ulazak, izlazak i brisanje - milioni redova za cijeli meč
- `<match>.strings.parquet`: svaki unos tabele stringova iz svakog ažuriranja i svakog punog snimka, vrijednost cijela; `userinfo`, `ActiveModifiers` i `EconItems` dekodirani iz svojih protobufova
- `selfCheck.completeness` u dokumentu meča broji frameove i poruke po Valveovom imenu, unose combat loga (`combatlog <type>`), događaje igre (`gameevent <name>`), unose tabele stringova (`stringtable <name>`) i ažuriranja entiteta (`entity <class>`); nekoliko ih se čuva samo sirovo (puni snimci entiteta koje gem preskače jer gradi iz delti, i unosi tabela čije vrijednosti ništa ne čita), izgubljeno 0

**Nije dostupno**

- glas: snimak ima postavke glasa, ali ne i podatke glasa
- imena iza hasheva i id-ova: zvukovi i čestice imenovani su hashevima datoteka igre, sposobnosti id-ovima; snimak ne nosi imena (predmeti se imenuju kroz gemov katalog gdje ih ima)
- sve što su znali samo klijenti samih igrača (njihova kamera, njihov ekran) mimo onoga što je server emitirao; kursor i svaka komanda su unutra

**Veličina**: sidecari zajedno su nešto veći od samog snimka, a najveći su paketi i entiteti; cijeli meč traje minutu-dvije u jednom procesu

## Provjereno {#verified}

provjereno na snimku javnog meča: ubistva, smrti, asistencije, nivo, last hitovi i denyji poklapaju se s igrinim vlastitim zapisom kraja meča za svih deset igrača; svaka poruka u sidecaru paketa ponovo se serijalizira bajt po bajt; tabela i statistike testovima na sintetičkim podacima

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
