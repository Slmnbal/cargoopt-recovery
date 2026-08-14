# Blind Replay Release ve Politika Karar Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `evaluation-release-gate-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T05` |
| Varsayılan politika | `RETAIN_RISK_BLIND` |

## 1. Amaç

Bu sözleşme blind replay'in geçerli bir deney olup olmadığını, ML-informed sonuç için yeterli operasyonel kanıt bulunup bulunmadığını ve hangi recovery politikasının tutulacağını birbirinden ayırır. ML-informed yöntemin kazanması proje tamamlanma koşulu değildir.

## 2. Gate sonucu

Her gate exact şu statülerden birini alır:

```text
PASS
FAIL
NOT_EVALUABLE
```

`NOT_EVALUABLE`, `PASS` olarak yorumlanamaz. Gate input değeri, denominator, threshold, comparison operator ve evidence artifact hash'i birlikte raporlanır.

## 3. Experiment integrity kapıları

Aşağıdaki gate'lerin tamamı `PASS` olmadan run geçerli blind kanıt değildir:

| Gate ID | PASS koşulu |
|---|---|
| `I01_ROSTER_OUTCOME_BLIND` | Roster builder source/candidate outcome okumamış; access audit temiz |
| `I02_ROSTER_DETERMINISTIC` | Rank hash, destination quota, no-backfill ve roster manifest yeniden üretilebilir |
| `I03_ASOF_ACCESS_VALID` | Bütün history outcome erişimleri `label_available_at <= cutoff` ve target dışı |
| `I04_SHARED_CASE_INPUT` | Üç strategy her case'te exact aynı `input_sha256` kullanmış |
| `I05_PRE_REVEAL_TERMINAL` | Bütün selected case × üç strategy canonical execution/validation reveal öncesi terminal |
| `I06_FREEZE_COMPLETE` | Pre-reveal freeze manifesti tam, canonical ve hash bağlı |
| `I07_REVEAL_AUTHORIZED` | Yetkili reveal freeze'dan sonra ve committed outcome hash'iyle yapılmış |
| `I08_NO_POST_REVEAL_MUTATION` | Primary plan/model/config/metric artifact'ı reveal sonrası değişmemiş |
| `I09_SCHEMA_AND_HASH_INTEGRITY` | Bütün zorunlu schema, contract ve content hash kontrolleri geçmiş |
| `I10_NUMERIC_INTEGRITY` | NaN/Inf/fractional kuruş yok; realized cost reconciliation tam |

Bir integrity gate `FAIL` veya `NOT_EVALUABLE` ise:

```text
run_status = INVALID_EXPERIMENT
policy_decision = NO_DECISION_INVALID_EXPERIMENT
```

Bu durumda etki metriği descriptive audit için hesaplanmış olsa bile blind superiority iddiası kurulamaz.

## 4. Evidence ve operasyonel yeterlilik kapıları

Integrity geçtikten sonra aşağıdaki kapılar exact hesaplanır:

| Gate ID | PASS koşulu |
|---|---|
| `E01_MIN_PAIRED_CASES` | `complete_paired_triggered_count >= 30` |
| `E02_MIN_UNIQUE_DATES` | `unique_paired_dates >= 10` |
| `E03_MIN_DESTINATIONS` | `unique_paired_destinations >= 5` |
| `E04_PLAN_COVERAGE_GREEDY` | Greedy `valid_plan_coverage >= 0.95` |
| `E05_PLAN_COVERAGE_RISK_BLIND` | Risk-blind `valid_plan_coverage >= 0.95` |
| `E06_PLAN_COVERAGE_ML_INFORMED` | ML-informed `valid_plan_coverage >= 0.95` |
| `E07_TRIGGERED_PAIRED_COVERAGE` | `triggered_paired_coverage >= 0.95` |
| `E08_VALIDATOR_GREEDY` | Greedy `emitted_plan_validator_pass_rate == 1.00` |
| `E09_VALIDATOR_RISK_BLIND` | Risk-blind `emitted_plan_validator_pass_rate == 1.00` |
| `E10_VALIDATOR_ML_INFORMED` | ML-informed `emitted_plan_validator_pass_rate == 1.00` |
| `E11_OPTIMAL_RATE_RISK_BLIND` | Risk-blind `optimal_rate >= 0.90` |
| `E12_OPTIMAL_RATE_ML_INFORMED` | ML-informed `optimal_rate >= 0.90` |

Plan coverage ve MILP optimal rate denominator'ı bütün `selected_roster_count`'tır; yalnızca triggered veya başarılı case'lere daraltılmaz. Triggered paired coverage denominator'ı `triggered_count`'tır.

Bir E-gate `FAIL` veya `NOT_EVALUABLE` ise:

```text
run_status = INSUFFICIENT_EVIDENCE
policy_decision = RETAIN_RISK_BLIND
```

Bu sonuç sistemin veya projenin başarısız olduğu anlamına gelmez. Hangi denominator'ın yetersiz olduğu açıkça raporlanır; threshold sonuca göre gevşetilmez.

## 5. Etki kapıları

Integrity ve bütün evidence kapıları geçtikten sonra ML-informed politikanın benimsenmesi için ikisi de zorunludur:

| Gate ID | PASS koşulu |
|---|---|
| `P01_MEAN_COST_IMPROVEMENT` | `aggregate_relative_improvement >= 0.05` |
| `P02_CLUSTER_CI_BELOW_ZERO` | Primary `mean(D)` `%95` cluster bootstrap `ci_upper_kurus < 0` |

`0.05` dahil geçer; CI upper bound exact sıfırsa geçmez. Karşılaştırmalar rounding öncesi decimal değerle yapılır.

İki etki gate'i de `PASS` ise:

```text
run_status = VALID_POSITIVE
policy_decision = ADOPT_ML_INFORMED
```

En az biri `FAIL` veya `NOT_EVALUABLE` ise:

```text
run_status = VALID_NEUTRAL_OR_NEGATIVE
policy_decision = RETAIN_RISK_BLIND
```

## 6. Karar önceliği

Status tek ve deterministik sırayla atanır:

1. Herhangi integrity gate geçmezse `INVALID_EXPERIMENT`.
2. Integrity geçer fakat herhangi evidence/operational gate geçmezse `INSUFFICIENT_EVIDENCE`.
3. Integrity ve evidence geçer, iki impact gate de geçerse `VALID_POSITIVE`.
4. Diğer bütün geçerli sonuçlar `VALID_NEUTRAL_OR_NEGATIVE`.

Bir alt sıradaki olumlu metric üst sıradaki başarısızlığı override edemez.

## 7. İzinli politika kararları

```text
ADOPT_ML_INFORMED
RETAIN_RISK_BLIND
NO_DECISION_INVALID_EXPERIMENT
```

- `ADOPT_ML_INFORMED`: Yalnızca bu blind replay scope'unda varsayılan recovery optimization policy'si olarak önerilir; canlı operasyon onayı değildir.
- `RETAIN_RISK_BLIND`: ML-informed kazanmadığında veya kanıt yetersiz olduğunda güvenli varsayılandır.
- `NO_DECISION_INVALID_EXPERIMENT`: Deney bütünlüğü bozulduğunda mevcut politika hakkında bu run'dan karar çıkarılmaz.

Greedy hiçbir durumda default policy olarak otomatik benimsenmez. Greedy'nin daha iyi görünmesi analiz ve model/OR inceleme bulgusudur; yeni politika kararı ayrı görev/onay gerektirir.

## 8. Sonuç dili

| Run status | İzinli kısa sonuç |
|---|---|
| `VALID_POSITIVE` | “Dondurulmuş blind replay koşullarında ML-informed MILP için benimseme kapıları geçti.” |
| `VALID_NEUTRAL_OR_NEGATIVE` | “Deney geçerliydi; ML-informed benimseme kapılarını geçmedi, risk-blind korundu.” |
| `INSUFFICIENT_EVIDENCE` | “Deney bütünlüğü korundu fakat önceden tanımlı kanıt/operasyon eşikleri karşılanmadı.” |
| `INVALID_EXPERIMENT` | “Blind deney bütünlüğü sağlanamadı; politika kararı üretilmedi.” |

Şu ifadeler yasaktır:

- “Turkish Cargo'da `%X` tasarruf sağlandı.”
- “ML alarm modeli doğru uçuşları buldu.”
- “Nedensel operasyon etkisi kanıtlandı.”
- `FEASIBLE_TIMEOUT` planları için “optimal”.
- Planned lateness için “gerçekleşen teslimat SLA'sı”.

Doğru maliyet nitelemesi:

> Açık BTS yolcu uçuş outcome'ları ve sentetik kargo üzerinde nominal 2024 TL deney maliyeti; gerçek Turkish Cargo verisi veya finansal etkisi değildir.

## 9. Approval ve publish sınırı

Evaluation engine yalnızca önerilen `run_status` ve `policy_decision` artifact'ını üretir. Politika artifact'ının `APPROVED` hale gelmesi insan onayı gerektirir. Model registry, API/UI veya sonraki faz kendiliğinden değiştirilemez.

İnsan, geçmeyen gate'i override ederek `ADOPT_ML_INFORMED` veremez. Böyle bir iş kararı alınırsa blind replay sonucu dışında ayrı, açıkça nitelendirilmiş karar olmalıdır.

## 10. Değişiklik yönetimi

Gate listesi, threshold, denominator, karşılaştırma operatörü, status önceliği veya policy mapping değişirse yeni contract sürümü, ADR, etki analizi ve açık insan onayı gerekir. Outcome görüldükten sonra `evaluation-release-gate-v1` geriye dönük ayarlanamaz.
