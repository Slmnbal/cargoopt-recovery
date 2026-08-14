# ADR-005 — Multi-Horizon As-of Uçuş Riski ve Recovery Batch Seçimi

| Alan | Değer |
|---|---|
| Durum | Accepted |
| Tarih | 2026-08-13 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | PH0-T03 kapsam düzeltmesi |
| Supersedes | ADR-003 içindeki target-flight T-6-only prediction kapsamı |

## Bağlam

ADR-003 her uçuş riskini kendi planlanan kalkışından altı saat önce (`T-6`) üretmek üzere tanımladı. PH0-T03 ise kaynak uçuşun T-6 recovery kararından sonraki 24 saatte kalkacak aday uçuşları değerlendirmektedir.

Örnek:

```text
source recovery decision = 10:00
candidate departure       = 20:00
candidate own T-6         = 14:00
```

Candidate'ın T-6 tahmini recovery kararından dört saat sonra üretilir. Bu skoru 10:00 kararında kullanmak gelecekteki artifact'i geçmişe taşır ve point-in-time leakage yaratır. Candidate'ları ilk altı saatle sınırlamak ise onaylanmış 24 saatlik recovery penceresini anlamsızlaştırır ve gerçekçi alternatif havuzunu daraltır.

## Karar

### 1. Source karar anı korunur

```text
recovery_decision_at = source_scheduled_departure_at_utc - 6 hours
```

Source T-6, projenin karar anıdır. Bu değer değişmez.

### 2. Tek multi-horizon model

Her target uçuş için dört as-of feature snapshot oluşturulur:

```text
H = {24, 18, 12, 6}
prediction_cutoff_at(f,h) = scheduled_departure_at_utc(f) - h
```

- Tek classification modeli kullanılır.
- `lead_time_hours ∈ {24,18,12,6}` 27. model feature'ıdır.
- Horizon başına ayrı model veya calibrator otomatik oluşturulmaz.
- Label `severe-disruption-label-v1` olarak değişmeden kalır.
- As-of rolling history her horizonun kendi cutoff'una göre yeniden hesaplanır.

### 3. Latest-available ceiling seçimi

Recovery kararı ile candidate kalkışı arasındaki süre `delta` olsun:

```text
0 < delta <= 24
selected_horizon = min { h in H | h >= delta }
```

Bu kural:

- 0–6 saatte T-6;
- 6–12 saatte T-12;
- 12–18 saatte T-18;
- 18–24 saatte T-24

forecast'ini seçer. Seçilen skor karar anından sonra üretilmiş olamaz ve karar anında en fazla altı saat eskidir.

### 4. Partition ve evaluation

- Partition target `FlightDate` ile belirlenir; cutoff tarihiyle değil.
- Aynı uçuşun dört horizon satırı aynı partition'da kalır.
- Model/preprocessing yalnızca TRAIN uçuşlarının dört horizon satırında fit edilir.
- Global metriklere ek olarak her horizon için PR-AUC, Brier, ECE ve reliability raporlanır.
- Confidence interval ve bootstrap flight-level cluster kullanır; dört satırı bağımsız uçuş sayamaz.
- Bir horizon release guardrail'ini geçmezse komşu horizon tahmini kopyalanmaz; model ACTIVE olamaz.

### 5. Recovery prediction batch

OR batch, recovery kararında var olan forecast artifact'lerinden assemble edilir:

```text
prediction.produced_at_utc <= recovery_decision_at
prediction.horizon == selected_horizon(candidate)
candidate_flight_ids == prediction_flight_ids
```

Partial, future, duplicate, stale veya mixed-model batch fail-closed reddedilir. Risk-blind strateji olasılık katsayısını sıfır kullansa da paired snapshot bütünlüğü için aynı tam batch'i gerektirir.

## Sürüm etkisi

| Artifact | Önceki | Yeni |
|---|---|---|
| Prediction contract | `flight-severe-disruption-prediction-v1` | `v2` |
| Feature contract | `flight-feature-availability-v1` | `v2` |
| Feature schema | `flight-risk-features-v1` — 26 feature | `v2` — 27 feature |
| Data quality | `cargoopt-data-quality-v1` | `v2` |
| Source decision | T-6 | T-6 — değişmedi |
| Label | severe-disruption v1 | değişmedi |

Henüz uygulama, dataset snapshot, feature artifact veya model oluşturulmadığı için byte/data migration gerekmez. Eski v1 belgeleri tarihsel karar izi olarak korunur; yeni implementation yalnızca v2 sözleşmelerini kullanır.

## Gerekçe

- 24 saatlik candidate penceresi gelecekte üretilmiş skor olmadan korunur.
- Altı saatlik ladder, karar anında forecast yaşını altı saatin altında sınırlar.
- Tek model scope creep'i kontrol eder ve lead-time etkisini öğrenebilir.
- Fixed horizon enum'u eğitim ve serving eşleşmesini test edilebilir yapar.
- Flight-level grouping aynı label'ın dört kez bulunmasından kaynaklanan değerlendirme yanlılığını azaltır.
- Source T-6 kararını korumak önceki proje anlatımı ve operasyon akışını bozmaz.

## Sonuçlar

Olumlu:

- OR candidate olasılıkları point-in-time doğru olur.
- Her candidate için karar anında mevcut tekil forecast seçilebilir.
- Feature lineage horizon düzeyinde izlenebilir.
- Recovery penceresi 24 saat olarak korunur.

Maliyet ve sınırlamalar:

- Feature satır sayısı uygun uçuş başına yaklaşık dört katına çıkar.
- Multi-horizon model calibration'ı horizon bazında ayrıca raporlanmalıdır.
- T-24 performansı T-6'dan zayıf olabilir; bu saklanamaz.
- Altı saatlik discretization, tam continuous as-of scoring değildir.

## Reddedilen alternatifler

- Candidate'ın gelecekte üretilecek T-6 skorunu kullanmak
- Bütün candidate'ları source T-6 anında T-6 modeliyle etiketsiz şekilde score etmek
- Candidate havuzunu yalnızca ilk altı saate daraltmak
- Eksik horizon için `0.5`, prevalence veya komşu skor yazmak
- Her horizon için dört bağımsız model oluşturmak
- Daily batch kullanıp forecast yaşını 24 saatten fazla belirsiz bırakmak
- Candidate outcome'unu risk skoru yerine kullanmak

## Uygulama kapıları

Phase 2/3 başlamadan önce otomatik testler en az şu kanıtları sağlamalıdır:

- dört horizon cutoff formülü;
- aynı flight horizonlarının aynı partition'da kalması;
- T-24 satırında daha geç veri kullanılmaması;
- ceiling horizon sınırları `6`, `12`, `18`, `24` ve epsilon çevresinde;
- `produced_at <= recovery_decision_at`;
- her candidate için exact bir forecast;
- 27 feature'ın exact schema/hash eşleşmesi;
- horizon bazında calibration raporu.

Bu ADR kod, dependency, veri üretimi veya model eğitimini başlatmaz.

## Değişiklik koşulu

Horizon seti, ceiling fonksiyonu, source karar anı, forecast age sınırı, lead-time feature, model sayısı, calibration politikası veya batch selection değişikliği yeni ADR, contract sürümü, leakage analizi ve açık insan onayı gerektirir. Blind sonuç görüldükten sonra v2 geriye dönük ayarlanamaz.
