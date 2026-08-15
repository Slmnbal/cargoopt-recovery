# ADR-010 — BTS Fiziksel Header ve Canonical Alan Ayrımı

| Alan | Değer |
|---|---|
| Durum | Accepted |
| Tarih | 2026-08-15 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | `PH2-T02-R11` |
| Kanıt görevleri | `PH2-T02-R2`, `PH2-T02-R10` |

## Bağlam

BTS selected-field formu alanları iş odaklı adlarla sunar; üretilen CSV ise
aynı alanları fiziksel kaynak kodlarıyla yazar. R2, 15 form control'ünün iş
alanı ve kaynak kodu ilişkisini exact olarak çıkardı. R10, Ocak 2024
selected-field ZIP içindeki tek CSV'nin raw header'ını yalnız header okuyarak
exact 15 fiziksel kod olarak gözledi. Eksik, fazla, duplicate veya boş kolon
yoktu; hiçbir data row okunmadı.

Önceki sözleşme raw CSV header'ında business label beklediği için kaynak
uyumlu olmasına rağmen literal isim eşitliği kapısında durdu. Alanların iş
anlamı, label formülü ve accepted canonical 15-field listesi değişmedi.

## Karar

Kaynak fiziksel şeması ile canonical iş şeması ayrı sözleşmeler olarak
tutulacaktır.

1. Raw CSV header, `BTS_DATA_CONTRACT.md` içindeki 15 fiziksel koda sıra dahil
   tam eşit olmalıdır.
2. Raw doğrulama geçtikten sonra yalnız aynı belgede yazılı kapalı `15 -> 15`
   mapping uygulanabilir.
3. Mapping sonucu canonical alanlar accepted iş sözleşmesi sırasına
   deterministik olarak dizilir.
4. Her iki tarafta cardinality, uniqueness ve exact set/order doğrulanır.
5. Fuzzy match, alias keşfi, case-fold tahmini, sessiz projection veya fallback
   yoktur; her drift `SNAPSHOT_FATAL` olur.

## Gerekçe

Bu karar kaynak gerçekliğini iş modelinden ayırır, ancak esneklik adı altında
şema tahmini yapmaz. Mapping R2 ve R10 kanıtlarından mekanik olarak oluşur;
kolon anlamı tahmin edilmez. Böylece ingestion ileride BTS raw formatını exact
doğrularken domain ve ML/OR katmanları anlaşılır canonical adları kullanabilir.

## Sonuçlar

Olumlu:

- Kaynak uyumluluk kapısı gerçek fiziksel header üzerinden doğrulanır.
- Domain sözleşmesi ve label formülü değişmez.
- Mapping sürümlü, test edilebilir ve audit edilebilirdir.
- Schema drift sessizce üretime taşınmaz.

Maliyet ve sınırlamalar:

- Ingestion iki ayrı şema kapısı uygulamak zorundadır.
- BTS fiziksel header'ında tek bir isim veya sıra değişikliği bile snapshot'ı
  durdurur ve inceleme gerektirir.
- Bu ADR veri indirme veya ingestion implementation yetkisi vermez.

## Reddedilen alternatifler

- CSV'de business label isimlerini zorunlu tutmak
- Kolonları fuzzy veya case-insensitive eşlemek
- Eksik/fazla kolonlardan ihtiyaç duyulan 15 alanı sessizce project etmek
- Fiziksel BTS kodlarını domain, ML ve OR katmanlarında kalıcı iş adları yapmak
- Raw kolon sırasını yok sayıp yalnız set eşitliği aramak

## Değişiklik koşulu

Fiziksel header, mapping, canonical alan listesi, sıra veya alan anlamı
değişirse yeni kaynak kanıtı, contract sürümü, ADR etkisi ve açık insan onayı
gerekir. Sonucu geçirmek için mapping gevşetilemez.
