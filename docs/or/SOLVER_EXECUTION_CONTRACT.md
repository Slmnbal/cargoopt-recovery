# HiGHS Solver Execution ve Status Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `highs-execution-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T04` |
| Solver | HiGHS |
| Time limit | 60 saniye/case/strateji |
| Relative MIP gap | `0.001` |

## 1. Amaç

Bu sözleşme HiGHS native sonucu ile CargoOpt execution status'u arasındaki fail-closed mapping'i tanımlar. Solver çıktısı başarı varsayımıyla yorumlanmaz. Timeout hiçbir koşulda `OPTIMAL`, incumbent olmayan run ise plan olarak sunulamaz.

Bu belge HiGHS kurulumu veya dependency sürümü seçmez; Phase 1 dependency onayında pinned sürüm ayrıca kaydedilecektir.

## 2. Dondurulmuş logical options

| Option | Değer | Amaç |
|---|---:|---|
| `time_limit` | `60.0` saniye | Primary ve varsa secondary toplam solver bütçesi |
| `mip_rel_gap` | `0.001` | En fazla `%0,1` configured optimality tolerance |
| `threads` | `1` | Aynı ortamda deterministik yürütme |
| `random_seed` | `20240831` | Solver randomization sabitleme |
| `presolve` | `on` | Varsayılan performans; run artifact'ında kaydedilir |
| warm start | `disabled` | Stratejiler arası incumbent aktarımını engelleme |

Pinned HiGHS adapter option adları farklıysa adapter mapping'i ayrıca test edilir; logical değerler değişemez. Unsupported option sessizce ignore edilemez, execution başlamadan `ERROR` olur.

## 3. Execution sırası

1. OR input schema ve hash kapısı geçer.
2. Eligibility ve cost matrix canonical oluşturulur.
3. Model manifesti ve hash'i oluşturulur.
4. Primary MILP kalan budget `60s` ile çalışır.
5. Primary `OPTIMAL` ise kalan pozitif budget ile secondary tie-break çalışabilir.
6. Native status, termination, incumbent, bounds, gap ve runtime normalize edilir.
7. Plan yalnızca izinli status ve incumbent varsa serialize edilir.
8. Plan bağımsız validator'a verilir.
9. Validator `VALID` olmadan downstream publish yapılmaz.

Model build ve input validation süreleri ayrı ölçülür; `60s` HiGHS primary + secondary toplam wall-clock bütçesidir.

## 4. CargoOpt solver status enum'u

Exact enum:

```text
OPTIMAL
FEASIBLE_TIMEOUT
INFEASIBLE
NO_SOLUTION_TIMEOUT
ERROR
```

Başka status string'i output schema'ya yazılamaz.

## 5. Mapping tablosu

| CargoOpt status | Zorunlu koşullar | `plan_emitted` |
|---|---|---:|
| `OPTIMAL` | Native optimal termination; incumbent var; finite primal/dual bound; recomputed relative gap `<= 0.001` | `true` |
| `FEASIBLE_TIMEOUT` | Time limit termination; incumbent var; objective finite | `true` |
| `INFEASIBLE` | Native proven infeasible; incumbent yok | `false` |
| `NO_SOLUTION_TIMEOUT` | Time limit termination; incumbent yok | `false` |
| `ERROR` | Unbounded, numerical failure, option failure, exception, inconsistent status veya diğer bütün durumlar | `false` |

Native `optimal` kelimesi tek başına yeterli değildir; incumbent, bound ve gap alanları da doğrulanır. Native time limit ile biten run'ın gap'i küçük görünse bile native optimal termination yoksa `FEASIBLE_TIMEOUT` kalır.

## 6. Relative gap

Minimizasyon için bağımsız audit değeri:

```text
relative_gap = abs(primal_bound - dual_bound) / max(abs(primal_bound), 1)
```

- Bounds integer kuruş objective birimindedir.
- Solver-native gap ayrıca değiştirilmeden saklanır.
- Native ve recomputed gap `1e-9` mutlak toleranstan fazla ayrışırsa `ERROR` olur.
- `OPTIMAL`, configured tolerance içinde solver-certified optimum anlamındadır; exact zero-gap iddiası ancak gap gerçekten `0` ise yapılabilir.
- Gap yok, NaN, infinity veya negatifse `ERROR` olur.

## 7. Time limit ve incumbent politikası

- `FEASIBLE_TIMEOUT`, optimalite değil uygulanabilir incumbent bulunduğunu ifade eder.
- Incumbent plan aynı bağımsız validator kontrollerinin tamamından geçmelidir.
- Timeout planı UI'da veya raporda `optimal` kelimesiyle etiketlenemez.
- Incumbent yoksa boş assignment listesi planmış gibi üretilmez.
- Time limit otomatik iki katına çıkarılamaz; gap gevşetilemez; solver başka solver'a fallback yapamaz.
- Otomatik retry yalnızca aynı immutable input ve birebir aynı options ile, teknik transient error için ayrı execution ID ile yapılabilir; birincil result overwrite edilemez.

## 8. INFEASIBLE politikası

Modelde her shipment için `UNASSIGNED` bulunduğu için schema-valid input yapısal olarak feasible olmalıdır.

`INFEASIBLE` durumunda:

- assignment veya unassigned planı üretilmez;
- bütün-strategy backtest sonucu olarak normalleştirilmez;
- model/input/eligibility/cost hash'leri korunur;
- execution release-blocking anomaly olur;
- input kapısı, model assembly ve solver adapter araştırılır;
- kullanıcıya “kargo atanamadı” diye yanlış sunulmaz.

Validator solver'ın infeasibility kanıtını yeniden üretmez. Native solver raporu audit artifact'ıdır.

## 9. ERROR kapsamı

En az:

```text
UNBOUNDED_OR_UNBOUNDED_OR_INFEASIBLE
NUMERICAL_FAILURE
UNSUPPORTED_OPTION
SOLVER_NOT_AVAILABLE
MODEL_ASSEMBLY_MISMATCH
NONFINITE_BOUND
GAP_MISMATCH
INTERRUPTED
EXCEPTION
UNKNOWN_NATIVE_STATUS
```

durumları `ERROR` olur. Error reason, safe message ve native status saklanır; stack trace kullanıcıya gösterilmez, secret içerebilecek environment/log alanları output'a yazılmaz.

## 10. Tie-break execution

| Primary sonucu | Secondary davranışı |
|---|---|
| `OPTIMAL` ve kalan süre var | Primary objective exact sabitlenir; secondary çalışır |
| `OPTIMAL` ve kalan süre yok | Plan korunur; `tie_break_status=NOT_RUN_NO_TIME` |
| `FEASIBLE_TIMEOUT` | Secondary çalışmaz; `NOT_RUN_PRIMARY_NOT_OPTIMAL` |
| No-plan status | Secondary çalışmaz |

Tie-break status enum'u:

```text
COMPLETED
INCOMPLETE_TIMEOUT
NOT_RUN_NO_TIME
NOT_RUN_PRIMARY_NOT_OPTIMAL
NOT_APPLICABLE_NO_PLAN
ERROR
```

Secondary sırasında error oluşursa primary status'u `OPTIMAL` olan incumbent korunabilir; solver status `OPTIMAL`, `tie_break_status=ERROR` olur. Bu durum raporda görünür ve exact assignment determinism guardrail'i başarısız sayılır; plan feasibility için yine validator'a gider.

## 11. Zorunlu execution alanları

Her run en az:

- `solver_execution_id`;
- `case_id`, `strategy`, `input_snapshot_id/hash`;
- model/eligibility/cost matrix hash'leri;
- solver name/version/adapter version;
- logical ve native option map;
- start/end UTC, model build ve solver runtime;
- native model/solver/termination status;
- CargoOpt normalized status;
- `has_incumbent`, `plan_emitted`;
- primal bound, dual bound, native ve recomputed gap;
- MIP node count ve iteration count mevcutsa;
- primary objective kuruş;
- secondary objective ve tie-break status;
- deterministic environment fingerprint;
- log SHA-256

taşır. Bulunmayan optional native metric `null` olabilir; zorunlu status kanıtı null olamaz.

## 12. Plan yayınlama matrisi

| Execution | Plan serialize | Validator | Downstream publish |
|---|---:|---:|---:|
| `OPTIMAL` | Evet | Zorunlu | Yalnızca `VALID` |
| `FEASIBLE_TIMEOUT` | Evet | Zorunlu | Yalnızca `VALID`, status korunarak |
| `INFEASIBLE` | Hayır | `NOT_APPLICABLE_NO_PLAN` | Hayır |
| `NO_SOLUTION_TIMEOUT` | Hayır | `NOT_APPLICABLE_NO_PLAN` | Hayır |
| `ERROR` | Hayır | `NOT_APPLICABLE_NO_PLAN` | Hayır |

## 13. Tekrar üretilebilirlik sınırı

Aynı input, code, dependency lock, HiGHS/adapter sürümü, options, OS/CPU environment fingerprint ve ordered model assembly saklanır. Aynı ortamda primary objective ve validation sonucu byte-identical hedeflenir.

Farklı HiGHS, compiler, CPU veya numeric library sürümünde aynı tie assignment garantisi verilmez. Böyle bir fark sessizce overwrite edilmez; execution artifact'ları ayrı tutulur.

## 14. Değişiklik koşulu

Time limit, gap, thread, seed, presolve, warm-start, status mapping, retry, incumbent publish veya tie-break execution değişikliği yeni contract sürümü, ADR, karşılaştırılabilirlik analizi ve açık insan onayı gerektirir.
