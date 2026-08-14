# Bağımsız Plan Validation Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `plan-validator-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T04` |
| Input | `or-input-v1` + `or-output-v1` plan |
| Yetki | Feasibility, integrity ve cost doğrulaması |

## 1. Amaç

Validator, greedy veya MILP tarafından üretilmiş planın input snapshot ile gerçekten uyumlu olduğunu bağımsız yeniden hesaplar. Solver'ın veya planner'ın “feasible/optimal” iddiasına güvenmez.

Validator optimalite kanıtlamaz, planı iyileştirmez, assignment seçmez ve solver status'u yükseltmez. `VALID`, yalnızca sözleşme kapsamındaki bütün structural, domain, capacity ve cost kontrollerinin geçtiğini söyler.

## 2. Bağımsızlık sınırı

Validator:

- Pyomo model, variable, constraint, expression veya result object import edemez;
- HiGHS state, model state, incumbent vector veya solver memory okuyamaz;
- planner'ın eligibility/cost summary sonucuna güvenemez;
- aynı domain/cost contract'ını saf input alanlarından yeniden uygular;
- yalnızca immutable OR input JSON, plan JSON ve gerekiyorsa solver execution JSON okur;
- kendi code SHA, contract ID ve validation runtime'ını raporlar.

Domain kuralları ortak, saf ve solver'dan bağımsız bir library'de uygulanabilir; optimizer'a ait model-builder fonksiyonları çağrılamaz.

## 3. Validator status enum'u

```text
VALID
INVALID
NOT_APPLICABLE_NO_PLAN
ERROR
```

| Status | Anlam |
|---|---|
| `VALID` | Bütün zorunlu checks geçti; violation yok |
| `INVALID` | En az bir contract violation bulundu |
| `NOT_APPLICABLE_NO_PLAN` | Execution status plan yayımlamaya izin vermedi |
| `ERROR` | Validator kendi çalışmasını güvenilir tamamlayamadı |

`ERROR`, `VALID` veya `INVALID` yerine varsayılan kabul edilemez. Validation raporu yoksa plan publish edilemez.

## 4. Validation girdileri

Zorunlu:

- exact OR input snapshot bytes ve SHA-256;
- plan artifact ve SHA-256;
- plan strategy;
- cost policy ve cost matrix contract;
- mathematical model contract;
- solver execution artifact — yalnızca MILP için;
- greedy execution trace — yalnızca greedy için.

Input/plan hash veya contract version eşleşmiyorsa diğer business checks çalışsa bile sonuç `INVALID` olur.

## 5. Check sırası

Checks fail-fast değildir; güvenli biçimde mümkün olan bütün ihlaller tek raporda toplanır. Ancak schema okunamıyor veya hash güvenilmezse dependent checks `SKIPPED_DEPENDENCY` olarak işaretlenir ve status `INVALID`/`ERROR` olur.

Sıra:

1. Artifact parse ve schema
2. Contract/version ve hash binding
3. ID/cardinality
4. Assignment completeness
5. Domain eligibility
6. Weight/volume capacity
7. Cost coefficient ve summary reconciliation
8. Strategy-specific kurallar
9. Execution/status tutarlılığı
10. Canonical output ve report hash

## 6. Schema ve artifact bütünlüğü

Validator:

- input `or-input-v1`, output `or-output-v1` olmalı;
- bilinmeyen alan olmamalı;
- `case_id`, `input_snapshot_id`, `input_sha256`, model/cost/eligibility hash'leri eşleşmeli;
- plan ID ve content hash canonical serialization'dan yeniden hesaplanmalı;
- plan timestamp'i hash materyaline dahil değilse schema kuralına uymalı;
- outcome alanı planning artifact'larında bulunmamalı;
- NaN, infinity, naive datetime veya fractional kuruş bulunmamalı

kontrollerini yapar.

## 7. Assignment completeness

Her input shipment için plan içinde exact bir decision row bulunmalıdır.

```text
input_shipment_ids == plan_decision_shipment_ids
```

Her row:

- `ASSIGNED` ise exact bir `flight_id` taşır;
- `UNASSIGNED` ise `flight_id` null taşır;
- iki state dışında değer taşımaz;
- aynı shipment için duplicate değildir;
- inputta olmayan shipment veya flight içermez.

Missing row “unassigned varsayımıyla” tamamlanamaz.

## 8. Eligibility yeniden hesaplama

Her `ASSIGNED` pair için validator OR inputtan yeniden:

- source flight'tan farklı candidate;
- case/origin/destination eşleşmesi;
- direct flight;
- recovery window;
- `departure >= ready_at + handling`;
- PHARMA için `requires_cold_chain` ve `cold_chain_capable`;
- valid candidate prediction ve latest-available horizon;
- positive capacity

kontrollerini yapar.

Planner'ın pair'i “eligible” etiketlemesi kanıt değildir. Tek bir uygunsuz assignment bütün planı `INVALID` yapar.

## 9. Capacity reconciliation

Her flight için plan decision row'larından:

```text
recomputed_weight_kg[f] = sum(weight_kg[s] for assigned s to f)
recomputed_volume_m3[f] = sum(volume_m3[s] for assigned s to f)
```

hesaplanır.

- Weight bir ondalık, volume üç ondalık exact decimal arithmetic kullanır.
- `recomputed_weight_kg <= capacity_weight_kg` olmalıdır.
- `recomputed_volume_m3 <= capacity_volume_m3` olmalıdır.
- Plan `flight_loads` değerleri recomputed değerlerle exact eşleşmelidir.
- Utilization display oranı karar için kullanılmaz; doğrulama capacity ve load decimal değerleriyle yapılır.
- Negatif residual veya yuvarlama toleransıyla constraint geçirme yasaktır.

## 10. Cost reconciliation

Validator `cost-policy-try-v1` ile her decision row'un maliyetini yeniden hesaplar.

ASSIGNED için:

```text
risk-blind:
  handling_kurus + delay_kurus

ML-informed:
  handling_kurus + delay_kurus + expected_disruption_kurus
```

UNASSIGNED için:

```text
unassigned_penalty_kurus
```

Kurallar:

- TRY yalnızca canonical Decimal üzerinden `×100` integer kuruşa çevrilir.
- Per-row handling, delay, expected risk, unassigned ve total değerleri exact eşleşir.
- Plan cost summary, per-row integer kuruş toplamıyla exact eşleşir.
- Risk-blind ve greedy için expected disruption cost exact `0` olmalıdır.
- ML-informed expected risk, selected immutable probability ve consequence ile yeniden hesaplanır.
- Outcome/realized cost planning planında bulunamaz.
- Bir kuruş fark dahi `COST_RECONCILIATION_MISMATCH` olur; tolerance yoktur.

## 11. Strategy-specific kontroller

### 11.1 Greedy

Validator veya ayrı saf baseline verifier:

- shipment sort key'i;
- candidate sort key'i;
- her adım öncesi residual capacities;
- seçilen ilk feasible candidate;
- unassigned kararı

ile greedy trace'i yeniden oynatır. Feasible fakat deterministic greedy algoritmasının seçmeyeceği plan `GREEDY_REPLAY_MISMATCH` ile invalid olur.

### 11.2 MILP

Validator:

- plan strategy ile cost column seçiminin eşleşmesini;
- model/eligibility/cost matrix hash binding'ini;
- execution status ve `plan_emitted` tutarlılığını;
- plan primary objective ile recomputed objective eşleşmesini

kontrol eder.

Validator HiGHS optimality proof veya dual bound'u yeniden çözmez. `OPTIMAL` kelimesinin doğruluğu solver execution contract'ının status evidence kontrolüne dayanır; validator sadece evidence alanlarının mevcut/tutarlı olduğunu kontrol eder.

## 12. Solver status tutarlılığı

| Solver status | Plan beklenir | Validator sonucu |
|---|---:|---|
| `OPTIMAL` | Evet | Tam checks |
| `FEASIBLE_TIMEOUT` | Evet | Tam checks; status korunur |
| `INFEASIBLE` | Hayır | `NOT_APPLICABLE_NO_PLAN` |
| `NO_SOLUTION_TIMEOUT` | Hayır | `NOT_APPLICABLE_NO_PLAN` |
| `ERROR` | Hayır | `NOT_APPLICABLE_NO_PLAN` |

No-plan status yanında plan bulunursa `UNEXPECTED_PLAN_FOR_STATUS` ile invalid audit event oluşur. Plan status varken plan bulunmazsa `MISSING_PLAN_FOR_STATUS` olur.

## 13. Violation reason code'ları

Exact ve benzersiz kodlar:

```text
INPUT_SCHEMA_MISMATCH
OUTPUT_SCHEMA_MISMATCH
CONTRACT_VERSION_MISMATCH
INPUT_HASH_MISMATCH
PLAN_HASH_MISMATCH
MODEL_HASH_MISMATCH
ELIGIBILITY_HASH_MISMATCH
COST_MATRIX_HASH_MISMATCH
UNKNOWN_SHIPMENT
UNKNOWN_FLIGHT
DUPLICATE_SHIPMENT_DECISION
MISSING_SHIPMENT_DECISION
INVALID_ASSIGNMENT_STATE
INVALID_FLIGHT_NULLABILITY
INELIGIBLE_ASSIGNMENT
TIME_WINDOW_VIOLATION
DESTINATION_VIOLATION
COLD_CHAIN_VIOLATION
WEIGHT_CAPACITY_EXCEEDED
VOLUME_CAPACITY_EXCEEDED
FLIGHT_LOAD_RECONCILIATION_MISMATCH
COST_RECONCILIATION_MISMATCH
STRATEGY_COST_COLUMN_MISMATCH
GREEDY_REPLAY_MISMATCH
PREDICTION_BINDING_MISMATCH
FUTURE_PREDICTION_USED
OUTCOME_FIELD_PRESENT
NONFINITE_VALUE
FRACTIONAL_KURUS
UNEXPECTED_PLAN_FOR_STATUS
MISSING_PLAN_FOR_STATUS
SOLVER_EVIDENCE_MISMATCH
NONCANONICAL_OUTPUT
```

Violation en az code, entity type, entity ID, field, expected, actual ve safe message taşır. Büyük/sensitive raw payload rapora kopyalanmaz.

## 14. Validation raporu

En az:

- `validation_report_id`;
- validator contract/code version ve code SHA;
- input/plan/execution ID ve hash'leri;
- strategy;
- status;
- started/finished UTC ve runtime;
- checks total/passed/failed/skipped;
- violation listesi;
- recomputed shipment/assignment/unassigned counts;
- flight capacity reconciliation summary;
- recomputed cost summary kuruş;
- report content SHA-256

taşır.

`VALID` için:

```text
failed_checks == 0
violations == []
recomputed_total_cost_kurus == plan_total_cost_kurus
```

zorunludur.

## 15. Publish kapısı

Plan yalnızca:

```text
plan exists
AND execution status in {HEURISTIC_FEASIBLE, OPTIMAL, FEASIBLE_TIMEOUT}
AND validation status == VALID
AND validation.plan_hash == plan.content_hash
```

ise API/UI/backtest tüketimine açılabilir.

Invalid plan overwrite edilmez; plan ve validation report audit için immutable tutulur. Publishability, immutable planın içine sonradan yazılmaz; validation report içindeki `publishable=false` ve publish gate sonucu üzerinden belirlenir.

## 16. Değişiklik koşulu

Validator independence, check seti, decimal tolerance, reason code, status veya publish gate değişirse yeni contract sürümü, failure-mode analizi, ADR ve açık insan onayı gerekir.
