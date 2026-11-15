---
title: "Steam statistika (platforma)"
nav_order: 43
lang: "hr"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Steam statistika (platforma) {#steam-statistics-platform}

Watcher sprema ono što Steam statistika čuva o vašim igrama, pa svoju povijest kasnije možete pogledati kao statistiku i vremensku crtu.

*Tehnički podaci: adapter `steam-stats`, vrsta [`platform`](sources-and-rules.md); radi stalno (ne čeka da igra počne) i traži nove podatke svakih 30 s.*

## Što se bilježi {#what-is-recorded}

- svaka statistika koju igra sprema u Steamu (njezini nazivi i vrijednosti), po igri, kad se promijeni
- otključavanja postignuća s prikaznim nazivom, opisom i vremenom otključavanja
- promjene statistike sa starom vrijednošću, novom vrijednošću i razlikom
- vrijeme igranja (minute, zadnje dva tjedna) i vrijeme zadnje igre

## Odakle dolazi {#where-it-comes-from}

Steamov lokalni predmemorijski spremnik statistika %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin uz UserGameStatsSchema_&lt;appid>.bin; vrijeme igranja iz %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% iz HKCU\Software\Valve\Steam SteamPath)

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Ono što pokretač i upravljački program grafike čuvaju o igranju: Steamova statistika, postignuća, vrijeme igranja i vremenske crte, te NVIDIA-ini istaknuti trenuci i isječci.

Nijedan od ovih izvora ne traži da igra surađuje ili da je pokrenuta, pa su tri adaptera ovdje uvijek uključena i gledaju nekoliko datoteka svakih nekoliko sekundi.

#### Steam statistika (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, ponovno piše Steam klijent kad god igra spremi svoju statistiku, dekodira se shemom `UserGameStatsSchema_<appid>.bin` pored nje (binarni KeyValues, vidi `_steam.py`). Statistike su cijeli ili decimalni brojevi kako ih igra definira; postignuća su bitovi s vremenom otključavanja u Unix sekundama. Vrijeme igranja je u `<Steam>\userdata\<account>\config\localconfig.vdf` pod apps/&lt;appid>: Playtime i Playtime2wks u minutama, LastPlayed u Unix sekundama. Steam se pronalazi kroz HKCU\Software\Valve\Steam SteamPath.
Stats API: <https://partner.steamgames.com/doc/features/achievements>

Isti modul služi i: [NVIDIA istaknuti trenuci (platforma)](game-nvidia-highlights.md), [Steam vremenska crta (platforma)](game-steam-timeline.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Os prema gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nijedno |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovi podaci idu u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje `heat.parquet`-a, pa preglednik 3DHeat sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igrano na mreži (`multiplayer`): **ne**. `games --markdown` to prikazuje kao "jednoigrač".
- Vrsta `platform`: čita samo ono što igra ili platforma predaje (ono što Steam ili upravljački program grafike čuva), pa bilježi i na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Watcher slijedi 3DHeatovo [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži pročita se ili sačuva, ništa se ne baca. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi sačuva se cijeli u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- svaka statistika iz datoteke statistika po svom API nazivu (int, float, avgrate), svaki bit postignuća s vremenom otključavanja, imenovan i opisan prema shemi
- promjene u odnosu na zadnje čitanje (stara, nova, razlika), nova otključavanja; vrijeme igranja, vrijeme zadnje dvije tjedne i zadnja igra iz localconfig.vdf

**Čuva se sirovo**

- `UserGameStats`: bajtovi datoteke statistika, cijeli, pri svakom bilježenju (`crc`, `PendingChanges`, bitovi postignuća koje shema više ne definira i svaki ključ koji dekoder preskoči nalaze se u njoj)
- `UserGameStatsSchema`: bajtovi datoteke sheme pored nje, pa se statistike mogu dekodirati iz same sesije (nazivi svake statistike i postignuća na svim jezicima, ikone, zastavice)
- `localconfig_app`: cijeli blok igre iz localconfig.vdf kao JSON (stanje sinkronizacije u oblaku, opcije pokretanja, značke i svaki ostali ključ koji Steam čuva po igri) kad se bilježi vrijeme igranja
- datoteka statistika koju dekoder ne može pročitati (presječena usred pisanja, ili novi raspored): njezini bajtovi i shema u sesiji bez redaka (`used` false; `unreadable` u meta.json)

**Nije dostupno**

- ostatak localconfig.vdf (prijatelji, chat, Steam postavke): nije igrin i privatan je
- vrijednosti statistike između dva zapisa: Steam ponovno piše datoteku kad igra spremi statistiku, obično kad se zatvori
- globalni postoci postignuća i statistike drugih igrača: nalaze se na Steamovim serverima, ne ovdje

**Veličina**: nekoliko KB po zabilježenom sjedenju, plus shema (do nekoliko stotina KB za igru s mnogo postignuća) - znatno manje od 1 MB po satu igranja; zstd smanji tekst sheme za pola ili više

## Provjereno {#verified}

testirano na pravim datotekama statistika i shema s lokalne instalacije; otkrivanje promjena testirano na datotekama izgrađenim u binarnom KeyValues formatu

## Izvor {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i pokrenite ga ponovno umjesto uređivanja ove stranice. -->
