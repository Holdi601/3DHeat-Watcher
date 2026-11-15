---
title: "Steam statistika (platforma)"
nav_order: 43
lang: "bs"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Steam statistika (platforma) {#steam-statistics-platform}

Watcher sprema ono što Steam statistika čuva o vašim igrama, pa svoju historiju poslije možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `steam-stats`, vrsta [`platform`](sources-and-rules.md); radi stalno (ne čeka da igra krene) i svakih 30 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- svaka statistika koju igra sprema u Steam (njena vlastita imena i vrijednosti), po igri, kad se promijeni
- otključavanja postignuća s prikaznim imenom, opisom i vremenom otključavanja
- promjene statistike sa starom vrijednošću, novom vrijednošću i razlikom
- vrijeme igranja (minute, zadnje dvije sedmice) i vrijeme zadnjeg igranja

## Odakle dolazi {#where-it-comes-from}

Steamov lokalni keš statistike %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin uz UserGameStatsSchema_&lt;appid>.bin; vrijeme igranja iz %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% iz HKCU\Software\Valve\Steam SteamPath)

## Kako to uključiti {#how-to-switch-it-on}

Ništa se ne mora uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Ono što pokretač i grafički drajver čuvaju o igranju: Steamova statistika,
postignuća, vrijeme igranja i vremenske linije, te NVIDIA-ini highlighti i klipovi.

Nijedan od ovih izvora ne traži da igra sarađuje niti da radi, pa su tri
adaptera ovdje uvijek uključena i svakih nekoliko sekundi gledaju nekoliko datoteka.

#### Steam statistika (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, koju
Steam klijent prepisuje svaki put kad igra spremi svoju statistiku, dekodirana shemom
`UserGameStatsSchema_<appid>.bin` pored nje (binarni KeyValues, vidite `_steam.py`).
Statistike su cijeli ili decimalni brojevi kako ih igra definira; postignuća su biti
s vremenom otključavanja u Unix sekundama. Vrijeme igranja je u
`<Steam>\userdata\<account>\config\localconfig.vdf` pod apps/&lt;appid>:
Playtime i Playtime2wks u minutama, LastPlayed u Unix sekundama.
Steam se nalazi preko HKCU\Software\Valve\Steam SteamPath.
Stats API: <https://partner.steamgames.com/doc/features/achievements>

Isti modul služi i: [NVIDIA highlighti (platforma)](game-nvidia-highlights.md), [Steam Timeline (platforma)](game-steam-timeline.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | ne |
| Osa gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nema |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **ne**. `games --markdown` to prikazuje kao "singleplayer".
- Vrsta `platform`: čita samo ono što igra ili platforma daje (ono što Steam ili grafički drajver čuva), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor drži čita se ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, zatim svako polje čuvano po imenu; `used` označava šta je postalo i redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- svaka statistika iz datoteke statistike po svom API imenu (int, float, avgrate), svaki bit postignuća s vremenom otključavanja, imenovan i opisan shemom
- promjene u odnosu na zadnje čitanje (staro, novo, razlika), nova otključavanja; vrijeme igranja, vrijeme igranja u dvije sedmice i zadnje igranje iz localconfig.vdf

**Čuva se sirovo**

- `UserGameStats`: bajtovi datoteke statistike, cijeli, svaki put kad se snimi (u njima su `crc`, `PendingChanges`, biti postignuća koje shema više ne definira i svaki ključ koji dekoder preskoči)
- `UserGameStatsSchema`: bajtovi datoteke sheme pored nje, da se statistika može dekodirati samo iz sesije (imena svake statistike i postignuća na svakom jeziku, ikone, zastavice)
- `localconfig_app`: cijeli blok igre iz localconfig.vdf kao JSON (stanje sinkronizacije oblaka, opcije pokretanja, značke i svaki drugi ključ koji Steam čuva po igri) kad se snima njeno vrijeme igranja
- datoteka statistike koju dekoder ne može pročitati (prekinuta usred pisanja, ili novi raspored): njeni bajtovi i shema u sesiji bez redova (`used` false; `unreadable` u meta.json)

**Nije dostupno**

- ostatak localconfig.vdf (prijatelji, chat, Steam postavke): nije od igre, i privatan je
- vrijednosti statistike između dva upisa: Steam prepisuje datoteku kad igra spremi svoju statistiku, obično kad se zatvori
- globalni postoci postignuća i statistike drugih igrača: oni su na Steamovim serverima, ne ovdje

**Veličina**: nekoliko KB po snimljenom igranju, plus shema (do nekoliko stotina KB za igru s mnogo postignuća) - znatno manje od 1 MB po satu igranja; zstd smanjuje tekst sheme za pola ili više

## Provjereno {#verified}

testirano na pravim datotekama statistike i shemama s lokalne instalacije; otkrivanje promjena testirano na datotekama izgrađenim u binarnom formatu KeyValues

## Izvor {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
