# OR Matematiksel Model ve Greedy Baseline Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `cargo-recovery-math-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T04` |
| Input | `or-input-v1` |
| Cost policy | `cost-policy-try-v1` |
| Para birimi | integer kuruş |

## 1. Amaç ve sınır

Bu sözleşme, tek bir `recovery_case` içindeki bölünemez sentetik gönderileri uygun doğrudan aday uçuşlara atamak için greedy baseline, risk-blind MILP ve ML-informed MILP'in kesin karar uzayını tanımlar.

Üç strateji aynı immutable OR input snapshot'ını kullanır. Greedy heuristic'tir. İki MILP aynı variable ve hard constraint setini kullanır; aralarındaki tek business-objective farkı ML-informed modeldeki expected disruption cost'tur.

## 2. Model kurulmadan önce zorunlu input kapısı

`OR_INPUT_SCHEMA.yaml` doğrulanmadan model kurulmaz. En az:

- snapshot/schema/hash geçerli;
- 50–500 benzersiz shipment;
- 2–30 benzersiz candidate flight;
- candidate ve prediction ID kümeleri tam eşit;
- prediction batch immutable ve point-in-time doğru;
- TRY cost policy exact;
- bütün sayı ve timestamp'ler geçerli;
- outcome alanları yok

olmalıdır. Invalid input bir solver sonucu değildir; `INPUT_REJECTED` olarak model kurulmadan durur.

## 3. Kümeler

| Sembol | Anlam |
|---|---|
| `S` | Shipment ID'lerinin artan sıralı kümesi |
| `F` | Candidate flight ID'lerinin artan sıralı kümesi |
| `E ⊆ S×F` | Bütün domain eligibility koşullarını sağlayan shipment–flight çiftleri |
| `E_s` | Shipment `s` için uygun candidate'lar |
| `E_f` | Flight `f` için uygun shipment'lar |

`E`, model tarafından maliyete bakılarak yaratılmaz. `CARGO_DOMAIN_CONTRACT.md` kurallarıyla inputtan deterministik hesaplanır:

- origin/destination tam eşleşir;
- rota doğrudandır;
- kalkış/varış recovery penceresindedir;
- `departure >= ready_at + handling`;
- PHARMA için cold-chain vardır;
- capacity alanları pozitiftir;
- candidate için geçerli prediction bulunur.

`(s,f) ∉ E` ise `x[s,f]` değişkeni hiç oluşturulmaz. Büyük ceza vererek uygunsuz çifti modelde tutmak yasaktır.

## 4. Parametreler

Shipment için:

```text
w[s]       = weight_kg
v[s]       = volume_m3
q[s]       = unassigned_penalty_kurus
```

Flight için:

```text
W[f]       = capacity_weight_kg
V[f]       = capacity_volume_m3
p[f]       = selected severe_disruption_probability
```

Uygun pair için:

```text
c_blind[s,f] = risk_blind_assignment_cost_kurus
c_ml[s,f]    = ml_informed_assignment_cost_kurus
```

### 4.1 Kuruş dönüşümü

Cost contract önce `ROUND_HALF_UP` ile `0.01 TRY` üretir:

```text
cost_kurus = exact_integer(cost_try_decimal × 100)
```

- Float binary representation doğrudan coefficient olamaz.
- `Decimal` canonical string üzerinden dönüştürülür.
- Dönüşüm sonrası kalan fractional kuruş varsa model kurulmaz.
- Solver objective, plan output ve validator aynı integer cost matrix hash'ini kullanır.

Zorunlu ilişki:

```text
c_ml[s,f]
  = c_blind[s,f]
  + expected_disruption_cost_kurus[s,f]
```

## 5. Karar değişkenleri

```text
x[s,f] ∈ {0,1}  for every (s,f) in E
u[s]   ∈ {0,1}  for every s in S
```

- `x[s,f] = 1`: shipment `s`, flight `f`'ye tam atanmıştır.
- `u[s] = 1`: shipment `s`, açıkça `UNASSIGNED` kalmıştır.
- Continuous/fractional assignment yoktur.
- Shipment bölme, birden fazla uçuş veya kısmi weight/volume transferi yoktur.

## 6. Hard constraint'ler

### 6.1 Exactly-one kararı

Her shipment için:

```text
sum(x[s,f] for f in E_s) + u[s] = 1
```

`E_s` boşsa bu eşitlik `u[s] = 1` yapar.

### 6.2 Ağırlık kapasitesi

Her candidate flight için:

```text
sum(w[s] × x[s,f] for s in E_f) <= W[f]
```

### 6.3 Hacim kapasitesi

Her candidate flight için:

```text
sum(v[s] × x[s,f] for s in E_f) <= V[f]
```

Zaman, destination ve cold-chain ayrıca yumuşak penalty değildir; `E` dışında bırakılarak hard uygulanır. Solver çıktısı sonradan bağımsız validator tarafından aynı kurallarla yeniden kontrol edilir.

## 7. Yapısal feasibility

Geçerli her input için:

```text
x[s,f] = 0 for all (s,f) in E
u[s]   = 1 for all s in S
```

ataması bütün hard constraint'leri sağlar. Dolayısıyla input kapısı geçmiş bu modelin yapısal olarak feasible olması gerekir.

HiGHS `INFEASIBLE` döndürürse sahte assignment üretilmez. Durum release-blocking model/implementation anomalisi olarak raporlanır; input, model assembly ve solver artifact'i incelenir.

## 8. Risk-blind MILP

```text
minimize Z_blind =
  sum(c_blind[s,f] × x[s,f] for (s,f) in E)
  + sum(q[s] × u[s] for s in S)
```

Prediction batch snapshot'ta bulunur ancak probability coefficient'i business objective'te kullanılmaz.

## 9. ML-informed MILP

```text
minimize Z_ml =
  sum(c_ml[s,f] × x[s,f] for (s,f) in E)
  + sum(q[s] × u[s] for s in S)
```

Tek controlled fark:

```text
Z_ml - Z_blind
  = sum(expected_disruption_cost_kurus[s,f] × x[s,f] for (s,f) in E)
```

ML-informed modelde yeni constraint, risk threshold, candidate filtresi, capacity rezervi veya shipment priority değişikliği yapılamaz.

## 10. Deterministik greedy baseline

Greedy yalnızca `c_blind` kullanır ve solver çağırmaz.

### 10.1 Shipment sırası

Ascending tuple sırası:

```text
(
  cargo_priority_rank,       # PHARMA=0, EXPRESS=1, STANDARD=2
  delivery_due_at_utc,
  ready_at_utc,
  -weight_kg,
  -volume_m3,
  shipment_id
)
```

### 10.2 Candidate sırası

Her shipment için yalnızca `E_s` içindeki uçuşlar şu ascending tuple ile sıralanır:

```text
(
  c_blind[s,f],
  scheduled_arrival_at_utc[f],
  scheduled_departure_at_utc[f],
  flight_id
)
```

### 10.3 Algoritma

1. Residual weight ve volume capacity, input capacity'ye eşit başlatılır.
2. Shipment'lar Bölüm 10.1 sırasıyla işlenir.
3. Bölüm 10.2 sırasındaki ilk, hem weight hem volume residual kapasitesi yeterli uçuş seçilir.
4. Seçim varsa shipment tam atanır ve iki residual kapasite exact decimal arithmetic ile azaltılır.
5. Seçim yoksa shipment `UNASSIGNED` olur.
6. Plan canonical shipment ID sırasıyla serialize edilir.
7. Bağımsız validator geçmeden `HEURISTIC_FEASIBLE` yayımlanamaz.

Greedy prediction probability, outcome veya gelecekteki residual seçimleri için look-ahead kullanamaz.

## 11. MILP deterministic tie-break

Business objective integer kuruş olduğundan tie-break iki aşamalıdır:

### Aşama 1 — primary

İlgili `Z_blind` veya `Z_ml` minimize edilir. Yalnızca solver, `highs-execution-v1` kapsamında `OPTIMAL` döndürürse solver-certified incumbent integer maliyeti `Z*` sabitlenir. `OPTIMAL`, configured `0.001` gap toleransı içindeki sertifikadır; gap sıfır değilse matematiksel exact optimum iddiası kurulmaz.

### Aşama 2 — secondary

```text
primary_cost_kurus = Z*
decision_rank(s,f) = 1-based rank of flight_id in sorted F
unassigned_rank(s) = |F| + 1

minimize T =
  sum(decision_rank(s,f) × x[s,f] for (s,f) in E)
  + sum(unassigned_rank(s) × u[s] for s in S)
```

- Secondary aşama primary kuruş maliyetini değiştiremez.
- Primary optimal değilse secondary aşama çalışmaz.
- İki aşama aynı toplam 60 saniyelik bütçeyi paylaşır.
- Secondary zaman aşımında primary status'u `OPTIMAL` olan incumbent korunur; execution `OPTIMAL`, `tie_break_status=INCOMPLETE_TIMEOUT` olur.
- Secondary score'da kalan eşitlikler sorted set/variable insertion, tek thread, sabit seed ve pinned solver sürümüyle çözülür.
- Aynı platform ve pinned artifact'lar için tekrar üretilebilirlik hedeflenir; farklı HiGHS sürümlerinde aynı optimal assignment garantisi iddia edilmez. Primary cost ve validator sonucu yine aynı olmalıdır.

Tie-break için business objective'e epsilon, gizli penalty veya float perturbation eklenemez.

## 12. Model büyüklüğü sınırı

Maksimum dense durumda:

```text
|x| <= 500 × 30 = 15,000
|u| <= 500
exactly-one constraints <= 500
capacity constraints <= 30 weight + 30 volume
```

Eligibility sparse ise yalnızca `E` pair'leri oluşturulur. Yeni multi-leg, split, ULD veya network-flow değişkeni v1'e eklenemez.

## 13. Model manifesti

Her MILP execution en az:

- model contract ID;
- OR input snapshot ID/hash;
- eligibility matrix hash;
- cost matrix hash;
- strategy;
- `|S|`, `|F|`, `|E|`;
- binary variable ve constraint sayıları;
- ordered shipment/flight ID hash'leri;
- model builder code SHA;
- solver contract ID

taşır. Manifest hash'i solver execution ve plan artifact'ına bağlanır.

## 14. Değişiklik koşulu

Set, eligibility, variable, constraint, objective, greedy sort key, tie-break veya kuruş dönüşümü değişirse yeni contract sürümü, ADR, karşılaştırılabilirlik analizi ve açık insan onayı gerekir. Blind sonuç görüldükten sonra v1 geriye dönük değiştirilemez.
