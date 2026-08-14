# İkincil Sensitivity Analysis Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `evaluation-sensitivity-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T06` |
| Rol | Secondary, pre-registered, non-release |
| Tasarım | One-factor-at-a-time (`OFAT`) |

## 1. Amaç ve kesin yetki sınırı

Bu sözleşme, primary blind replay tamamlandıktan sonra ML-informed ile risk-blind MILP arasındaki maliyet yönünün iki sentetik varsayım ailesine karşı nasıl değiştiğini betimlemek için küçük ve dondurulmuş bir robustness çalışması tanımlar.

Sensitivity sonucu:

- primary `evaluation_run_id`, `run_status`, `policy_decision`, gate veya `%95` CI değerini değiştiremez;
- `ADOPT_ML_INFORMED` kararı üretemez veya geçmeyen bir release gate'i override edemez;
- yeni primary experiment, nedensel analiz veya gerçek maliyet çalışması değildir;
- cost/capacity ayarlamak için outcome'dan öğrenme veya grid arama yapamaz.

Primary release kararı her zaman `evaluation-release-gate-v1` çıktısıdır. Sensitivity yalnız ayrı bir `sensitivity_run_id` ile descriptive appendix üretir.

## 2. Çalışma önkoşulları

Sensitivity yalnız aşağıdaki koşulların tamamında başlayabilir:

1. Primary run'ın experiment integrity gate'leri `PASS` ve `run_status != INVALID_EXPERIMENT` olmalıdır.
2. Primary roster, triggered cohort, dataset, outcome snapshot ve bütün base artifact hash'leri immutable olmalıdır.
3. Bu sözleşme ve dört non-baseline scenario full outcome reveal'dan önce freeze manifestine commit edilmiş olmalıdır.
4. Triggered case ID listesi outcome custodian tarafından hash bağlı, read-only bir authorization artifact'ı olarak planner'a verilmelidir.
5. Sensitivity planner'ın source veya candidate outcome tablosuna erişimi olmamalıdır.

Primary `INSUFFICIENT_EVIDENCE` veya `VALID_NEUTRAL_OR_NEGATIVE` olsa bile descriptive sensitivity çalıştırılabilir; sonuç primary status'u yükseltemez.

## 3. Popülasyon ve stratejiler

Population, primary selected roster içinden reveal sonrası oluşturulan exact `TRIGGERED` cohort'tur. `NOT_TRIGGERED` veya source outcome'u `UNKNOWN` case eklenemez. Outcome'a göre yeni source, destination veya candidate seçilemez.

Yalnız şu iki strateji çalıştırılır:

```text
RISK_BLIND_MILP
ML_INFORMED_MILP
```

Greedy sensitivity kapsamı dışındadır. İki MILP aynı scenario-adjusted input hash'i, shipment'ları, candidate'ları, predictions'ı, variable/constraint setini, HiGHS options'ını ve validator'ı kullanır. Tek kontrollü business-objective farkı primary contract'taki expected disruption cost terimi olarak kalır.

## 4. Dondurulmuş scenario kataloğu

Primary baseline yeniden solve edilmez; dondurulmuş primary artifact'lardan referans olarak okunur.

| Scenario ID | Factor | Multiplier | Değişen alan | Sabit kalanlar |
|---|---|---:|---|---|
| `SENS-RISK-075` | `DISRUPTION_CONSEQUENCE` | `0.75` | Üç cargo class için disruption consequence | Capacity ve diğer cost'lar |
| `SENS-RISK-125` | `DISRUPTION_CONSEQUENCE` | `1.25` | Üç cargo class için disruption consequence | Capacity ve diğer cost'lar |
| `SENS-CAPACITY-090` | `AVAILABLE_CAPACITY` | `0.90` | Her candidate weight ve volume capacity | Bütün cost'lar |
| `SENS-CAPACITY-110` | `AVAILABLE_CAPACITY` | `1.10` | Her candidate weight ve volume capacity | Bütün cost'lar |

Exact non-baseline scenario count `4`'tür. Başka multiplier, interpolation, joint grid, random scenario, outcome-temelli scenario veya adaptive search eklenemez.

## 5. Disruption consequence overlay

Cargo class `c` için:

```text
scenario_disruption_consequence_try[c]
  = ROUND_HALF_UP(
      base_disruption_consequence_try[c] × scenario_multiplier,
      0.01 TRY
    )
```

Solver coefficient'i exact `TRY × 100` integer kuruştur. Handling, planned delay cost ve unassigned penalty `cost-policy-try-v1` değerlerinde kalır.

Scenario başlamadan şu dominance invariant'ı üç cargo class için tekrar kanıtlanır:

```text
unassigned_penalty_try[c]
  > handling_cost_try[c]
  + 24 × delay_cost_per_hour_try[c]
  + scenario_disruption_consequence_try[c]
```

Invariant geçmezse scenario `INVALID_SCENARIO`; multiplier otomatik düzeltilmez.

Realized sensitivity cost, aynı scenario consequence ile hesaplanır:

```text
realized_assignment_cost_try[s,f,q]
  = base_handling_cost_try[c]
  + base_planned_delay_cost_try[s,f]
  + y[f] × scenario_disruption_consequence_try[c]
```

## 6. Available capacity overlay

Candidate `f` için base canonical decimal capacity'ler ayrı ayrı ölçeklenir:

```text
scenario_weight_capacity_kg[f]
  = ROUND_FLOOR(base_weight_capacity_kg[f] × multiplier, 0.1 kg)

scenario_volume_capacity_m3[f]
  = ROUND_FLOOR(base_volume_capacity_m3[f] × multiplier, 0.001 m3)
```

- Sonuç pozitif olmalıdır.
- Shipment, cargo mix, cold-chain, SLA, schedule, candidate, probability ve cost alanları değişmez.
- Capacity yeniden random üretilmez; generator seed ilerletilmez.
- Her strategy exact aynı scenario capacity snapshot'ını kullanır.
- Capacity toplamı scenario manifestinde base ve adjusted olarak ayrı reconcile edilir.

Capacity scenario realized cost'u base `cost-policy-try-v1` ile hesaplanır.

## 7. Kesin sabitler

Sensitivity sırasında şunlar değiştirilemez:

- source roster, triggered cohort ve destination listesi;
- shipment count, cargo mix, weight, volume, ready time, SLA veya cold-chain;
- candidate seti, schedule ve recovery penceresi;
- model, calibration veya candidate probability;
- handling, planned delay ve unassigned penalty katsayıları;
- constraint, variable, eligibility veya solver options;
- timeout, gap, seed, thread veya validator kuralları;
- primary pairing, bootstrap, threshold veya policy mapping.

## 8. Outcome izolasyonlu execution sırası

Her scenario şu sırayla çalışır:

1. Base triggered case ID/hash ve scenario catalog doğrulanır.
2. Outcome erişimi olmayan sensitivity input builder scenario overlay'i üretir.
3. İki MILP aynı adjusted input üzerinde bağımsız çalışır; warm start paylaşılmaz.
4. Plan ve execution artifact'ları `highs-execution-v1` ile normalize edilir.
5. Planlar `plan-validator-v1` ile validate edilir.
6. Scenario plan manifesti canonicalize edilip dondurulur.
7. Yalnız freeze sonrasında evaluation runner committed candidate outcome'larını join eder.
8. Realized scenario cost ve descriptive metrikler hesaplanır.

Planner erişim logunda `Cancelled`, `Diverted`, `ArrDelayMinutes`, `severe_disruption` veya realized cost görülürse scenario ve sensitivity run `INVALID_SENSITIVITY_RUN` olur.

## 9. Pairing ve missingness

Scenario `q` içinde case paired-complete olur yalnızca:

- iki strategy exact aynı adjusted input hash'ini kullanmış;
- iki strategy plan emit etmiş ve validator `VALID` olmuş;
- atanan candidate'ların binary outcome'ları mevcut;
- scenario realized cost reconciliation geçmiş

ise.

`FEASIBLE_TIMEOUT + VALID` plan pairing'e girebilir ancak optimal diye sunulamaz. Her scenario için triggered count, paired-complete count, paired coverage, strategy status dağılımı ve exclusion reason count raporlanır. Eksik case sessizce denominator dışına atılamaz.

## 10. Descriptive metrikler

Paired-complete case `i`, scenario `q` için:

```text
D_i_q_kurus
  = realized_cost_ml_informed_i_q_kurus
  - realized_cost_risk_blind_i_q_kurus
```

Her scenario şu çıktıları verir:

- paired case count ve coverage;
- iki strategy için total/mean/median realized cost;
- `mean(D_q)`, `median(D_q)` ve total difference;
- aggregate relative improvement;
- unassigned shipment count/rate;
- `OPTIMAL`, `FEASIBLE_TIMEOUT`, no-plan ve error dağılımı;
- validator pass rate;
- direction flag.

Direction flag:

```text
FAVORS_ML
  if mean(D_q) < 0 AND aggregate_relative_improvement > 0

FAVORS_RISK_BLIND
  if mean(D_q) > 0 AND aggregate_relative_improvement < 0

MIXED_OR_TIED
  otherwise
```

Primary baseline ile dört scenario tek robustness tablosunda gösterilir. Bootstrap, CI, p-value, yeni release threshold veya “robust adoption score” hesaplanmaz.

## 11. Output ve iddia politikası

Sensitivity output en az:

- `sensitivity_run_id` ve content SHA-256;
- primary evaluation run/freeze/outcome hash binding;
- contract ve exact scenario catalog hash'i;
- planner outcome-access audit hash'i;
- scenario başına input/plan/validation manifest hash'leri;
- population, pairing, status, cost ve direction metrikleri;
- exclusion reason'lar;
- `primary_policy_unchanged = true`;
- limitation listesi

taşır.

İzinli sonuç:

> “Önceden tanımlı dört ikincil sentetik senaryoda ML-informed ve risk-blind maliyet yönünün nasıl değiştiği raporlandı; primary blind politika kararı değiştirilmedi.”

Gerçek maliyet, canlı operasyon, nedensel etki veya Turkish Cargo tasarrufu iddiası yapılamaz.

## 12. Hata ve status sözleşmesi

Sensitivity run status:

```text
VALID_DESCRIPTIVE
PARTIAL_DESCRIPTIVE
INVALID_SENSITIVITY_RUN
NOT_RUN_PRIMARY_INVALID
```

- Dört scenario tam ve valid ise `VALID_DESCRIPTIVE`.
- Integrity korunmuş fakat scenario execution/missingness nedeniyle bazı sonuçlar eksikse `PARTIAL_DESCRIPTIVE`.
- Outcome leakage, post-freeze mutation veya hash/schema ihlalinde `INVALID_SENSITIVITY_RUN`.
- Primary experiment invalid ise `NOT_RUN_PRIMARY_INVALID`.

Hiçbir status primary policy mapping'i taşıyamaz.

## 13. Değişiklik yönetimi

Population, strategy, factor, multiplier, rounding, scenario count, outcome isolation, pairing veya metric değişirse yeni contract sürümü, ADR, compute/scope ve blind-integrity analizi ile açık insan onayı gerekir. Primary outcome görüldükten sonra v1 scenario kataloğu geriye dönük değiştirilemez.
