# ADR-002 — Faz Kapıları ve Codex Çalışma Yönetişimi

| Alan | Değer |
|---|---|
| Durum | Accepted |
| Tarih | 2026-08-13 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | PH0-T01 |

## Bağlam

Proje; veri mühendisliği, ML, matematiksel optimizasyon, API/UI ve RAG + LLM bileşenleri içerir. Gelecek fazlar için erken dependency, abstraction veya placeholder hazırlanması scope creep, yanlış varsayım ve test edilmeyen altyapı yaratabilir. Kullanıcı başlangıç aşamasında belirsizlik ve profesyonel akış hatası istememektedir.

## Karar

### Tek aktif faz

- Aynı anda yalnızca bir faz `ACTIVE` olabilir.
- Tamamlanan faz `COMPLETED`, başlanmayan faz `LOCKED` olur.
- Faz durumu `docs/phase-status.yaml` içindeki tek yetkili kayıttır.
- Sonraki faz ancak geçiş kapısı karşılandıktan ve kullanıcı açıkça onayladıktan sonra açılır.

### Faz izolasyonu

Kilitli faz için aşağıdakiler oluşturulamaz:

- Kod veya klasör
- Dependency veya lock-file değişikliği
- Endpoint veya UI
- Database tablo/migration
- Config veya environment değişkeni
- Interface, abstraction veya adapter
- Placeholder, TODO implementation veya boş fixture

Gelecek faz yalnızca mimari/spesifikasyon gereği Phase 0 dokümanlarında tanımlanabilir; çalıştırılabilir hazırlık yapılamaz.

### Görev bazlı onay

Her görev:

- tek bir faza bağlıdır;
- açık amaç, kapsam ve kapsam dışı iş taşır;
- izinli ve yasak dosyaları belirtir;
- acceptance kriterleri ile gerekli testleri tanımlar;
- dependency/migration yetkisini açıkça belirtir;
- zorunlu durma koşullarını listeler.

Codex önce dosya bazlı planı sunar. İnsan planı onayladıktan sonra uygulama yapılır. Bir görev onayı sonraki göreve veya faza aktarılmaz.

### Doğrulama ve raporlama

- Çalıştırılmayan kontrol başarılı sayılamaz.
- Test veya acceptance kriteri başarısızsa görev `COMPLETED` olamaz.
- Başarısızlığı saklamak için test zayıflatılamaz.
- Görev kapanışında değişen dosyalar, doğrulama kanıtı, kalan risk ve faz durumu raporlanır.

### Değişiklik yönetimi

- Onaylı kapsam dışı ihtiyaç yeni görev veya revize görev sözleşmesi gerektirir.
- Ürün/veri/deney kararları ADR gerektirir.
- Dependency ve migration ayrıca insan onayı gerektirir.
- Kullanıcı değişiklikleri korunur; çakışmada Codex durur.

## Gerekçe

- Faz kapıları, yanlış temelin sonraki bileşenlere yayılmasını önler.
- Dosya allowlist'i istemsiz kapsam genişlemesini görünür hale getirir.
- Plan onayı, kullanıcıyı mimari ve risk kararlarında yetkili tutar.
- Test kanıtı, “çalışıyor” iddiasını yeniden üretilebilir yapar.
- RAG dependency'lerinin Phase 8'e kadar yasaklanması ML + OR çekirdeğini bağımsız tutar.

## Sonuçlar

Olumlu:

- Scope creep ve erken abstraction riski azalır.
- Her değişiklik izlenebilir ve geri değerlendirilebilir olur.
- Mülakatta profesyonel mühendislik yönetişimi gösterilebilir.
- Çekirdek proje Copilot'dan bağımsız tamamlanabilir.

Maliyet:

- Daha fazla dokümantasyon ve açık onay adımı gerekir.
- Hızlı görünen ancak doğrulanmamış çapraz-faz geliştirmeler reddedilir.
- Yeni fikirler aktif görevi kesintiye uğratmadan sonraki planlamayı bekler.

## Reddedilen alternatifler

- Tek seferde bütün repository skeleton'ını oluşturmak
- “Sonra kullanılır” gerekçesiyle dependency veya interface eklemek
- Codex'in belirsiz gereksinimlerde kendi tercihini sessizce uygulaması
- Test çalıştırmadan görevi tamamlandı saymak
- Phase 8 altyapısını Phase 1 database migration'ına eklemek

## Değişiklik koşulu

Bu yönetişim modeli ancak yeni ADR ve açık insan onayıyla değiştirilebilir. Faz izolasyonunu gevşeten değişiklikte scope, test, veri bütünlüğü ve geri dönüş etkisi ayrıca açıklanmalıdır.

