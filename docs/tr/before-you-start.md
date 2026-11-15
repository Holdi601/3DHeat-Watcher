---
title: "Başlamadan önce"
nav_order: 2
lang: tr
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Başlamadan önce {#before-you-start}

Komut satırında yeni misiniz? Bu sayfa sizi hiçbir şeyden yaklaşık on dakikada çalışan bir 3DHeat Watcher'a götürür. Komutları *terminal* denilen bir pencereye yazarsınız: bir satır yazar ve Enter'a basarsınız.

## 1. Python'u kurun {#install-python}

1. <https://www.python.org/downloads/> adresinden Python 3.10 ya da daha yeni bir sürüm indirin.
2. Kurulum programını çalıştırın. İlk ekranda **Add python.exe to PATH** kutusunu işaretleyin, sonra **Install Now** (Şimdi yükle) düğmesine tıklayın.
3. Denetleyin: bir terminal açın (3. adım) ve `python --version` yazın. `Python 3.` ve 10 veya daha büyük bir sayı görmelisiniz.

Linux ya da macOS'ta Python genellikle zaten kuruludur: bu sayfalarda `python` yazan yerde `python3` kullanın.

## 2. 3DHeat Watcher'ı alın {#get-3dheat-watcher}

[Sürümler sayfasından](https://github.com/Holdi601/3DHeat-Watcher/releases) zip dosyasını indirin ve açın; örneğin `C:\Tools\3DHeat-Watcher` klasörüne. (Git'iniz varsa `git clone` de çalışır.)

## 3. Klasörde bir terminal açın {#open-a-terminal-in-that-folder}

- **Windows:** klasörü Dosya Gezgini'nde açın, adres çubuğuna tıklayın, `powershell` yazın ve Enter'a basın. Zaten o klasörde olan mavi ya da siyah bir pencere açılır.
- **macOS / Linux:** *Terminal*'i açın, `cd ` yazın (bir boşlukla), klasörü pencereye sürükleyin ve Enter'a basın.

`cd <folder>` terminali başka bir klasöre taşır. Bu sayfalardaki tüm komutlar aracın kendi klasöründe yazılır.

## 4. Gereken şeyleri kurun {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Sonunda `Successfully installed ...` (ya da `Requirement already satisfied`) görmelisiniz.

## 5. Çalıştığını denetleyin {#check-it-works}

```bash
python -m heat3d_watch --version
```

Şunu görmelisiniz: `1.0.2 (sürüm numarası)`.

## Bu sayfalardaki komutları nasıl okursunuz {#how-to-read-the-commands-on-these-pages}

- `<açı parantezleri>` içindeki sözcükler yer tutucudur: kendi dosya ya da klasörünüzü yazın, işaretler olmadan. `python -m heat3d_watch sessions --game <name>` demek, parantez kısmını değiştirmeniz demektir.
- Boşluk içeren bir yol tırnak içine girer: `"C:\My Games\my file"`.
- Örneklerde `#` ile başlayan satırlar açıklamadır; bunları yazmazsınız.
- Başarı şöyle görünür: `python -m heat3d_watch games` komutundan sonra, oyun başına bir satırlık bir tablo.

## Sık görülen hatalar {#common-errors}

| Gördüğünüz | Yapın |
|---|---|
| `'python' is not recognized` ya da `command not found` | Python PATH üzerinde değil: kurulum programını yeniden çalıştırın, **Add python.exe to PATH** kutusunu işaretleyin, sonra yeni bir terminal açın. macOS/Linux'ta `python3` deneyin. |
| `No module named ...` | 4. adım atlanmış ya da başka bir klasörde çalıştırılmış: aracın klasörüne `cd` ile gidin ve yeniden çalıştırın. |
| `pip is not recognized` | `pip ...` yerine `python -m pip ...` kullanın. |
| `No such file or directory` / `can't open file` | Terminal yanlış klasörde ya da yol yanlış yazılmış: kontrol edin; boşluk içeren yolları tırnak içine alın. |
| `error:` satırıyla biten kırmızı metin | Son satırı okuyun: neyin eksik olduğunu söyler. [Komutlar](../commands.md) sayfası iletileri listeler. |
