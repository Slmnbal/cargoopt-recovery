# Blind Replay, Freeze ve Outcome Reveal Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `blind-replay-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T05` |
| Blind dönem | `2024-12-01` — `2024-12-31` |
| Roster seed | `20240831` |
| Maksimum roster | `300` source recovery case |

## 1. Amaç ve kanıt sınırı

Bu sözleşme Aralık 2024 outcome'ları karar üretiminden ayrıyken recovery case roster'ının nasıl seçileceğini, üç stratejinin nasıl dondurulacağını ve sonuçların ne zaman açılacağını tanımlar. Birincil deney şu soruyu yanıtlar:

> Gerçekte ciddi aksama yaşamış bir source uçuş için recovery tetikleyicisinin doğru veya dışarıdan verilmiş olduğu koşulunda, ML-informed MILP aynı dondurulmuş case üzerinde risk-blind MILP'ten daha düşük gerçekleşen sentetik maliyet üretiyor mu?

Bu deney:

- source alert modelinin precision, recall, F1 veya threshold başarısını ölçmez;
- uçtan uca alarm üretme performansını kanıtlamaz;
- gerçek Turkish Cargo operasyonu, maliyeti veya nedensel etki iddiası değildir;
- ML-informed yaklaşımın kazanacağını varsaymaz.

## 2. Roller ve erişim ayrımı

| Rol | Pre-reveal okuyabilir | Pre-reveal okuyamaz |
|---|---|---|
| Roster builder | Dondurulmuş schedule, airport set, source/candidate eligibility | Source/candidate outcome, label, prediction probability |
| As-of feature builder | Yalnızca availability gateway'in izin verdiği geçmiş label'lar | Target flight outcome'u ve cutoff sonrası label |
| Prediction/OR runner | Feature, forecast, sentetik cargo ve immutable OR input | Outcome artifact'ı veya realized cost |
| Evaluation runner | Roster, plan, execution, validation ve freeze manifesti | Reveal yetkisine kadar bütün outcome değerleri |
| Outcome custodian | Outcome vault ve erişim logu | Plan veya model seçimini değiştirme yetkisi |

Tek process içinde rol taklidi yeterli kanıt değildir. Phase 5 implementation'ı en azından ayrı erişim kimlikleri veya ayrı read policy'leri ve denetlenebilir access ledger üretmelidir. Evaluation runner'a pre-reveal outcome join'i teknik olarak kapalı olmalıdır.

## 3. Point-in-time walk-forward ayrımı

“Blind dönem” Aralık içindeki daha önce sonuçlanmış uçuşların gerçek karar anında bilinebilecek geçmişinin feature olarak hiç kullanılamaması anlamına gelmez. Her forecast satırı mevcut ML sözleşmesine göre şu kapıdan geçer:

```text
history.flight_instance_id != target.flight_instance_id
history.scheduled_departure_at_utc < target.prediction_cutoff_at
history.label_available_at <= target.prediction_cutoff_at
label_available_at = history.scheduled_arrival_at_utc + 24 hours
```

Zorunlu ayrım:

- availability gateway, yukarıdaki koşulu sağlayan Aralık geçmiş outcome'larını yalnızca feature aggregate üretmek için açabilir;
- açılan raw outcome satırı prediction veya OR runner'a verilmez;
- evaluation runner bütün outcome snapshot'ını ancak full reveal sonrasında okuyabilir;
- source veya candidate'ın kendi outcome'u kendi case planında hiçbir koşulda kullanılamaz;
- gateway her okuma için target flight, horizon, cutoff, history flight ve `label_available_at` değerini hash bağlı access ledger'a yazar.

Roster ve plan üretimi `recovery_decision_at ASC, recovery_case_id ASC` sırasıyla walk-forward yürütülür. Aynı timestamp için ikinci anahtar canonical case ID'dir.

## 4. Blind partition ve dondurulmuş evren

Roster şu önceden dondurulmuş kimliklere bağlanır:

- `dataset_id` ve `processed_schedule_sha256`;
- `top20_airport_set_id`;
- tek source hub AirportID;
- train dönemiyle seçilmiş, en fazla 10 destination AirportID listesi;
- `flight-severe-disruption-prediction-v2` model/calibration artifact'ları;
- `synthetic-cargo-v1`, `cost-policy-try-v1` ve `or-input-v1` sözleşmeleri.

Destination listesi veya hub Aralık outcome'u, prediction skoru ya da recovery sonucu görülerek değiştirilemez.

## 5. Outcome-blind source eligibility

Bir source flight ancak aşağıdaki pre-outcome koşulların tamamını sağlarsa roster adayıdır:

1. Target `FlightDate` Aralık 2024 içindedir.
2. Origin dondurulmuş source hub, destination dondurulmuş destination listesindedir.
3. Schedule, timezone ve partition kalite kapıları geçerlidir.
4. `recovery_decision_at = source_scheduled_departure_at_utc - 6h` hesaplanabilir.
5. Karar anından sonraki 24 saat içinde aynı origin–destination için en az 2, en fazla 30 schedule-eligible doğrudan candidate vardır.
6. Her candidate için karar anında mevcut exact ceiling-horizon prediction bulunur.
7. Dondurulmuş sentetik generator geçerli shipment/capacity snapshot'ı üretir.
8. Exact bir `or-input-v1` snapshot'ı bütün üç strateji için kullanılabilir.

Source/candidate `Cancelled`, `Diverted`, `ArrDelayMinutes`, `severe_disruption`, realized cost ve model probability'si source roster seçim fonksiyonuna giremez. Prediction artifact'ının varlığı eligibility'dir; probability değeri ranking veya filtre değildir.

Koşullardan biri sağlanmazsa case `PRE_REVEAL_INELIGIBLE` olarak reason code ile roster candidate audit'inde kalır; ilk 30 seçiminden sonra onun yerine outcome'a bakılarak yeni case alınamaz.

## 6. Deterministik roster algoritması

Her eligible source için lower-case SHA-256 hex rank üretilir:

```text
rank_material = UTF8(
  "blind-roster-v1|20240831|" +
  canonical_destination_airport_id + "|" +
  source_flight_instance_id
)

selection_rank_sha256 = SHA-256(rank_material)
```

Algoritma:

1. Eligible source'lar destination AirportID'ye göre gruplanır.
2. Her grup `(selection_rank_sha256 ASC, source_flight_instance_id ASC)` ile bytewise ASCII sıralanır.
3. Her destination için ilk `min(30, eligible_count)` case seçilir.
4. Destination kotası başka destination'a taşınmaz; kullanılmayan kota için global backfill yapılmaz.
5. En fazla 10 destination nedeniyle toplam roster en fazla `10 × 30 = 300` case olur.
6. Roster manifesti seçilen ve seçilmeyen bütün eligible case ID'leri, rank'leri, grup sıra numaralarını ve seçim nedenini taşır.

Rank materyalindeki alanlar canonical string'dir; whitespace, locale, tarih formatı veya map iteration sırası hash'i etkileyemez.

## 7. Pre-reveal plan üretimi

Seçilen her roster case için aynı immutable `or-input-v1` üzerinde exact şu sıra uygulanır:

1. `GREEDY_BASELINE`
2. `RISK_BLIND_MILP`
3. `ML_INFORMED_MILP`

Stratejilerin execution sırası sonucu karşılaştırma anlamını değiştirmez; warm start, incumbent veya mutable capacity state paylaşımı yasaktır. Her strateji kendi execution artifact'ını ve validation report'unu üretir.

- Greedy planı `HEURISTIC_FEASIBLE` ve validator `VALID` olmadan yayımlanabilir sayılmaz.
- MILP planı yalnızca `OPTIMAL` veya `FEASIBLE_TIMEOUT` ve validator `VALID` ise yayımlanabilir.
- `INFEASIBLE`, `NO_SOLUTION_TIMEOUT` veya `ERROR` için plan uydurulmaz.
- No-plan execution için validator sonucu `NOT_APPLICABLE_NO_PLAN` olarak saklanır.
- Invalid plan silinmez ve geçerli planla sessizce değiştirilmez.

Teknik transient `ERROR` için aynı input, code, options ve environment ile en fazla bir retry yapılabilir. Retry ayrı execution ID alır. `FEASIBLE_TIMEOUT`, `INFEASIBLE`, `NO_SOLUTION_TIMEOUT` veya `INVALID` sonucu için retry yapılamaz. Canonical attempt, ilk attempt `ERROR` değilse ilk attempt; ilk attempt `ERROR` ve izinli retry varsa retry'dır. Bütün attempt'ler freeze manifestinde kalır.

## 8. Freeze manifesti

Full reveal'dan önce `pre_reveal_freeze_manifest` immutable ve SHA-256 bağlı olarak dondurulur. En az şunları içerir:

- contract/schema sürümleri ve evaluation config;
- roster candidate audit'i, selected roster ve rank hash'leri;
- dataset, raw-source manifest, schedule snapshot ve kapalı outcome vault hash'i;
- airport, hub ve destination set kimlikleri;
- feature config/snapshot, availability access ledger ve code SHA;
- preprocessing, model, calibration ve bütün forecast artifact hash'leri;
- sentetik cargo/capacity generator config, seed, version ve output hash'leri;
- cost policy ve canonical cost matrix hash'leri;
- her case'in OR input ID/hash'i;
- üç stratejinin bütün execution/attempt, plan ve validation artifact ID/hash'leri;
- solver/validator sürümleri, options ve environment fingerprint;
- evaluation code/config/schema hash'leri;
- artifact sayıları, eksik artifact reason code'ları ve canonical manifest hash'i.

Outcome vault'un `processed_outcome_sha256` değeri commit olarak manifestte bulunabilir; plaintext outcome, label dağılımı, satır özeti veya metrik pre-reveal tüketicisine açılamaz.

Freeze ancak bütün selected roster case'leri için üç canonical execution ve karşılık gelen validation terminal artifact'ı bulunduğunda `COMPLETE` olur. Terminal artifact no-plan/error olabilir; eksik kayıt olamaz.

## 9. Outcome reveal protokolü

Full reveal şu sıraya uyar:

1. Freeze manifesti canonicalize edilir ve `COMPLETE` olduğu doğrulanır.
2. `freeze_manifest_sha256` ve UTC zaman damgası yazılır.
3. Yetkili insan onayıyla tekil `reveal_authorization_id` kaydedilir.
4. Outcome vault hash'i freeze manifestindeki commit ile eşleştirilir.
5. Outcome snapshot evaluation runner'a read-only açılır.
6. Reveal zamanı, outcome hash'i, row count ve access principal kaydedilir.
7. Triggered cohort ve realized cost yalnızca bundan sonra hesaplanır.

Freeze tamamlanmadan manuel outcome erişimi run'ı `INVALID_EXPERIMENT` yapar. Outcome hash'i değişirse eski run yeniden kullanılmaz.

## 10. Triggered cohort

Reveal sonrasında selected roster içindeki case `TRIGGERED` olur yalnızca:

```text
source_outcome.severe_disruption == 1
```

`source_outcome == UNKNOWN` ise case `SOURCE_OUTCOME_UNKNOWN`; `0` ise `NOT_TRIGGERED` olur. Source outcome'u roster'a case eklemek, çıkarmak, yeniden planlamak veya candidate seçmek için kullanılamaz.

Planlar bütün roster için pre-reveal üretildiği için triggered cohort'a geçiş plan availability'yi outcome'a göre üretmez. Birincil paired maliyet analizi yalnızca `TRIGGERED` cohort'ta yapılır. `NOT_TRIGGERED` case'ler roster ve operasyonel coverage denominator'larında kalır ancak recovery etki hesabına girmez.

## 11. Post-reveal mutation yasağı

Full reveal'dan sonra birincil run için şunlar değiştirilemez:

- roster, case eligibility veya candidate listesi;
- feature, model, calibration veya prediction;
- sentetik shipment/capacity generator ya da seed;
- cost, objective, constraint, solver option veya timeout;
- execution, plan, validation ve canonical attempt;
- pairing, metric, bootstrap, threshold veya release kuralı.

Aynı dondurulmuş artifact'ların deterministic rapor rendering'i tekrar çalıştırılabilir. Kural veya kod düzeltmesi gereken reanalysis `EXPLORATORY_POST_REVEAL` olarak ayrı run ID alır ve primary blind kanıtı yerine geçemez.

## 12. Artifact durumları ve reason code'lar

```text
PRE_REVEAL_INELIGIBLE
SELECTED
NOT_SELECTED_DESTINATION_QUOTA
FREEZE_COMPLETE
FREEZE_INCOMPLETE
NOT_REVEALED
REVEALED
TRIGGERED
NOT_TRIGGERED
SOURCE_OUTCOME_UNKNOWN
EXPLORATORY_POST_REVEAL
```

Minimum failure reason code seti:

```text
OUTCOME_ACCESSED_BEFORE_FREEZE
OUTCOME_HASH_MISMATCH
OUTCOME_USED_IN_ROSTER_SELECTION
PREDICTION_USED_IN_ROSTER_RANKING
ASOF_AVAILABILITY_VIOLATION
MISSING_ASOF_ACCESS_LEDGER
ROSTER_HASH_MISMATCH
DESTINATION_QUOTA_EXCEEDED
GLOBAL_BACKFILL_DETECTED
MISSING_STRATEGY_EXECUTION
INPUT_HASH_MISMATCH_ACROSS_STRATEGIES
POST_REVEAL_PLAN_MUTATION
UNAUTHORIZED_REVEAL
```

## 13. Değişiklik yönetimi

Blind dönem, roster kotası, seed, hash materyali, eligibility, walk-forward availability, retry, freeze manifesti, reveal sırası veya triggered cohort tanımı değişirse yeni contract sürümü, leakage analizi, ADR ve açık insan onayı gerekir. Outcome görüldükten sonra `blind-replay-v1` geriye dönük değiştirilemez.
