# ADR-001 — Proje Kapsamı ve Başlangıç Kararları

| Alan | Değer |
|---|---|
| Durum | Accepted |
| Tarih | 2026-08-13 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | PH0-T01 |

## Bağlam

CargoOpt Recovery'nin OR, klasik ML ve AI Engineer ilanları için güçlü olması istenirken ML, optimizasyon ve RAG katmanlarının tek bir belirsiz mega-sisteme dönüşme riski bulunmaktadır. Tahmin zamanı, hedef etiketi, havalimanı seçimi ve veri ayrımı kesinleşmeden geliştirilecek bir veri hattı leakage ve yeniden üretilebilirlik sorunlarına yol açabilir.

## Karar

### Çekirdek ürün

Çekirdek ürün tek bir recovery iş problemine odaklanacaktır:

- ML, aday uçuşların ciddi aksama olasılığını üretir.
- OR, gönderileri uygun alternatif uçuşlara atar.
- Validator, planı Pyomo state'inden bağımsız olarak doğrular.
- Historical replay, stratejileri gerçekleşen uçuş sonuçlarıyla karşılaştırır.
- API/UI, sonucu hesaplamadan gösterir.

### Tahmin ve hedef

- Tahmin zamanı `T-6` olarak sabitlenmiştir.
- Ciddi aksama etiketi `Cancelled == 1 OR Diverted == 1 OR ArrDelayMinutes >= 60` olarak tanımlanmıştır.
- Model tek bir binary classification problemi çözer.

### Veri evreni

- Uçuş kaynağı resmî BTS Reporting Carrier On-Time Performance verisidir.
- Dönem 1 Ocak–31 Aralık 2024'tür.
- En yoğun 20 havalimanı yalnızca Ocak–Ağustos eğitim döneminden seçilir ve dondurulur.
- Train Ocak–Ağustos, validation Eylül–Ekim, test Kasım, blind replay Aralık'tır.
- Kargo, kapasite, SLA ve maliyet verileri deterministik sentetiktir.

### Problem sınırı

- Tek hub, en fazla 10 destinasyon
- 24 saat recovery penceresi
- En fazla 30 aday uçuş ve 500 gönderi
- Yalnızca doğrudan uçuş
- Split shipment yok
- `STANDARD`, `EXPRESS`, `PHARMA`
- HiGHS zorunlu solver

### RAG + LLM

- RAG + LLM çekirdek karar sisteminden ayrı, downstream ve salt okunur Phase 8 modülüdür.
- Yalnızca kamuya açık, Türkçe, kaynağı ve kullanım koşulu doğrulanabilir belgeler kullanılır.
- Sentetik politika veya prosedür corpus'a alınmaz.
- Copilot assignment, constraint, objective, solver sonucu veya operasyon verisi değiştiremez.

### Geliştirme ve maliyet

- Çalışma Codex in ChatGPT Work üzerinden yürütülür.
- Ücretli API veya yönetilen servis zorunlu değildir.
- Claude'a özel çalışma dosyası veya akışı kullanılmaz.

## Gerekçe

- T-6, feature availability için kesin bir cutoff sağlar.
- Diversion hava kargo teslimatı açısından ciddi operasyonel aksama olduğundan hedefe dahildir.
- Top-20 seçimini yalnızca eğitim döneminden yapmak gelecek dönem dağılımına bakmayı engeller.
- Zaman bazlı ayrım gerçek kullanım düzenine rastgele ayrımdan daha yakındır.
- Deterministik sentetik kargo, gerçek şirket verisi olmadan OR deneyini tekrar üretilebilir kılar.
- Copilot'u downstream tutmak LLM hatasının karar doğruluğunu bozamamasını sağlar.

## Sonuçlar

Olumlu:

- ML ve OR sorumlulukları ölçülebilir kalır.
- Leakage ve blind tuning riski azalır.
- Proje ücretsiz ve yerel olarak yeniden üretilebilir.
- OR ve AI Engineer anlatıları aynı çekirdeği bozmadan ayrıştırılır.

Maliyet ve sınırlamalar:

- BTS verisi Turkish Cargo verisi değildir.
- Kargo maliyetlerinin sentetik olması gerçek finansal etki iddiasını engeller.
- T-6 cutoff'u gerçek operasyon politikasının doğrulanmış karşılığı değil, proje deney sözleşmesidir.
- Açık Türkçe corpus şirket içi politika sorularını kapsamayabilir; Copilot bu durumda çekimser kalır.

## Reddedilen alternatifler

- Rastgele train/test split
- Tüm 2024 verisiyle top-20 havalimanı seçimi
- Diversion sonucunu görmezden gelmek
- ML'nin doğrudan gönderi ataması üretmesi
- LLM'nin solver veya veritabanına yazma yetkisi
- Phase 1'de gelecekteki RAG altyapısını hazırlamak
- Gerçek şirket verisi varmış gibi sentetik politika üretmek

## Değişiklik koşulu

Bu karar; yeni ADR, veri/deney etkisi analizi, backtest bütünlüğü incelemesi ve açık insan onayı olmadan değiştirilemez.

