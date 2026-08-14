# Uçuş Ciddi Aksama Multi-Horizon Tahmin Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `flight-severe-disruption-prediction-v2` |
| Durum | Accepted |
| Feature schema | `flight-risk-features-v2` |
| Label schema | `severe-disruption-label-v1` |
| İlgili görev | `PH0-T03` |
| Önceki sürüm | `flight-severe-disruption-prediction-v1` |

## 1. Tahmin sorusu

Tek model, her uçuş ve izinli lead time için şu olasılığı üretir:

```text
P(severe_disruption = 1 | prediction_cutoff_at anında kullanılabilir feature'lar,
                          lead_time_hours)
```

Çıktı gecikme dakikası değil, tek binary classification olasılığıdır. Source recovery kararı kendi `T-6` anında verilir; 24 saatlik candidate penceresinin tamamında gelecekte üretilmiş skor kullanmamak için tahminler dört sabit ufukta hazırlanır.

## 2. Forecast ladder

İzinli ufuklar:

```text
H = {24, 18, 12, 6} hours
prediction_cutoff_at(f,h) = scheduled_departure_at_utc(f) - h
lead_time_hours = h
```

- Tek bir multi-horizon model kullanılır; horizon başına ayrı model v2 kapsamında yoktur.
- Her uygun uçuş TRAIN, VALIDATION, ML_TEST veya BLIND_REPLAY partition'ında en fazla dört feature satırı üretir.
- Aynı uçuşun dört satırı aynı target partition'da kalır; flight-level split yapılamaz.
- `lead_time_hours` model girdisidir ve yalnızca `6`, `12`, `18`, `24` olabilir.
- Her feature, kendi satırının `prediction_cutoff_at` anına göre as-of hesaplanır.
- T-24 satırı T-6 verisi göremez; horizon satırları birbirlerinin feature veya prediction'ını kullanamaz.

## 3. Recovery kararında candidate skoru seçimi

Kaynak uçuş `s` için:

```text
recovery_decision_at = source_scheduled_departure_at_utc - 6 hours
delta_hours(f) = (candidate_scheduled_departure_at_utc(f) - recovery_decision_at) / 1 hour
```

Candidate case'e yalnızca `0 < delta_hours <= 24` iken girebilir. Kullanılacak horizon:

```text
selected_horizon(f)
  = min { h in H | h >= delta_hours(f) }
selected_prediction_produced_at
  = candidate_scheduled_departure_at_utc(f) - selected_horizon(f)
```

Bu, recovery kararında mevcut olan en yakın forecast'tir.

| Karara göre aday kalkışı | Seçilen horizon | Forecast yaşı |
|---:|---:|---:|
| `(0, 6] saat` | `T-6` | `[0, 6) saat` |
| `(6, 12] saat` | `T-12` | `[0, 6) saat` |
| `(12, 18] saat` | `T-18` | `[0, 6) saat` |
| `(18, 24] saat` | `T-24` | `[0, 6) saat` |

Zorunlu invariant'lar:

```text
selected_prediction_produced_at <= recovery_decision_at
recovery_decision_at - selected_prediction_produced_at < 6 hours
selected_prediction.flight_instance_id == candidate.flight_id
selected_prediction.lead_time_hours == selected_horizon
```

Karar anından sonra üretilmiş daha yakın bir forecast kullanılamaz. “Latest available” seçiminde wall-clock ingest zamanı değil, contract `produced_at = scheduled_departure - horizon` zamanı esas alınır.

## 4. Label

```text
severe_disruption = 1
if Cancelled == 1
   OR Diverted == 1
   OR ArrDelayMinutes >= 60
else 0
```

Label üretim sırası:

1. `Cancelled == 1` ise `1`.
2. Aksi halde `Diverted == 1` ise `1`.
3. Aksi halde sonlu `ArrDelayMinutes >= 60` ise `1`.
4. Aksi halde sonlu `0 <= ArrDelayMinutes < 60` ise `0`.
5. Outcome eksik veya çelişkiliyse `UNKNOWN`; uçuşun hiçbir horizon satırı model/evaluation evrenine giremez.

Target outcome feature matrix, prediction request veya OR planning snapshot'ına giremez.

## 5. Tahmin evreni

Bir uçuş–horizon satırı ancak:

- dataset snapshot `ACTIVE`;
- origin ve destination dondurulmuş top-20 kümesinde ve farklı;
- timezone mapping tekil;
- planlanan kalkış/süre geçerli;
- target tarihi `2024-02-01` veya sonrası;
- horizon izinli enum içinde;
- `flight-risk-features-v2` satırı eksiksiz ve sonlu;
- bütün as-of history kendi cutoff'una göre uygun

ise score edilebilir.

Eksik horizon için `0.0`, `0.5`, prevalence veya komşu horizon olasılığı kopyalanmaz. Gerekli candidate forecast'i yoksa OR batch'i fail-closed reddedilir.

## 6. Partition ve fit politikası

| Partition | Target uçuş tarihi | Yetki |
|---|---|---|
| `TRAIN` | 2024-01-01 — 2024-08-31 | Warm-up; 2024-02-01 sonrası dört horizonla fit |
| `VALIDATION` | 2024-09-01 — 2024-10-31 | Model, calibration ve sınırlı tuning |
| `ML_TEST` | 2024-11-01 — 2024-11-30 | Dondurulmuş değerlendirme |
| `BLIND_REPLAY` | 2024-12-01 — 2024-12-31 | Dondurulmuş karar replay'i |

- Partition, horizon cutoff tarihine değil target `FlightDate` değerine göre belirlenir.
- Aynı `flight_instance_id` bütün horizonlarıyla tek partition'dadır.
- Rastgele row split ve horizon bazında ayrıştırma yasaktır.
- Model/preprocessing yalnızca TRAIN flight'larının horizon satırlarında fit edilir.
- BLIND_REPLAY model, feature, horizon, generator, maliyet, objective veya case seçimi ayarlamak için kullanılamaz.
- Validation/test/blind öncesi outcome yalnızca as-of availability sağlarsa rolling feature'a girebilir; model yeniden fit edilmez.

## 7. Model input sözleşmesi

Tek yetkili liste `docs/ml/FEATURE_AVAILABILITY.yaml` içindeki 27 `derived_features` satırıdır. `flight-risk-features-v1` yerine `flight-risk-features-v2` kullanılır; tek business feature farkı `lead_time_hours` alanıdır.

Teknik metadata, model girdisi değildir:

```text
flight_instance_id
feature_snapshot_id
prediction_cutoff_at
feature_schema_version
dataset_id
top20_airport_set_id
```

Model matrix:

- yalnızca `model_input: true` alanları ve exact kolon sırasını içerir;
- target outcome ve audit-only BTS alanlarını içermez;
- train-fitted preprocessing artifact'ını kullanır;
- NaN, infinity, schema dışı kolon veya bilinmeyen horizon kabul etmez.

## 8. As-of rolling feature sözleşmesi

Her target horizon satırı ve `W ∈ {7,30}` için history ancak:

```text
history.flight_instance_id != target.flight_instance_id
history.scheduled_departure_at_utc < target.prediction_cutoff_at
history.label_available_at <= target.prediction_cutoff_at
history.scheduled_departure_at_utc >= target.prediction_cutoff_at - W days
```

koşullarında kullanılır. Route/origin/destination/carrier oranları aynı cutoff'un global prior'ıyla ve `prior_strength = 20` ile yumuşatılır.

Multi-horizon satırları toplu daily aggregate'e join edilmez; her unique cutoff as-of hesaplanır. Aynı target flight'ın outcome'u hiçbir horizonun history'sine giremez.

## 9. Model adayları

Yalnızca:

1. `DummyClassifier`
2. `LogisticRegression`
3. `XGBoost binary classifier`

karşılaştırılır. Üçü de aynı multi-horizon matrix'i ve `lead_time_hours` feature'ını kullanır. Horizon başına model, transformer, tabular neural network veya ensemble yeni kapsam/ADR/onay gerektirir.

## 10. Calibration

Validation üzerinde tek global calibrator için calibration yok, sigmoid/Platt ve isotonic karşılaştırılır. Calibration TRAIN fit + VALIDATION seçim akışına uyar.

Global ve ayrı ayrı `T-24`, `T-18`, `T-12`, `T-6` Brier, ECE ve reliability sonuçları raporlanır. Bir horizon kabul guardrail'ini karşılamıyorsa komşu horizon skoru kopyalanmaz ve model `ACTIVE` olamaz; horizon-specific calibrator otomatik eklenmez.

## 11. Değerlendirme metrikleri

Global ve horizon bazında:

- PR-AUC
- ROC-AUC
- Brier score
- log loss
- expected calibration error
- reliability diagram
- precision, recall, F1
- confusion matrix
- prevalence
- batch latency ve throughput

raporlanır. Accuracy tek başına seçim yaptırmaz. OR threshold değil sürekli kalibre olasılık kullanır.

Aynı uçuşun dört satırı bağımsız örnek gibi güven aralığını yapay daraltamaz; bootstrap veya confidence interval hesapları flight-level cluster üzerinden yapılır.

## 12. Forecast artifact

Her uçuş–horizon forecast satırı:

```json
{
  "prediction_record_id": "...",
  "flight_instance_id": "...",
  "lead_time_hours": 12,
  "produced_at_utc": "2024-12-10T00:00:00Z",
  "feature_snapshot_id": "...",
  "feature_schema_version": "flight-risk-features-v2",
  "model_version": "cargoopt-risk-xgb-2.0.0",
  "calibration_version": "isotonic-2.0.0",
  "severe_disruption_probability": 0.73
}
```

```text
prediction_record_id = SHA-256(
  flight_instance_id | lead_time_hours | feature_snapshot_id |
  model_version | calibration_version
)
```

- `(flight_instance_id, lead_time_hours, model_version, calibration_version)` benzersizdir.
- `produced_at_utc = scheduled_departure_at_utc - lead_time_hours` olmalıdır.
- Olasılık sonlu ve `[0,1]` içinde, en fazla altı ondalıktır.
- Artifact immutable'dır; aynı ID overwrite edilemez.

## 13. OR prediction batch

Recovery decision anında yalnızca Bölüm 3 kuralıyla seçilmiş candidate forecast'leri yeni immutable batch'e assemble edilir:

```json
{
  "prediction_batch_id": "...",
  "recovery_case_id": "...",
  "assembled_at_utc": "...source T-6...",
  "frozen": true,
  "model_version": "cargoopt-risk-xgb-2.0.0",
  "calibration_version": "isotonic-2.0.0",
  "rows": []
}
```

Batch kuralları:

- `assembled_at_utc == recovery_decision_at`;
- her candidate için tam bir satır;
- candidate olmayan satır yok;
- her row `produced_at_utc <= assembled_at_utc`;
- her row seçilen ceiling horizon ile eşleşir;
- row `flight_instance_id` değerleri benzersizdir;
- model/calibration/schema sürümleri batch içinde aynıdır;
- batch immutable ve content SHA-256 ile korunur.

## 14. Hata sözleşmesi

| Kod | Davranış |
|---|---|
| `INVALID_FORECAST_HORIZON` | Feature/prediction satırı reddedilir |
| `FUTURE_PREDICTION_AT_DECISION` | OR batch tamamı reddedilir |
| `WRONG_LATEST_AVAILABLE_HORIZON` | OR batch tamamı reddedilir |
| `MISSING_CANDIDATE_PREDICTION` | Partial batch verilmez; batch reddedilir |
| `DUPLICATE_FLIGHT_PREDICTION` | Batch reddedilir |
| `MIXED_MODEL_VERSION` | Batch reddedilir |
| `FEATURE_SCHEMA_MISMATCH` | Batch reddedilir |
| `FEATURE_NOT_AVAILABLE_AT_CUTOFF` | Forecast üretimi başarısız |
| `PREDICTION_OUT_OF_RANGE` | Contract failure |
| `MODEL_ARTIFACT_MISMATCH` | Forecast üretimi başlamaz |
| `INSUFFICIENT_HISTORY` | Varsayılan risk yazılmaz |

## 15. Tekrar üretilebilirlik ve release

Prediction'ı tekrar üretmek için dataset, feature snapshot, top-20 set, code SHA, feature config, preprocessing, model/calibration hash, dependency lock, random seed ve request kimliği sabitlenir. `latest` etiketiyle release forecast üretilemez.

Model durumları `CANDIDATE`, `VALIDATED`, `ACTIVE`, `REJECTED`, `ARCHIVED`'dır. Leakage, schema, global calibration ve dört horizon raporu geçmeden model `ACTIVE` olamaz. Modelin ACTIVE olması ML-informed OR politikasının kabul edildiği anlamına gelmez; Phase 5 blind kapısı ayrıdır.

## 16. Değişiklik yönetimi

Horizon seti, ceiling seçim kuralı, source T-6 decision, feature listesi, label, availability, smoothing, partition, model ailesi, calibration veya batch schema değişirse yeni contract/schema sürümü ve ADR gerekir. Blind sonuç görüldükten sonra v2 geriye dönük ayarlanamaz.
