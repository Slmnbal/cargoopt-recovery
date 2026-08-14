# ADR-006 — OR Formülü, HiGHS Status ve Bağımsız Validator Kararı

| Alan | Değer |
|---|---|
| Durum | Accepted |
| Tarih | 2026-08-13 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | PH0-T04 |

## Bağlam

CargoOpt Recovery aynı immutable recovery case üzerinde deterministic greedy, risk-blind MILP ve ML-informed MILP'i karşılaştıracaktır. Set, constraint, objective ve solver status anlamları kod öncesinde sabitlenmezse iki MILP arasında yalnızca ML riskinin değiştiği iddiası doğrulanamaz. Timeout yanlışlıkla optimal gösterilebilir, infeasible durumda sahte assignment üretilebilir veya planner'ın kendi summary'si doğrulama sanılabilir.

Maliyetler sentetik nominal 2024 TRY'dir ve cost policy 0,01 TRY hassasiyetindedir. Float coefficient ve farklı cost builder'lar bir kuruş reconciliation farkı yaratabilir. Bu nedenle solver, output ve validator aynı canonical integer-kuruş cost matrix'e bağlanmalıdır.

## Karar

### 1. Matematiksel karar uzayı

- `x[s,f]` yalnızca domain açısından uygun `E ⊆ S×F` çiftleri için binary assignment'tır.
- `u[s]`, shipment'ın `UNASSIGNED` kalmasını temsil eden binary değişkendir.
- Her shipment için `sum(x[s,f]) + u[s] = 1` uygulanır.
- Her flight için weight ve volume capacity hard constraint'tir.
- Zaman, destination, direct-route ve PHARMA cold-chain uygunsuzluğu penalty değil, `E` dışında bırakma sebebidir.
- Split shipment veya continuous assignment yoktur.

Geçerli inputta bütün `u=1` çözümü feasible olduğundan solver `INFEASIBLE` sonucu normal iş sonucu değil, model/assembly anomalisi kabul edilir.

### 2. Objective ayrımı

Risk-blind:

```text
assignment = handling + planned lateness
```

ML-informed:

```text
assignment = handling + planned lateness
             + probability × disruption consequence
```

Set, variable, eligibility, hard constraint, unassigned penalty ve input aynıdır. ML-informed modele risk threshold veya ek constraint konulmaz.

### 3. Integer kuruş

- Cost policy önce `ROUND_HALF_UP` ile iki ondalık TRY üretir.
- Solver coefficient'i exact `cost_try × 100` integer kuruştur.
- Solver planı ve validator aynı cost matrix SHA-256 değerini kullanır.
- Fractional kuruş veya binary float'tan doğrudan coefficient üretimi fail-closed reddedilir.

### 4. Greedy baseline

Greedy risk-blind'dır:

- shipment sırası: cargo priority, due time, ready time, azalan weight/volume, shipment ID;
- candidate sırası: risk-blind cost, planlanan varış, kalkış, flight ID;
- ilk residual weight ve volume kapasitesi yeterli candidate seçilir;
- yoksa `UNASSIGNED` olur.

Algoritma deterministic trace üretir ve validator/verifier tarafından tekrar oynatılır.

### 5. HiGHS execution

Logical options:

```text
time_limit = 60 seconds
mip_rel_gap = 0.001
threads = 1
random_seed = 20240831
presolve = on
warm_start = false
```

Exact solver status enum'u:

```text
OPTIMAL
FEASIBLE_TIMEOUT
INFEASIBLE
NO_SOLUTION_TIMEOUT
ERROR
```

- `OPTIMAL`, native optimal termination, incumbent, finite bounds ve recomputed gap `<=0.001` gerektirir.
- Time limit + incumbent `FEASIBLE_TIMEOUT` olur.
- Time limit + no incumbent `NO_SOLUTION_TIMEOUT` olur.
- No-plan status assignment artifact'i üretemez.
- Unbounded, numerical veya inconsistent native sonuç `ERROR` olur.

### 6. Tie-break

Primary integer-kuruş objective `highs-execution-v1` kapsamında `OPTIMAL` olduktan sonra solver-certified incumbent maliyeti için exact `Z=Z*` eşitliği kurulur ve deterministic decision-rank toplamı minimize edilir. `OPTIMAL`, configured `0.001` gap toleransındaki solver sertifikasıdır; gap sıfır değilse matematiksel exact optimum iddiası değildir. Secondary aşama incumbent primary cost'u değiştiremez ve primary + secondary toplam 60 saniyeyi paylaşır.

Secondary tamamlanamazsa primary status'u `OPTIMAL` olan plan korunur, `tie_break_status` başarısızlığı açıkça raporlanır. Aynı pinned environment'ta repeatability hedeflenir; farklı solver/compiler/CPU sürümlerinde aynı solver-certified assignment iddia edilmez.

### 7. Bağımsız validator

Validator:

- Pyomo veya HiGHS state'i okuyamaz;
- immutable OR input ve plan JSON'dan eligibility'yi yeniden hesaplar;
- exact shipment completeness, weight, volume, time, destination ve cold-chain kontrolü yapar;
- bütün cost component ve total'ı integer kuruş olarak yeniden hesaplar;
- greedy trace'i replay eder;
- solver evidence alanlarının status ile tutarlılığını kontrol eder;
- optimaliteyi kendisinin kanıtladığını iddia etmez.

Plan ancak execution plan yayımlamaya izin veriyor ve validation `VALID` ise downstream publish edilebilir.

## Gerekçe

- Sparse `E` uygunsuz assignment'ı büyük penalty ile gizlemekten daha güvenlidir.
- Açık `UNASSIGNED`, capacity yetersizliğini sahte assignment veya infeasibility yerine ölçülebilir yapar.
- Integer kuruş planner/validator arasında exact reconciliation sağlar.
- Aynı variable/constraint seti ML riskinin katkısını izole eder.
- Timeout status ayrımı yanlış optimalite iddiasını önler.
- Bağımsız validator solver/model-builder bug'larını aynı state'e güvenmeden yakalayabilir.
- Greedy'nin exact sırası karşılaştırılabilir deterministic baseline üretir.

## Sonuçlar

Olumlu:

- OR formülü mülakatta matematiksel olarak savunulabilir.
- Her planın feasibility ve maliyeti bağımsız kanıtlanabilir.
- Timeout incumbent'i kaybedilmeden ama optimalmiş gibi sunulmadan değerlendirilebilir.
- Strategy artifact'ları aynı input ve cost hash'ine bağlanır.
- Backtest'e yalnızca doğrulanmış planların girmesi için kapı oluşur.

Maliyet ve sınırlamalar:

- Validator domain ve cost hesaplarını ikinci kez uygular.
- Tek thread performansı düşürebilir fakat repeatability'yi kolaylaştırır.
- Secondary tie-break kalan solver süresini tüketebilir.
- Validator optimalite kanıtlamaz; solver evidence'a ihtiyaç devam eder.
- Farklı HiGHS/platform sürümleri aynı solver-certified primary assignment'ı seçmeyebilir.

## Reddedilen alternatifler

- Uygunsuz pair'leri büyük-M penalty ile modelde tutmak
- `UNASSIGNED` değişkenini kaldırmak
- Timeout incumbent'ini `OPTIMAL` etiketlemek
- Incumbent yokken boş assignment'ı plan gibi sunmak
- Risk-blind ve ML-informed için farklı constraint veya candidate seti kullanmak
- Float TRY coefficient'i doğrudan solver'a vermek
- Objective'e açıklanmamış epsilon eklemek
- Pyomo variable değerlerini validator kanıtı saymak
- Validator içinde modeli yeniden solve ederek feasibility kontrol etmek
- Infeasible durumda greedy'ye sessiz fallback yapmak
- Solver değiştirerek otomatik retry yapmak

## Uygulama kapıları

Phase 4 başlamadan önce:

- Pyomo ve HiGHS dependency/sürüm/lisans kararı ayrıca onaylanmalı;
- solver adapter option mapping test edilmelidir;
- küçük golden MILP fixture'ları optimal, timeout-with-incumbent, timeout-without-incumbent ve error path'lerini kapsamalıdır;
- validator mutation testleri her reason code ailesini tetiklemelidir;
- planner ve validator cost builder'larının aynı çıktı hash'ini üretmesi test edilmelidir;
- geçerli inputta all-unassigned witness testi bulunmalıdır;
- no-plan status için assignment serialization'ın imkânsız olduğu test edilmelidir.

Blind replay inclusion/exclusion ve istatistik politikası PH0-T05 kapsamıdır. Bu ADR kod, dependency, solver kurulumu veya optimizasyon çalıştırmayı başlatmaz.

## Değişiklik koşulu

Set, variable, constraint, objective, cost unit, greedy sıra, solver option/status, tie-break, validator bağımsızlığı veya publish gate değişirse yeni ADR/contract sürümü, failure-mode ve karşılaştırılabilirlik analizi ile açık insan onayı gerekir. Blind sonuç görüldükten sonra v1 geriye dönük değiştirilemez.
