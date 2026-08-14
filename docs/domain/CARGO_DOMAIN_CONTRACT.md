# Cargo Domain ve Recovery Case Sözleşmesi

| Alan | Değer |
|---|---|
| Sözleşme kimliği | `cargo-domain-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T03` |
| Zaman standardı | UTC, timezone-aware |
| Ağırlık | kilogram (`kg`) |
| Hacim | metreküp (`m3`) |
| Para birimi | `TRY` |
| Maliyet temeli | `SYNTHETIC_NOMINAL_2024` |

## 1. Amaç ve dürüstlük sınırı

Bu sözleşme, tek bir uçuş aksama riski karşısında sentetik gönderilerin alternatif uçuşlara atanması için domain anlamını tanımlar. Uçuş schedule ve ML olasılığı açık BTS verisinden türetilebilir; gönderi, kargo kapasitesi, cold-chain uygunluğu, SLA ve bütün TL katsayıları sentetiktir.

`TRY` kullanımı tutarların gerçek olduğu anlamına gelmez. Değerler gerçek THY/Turkish Cargo fiyatı, tarifesi, maliyeti, tasarrufu veya finansal etkisi olarak sunulamaz. KDV, enflasyon ve döviz dönüşümü v1 kapsamında yoktur.

## 2. Terimler

| Terim | Kesin anlam |
|---|---|
| `recovery_case` | Tek kaynak uçuş, tek origin, tek destination, sentetik gönderiler ve uygun alternatif uçuşlardan oluşan bağımsız karar problemi |
| Kaynak uçuş | Gönderilerin başlangıçta bağlı olduğu, alternatife atanacak schedule kaydı |
| Aday uçuş | Aynı origin ve destination için recovery penceresinde kalan doğrudan alternatif |
| Gönderi | Bölünemeyen tek sentetik kargo birimi |
| `UNASSIGNED` | Gönderinin hiçbir aday uçuşa atanmadığını belirten açık karar |
| Risk-blind | Alternatif uçuş ML olasılığını objective katsayısına koymayan MILP |
| ML-informed | Aynı MILP'e yalnızca beklenen aksama maliyetini ekleyen strateji |
| Outcome | Uçuş sonrası bilinen `severe_disruption` gerçekleşmesi; yalnızca replay değerlendirmesinde kullanılır |

## 3. Ağ ve case sınırı

### 3.1 Ana merkez

Tek ana merkez, PH0-T02'de yalnızca TRAIN döneminden seçilen dondurulmuş top-20 havalimanı listesindeki en yüksek toplam origin + destination operasyon sayısına sahip havalimanıdır. Eşitlikte küçük `AirportID` kazanır.

### 3.2 Destinasyonlar

- Ana merkezden doğrudan ulaşılan en fazla 10 destination kullanılır.
- Sıralama yalnızca TRAIN dönemindeki doğrudan uçuş sayısına göre azalan yapılır.
- Eşitlikte küçük destination `AirportID` kazanır.
- Seçilen liste validation, ML test ve blind replay boyunca dondurulur.
- “10 destinasyon”, tek problemde farklı destination'ların karıştırılması değildir; en fazla 10 bağımsız case akışıdır.

### 3.3 Recovery case kimliği

Doğal case anahtarı:

```text
source_flight_id | cargo-domain-v1 | synthetic-cargo-v1 | cost-policy-try-v1
```

`case_id`, bu UTF-8 metnin küçük harfli 64 karakterlik SHA-256 hex özetidir. Aynı kaynak uçuş ve sözleşme sürümleri aynı `case_id`'yi üretir.

Her case:

- tam bir `source_flight_id` içerir;
- `origin_airport_id == hub_airport_id` koşulunu sağlar;
- tam bir `destination_airport_id` içerir;
- 50–500 gönderi içerir;
- en az 2, en fazla 30 aday uçuş içerir;
- başka case'in kapasitesi veya gönderisiyle ortak karar değişkeni kullanmaz.

Case seçim algoritması ve blind değerlendirme örneklemesi PH0-T03 kapsamı dışındadır. Bu sözleşme yalnızca seçilmiş bir case'in geçerliliğini tanımlar.

## 4. Zaman sözleşmesi

```text
prediction_cutoff_at = source_scheduled_departure_at - 6 hours
recovery_window_start_at = prediction_cutoff_at
recovery_window_end_at = prediction_cutoff_at + 24 hours
```

- Bütün timestamp'ler ISO-8601 UTC ve `Z` suffix'li olmalıdır.
- Naive veya origin-local timestamp OR girdisine kabul edilmez.
- Kaynak ve aday uçuş zamanları PH0-T02 schedule katmanından gelir.
- Aday uçuşun planlanan kalkışı recovery başlangıcından kesinlikle sonra, planlanan varışı recovery bitişine eşit veya önce olmalıdır.
- Aday varışı üst sınıra eşitse kabul edilir.

## 5. Gönderi sözleşmesi

### 5.1 Cargo sınıfları

| Alan | `STANDARD` | `EXPRESS` | `PHARMA` |
|---|---:|---:|---:|
| Öncelik sırası | 1 | 2 | 3 |
| Minimum handling | 60 dk | 45 dk | 90 dk |
| SLA slack | 12 saat | 4 saat | 2 saat |
| Cold-chain zorunlu | Hayır | Hayır | Evet |

`delivery_due_at = source_scheduled_arrival_at + sla_slack` olarak üretilir. Ayrı, serbestçe değişebilen bir priority alanı yoktur; öncelik doğrudan `cargo_type` ile tanımlıdır.

### 5.2 Zorunlu gönderi alanları

| Alan | Kural |
|---|---|
| `shipment_id` | Case içinde benzersiz, deterministik string |
| `case_id` | Parent case ile tam eşleşir |
| `cargo_type` | `STANDARD`, `EXPRESS` veya `PHARMA` |
| `weight_kg` | Pozitif, bir ondalık hassasiyet |
| `volume_m3` | Pozitif, üç ondalık hassasiyet |
| `ready_at_utc` | Recovery penceresi içinde timezone-aware UTC |
| `handling_minutes` | Cargo sınıfı tablosuyla tam eşleşir |
| `delivery_due_at_utc` | Kaynak planlanan varış + sınıf SLA slack |
| `requires_cold_chain` | Yalnızca PHARMA için `true` |

Gönderi bölünemez. Ağırlık veya hacmin bir kısmı farklı uçuşlara aktarılamaz.

## 6. Aday uçuş uygunluğu

Bir aday uçuş case listesine girebilmek için:

1. `flight_id != source_flight_id` olmalıdır.
2. Origin, case origin ile aynı olmalıdır.
3. Destination, case destination ile aynı olmalıdır.
4. Rota doğrudan olmalıdır.
5. Planlanan kalkış recovery başlangıcından sonra; planlanan varış recovery bitişine eşit veya önce olmalıdır.
6. Planlanan varış, planlanan kalkıştan sonra olmalıdır.
7. `capacity_weight_kg > 0` ve `capacity_volume_m3 > 0` olmalıdır.
8. Immutable prediction batch içinde aynı `flight_id` için tek, geçerli olasılık bulunmalıdır.

Candidate için seçilen olasılık `flight-severe-disruption-prediction-v2` ceiling kuralına uyar:

```text
delta_hours = candidate_departure - recovery_decision_at
selected_horizon = min { h in {24,18,12,6} | h >= delta_hours }
prediction_produced_at = candidate_departure - selected_horizon
prediction_produced_at <= recovery_decision_at
```

Karardan sonra üretilmiş daha yakın horizon skoru kullanılamaz.

Bir gönderi–uçuş çifti ayrıca şu koşullarda uygundur:

```text
candidate_scheduled_departure_at >= ready_at + handling_minutes
```

PHARMA için ek olarak `cold_chain_capable == true` zorunludur.

## 7. Atama semantiği ve hard constraint'ler

Her gönderi için tam olarak biri gerçekleşir:

```text
sum(x[shipment, flight]) + unassigned[shipment] = 1
```

Hard constraint'ler:

- yalnızca uygun shipment–flight çiftleri için `x = 1` olabilir;
- uçuş toplam ağırlığı `capacity_weight_kg` değerini aşamaz;
- uçuş toplam hacmi `capacity_volume_m3` değerini aşamaz;
- PHARMA cold-chain olmayan uçuşa atanamaz;
- farklı destination'a atama yapılamaz;
- `UNASSIGNED` her zaman izinli olduğundan model kapasite yüzünden sahte assignment üretmez.

`UNASSIGNED`, constraint ihlali değildir; yüksek ve açık maliyetli gerçek bir karar durumudur.

## 8. ML, generator ve outcome ayrımı

| Veri | Generator okuyabilir | OR objective okuyabilir | Blind replay okuyabilir |
|---|---:|---:|---:|
| Kaynak/aday schedule | Evet | Evet | Evet |
| Sentetik gönderi ve kapasite | Üretir | Evet | Evet |
| Kalibre ML olasılığı | Hayır | Yalnızca ML-informed | Evet |
| `Cancelled`, `Diverted`, `ArrDelayMinutes` | Hayır | Hayır | Evet |
| Gerçekleşmiş `severe_disruption` | Hayır | Hayır | Evet |

Risk-blind ve ML-informed stratejiler aynı `case_id`, shipment snapshot, candidate snapshot ve cost policy üzerinde çalışır. Kontrollü tek fark, ML-informed objective'teki immutable olasılık terimidir.

## 9. Fail-closed durumları

Aşağıdakilerden biri varsa OR çalıştırılmaz:

- schema veya contract sürümü bilinmiyor;
- duplicate ID bulunuyor;
- case parent-child anahtarları eşleşmiyor;
- zaman naive veya recovery penceresi geçersiz;
- aday sayısı 2'den az veya 30'dan fazla;
- gönderi sayısı 50'den az veya 500'den fazla;
- ağırlık/hacim sıfır, negatif, NaN veya sonsuz;
- cargo enum'u bilinmiyor;
- PHARMA cold-chain semantiği bozuk;
- cost policy farklı veya eksik;
- aday uçuşlardan biri için olasılık yok, duplicate ya da `[0,1]` dışında;
- candidate horizon ceiling kuralıyla eşleşmiyor veya prediction karar anından sonra üretilmiş;
- outcome alanı OR snapshot'ına sızmış;
- snapshot hash'i manifestle eşleşmiyor.

## 10. Değişiklik koşulu

Cargo enum'u, case kardinalitesi, recovery penceresi, eligibility, birimler, hard constraint veya ML/outcome sınırı değişirse yeni contract sürümü, ADR, geriye uyumluluk analizi ve açık insan onayı gerekir.
