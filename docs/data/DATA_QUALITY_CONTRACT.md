# Veri Kalitesi ve Snapshot Aktivasyon Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `cargoopt-data-quality-v2` |
| Durum | Accepted |
| İlgili veri sözleşmesi | `bts-reporting-otp-contract-v1` |
| İlgili görev | `PH0-T03` |

## 1. İlke

Veri kalitesi “temizlemeyi başarıyla bitirmek” değil, verinin ne zaman kullanılamaz sayılacağını açıkça belirlemektir. Hiçbir satır sessizce düzeltilmez, outcome uydurulmaz veya snapshot kalite kapısı atlanmaz.

Durumlar:

| Seviye | Sonuç |
|---|---|
| `INFO` | Manifest metriği; akışı etkilemez |
| `WARNING` | Snapshot devam edebilir; rapor ve gerekçe zorunlu |
| `ROW_QUARANTINE` | Satır model/evaluation evrenine giremez |
| `SNAPSHOT_FATAL` | İlgili aylık veya birleşik snapshot aktive edilemez |

## 2. Kaynak artifact kontrolleri

| Kontrol | Başarı koşulu | İhlal |
|---|---|---|
| Aylık kapsam | 2024 için tam 12 artifact | `SNAPSHOT_FATAL` |
| Kaynak kimliği | Her artifact için resmî URL ve indirme zamanı | `SNAPSHOT_FATAL` |
| Byte bütünlüğü | Byte size `> 0` ve SHA-256 mevcut | `SNAPSHOT_FATAL` |
| Parse | Archive/CSV hatasız açılabilir | `SNAPSHOT_FATAL` |
| Aylık satır | Her ay `row_count > 0` | `SNAPSHOT_FATAL` |
| Kaynak değişmezliği | Aynı dataset ID altında hash değişmez | `SNAPSHOT_FATAL` |

Aynı URL daha sonra farklı byte üretirse mevcut snapshot overwrite edilmez; yeni source artifact kimliği ve inceleme gerekir.

## 3. Şema kontrolleri

Şema iki ayrı kapıda doğrulanır. Birinci kapı, raw CSV header'ının BTS veri
sözleşmesindeki 15 fiziksel kaynak koduna sıra dahil tam eşitliğidir:

```text
actual_raw_header_order == expected_physical_header_order
```

İkinci kapı, yalnızca sözleşmede yazılı bire bir eşleme uygulandıktan sonra
canonical 15 iş alanının kabul edilen sıra ve kümeye tam eşitliğidir:

```text
mapped_and_reordered_columns == expected_canonical_columns_order
```

- Raw header'da eksik, fazla, duplicate, boş veya yeri değişmiş kolon: `SNAPSHOT_FATAL`
- Kapalı mapping dışında kalan fiziksel veya canonical kolon: `SNAPSHOT_FATAL`
- Mapping cardinality'sinin `15 -> 15` olmaması: `SNAPSHOT_FATAL`
- Canonical alanda eksik, fazla veya duplicate kolon: `SNAPSHOT_FATAL`
- Beklenmeyen tip: güvenli ve kayıpsız parse mümkün değilse `SNAPSHOT_FATAL`
- Otomatik fuzzy match, case-insensitive tahmin, alias fallback veya sessiz rename/projection: yasak

Fiziksel kodların iş alanlarına farklı sırada gelmesi beklenen kaynak
davranışıdır; yalnız exact raw sıra doğrulandıktan sonra contract mapping'iyle
canonical sıraya deterministik reorder yapılabilir. Başka hiçbir reorder kabul
edilmez.

## 4. Satır seviyesi structural kontroller

| Alan/kural | Kabul koşulu | İhlal |
|---|---|---|
| `FlightDate` | Geçerli tarih ve 2024 içinde | `ROW_QUARANTINE` |
| `DOT_ID_Reporting_Airline` | Pozitif integer | `ROW_QUARANTINE` |
| Flight number | Boş olmayan canonical string | `ROW_QUARANTINE` |
| Origin/Dest AirportID | Pozitif integer ve farklı | `ROW_QUARANTINE` |
| Origin/Dest code | Boş olmayan uppercase display code | `ROW_QUARANTINE` |
| `CRSDepTime` / `CRSArrTime` | Geçerli `hhmm`; `2400` özel kuralı | `ROW_QUARANTINE` |
| `CRSElapsedTime` | Sonlu ve `> 0` dakika | `ROW_QUARANTINE` |
| `Distance` | Sonlu ve `> 0` mil | `ROW_QUARANTINE` |
| `Cancelled` / `Diverted` | Her biri `0` veya `1` | `ROW_QUARANTINE` |
| Outcome tutarlılığı | İkisi aynı anda `1` değil | `ROW_QUARANTINE` |
| Completed outcome | İkisi `0` ise ArrDelayMinutes sonlu ve `>= 0` | `ROW_QUARANTINE` |
| Timezone mapping | Origin ve destination için tek IANA zone | `ROW_QUARANTINE` |

Whitespace/format canonicalization yapılabilir; orijinal değer audit kaydında korunur. İş anlamını değiştiren düzeltme yapılamaz.

## 5. Duplicate kontrolleri

| Durum | Davranış |
|---|---|
| Exact duplicate | Bir kayıt tutulur; duplicate count ve source locator'lar manifestte saklanır |
| Conflicting duplicate | `SNAPSHOT_FATAL`; otomatik tercih yapılamaz |
| Exact duplicate oranı `<= 0.1%` | `WARNING` ile devam |
| Exact duplicate oranı `> 0.1%` | `SNAPSHOT_FATAL` ve kaynak incelemesi |

Oran denominator'ı parse edilen aylık ham satır sayısıdır.

## 6. Karantina bütçesi

Karantina nedeni kodları en az şunlardır:

```text
INVALID_DATE
INVALID_SCHEDULED_TIME
MISSING_IDENTITY
INVALID_AIRPORT_PAIR
MISSING_TIMEZONE
INVALID_SCHEDULE_DURATION
INVALID_DISTANCE
INVALID_BINARY_OUTCOME
CONFLICTING_CANCEL_DIVERT
MISSING_COMPLETED_ARRIVAL_DELAY
CONFLICTING_DUPLICATE
```

Snapshot eşikleri:

| Metrik | Eşik | Sonuç |
|---|---:|---|
| Toplam row quarantine oranı | `<= 0.5%` | Kabul edilebilir, rapor zorunlu |
| Toplam row quarantine oranı | `> 0.5%` | `SNAPSHOT_FATAL` |
| Herhangi ay quarantine oranı | `> 1.0%` | `SNAPSHOT_FATAL` |
| Model-eligible satırda label unknown | `0` | Aksi `SNAPSHOT_FATAL` |
| Model-eligible satırda feature NaN/Inf | `0` | Aksi `SNAPSHOT_FATAL` |

Eşiği aşan satırları silerek snapshot'ı geçirmek yasaktır. Kaynak veya sözleşme incelenir.

## 7. Zaman ve leakage kontrolleri

Source recovery kararı `T-6` anında verilir. Model feature'ları ise izinli `T-24`, `T-18`, `T-12`, `T-6` forecast ladder'ının her satırı için kendi cutoff'una göre hesaplanır.

Her feature satırı için zorunlu invariant'lar:

```text
lead_time_hours in {24, 18, 12, 6}
prediction_cutoff_at = scheduled_departure_at_utc - lead_time_hours
history_row.flight_instance_id != target.flight_instance_id
history_row.label_available_at <= prediction_cutoff_at
history_row.scheduled_departure_at_utc < prediction_cutoff_at
```

Rolling pencere için ayrıca:

```text
prediction_cutoff_at - window <= history_row.scheduled_departure_at_utc
```

Kontroller:

- Target label veya outcome feature matrix'te bulunamaz.
- Validation/test/blind partition aggregate'i toplu hesaplanamaz.
- Her hedef satırı as-of cutoff ile bağımsız hesaplanır.
- Encoder/imputer/scaler yalnızca izinli training satırlarında fit edilir.
- Model validation/test/blind geçmiş outcome'larıyla yeniden fit edilemez.
- Blind replay outcome'u reveal adımından önce prediction/optimization hattına giremez.
- Aynı uçuşun bütün horizon satırları target `FlightDate` ile aynı partition'da kalır.
- T-24 feature satırı daha geç horizonların feature veya prediction'ını kullanamaz.
- Recovery candidate forecast'i için `produced_at_utc <= recovery_decision_at` olmalıdır.
- Selected candidate horizon, `min{h in {24,18,12,6} | h >= time_to_departure}` kuralıyla eşleşmelidir.
- Recovery kararından sonra üretilen daha yakın forecast'e look-ahead yapılamaz.

Tek bir ihlal `SNAPSHOT_FATAL` kabul edilir; tolerans yoktur.

## 8. Feature kalite kontrolleri

| Kontrol | Koşul |
|---|---|
| Feature schema | Exact `flight-risk-features-v2` |
| Row identity | Her `(flight_instance_id, lead_time_hours)` bir kez |
| Horizon coverage | Her model-eligible uçuş için tam `{24,18,12,6}` |
| Partition grouping | Aynı flight'ın bütün horizonları aynı partition |
| Model input | Sadece allowlist feature'lar |
| Olasılık öncesi numeric | Sonlu; NaN/Inf yok |
| Oranlar | `[0, 1]` |
| History counts | Integer ve `>= 0` |
| Kategorik değer | Train vocabulary veya `__UNKNOWN__` |
| Route | Origin ve destination feature'larıyla tutarlı |
| Smoothed rate | Aynı as-of global prior ve `prior_strength=20` |
| Determinizm | Aynı source/config/code aynı feature hash |

Train'de görülmeyen fakat kaynakta geçerli bir carrier/category, validation/test/blind sırasında `__UNKNOWN__` olur. Bu mapping train-fitted artifact'ta sürümlenir; satır silinmez.

## 9. Distribution ve drift raporu

Snapshot aktivasyonunu otomatik reddetmeyen fakat raporlanması zorunlu metrikler:

- Aylık uçuş ve label sayısı
- Severe disruption prevalence
- Carrier/origin/destination/route cardinality
- Mesafe ve scheduled elapsed quantile'ları
- Unseen category oranı
- Rolling history count dağılımı
- Horizon bazında row count, prevalence ve feature dağılımı
- Feature PSI ve kategorik Jensen-Shannon divergence — validation/test/blind için

Drift eşikleri Phase 3 model evaluation sözleşmesinde release guardrail olarak belirlenir. Phase 2'de drift raporu üretilir fakat metrik sonucu görülerek zaman split'i değiştirilemez.

## 10. Top-20 kontrolü

- Seçim yalnızca TRAIN tarih aralığından yapılır.
- İptal/diversion dahil scheduled operation sayılır.
- Sıralama `total_operations DESC, AirportID ASC` olur.
- Tam 20 benzersiz AirportID bulunmalıdır.
- Dondurulmuş listenin hash'i manifestte bulunmalıdır.
- Validation/test/blind verisi seçim fonksiyonuna giremez.
- Modeling evreninde origin/destination küme dışı satır bulunamaz.

## 11. Split kontrolü

```yaml
TRAIN:
  start: 2024-01-01
  end: 2024-08-31
  first_model_target_date: 2024-02-01
VALIDATION:
  start: 2024-09-01
  end: 2024-10-31
ML_TEST:
  start: 2024-11-01
  end: 2024-11-30
BLIND_REPLAY:
  start: 2024-12-01
  end: 2024-12-31
```

Bir `flight_instance_id` yalnızca bir target partition'da bulunabilir. Partition sınırları config'ten okunur ama v1 contract ile hash'lenir; run-time parametreyle değiştirilemez.

## 12. Snapshot aktivasyon raporu

Aktivasyon raporu en az şunları içerir:

```yaml
report_id: ""
dataset_id: ""
contract_id: bts-reporting-otp-contract-v1
quality_contract_id: cargoopt-data-quality-v2
checks_total: 0
checks_passed: 0
warnings: []
fatal_errors: []
raw_rows: 0
processed_rows: 0
quarantined_rows: 0
exact_duplicates_removed: 0
conflicting_duplicates: 0
feature_rows_by_partition: {}
top20_airport_set_id: ""
schedule_snapshot_sha256: ""
outcome_snapshot_sha256: ""
feature_snapshot_sha256: ""
decision: REJECTED
```

`decision` yalnızca `ACTIVATED` veya `REJECTED` olabilir. Fatal check varken `ACTIVATED` üretilemez. Rapor artifact'ı olmadan snapshot kullanılamaz.

## 13. Test fixture kuralları

Phase 2 testleri için küçük fixture'lar gerçek veri şemasını temsil edebilir. Fixture:

- gerçek kişi veya müşteri bilgisi içermez;
- outcome null ve duplicate edge-case'lerini kapsar;
- expected quarantine reason code taşır;
- tam BTS arşivinden fark edilmeden kopyalanmış büyük veri içermez;
- blind replay outcome'larını geliştirme fixture'ı olarak kullanmaz.

## 14. Değişiklik yönetimi

Kalite eşiğini sonucu geçirmek için düşürmek yasaktır. Eşik, forecast horizon veya as-of seçim kuralı değişikliği yeni contract sürümü, gerekçe, etki analizi, ADR ve insan onayı gerektirir. Blind sonuç görüldükten sonra v2 kalite kuralları değiştirilemez.
