---
title: "NVIDIA highlights (platforma)"
nav_order: 34
lang: "bs"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platforma) {#nvidia-highlights-platform}

Watcher sprema ono što NVIDIA highlights čuva o vašim igrama, da svoju historiju kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `nvidia-highlights`, vrsta [`platform`](sources-and-rules.md); radi cijelo vrijeme (ne čeka da se igra pokrene) i svakih 10 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- svaki novi klip, highlight ili snimak ekrana: igra, datoteka, vrsta, dužina i trenutak (wall-clock ms)
- id i naziv highlighta kad ga je igra registrovala kod NVIDIA-e
- gdje je igrač bio u tom trenutku, ako je neki drugi adapter tada snimao istu igru
- zahtjevi za highlight koje igre s GfeSDK-om bilježe, čak i kad se nijedan klip ne zadrži

## Odakle dolazi {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; klipovi u folderu za snimanje (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) i &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Kako ga uključiti {#how-to-switch-it-on}

NVIDIA App: uključen Instant Replay ili Highlights, klipovi spremljeni prečicom ili od same igre

## Kako radi {#how-it-works}

Ono što launcher i grafički drajver čuvaju o igranju: Steamova statistika,
postignuća, vrijeme igranja i vremenske linije, te NVIDIA-ini highlighti i klipovi.

Nijedan od ovih izvora ne traži da igra sarađuje niti da je pokrenuta, pa su tri
adaptera ovdje uvijek uključena i svakih nekoliko sekundi pogledaju nekoliko datoteka.

#### NVIDIA highlights i klipovi (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Ono što NVIDIA App / GeForce Experience čuva, sve pod
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      the gallery index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (where clips are saved),
                     settings.tempDirectory (highlights wait in
                     <temp>\Highlights\<game> until saved)
Highlights\<game>\config.json  the highlight kinds a game registered:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
i sami fajlovi klipova, `<capture folder>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (snimci ekrana: `<Game> Screenshot yyyy.mm.dd - ...png`); vrijeme u
imenu je lokalno vrijeme kad je klip spremljen. Igre s GfeSDK-om također bilježe
svoje pozive highlighta u `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Šta ovo može i ne može dati: igra koja podržava NVIDIA Highlights
(GfeSDK) jednom registruje vrste highlighta - id poput "kill", značaj,
tagove, prikazni naziv - a kasnije samo kaže "highlight &lt;id>,
od &lt;ms> prije sada do &lt;ms> poslije". Nema položaja, nema meča ili
runde, nema protivnika, nema prilagođenih podataka: SDK nema polje ni za šta od toga. Spremljeni
klip dodaje datoteku, naziv igre, dužinu i vrijeme. Dakle ono što se
bilježi je "ova vrsta trenutka, u ovoj igri, u ovo vrijeme" - a mjesto
samo tako što se vrijeme potraži u snimku iste igre iz nekog drugog adaptera
(`position_at`), što ovaj adapter radi za svaki klip koji bilježi.
<https://developer.nvidia.com/highlights>

Svaki adapter čuva ono što je već vidio u `<data>\state\<id>.json`, pa
ponovno pokretanje ništa ne bilježi dvaput.

Svaka sesija također čuva cijelo ono iz čega su njeni redovi nastali (3DHeat-ovo pravilo
konvertera, docs/converters.md u repozitoriju preglednika), u `heat.raw.parquet`:
bajtove datoteke statistike i njene sheme te blok localconfig igre
(steam-stats; datoteka statistike koju dekoder ne može pročitati dobija sesiju koja drži samo
njene bajtove), zaglavlje datoteke vremenske linije i svaki unos kao JSON
(steam-timeline), unos galerijskog indeksa svakog klipa, definicije highlighta igre
i svaku liniju GfeSDK loga, i one koje nisu zahtjevi za highlight
(nvidia-highlights).

Isti modul služi i za: [Steam statistika (platforma)](game-steam-stats.md), [Steam Timeline (platforma)](game-steam-timeline.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | samo posuđeni: mjesto koje drugi snimak iste igre ima za taj trenutak |
| Osa gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **ne**. `games --markdown` to prikazuje kao "single-player".
- Vrsta `platform`: čita samo ono što igra ili platforma daje (ono što Steam ili grafički drajver čuva), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- svaki novi klip i snimak ekrana: igra, datoteka, vrsta, medij, dužina (indeks, inače zaglavlje MP4), trenutak iz imena datoteke, id i naziv highlighta gdje ih je igra registrovala, i igračevo tadašnje mjesto iz snimka drugog adaptera
- GfeSDK zahtjevi za highlight (svaki `Posted Request HL...` osim poziva konfiguracije) s njihovim vremenom

**Čuva se sirovo**

- `UGC`: cijeli unos klipa iz galerijskog indeksa UGCTracker.json, svako polje koje NVIDIA piše
- `clip_file`: za klip koji indeks ne navodi, putanja datoteke, veličina, vrijeme i folder
- `highlights_config`: `Highlights\<game>\config.json` igre onako kako je napisan (značaj, tagovi, nazivi na svakom jeziku), jednom po sesiji
- `gfesdk_log`: svaka linija GfeSDK logova pročitana poslije prvog pokretanja, `used` istinito za zahtjeve za highlight i neistinito za ostalo (konfiguracija, postavke videa, vlastite poruke SDK-a)

**Nije dostupno**

- sami klipovi i snimci ekrana: video i slike ostaju tamo gdje ih je NVIDIA spremila; redovi navode datoteku
- ono što je bilo prije prvog pokretanja adaptera: uzima se kao već viđeno, da godine klipova ne postanu odjednom sesije (`baseline`; False ih snima)
- `apps` i `info` iz UGCTracker.json i GallerySettings.json: postavke aplikacije, a ne trenuci igranja; koristi se folder za snimanje koji navode
- položaji, runde, protivnici: GfeSDK nema polje za njih

**Veličina**: oko 1 KB po klipu i nekoliko KB definicija i linija loga po pokretanju igre: znatno manje od 1 MB na sat

## Provjereno {#verified}

testirano na pravom galerijskom indeksu, postavkama, definicijama highlighta i klipovima s lokalne instalacije; linije GfeSDK zahtjeva za highlight i id-ovi highlighta u klipovima nisu testirani

## Izvor {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
