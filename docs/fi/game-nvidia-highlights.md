---
title: "NVIDIA-kohokohdat (alusta)"
nav_order: 34
lang: "fi"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA-kohokohdat (alusta) {#nvidia-highlights-platform}

Watcher tallentaa sen, mitä NVIDIA-kohokohdat pitää pelejäsi koskevasta, jotta voit myöhemmin katsoa historiaasi kartalla 3DHeat-katselimessa.

*Tekniset tiedot: sovitin `nvidia-highlights`, tyyppi [`platform`](sources-and-rules.md); se toimii koko ajan (ei odota pelin käynnistymistä) ja etsii uutta dataa 10 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokainen uusi klippi, kohokohta tai kuvakaappaus: peli, tiedosto, tyyppi, pituus ja hetki (seinäkellon aika ms:nä)
- kohokohdan tunnus ja nimi, kun peli on rekisteröinyt sen NVIDIAlle
- missä pelaaja oli sillä hetkellä, kun toinen sovitin tallensi saman pelin silloin
- kohokohtapyynnöt, joita GfeSDK-pelit kirjaavat, vaikka klippiä ei säilytetä

## Mistä data tulee {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; klipit tallennuskansiossa (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) ja &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Miten se kytketään päälle {#how-to-switch-it-on}

NVIDIA App: Instant Replay tai Highlights päälle, klipit tallennetaan pikanäppäimellä tai pelin toimesta

## Miten se toimii {#how-it-works}

Mitä käynnistysohjelma ja näytönohjain pitävät tallessa pelaamisesta: Steamin tilastot, saavutukset, peliaika ja aikajanat sekä NVIDIAn kohokohdat ja klipit.

Mikään näistä lähteistä ei vaadi, että peli yhteistyöhön tai että se on käynnissä, joten tässä olevat kolme sovitinta ovat aina päällä ja katsovat muutamaa tiedostoa muutaman sekunnin välein.

#### NVIDIAn kohokohdat ja klipit (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Sen, minkä NVIDIA App / GeForce Experience pitää, kaikki kansiossa
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      galleriahakemisto: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (mihin klipit tallennetaan),
                     settings.tempDirectory (kohokohdat odottavat
                     <temp>\Highlights\<game>-kansiossa, kunnes ne tallennetaan)
Highlights\<game>\config.json  kohokohtatyypit, jotka peli on rekisteröinyt:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
ja itse klippitiedostot, `<capture folder>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (kuvakaappaukset: `<Game> Screenshot yyyy.mm.dd - ...png`); tiedostonimen aika on paikallinen aika, jolloin klippi tallennettiin. GfeSDK-pelit kirjaavat myös kohokohtakutsunsa tiedostoon `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Mitä tämä voi ja ei voi antaa: peli, joka tukee NVIDIA Highlightsia (GfeSDK), rekisteröi kohokohtatyypit kerran (tunnus kuten "kill", merkittävyys, tagit, näyttönimi), ja myöhemmin se sanoo vain "highlight <id>, from <ms> before now to <ms> after". Sijainteja, ottelua tai kierrosta, vastustajaa tai omaa dataa ei ole: SDK:ssa ei ole kenttää millekään niistä. Tallennettu klippi lisää tiedoston, pelin nimen, pituuden ja ajan. Tallennetaan siis "tällainen hetki tässä pelissä tähän aikaan", ja paikka vain katsomalla aikaa toisen sovittimen tallennuksesta samasta pelistä (`position_at`), mitä tämä sovitin tekee jokaiselle tallentamalleen klipille.
<https://developer.nvidia.com/highlights>

Jokainen sovitin pitää kirjaa siitä, minkä se on jo nähnyt, tiedostossa `<data>\state\<id>.json`, joten uudelleenkäynnistys ei tallenna mitään kahdesti.

Jokainen sessio tallentaa myös sen, mistä sen rivit tulivat, sellaisenaan (3DHeatin muunninsääntö, docs/converters.md katselimen repositoriossa), tiedostoon `heat.raw.parquet`: statistiikkatiedoston ja sen skeeman tavut sekä pelin localconfig-lohko (steam-stats; tiedosto, jota dekooderi ei osaa lukea, antaa session, jossa on vain sen tavut), aikajanatiedoston otsakkeen ja jokaisen merkinnän JSON-muodossa (steam-timeline), jokaisen klipin galleriahakemiston merkinnän, pelin kohokohtamääritykset ja jokaisen GfeSDK-lokirivin, myös ne, jotka eivät ole kohokohtapyyntöjä (nvidia-highlights).

Samaa moduulia käyttävät myös: [Steam-tilastot (alusta)](game-steam-stats.md), [Steam Timeline (alusta)](game-steam-timeline.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | vain lainattuna: se paikka, jonka toisella saman pelin tallennuksella on sille hetkelle |
| Ylösakseli | `y` |
| Yksiköt | metriä |
| Peilattu katselinta varten | ei mitään |
| Yksikköskaala (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`:n kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`:n footeriin. Näin 3DHeat-katselin kääntää ja skaalaa rivit itse, katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **ei**. `games --markdown` näyttää tämän muodossa "single-player".
- Tyyppi `platform`: se lukee vain sen, minkä peli tai alusta antaa ulos (sen, mitä Steam tai näytönohjain pitää tallessa), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissä. Lippu ratkaisee vain sen, saako muistia koskaan lukea.
- Muisti: tämän sovittimen lukema **ei koskaan**. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty verkkopeliksi. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (session `stats` tiedostossa `meta.json` ja taulussa `stats` tiedostossa `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Aaltosulkeissa oleva avain täydentyy ajon aikana (`score.{team}` on yksi avain per joukkue). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä listassa. Kohdassa "Mitä tallennetaan" ne on nimetty.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunninsääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): se, mitä lähde sisältää, luetaan tai tallennetaan, eikä mitään pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja sen jälkeen nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- jokainen uusi klippi ja kuvakaappaus: peli, tiedosto, tyyppi, media, pituus (indeksistä, muuten MP4-otsakkeesta), hetki tiedostonimestä, kohokohdan tunnus ja nimi, kun peli rekisteröi ne, ja pelaajan paikka silloin toisen sovittimen tallennuksesta
- GfeSDK-kohokohtapyynnöt (jokainen `Posted Request HL...`, paitsi asetuskutsut) aikoineen

**Tallennettu raakana**

- `UGC`: klipin koko merkintä galleriahakemistosta UGCTracker.json, jokainen kenttä, jonka NVIDIA kirjoittaa
- `clip_file`: klipille, jota hakemisto ei listaa, tiedoston polku, koko, aika ja kansio
- `highlights_config`: pelin `Highlights\<game>\config.json` sellaisenaan kirjoitettuna (merkittävyys, tagit, nimet jokaisella kielellä), kerran per sessio
- `gfesdk_log`: jokainen GfeSDK-lokirivi, jotka on luettu ensimmäisen ajon jälkeen; `used` on tosi kohokohtapyynnöille ja epätosi muille (asetukset, videoasetukset, SDK:n omat viestit)

**Ei saatavilla**

- klipit ja kuvakaappaukset itse: video ja kuvat jäävät sinne, minne NVIDIA ne tallensi; rivit nimeävät tiedoston
- se, mitä oli ennen sovittimen ensimmäistä ajoa: otetaan nähtyinä, joten vuosien klipit eivät muutu sessioiksi kerralla (`baseline`; False tallentaa ne)
- UGCTracker.jsonin `apps` ja `info` sekä GallerySettings.json: sovelluksen asetuksia, ei pelaamisen hetkiä; niiden nimeämä tallennuskansio käytetään
- sijainnit, kierrokset, vastustajat: GfeSDK:ssa ei ole kenttiä niille

**Koko**: noin 1 KB per klippi ja muutama KB määrityksiä ja lokirivejä per pelin käynnistys: selvästi alle 1 Mt tunnissa

## Todennettu {#verified}

Testattu oikealla galleriahakemistolla, asetuksilla, kohokohtamäärityksillä ja klipeillä paikallisesta asennuksesta. GfeSDK:n kohokohtapyyntörivit ja klippien kohokohtatunnukset ovat testaamattomia.

## Lähdekoodi {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
