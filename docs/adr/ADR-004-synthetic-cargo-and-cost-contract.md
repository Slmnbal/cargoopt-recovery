# ADR-004 — Sentetik Kargo, Recovery Case ve TRY Maliyet Kararı

| Alan | Değer |
|---|---|
| Durum | Accepted |
| Tarih | 2026-08-13 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | PH0-T03 |

## Bağlam

CargoOpt Recovery gerçek uçuş schedule ve outcome verisini açık BTS kaynağından kullanabilir; ancak gerçek kargo manifestosu, uçuş kargo kapasitesi, SLA, cold-chain ve operasyon maliyeti mevcut değildir. Bu boşluk sessiz varsayımlarla doldurulursa model gerçek şirket verisi kullanıyormuş gibi görünebilir, ML-informed yaklaşım lehine sentetik vaka üretilebilir veya OR objective'i ölçülemeyen katsayılar içerebilir.

Ayrıca “en fazla 10 destinasyon”, “24 saatlik recovery”, “öncelik”, “atanamama” ve “TL maliyeti” kavramlarının kod öncesinde tek anlamı olmalıdır. Risk-blind ve ML-informed MILP karşılaştırmasında olasılık dışında hiçbir input veya constraint değişmemelidir.

## Karar

### 1. Recovery case sınırı

- Bir case tek kaynak uçuş, tek origin ve tek destination içerir.
- Tek hub, TRAIN dönemindeki dondurulmuş top-20 listede en yüksek operasyon sayısına göre seçilir.
- En fazla 10 destination, TRAIN döneminde hub'dan doğrudan uçuş sayısına göre seçilir ve dondurulur.
- Her destination ayrı case akışıdır; farklı destination'lar tek MILP'e karıştırılmaz.
- Recovery penceresi `prediction_cutoff_at` ile başlar ve 24 saat sürer.
- Aday uçuşun planlanan kalkış ve varışı pencere içinde olmalıdır.
- Bir case 50–500 gönderi ve 2–30 aday doğrudan uçuş içerir.

Case örnekleme ve blind replay vaka seçimi bu ADR'nin kapsamı dışındadır. Seçilen case'in yapısal geçerliliği bu ADR ile belirlenir.

### 2. Gönderi sınıfları

Yalnızca üç cargo sınıfı vardır:

| Cargo | Oran | Handling | SLA slack | Cold-chain |
|---|---:|---:|---:|---:|
| `STANDARD` | 0,70 | 60 dk | 12 saat | Hayır |
| `EXPRESS` | 0,20 | 45 dk | 4 saat | Hayır |
| `PHARMA` | 0,10 | 90 dk | 2 saat | Evet |

Gönderi bölünmez; tam bir uçuşa atanır veya `UNASSIGNED` kalır. Ayrı serbest priority alanı kullanılmaz; cargo sınıfı hem SLA hem maliyet önceliğini taşır.

### 3. Deterministik generator

- Sözleşme kimliği `synthetic-cargo-v1`'dir.
- Master seed `20240831`, varsayılan shipment sayısı `200`'dür.
- Her attribute stateless SHA-256 materyalinden üretilir; ortak PRNG state'i yoktur.
- Cargo kotaları largest-remainder ile belirlenir.
- Ağırlık bounded ve küçük değerlere eğilimli dağıtılır; hacim ağırlık/yoğunluktan türetilir.
- Candidate toplam ağırlık ve hacim kapasitesi varsayılan `BALANCED_110` modunda talebin 1,10 katıdır ve deterministic paylaştırılır.
- Generator schedule ve config okuyabilir; ML olasılığı, outcome, solver sonucu veya replay metriği okuyamaz.

### 4. TL maliyet temeli

Para birimi `TRY`, temel `SYNTHETIC_NOMINAL_2024`, policy kimliği `cost-policy-try-v1` olarak kabul edilmiştir.

| Cargo | Handling | Gecikme/saat | Aksama sonucu | Atanamama |
|---|---:|---:|---:|---:|
| `STANDARD` | ₺500 | ₺250 | ₺10.000 | ₺50.000 |
| `EXPRESS` | ₺750 | ₺750 | ₺30.000 | ₺150.000 |
| `PHARMA` | ₺1.250 | ₺1.250 | ₺50.000 | ₺250.000 |

Bu değerler gerçek şirket maliyeti değildir. KDV, enflasyon ve döviz dönüşümü uygulanmaz.

### 5. Objective ayrımı

Ortak maliyet:

```text
base_assignment_cost = handling_cost + planned_lateness_hours × delay_cost_per_hour
```

Risk-blind objective yalnızca ortak maliyeti kullanır. ML-informed objective aynı maliyete:

```text
severe_disruption_probability × disruption_consequence
```

terimini ekler. Shipment, candidate, capacity, eligibility, constraint, unassigned penalty ve cost policy aynıdır.

Candidate olasılığı ADR-005'teki multi-horizon latest-available ceiling kuralıyla seçilir. `prediction.produced_at_utc <= recovery_decision_at` zorunludur; recovery kararından sonra üretilmiş bir forecast cost matrix'e giremez.

Blind replay'de assignment dondurulduktan sonra beklenen risk teriminin yerine gerçekleşmiş `severe_disruption × disruption_consequence` kullanılarak realized maliyet ölçülür. Outcome plan üretimine giremez.

### 6. Unassigned dominance

Her sınıf için:

```text
unassigned_penalty
  > handling + 24 × delay_per_hour + disruption_consequence
```

sağlanır. Böylece hard constraint'leri bozmadan yapılabilen her assignment, `UNASSIGNED` seçeneğinden daha ucuzdur. `UNASSIGNED` her zaman izinli olduğundan kapasite yetersizliği sahte assignment veya yanlış `INFEASIBLE` yorumu üretmez.

## Gerekçe

- Stateless hash, satır sırası ve paralellikten bağımsız tekrar üretilebilirlik sağlar.
- Exact cargo kotaları küçük sample'da sınıf kaymasını önler.
- Hacmin yoğunluk üzerinden ağırlığa bağlanması anlamsız bağımsız değer çiftlerini engeller.
- TL, mülakat anlatımını anlaşılır yapar; sentetik cost basis gerçek finansal iddiayı engeller.
- Unassigned dominance önceliği yumuşak maliyetle görünür kılarken hard constraint'leri korur.
- Tek controlled objective farkı ML katkısının paired karşılaştırmasını yorumlanabilir yapar.
- Generator'ın probability/outcome görmemesi senaryo yanlılığını sınırlar.

## Sonuçlar

Olumlu:

- Phase 2 generator ve Phase 4 OR için ölçülebilir interface oluşur.
- Aynı config/seed ile golden fixture üretilebilir.
- Maliyet matrisinin beklenen ve gerçekleşen sürümü ayrı tutulur.
- Model başarısız olsa bile risk-blind baseline aynı case üzerinde çalışır.
- Gerçek Turkish Cargo verisi kullanıldığı izlenimi azaltılır.

Maliyet ve sınırlamalar:

- Katsayılar ekonomik tahmin değil deney parametresidir.
- Kapasite ve cargo mix gerçek dağılımları temsil etmez.
- Tek hub, doğrudan rota ve split yasağı network gerçekçiliğini sınırlar.
- Sabit nominal TRY uzun dönem fiyat karşılaştırması için uygun değildir.
- Cold-chain boolean, detaylı sıcaklık/handling sürecini modellemez.

## Reddedilen alternatifler

- Para birimi olmayan SCU kullanmak
- Tutarları gerçek Turkish Cargo maliyeti gibi sunmak
- Generator'ı ML skoruna göre zorlaştırmak veya kolaylaştırmak
- Blind outcome'a bakarak seed, cargo mix veya kapasite ayarlamak
- Ağırlık ve hacmi bağımsız uniform üretmek
- Gönderiyi bölmeye izin vermek
- PHARMA cold-chain kuralını penalty'ye çevirmek
- Outcome'u expected objective içinde kullanmak
- Unassigned seçeneğini kaldırıp infeasible durumda sahte assignment üretmek
- Tek modelde farklı destination'lara rerouting yapmak

## Uygulama kapıları

Phase 2 generator başlamadan önce:

- `OR_INPUT_SCHEMA.yaml` için schema validator planı onaylanmalı;
- canonical hashing ve golden fixture testleri tanımlanmalı;
- generator dependency'leri ayrıca onaylanmalı;
- outcome/prediction denylist'i otomatik test edilmelidir.

Phase 4 OR başlamadan önce:

- matematiksel değişken ve constraint sözleşmesi ayrıca onaylanmalı;
- cost matrix tek canonical builder'dan üretilmeli;
- bağımsız validator aynı input schema'yı okuyabilmeli;
- deterministic iki aşamalı tie-break ve solver status politikası tanımlanmalıdır.

Bu ADR bu uygulamaları veya dependency'leri başlatmaz.

## Değişiklik koşulu

Case sınırı, cargo oranı, seed, aralık, capacity mode, eligibility, SLA, cold-chain, TRY katsayısı, objective terimi veya unassigned dominance değişirse yeni contract/policy sürümü, sensitivity etkisi, blind bütünlük analizi, ADR ve açık insan onayı gerekir. Blind sonuç görüldükten sonra birincil v1 geriye dönük değiştirilemez.
