# TRY Maliyet ve Objective Sözleşmesi

| Alan | Değer |
|---|---|
| Policy kimliği | `cost-policy-try-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T03` |
| Para birimi | `TRY` |
| Maliyet temeli | `SYNTHETIC_NOMINAL_2024` |
| Hassasiyet | `0.01 TRY` |

## 1. Finansal dürüstlük

Bu tutarlar matematiksel optimizasyon davranışını kontrollü biçimde karşılaştırmak için seçilmiş sentetik katsayılardır. Gerçek THY/Turkish Cargo maliyeti, fiyatı, cezası, tarifesi, tasarrufu veya bütçesi değildir. KDV hariç kabul edilir; enflasyon, iskonto, faiz ve döviz dönüşümü uygulanmaz.

Portföy ve UI'da tutar gösterilen her yerde şu niteleme bulunmalıdır:

> Sentetik nominal 2024 TL deney maliyeti; gerçek operasyonel veya finansal veri değildir.

## 2. Dondurulmuş katsayılar

| Cargo | `handling_cost_try` | `delay_cost_per_hour_try` | `disruption_consequence_try` | `unassigned_penalty_try` |
|---|---:|---:|---:|---:|
| `STANDARD` | 500 | 250 | 10.000 | 50.000 |
| `EXPRESS` | 750 | 750 | 30.000 | 150.000 |
| `PHARMA` | 1.250 | 1.250 | 50.000 | 250.000 |

Değerler config'den okunabilir ancak `cost-policy-try-v1` kimliği altında değiştirilemez. Farklı katsayı yeni policy kimliği ve ADR gerektirir.

## 3. Ortak türetilen değerler

Gönderi `s`, aday uçuş `f` için:

```text
lateness_seconds[s,f] = max(
  0,
  candidate_scheduled_arrival_at_utc[f] - delivery_due_at_utc[s]
)
lateness_hours[s,f] = lateness_seconds[s,f] / 3600
delay_cost_try[s,f] = lateness_hours[s,f] × delay_cost_per_hour_try[cargo_type[s]]
```

- Lateness planlanan varışla hesaplanır; gerçekleşmiş varış objective'e giremez.
- Recovery window nedeniyle `0 <= lateness_hours <= 24` invariant'ı zorunludur.
- Negatif lateness maliyet veya ödül üretmez.
- Uygun olmayan shipment–flight çifti için maliyet katsayısı üretilmez; çift eligibility maskesinde yoktur.

## 4. Risk-blind assignment maliyeti

```text
risk_blind_assignment_cost_try[s,f]
  = handling_cost_try[cargo_type[s]]
  + delay_cost_try[s,f]
```

Risk-blind strateji olasılığı objective katsayısında kullanmaz. Bununla birlikte adil paired karşılaştırma ve snapshot bütünlüğü için aynı immutable prediction batch final OR input içinde bulunur.

## 5. ML-informed assignment maliyeti

Immutable prediction batch'teki kalibre olasılık:

```text
p[f] = severe_disruption_probability[f], 0 <= p[f] <= 1
expected_disruption_cost_try[s,f]
  = p[f] × disruption_consequence_try[cargo_type[s]]

ml_informed_assignment_cost_try[s,f]
  = risk_blind_assignment_cost_try[s,f]
  + expected_disruption_cost_try[s,f]
```

`p[f]`, `flight-severe-disruption-prediction-v2` sözleşmesine göre recovery kararında mevcut `T-24/T-18/T-12/T-6` ceiling horizon forecast'idir. `produced_at_utc > recovery_decision_at` olan bir olasılıkla cost matrix üretilemez.

Risk-blind ile ML-informed arasındaki kontrollü tek business-objective farkı `expected_disruption_cost_try` terimidir. Constraint, shipment, candidate, kapasite, cost policy ve unassigned penalty aynıdır.

Olasılık eksik, duplicate, NaN, sonsuz, `[0,1]` dışında veya batch `frozen != true` ise hiçbir strateji çalıştırılmaz.

## 6. UNASSIGNED maliyeti ve dominance kanıtı

Gönderi atanmamışsa yalnızca sınıfın `unassigned_penalty_try` değeri uygulanır; handling, delay veya expected disruption ayrıca eklenmez.

Recovery penceresinin 24 saatlik üst sınırı ve `p <= 1` altında olası en yüksek ML-informed assignment maliyeti:

| Cargo | Üst sınır formülü | Maksimum | Unassigned | Dominance |
|---|---:|---:|---:|---:|
| `STANDARD` | `500 + 24×250 + 10.000` | 16.500 | 50.000 | Sağlanır |
| `EXPRESS` | `750 + 24×750 + 30.000` | 48.750 | 150.000 | Sağlanır |
| `PHARMA` | `1.250 + 24×1.250 + 50.000` | 81.250 | 250.000 | Sağlanır |

Zorunlu invariant:

```text
unassigned_penalty_try[c]
  > handling_cost_try[c]
  + 24 × delay_cost_per_hour_try[c]
  + disruption_consequence_try[c]
```

Bu kural, uygun ve kapasitesi bulunan atamayı maliyet açısından `UNASSIGNED` seçeneğinden daha iyi yapar. Hard constraint ihlalini yine de haklı çıkarmaz.

## 7. MILP objective

`x[s,f]` uygun çifte atama binary değişkeni, `u[s]` unassigned binary değişkenidir.

Risk-blind:

```text
minimize
  sum(risk_blind_assignment_cost_try[s,f] × x[s,f])
  + sum(unassigned_penalty_try[cargo_type[s]] × u[s])
```

ML-informed:

```text
minimize
  sum(ml_informed_assignment_cost_try[s,f] × x[s,f])
  + sum(unassigned_penalty_try[cargo_type[s]] × u[s])
```

Birincil objective'e gizli weight, normalize edilmiş skor veya açıklanmamış penalty eklenemez.

## 8. Blind replay gerçekleşen maliyet

Assignment dondurulduktan sonra outcome katmanından `y[f] = severe_disruption[f]` okunabilir:

```text
realized_assignment_cost_try[s,f]
  = handling_cost_try[cargo_type[s]]
  + delay_cost_try[s,f]
  + y[f] × disruption_consequence_try[cargo_type[s]]
```

Gerçekleşen toplam maliyet, seçilen assignment'ların realized maliyeti ile unassigned penalty toplamıdır. `y[f]`, plan oluşturulurken veya candidate eligibility belirlenirken kullanılamaz.

Kaynak uçuşun gerçekleşen aksama maliyeti bütün stratejiler için ortak sunk term olduğundan strateji objective'ine eklenmez. Raporlanacaksa ayrı `common_source_event_cost` olarak ve karşılaştırma farkını etkilemeden gösterilir.

## 9. Sayısal ve yuvarlama kuralları

- Girdi katsayıları decimal `0.01 TRY` hassasiyetinde saklanır.
- `lateness_seconds` integer'dır; saat dönüşümü exact decimal division olarak yapılır.
- Türetilen cost `ROUND_HALF_UP` ile iki ondalığa yuvarlanır.
- NaN ve infinity yasaktır.
- Solver'a verilen katsayı ile raporlanan katsayı aynı canonical cost matrix'ten gelir.
- Eşit optimal business objective durumunda epsilon eklenmez; ileride solver sözleşmesi iki aşamalı deterministic tie-break tanımlamalıdır.

## 10. Kapsam dışı maliyetler

v1 objective şunları içermez:

- yakıt, ekip, bakım veya filo maliyeti
- ULD packing veya tehlikeli madde maliyeti
- çok bacaklı transfer maliyeti
- dinamik fiyat, gelir veya müşteri lifetime value
- karbon maliyeti
- gerçek sözleşme cezası
- döviz veya enflasyon

Yeni maliyet terimi yeni policy sürümü, boyut/birim analizi, dominance kontrolü, sensitivity planı, ADR ve insan onayı gerektirir.
