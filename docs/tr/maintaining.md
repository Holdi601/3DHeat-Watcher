---
title: "Bu sayfaların bakımı"
nav_order: 15
lang: "tr"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Bu sayfaların bakımı {#maintaining-these-pages}

Her sürüm için kontrol listesi. Sayfalar, ne yaptığı kodun söylediği gibi söylemeli, bir başlangıç kullanıcısı, 8 yaşındaki bir çocuk ve bir uzman için iyi okunmalı ve 3DHeat görüntüleyicisinin desteklediği her dilde bulunmalıdır.

## Sürüm kontrol listesi {#release-checklist}

1. **Üretilen sayfaları koddan yeniden üretin**:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Commit etmeden önce aynısını `--check` ile çalıştırın; 0 ile çıkmalıdır:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Son sürümden bu yana olan özellikleri karşılaştırın.** `VERSION` sürümü tutar; etiketi `v<VERSION>`'dir:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Her yeni komut, seçenek, sütun, çıktı ya da davranış, ait olduğu sayfada bir satır alır ve `CHANGELOG.md` içinde **Docs** altında o sayfayı adlandıran bir satır alır.

3. **Bağımsız inceleme.** Değişikliği yazmamış biri, değişen sayfaları - diyagramlar ve resimler dahil - üç kez okur: bir başlangıç kullanıcısı olarak (hiç terminal kullanmamış), 8 yaşında biri olarak (ilk paragraf ne olduğunu ve neden olduğunu sade sözlerle söylüyor mu?) ve bir uzman olarak (bayraklar, varsayılanlar ve sütunlar kodun yaptığıyla birebir mi?).

4. **İncelemenin bulduklarını düzeltin.** Resimler gösterildiği gibi en fazla yaklaşık 900 px genişliğinde kalır, metin en az 12 px'tir; diyagramlar `tools/diagrams/*.json` dosyalarından `tools/flow2svg.py` ile üretilir. Örnekler yalnızca uydurma adlar kullanır (`de_x`, "Demo Valley", `<map>`): gerçek bir harita, oyuncu, maç kimliği ya da gerçek dosyalardan bir figür asla.

5. **Çeviriler.** Her çevrilmiş sayfa, hangi İngilizce kaynaktan yapıldığını gösteren karmayı kaydeder. İngilizce kaynağının karması değişen sayfaları yeniden çevirin, sonra her dil üç yoldan (sade, başlangıç, uzman) incelensin; diyagram etiketleri de dahil.

6. **Yalnızca sahibin onayından sonra gönderin.** Yerel olarak commit edin; ne zaman herkese açık olacağına sahip karar verir.

## Çeviriler: komutlar {#translations-the-commands}

Site, 3DHeat görüntüleyicisinin 40 diline çevrilmiştir: İngilizce `docs/` içinde, diğer her dil `docs/<lang>/` içinde aynı dosya adlarıyla. `tools/docs_i18n.py` kayıt işlerini yapar:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Yalnızca `todo` listesindekileri çevirin: Markdown, bağlantılar, kod, dosya ve sütun adlarını olduğu gibi bırakın, başlıkları ve resim açıklamalarını çevirin ve 3DHeat görüntüleyicisinin düğmeleri ve panelleri için kendi sözcüklerini kullanın (`src/i18n/locales/<lang>/` içindeki). Üretilen başvuru sayfaları ve terminal resimleri İngilizce kalır. Sitede, güncel olmayan bir çeviri bunu söyler ve İngilizce sayfaya bağlanır; eksik olan İngilizceye düşer. Üstbilgideki dil menüsü ve ana sayfanın tarayıcı diline göre yönlendirmesi `docs/_includes/` içinden gelir.
