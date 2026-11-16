---
title: "Steam-Statistiken (Plattform)"
nav_order: 42
lang: "de"
source: game-steam-stats.md
source_hash: "09ecf3611c02"
nav_exclude: true
search_exclude: true
---
# Steam-Statistiken (Plattform) {#steam-statistics-platform}

Der Watcher speichert, was Steam-Statistiken über deine Spiele festhält, damit du deinen Verlauf später als Statistik und Zeitleiste ansehen kannst.

*Technische Details: Adapter `steam-stats`, Art [`platform`](sources-and-rules.md); er läuft immer (er wartet nicht auf den Start eines Spiels) und sucht alle 30 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- jede Statistik, die ein Spiel in Steam speichert (ihre eigenen Namen und Werte), pro Spiel, bei jeder Änderung
- Erfolgsfreischaltungen mit Anzeigename, Beschreibung und Freischaltzeit
- Statistikänderungen mit altem Wert, neuem Wert und Differenz
- Spielzeit (Minuten, letzte zwei Wochen) und Zeitpunkt des letzten Spielens

## Woher es kommt {#where-it-comes-from}

Der lokale Statistik-Cache von Steam %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin mit UserGameStatsSchema_&lt;appid>.bin; die Spielzeit aus %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% aus HKCU\Software\Valve\Steam SteamPath)

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten. Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

Was der Launcher und der Grafiktreiber über das Spielen festhalten: Steam-Statistiken, Erfolge, Spielzeit und Zeitleisten sowie die Highlights und Clips von NVIDIA.

Keine dieser Quellen braucht, dass ein Spiel mitarbeitet oder läuft. Deshalb sind die drei Adapter hier immer an und schauen alle paar Sekunden in ein paar Dateien.

#### Steam-Statistiken (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin` wird vom Steam-Client jedes Mal neu geschrieben, wenn ein Spiel seine Statistiken speichert. Sie wird mit dem Schema `UserGameStatsSchema_<appid>.bin` daneben dekodiert (binäre KeyValues, siehe `_steam.py`). Statistiken sind Ganzzahlen oder Kommazahlen, wie das Spiel sie definiert. Erfolge sind Bits mit einer Freischaltzeit in Unix-Sekunden. Die Spielzeit steht in `<Steam>\userdata\<account>\config\localconfig.vdf` unter apps/&lt;appid>: Playtime und Playtime2wks in Minuten, LastPlayed in Unix-Sekunden. Steam wird über HKCU\Software\Valve\Steam SteamPath gefunden.
Statistik-API: <https://partner.steamgames.com/doc/features/achievements>

Dasselbe Modul bedient außerdem: [NVIDIA-Highlights (Plattform)](game-nvidia-highlights.md), [Steam-Zeitleiste (Plattform)](game-steam-timeline.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | nein |
| Hochachse | `y` |
| Einheiten | Meter |
| Für den Viewer gespiegelt | keine |
| Einheitenfaktor (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte stehen in der `meta.json` jeder Sitzung (`axes`) und, wenn die Sitzung Positionen hat, im Fuß der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst. Siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als Online-Spiel markiert (`multiplayer`): **nein**. `games --markdown` zeigt das als „Einzelspieler“.
- Art `platform`: Er liest nur, was das Spiel oder die Plattform herausgibt (was Steam oder der Grafiktreiber festhält). Deshalb zeichnet er auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur Adapter der Art `memory` lesen Speicher, und nie bei einem als Online-Spiel markierten Spiel. Siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (`stats` jeder Sitzung in `meta.json` und die Tabelle `stats` der `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit ergänzt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels nimmt, stehen nicht in dieser Liste. Was aufgezeichnet wird, steht oben und nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter erhält, ganz in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dazu jedes nach Namen behaltene Feld; `used` markiert, was auch zu Zeilen wurde). Der `selfCheck.completeness` in `meta.json` zählt jeden `type`. `lost` ist 0.

**Gelesen**

- jede Statistik der Statistikdatei nach ihrem API-Namen (int, float, avgrate), jedes Erfolgsbit mit seiner Freischaltzeit, benannt und beschrieben nach dem Schema
- Änderungen gegenüber dem letzten Lesen (alt, neu, Differenz), neue Freischaltungen; Spielzeit, Spielzeit der letzten zwei Wochen und zuletzt gespielt aus localconfig.vdf

**Roh behalten**

- `UserGameStats`: die Bytes der Statistikdatei, ganz, jedes Mal wenn sie aufgezeichnet wird (die `crc`, `PendingChanges`, Erfolgsbits, die das Schema nicht mehr definiert, und jeder Schlüssel, den der Dekoder überspringt, stehen darin)
- `UserGameStatsSchema`: die Bytes der Schemadatei daneben, damit die Statistiken allein aus der Sitzung dekodiert werden können (alle Namen der Statistiken und Erfolge in allen Sprachen, Symbole, Flags)
- `localconfig_app`: der ganze Block des Spiels aus localconfig.vdf als JSON (Cloud-Sync-Stand, Startoptionen, Abzeichen und jeder andere Schlüssel, den Steam pro Spiel führt), wenn seine Spielzeit aufgezeichnet wird
- eine Statistikdatei, die der Dekoder nicht lesen kann (mitten im Schreiben abgeschnitten oder ein neues Layout): ihre Bytes und das Schema in einer Sitzung ohne Zeilen (`used` false; `unreadable` in meta.json)

**Nicht verfügbar**

- der Rest von localconfig.vdf (Freunde, Chat, Steam-Einstellungen): nicht das Spiel, und privat
- Statistikwerte zwischen zwei Schreibvorgängen: Steam schreibt die Datei neu, wenn das Spiel seine Statistiken speichert, meist beim Schließen
- globale Erfolgsprozente und Statistiken anderer Spieler: sie liegen auf Steams Servern, nicht hier

**Größe**: einige KB pro aufgezeichneter Sitzung, dazu das Schema (bis zu einigen hundert KB bei einem Spiel mit vielen Erfolgen). Insgesamt weit unter 1 MB pro Stunde Spielzeit. zstd verkleinert den Text des Schemas um die Hälfte oder mehr.

## Geprüft {#verified}

Getestet an echten Statistikdateien und Schemata aus einer lokalen Installation. Die Erkennung von Änderungen ist an Dateien geprüft, die im binären KeyValues-Format gebaut wurden.

## Quelle {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
