# Blind Replay Metrik ve İstatistik Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `evaluation-metrics-statistics-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T05` |
| Primary comparison | `ML_INFORMED_MILP - RISK_BLIND_MILP` |
| Bootstrap | Source `FlightDate` cluster, `10.000` tekrar |
| Bootstrap seed | `20240831` |
| Güven düzeyi | `%95` |

## 1. Popülasyonlar ve denominator sözlüğü

Denominator'lar outcome görüldükten sonra sonuç iyileştirmek için değiştirilemez.

| Ad | Exact tanım |
|---|---|
| `eligible_source_count` | Pre-outcome eligibility'yi geçen source sayısı |
| `selected_roster_count` | Deterministik destination kotasıyla seçilen roster sayısı |
| `triggered_count` | Selected roster içinde reveal sonrası source `severe_disruption == 1` sayısı |
| `source_outcome_known_count` | Selected roster içinde source outcome'u `0/1` olan sayısı |
| `valid_plan_count[strategy]` | Selected roster içinde plan emitted ve validator `VALID` olan sayısı |
| `emitted_plan_count[strategy]` | Selected roster içinde plan artifact'ı yayımlayan canonical execution sayısı |
| `optimal_count[strategy]` | MILP stratejisi için selected roster içinde status `OPTIMAL` olan sayısı |
| `complete_paired_triggered_count` | Triggered cohort içinde üç geçerli planı ve gerekli bütün candidate outcome'ları bulunan case sayısı |
| `unique_paired_dates` | Complete paired triggered case'lerin benzersiz source `FlightDate` sayısı |
| `unique_paired_destinations` | Complete paired triggered case'lerin benzersiz destination AirportID sayısı |

`selected_roster_count == 0` ise oranlar `null` olur; sıfırmış gibi sunulmaz. `triggered_count == 0` ise paired metrik ve paired coverage `null` olur.

## 2. Case lifecycle ve complete pairing

Bir triggered case primary paired analize ancak aşağıdaki koşulların tamamıyla girer:

1. Greedy, risk-blind MILP ve ML-informed MILP aynı `input_sha256` değerine bağlıdır.
2. Üç stratejinin canonical execution'ı full reveal öncesi terminal durumdadır.
3. Üç strateji de plan emit etmiştir.
4. Üç planın validation status'u `VALID` ve plan hash binding'i doğrudur.
5. Her stratejinin atadığı her distinct candidate flight için outcome label `0/1` olarak mevcuttur.
6. Realized cost üç strateji için `cost-policy-try-v1` ile yeniden hesaplanmıştır.

Validator `VALID` olan `FEASIBLE_TIMEOUT` planı pairing'e girebilir; solver status'u korunur ve hiçbir raporda optimal olarak adlandırılmaz. `OPTIMAL` oranı ayrıca release gate'te ölçülür.

Bir stratejinin atamadığı candidate'ın outcome'u o stratejinin realized cost'u için gerekli değildir. `UNASSIGNED` decision outcome gerektirmez.

Eksik case sessizce silinmez. Her triggered case exact bir paired inclusion/exclusion reason taşır. `NOT_TRIGGERED` ve `SOURCE_OUTCOME_UNKNOWN` case'ler daha önceki attrition adımlarında raporlanır ve paired reason denominator'ına girmez:

```text
PAIRED_COMPLETE
MISSING_GREEDY_VALID_PLAN
MISSING_RISK_BLIND_VALID_PLAN
MISSING_ML_INFORMED_VALID_PLAN
INPUT_HASH_MISMATCH
MISSING_ASSIGNED_CANDIDATE_OUTCOME
REALIZED_COST_RECONCILIATION_ERROR
```

Her reason'ın sayısı ve case ID listesi raporlanır. Complete-case sonuçları, coverage metriklerinden ayrı sunulur.

## 3. Gerçekleşen sentetik maliyet

Gönderi `s`, atandığı candidate `f`, cargo sınıfı `c` ve reveal sonrası binary outcome `y[f]` için:

```text
planned_lateness_seconds[s,f] = max(
  0,
  candidate_scheduled_arrival_at_utc[f] - delivery_due_at_utc[s]
)

planned_delay_cost_try[s,f]
  = ROUND_HALF_UP(
      planned_lateness_seconds[s,f] / 3600
      × delay_cost_per_hour_try[c],
      0.01 TRY
    )

realized_assignment_cost_try[s,f]
  = handling_cost_try[c]
  + planned_delay_cost_try[s,f]
  + y[f] × disruption_consequence_try[c]
```

`UNASSIGNED` gönderi için:

```text
realized_unassigned_cost_try[s] = unassigned_penalty_try[c]
```

Case toplamı:

```text
realized_case_cost_try[strategy,i]
  = sum(realized_assignment_cost_try for ASSIGNED decisions)
  + sum(realized_unassigned_cost_try for UNASSIGNED decisions)
```

Bütün hesap solver ile aynı canonical `TRY × 100` integer kuruş biriminde yapılır. TRY yalnızca gösterim katmanında iki ondalıkla üretilir. Float accumulation, fractional kuruş, actual arrival time veya actual delay minutes maliyet formülüne giremez. Candidate outcome yalnızca `severe_disruption` binary label'ıdır.

Source event bütün stratejiler için ortak sunk term'dir ve paired farktan çıkarılmıştır. Raporlanırsa `common_source_event_cost` olarak ayrı ve karşılaştırma dışı gösterilir.

## 4. Birincil etki ölçüsü

Complete paired triggered case `i` için:

```text
D_i_kurus
  = realized_case_cost_kurus[ML_INFORMED_MILP,i]
  - realized_case_cost_kurus[RISK_BLIND_MILP,i]
```

İşaret yorumu:

- `D_i < 0`: ML-informed daha düşük maliyet;
- `D_i = 0`: eşit maliyet;
- `D_i > 0`: risk-blind daha düşük maliyet.

Birincil point estimate:

```text
mean_paired_difference_kurus = mean(D_i_kurus)
```

Birincil portföy etki yüzdesi:

```text
aggregate_relative_improvement
  = (
      sum(realized_cost_risk_blind_kurus)
      - sum(realized_cost_ml_informed_kurus)
    )
    / sum(realized_cost_risk_blind_kurus)
```

Payda `<= 0` ise oran `null` ve evidence gate `FAIL` olur. Pozitif oran ML-informed iyileşmesini gösterir. “Ortalama yüzde iyileşme” diye case yüzdelerinin aritmetik ortalaması kullanılmaz.

## 5. Raporlanan paired karşılaştırmalar

| Karşılaştırma | Rol | Çıktı |
|---|---|---|
| ML-informed − risk-blind | Primary inferential | Mean, median, aggregate relative improvement, `%95` cluster CI |
| Risk-blind − greedy | Secondary descriptive | Mean, median, toplam fark |
| ML-informed − greedy | Secondary descriptive | Mean, median, toplam fark |

Secondary karşılaştırmalar için confirmatory superiority, p-value veya multiplicity-adjusted iddia yapılmaz. Birincil karşılaştırma sonuca bakılarak değiştirilemez.

## 6. Deterministik source-date cluster bootstrap

Amaç aynı `FlightDate` içindeki case'lerin bağımlılığını korumaktır. Complete paired triggered dataset'teki benzersiz source tarihleri artan ISO tarih sırasıyla:

```text
G = [g_0, ..., g_(K-1)]
```

olarak dondurulur. `K`, unique paired date sayısıdır.

Her `b ∈ {0,...,9999}` replicate'i için `K` cluster replacement ile çekilir. Her draw `j ∈ {0,...,K-1}` için:

```text
counter = 0
material = UTF8(
  "cluster-bootstrap-v1|20240831|" +
  b + "|" + j + "|" + counter
)
v = unsigned_big_endian_integer(first_8_bytes(SHA-256(material)))
limit = floor(2^64 / K) × K

if v < limit:
    cluster_index = v mod K
else:
    counter = counter + 1 and repeat
```

Bu rejection-sampling adımı modulo bias'ı engeller. Integer alanlar sıfır dolgusu olmadan base-10 ASCII yazılır.

Seçilen her date cluster'ın bütün complete paired case'leri replicate'e eklenir; aynı date tekrar çekilirse bütün case'leri tekrar eklenir. Replicate statistic case-weighted'dır:

```text
bootstrap_mean_D[b]
  = sum(replicated D_i_kurus) / replicated_case_count
```

Date cluster'lar eşit olasılıkla çekilir; son aggregate'te her case kendi satırı kadar ağırlık taşır. Destination veya shipment düzeyinde ayrıca resampling yapılmaz.

## 7. `%95` percentile güven aralığı

`10.000` bootstrap mean değeri artan sıralanır. Quantile exact R-7 linear interpolation kullanır:

```text
h = (B - 1) × q
lo = floor(h)
hi = ceil(h)
Q(q) = values[lo] + (h - lo) × (values[hi] - values[lo])
```

```text
ci_lower_kurus = Q(0.025)
ci_upper_kurus = Q(0.975)
```

CI yalnızca primary `mean(D)` içindir. Bir kuruştan küçük ara CI değeri raporda decimal kuruş olarak saklanabilir; release karşılaştırması rounding öncesi exact decimal değerle yapılır. P-value hesaplanmaz veya CI'dan türetilmez.

## 8. Operasyonel kalite ve coverage metrikleri

Her strategy için:

```text
valid_plan_coverage
  = valid_plan_count[strategy] / selected_roster_count

emitted_plan_validator_pass_rate
  = valid_emitted_plan_count[strategy] / emitted_plan_count[strategy]

plan_emission_rate
  = emitted_plan_count[strategy] / selected_roster_count
```

`emitted_plan_count == 0` ise validator pass rate `null` olur ve positive gate geçemez.

Her MILP strategy için:

```text
optimal_rate = optimal_count[strategy] / selected_roster_count
feasible_timeout_rate = FEASIBLE_TIMEOUT_count / selected_roster_count
no_solution_timeout_rate = NO_SOLUTION_TIMEOUT_count / selected_roster_count
error_rate = ERROR_count / selected_roster_count
```

`INFEASIBLE` ayrıca anomaly count/rate olarak raporlanır. Gap özeti yalnızca plan emitted eden MILP execution'larında status'a göre ayrılarak count, median, p90 ve maximum içerir; `FEASIBLE_TIMEOUT` gap'i optimalite kanıtı gibi yorumlanmaz.

Triggered pairing:

```text
triggered_paired_coverage
  = complete_paired_triggered_count / triggered_count
```

## 9. Gönderi ve hizmet metrikleri

Complete paired triggered case'lerde strategy bazında:

- toplam ve case başına `UNASSIGNED` shipment sayısı;
- `unassigned_rate = unassigned_shipments / total_shipments`;
- assigned shipment için planned lateness `> 0` sayısı ve oranı;
- `service_failure = UNASSIGNED OR planned_lateness_seconds > 0` sayısı ve oranı;
- realized total/mean/median case cost;
- candidate severe-disruption exposure verilen atamaların sayısı.

Bu projede actual cargo teslimat verisi yoktur. Bu nedenle metrik yalnızca `planned_sla_breach` veya `planned_lateness` olarak adlandırılır; “gerçekleşen SLA”, on-time delivery veya müşteri hizmet seviyesi iddia edilmez. İptal/diversion sonrası actual arrival üretilemez.

## 10. Sonuçların segmentasyonu

Primary release kararı bütün complete paired triggered cohort üzerinde tek kez verilir. Aşağıdaki kırılımlar yalnızca descriptive'dir:

- cargo class;
- destination;
- source FlightDate;
- source recovery decision saati;
- solver status.

Küçük alt gruplar confirmatory etki iddiası üretmez. Sonuca göre yeni segment seçmek primary conclusion'ı değiştiremez.

## 11. Missingness ve attrition raporu

Zorunlu funnel:

```text
eligible source
→ selected roster
→ source outcome known
→ triggered
→ three strategies terminal
→ three valid plans
→ assigned candidate outcomes complete
→ complete paired triggered
```

Her geçiş için count, previous-step rate, selected-roster rate ve reason breakdown verilir. Execution failure veya missing outcome'u denominator'dan gizleyerek yalnızca başarılı case'leri göstermek yasaktır.

## 12. Sayısal ve tekrar üretilebilirlik kuralları

- Case cost ve component'ler integer kuruştur.
- Mean/median/ratio/CI için decimal arithmetic kullanılır; binary float release gate'e giremez.
- Case sırası `source_flight_date ASC, recovery_case_id ASC` olur.
- Bootstrap cluster listesi ISO date ASC olur.
- Aynı paired rows, config ve seed aynı bootstrap vector/hash'i üretmelidir.
- `bootstrap_vector_sha256` release artifact'ında tutulur.
- NaN, infinity veya silently coerced null bütün evaluation run'ını invalid yapar.

## 13. Değişiklik yönetimi

Population, denominator, pairing, realized cost, difference direction, relative improvement, bootstrap cluster/seed/repeat, quantile, CI veya metric semantiği değişirse yeni contract sürümü, karşılaştırılabilirlik analizi, ADR ve açık insan onayı gerekir. Outcome görüldükten sonra `evaluation-metrics-statistics-v1` değiştirilemez.
