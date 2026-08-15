# CargoOpt Recovery — Project Specification

| Alan | Değer |
|---|---|
| Belge sürümü | `0.10.9` |
| Durum | `PHASE_2_ACTIVE — PH2_T02_R2_DISCOVERY_RUNNING` |
| Onay tarihi | `2026-08-13` |
| Belge sahibi | Proje sahibi |
| Uygulama ortamı | Codex in ChatGPT Work |
| Aktif görev | `PH2-T02-R2` — resmî haklar zinciri ve form sözleşmesi Discovery doğrulaması |

## 1. Tek cümlelik tanım

> CargoOpt Recovery, uçuşların ciddi aksama olasılığını geçmiş performanstan tahmin eden ve risk altındaki sentetik hava kargo gönderilerini kapasite, zaman, destinasyon, öncelik, soğuk zincir ve maliyet kuralları altında uygun alternatif uçuşlara matematiksel olarak yeniden atayan; sonucu bağımsız doğrulama ve tarihsel blind replay ile değerlendiren production-oriented ML + Operations Research karar destek platformudur.

ML + OR çekirdeği bağımsız olarak kabul edildikten sonra ayrı bir RAG + LLM Ops Copilot modülü, doğrulanmış recovery planlarını kamuya açık Türkçe operasyon belgelerine dayanarak kaynaklı biçimde açıklar.

## 2. Projenin amacı

### 2.1 Operasyonel amaç

Bir uçuş ciddi aksama yaşadığında etkilenen gönderiler için şu soruyu cevaplamak:

> Hangi gönderi hangi alternatif uçuşa atanırsa bütün operasyon kısıtları korunurken beklenen ve tarihsel replay'de gerçekleşen toplam maliyet en düşük olur?

Sistem gerçek rezervasyon veya cargo operasyon sistemine işlem göndermez. Ürettiği çıktı açıklanabilir ve doğrulanabilir bir karar önerisidir.

### 2.2 Portföy amacı

Proje özellikle şu roller için kanıt üretir:

- Operations Research Scientist
- Optimization Engineer
- AI/ML Engineer
- Applied Scientist
- Decision Scientist
- Data Scientist — Optimization

Ana yetkinlik mesajı:

> Kalibre edilmiş ML tahminini deterministik matematiksel optimizasyona bağlayabiliyor, bütün constraint'leri bağımsız doğrulayabiliyor ve karar katkısını blind tarihsel replay ile ölçebiliyorum.

Ops Copilot tamamlanırsa ikincil mesaj:

> Doğrulanmış karar çekirdeğini değiştirmeden, kamuya açık Türkçe belgeler üzerinde kaynak zorunlu ve salt okunur bir RAG + LLM açıklama katmanı geliştirebiliyorum.

## 3. Kullanıcı ve temel kullanım senaryosu

Birincil kullanıcı, sentetik bir hava kargo operasyon kontrol uzmanıdır.

Temel senaryo:

1. Kaynak uçuş için ciddi aksama riski veya tarihsel aksama vakası belirlenir.
2. Etkilenen gönderiler ve takip eden 24 saatteki uygun doğrudan uçuşlar immutable snapshot olarak hazırlanır.
3. Greedy, risk-blind MILP ve ML-informed MILP aynı snapshot üzerinde çalıştırılır.
4. Bağımsız validator assignment, kapasite, zaman, destinasyon ve soğuk zincir kurallarını kontrol eder.
5. Stratejiler tarihsel gerçekleşen uçuş sonuçları üzerinden karşılaştırılır.
6. Kullanıcı doğrulanmış öneriyi, maliyetleri, kapasite kullanımını ve atanamama nedenlerini inceler.
7. Phase 8 tamamlanmışsa kullanıcı kararın ilgili açık Türkçe politika kaynaklarına dayalı açıklamasını sorabilir.

## 4. Sorumluluk ayrımı

| Bileşen | Tek sorumluluk | Ürettiği çıktı | Yetkisi dışında |
|---|---|---|---|
| Veri hattı | Karar anında bilinen bilgiyi sürümlemek | Veri/feature snapshot | Tahmin veya atama |
| ML | Ciddi aksama olasılığını tahmin etmek | Kalibre olasılık batch'i | Gönderi atamak |
| OR | Uygun gönderi-uçuş planını optimize etmek | Assignment planı | Risk tahmin etmek |
| Validator | Planı bağımsız doğrulamak | Validation raporu | Planı iyileştirmek |
| Backtest | Stratejilerin gerçekleşen etkisini ölçmek | Paired değerlendirme | Blind sonuca göre tuning |
| API/UI | Doğrulanmış bilgiyi sunmak | Karar paneli | İş kuralı hesaplamak |
| RAG retriever | İlgili açık Türkçe kaynakları bulmak | Citation adayları | Politika üretmek |
| LLM açıklayıcı | Facts ve kaynakları açıklamak | Kaynaklı Türkçe yanıt | Karar veya sayı hesaplamak |

## 5. Faz 0'da kilitlenen kararlar

### 5.1 Tahmin anı

- Source recovery kararı planlanan kaynak uçuş kalkışından tam altı saat önce verilir: `T-6`.
- `recovery_decision_at = source_scheduled_departure_at - 6h` olarak kaydedilir.
- Uçuş risk modeli tek multi-horizon modeldir; `T-24`, `T-18`, `T-12`, `T-6` as-of snapshot'larında score üretir.
- Her feature satırı kendi `prediction_cutoff_at = scheduled_departure_at - lead_time_hours` anına göre hesaplanır.
- `lead_time_hours ∈ {24,18,12,6}` model girdisidir.
- Recovery candidate için karar anında mevcut en yakın forecast ceiling kuralıyla seçilir; `produced_at > recovery_decision_at` olan skor yasaktır.
- Rolling istatistikler ilgili horizon cutoff'una kadar availability koşulunu sağlayan tamamlanmış uçuşlardan hesaplanır.
- İlgili cutoff anında mevcut olmadığı kanıtlanan hiçbir alan feature olamaz.

### 5.2 Hedef değişken

```text
severe_disruption = 1
if Cancelled == 1
   OR Diverted == 1
   OR ArrDelayMinutes >= 60
else 0
```

Bu tek binary classification hedefidir. Ayrı iptal, diversion veya gecikme modeli çekirdek kapsamda yoktur.

### 5.3 Havalimanı evreni

- En yoğun 20 havalimanı yalnızca Ocak–Ağustos 2024 eğitim dönemindeki uçuş sayılarıyla seçilir.
- Seçilen liste validation, test ve blind replay için dondurulur.
- Eylül–Aralık sonuçları havalimanı seçimini etkileyemez.

### 5.4 Zaman bölünmesi

| Bölüm | Dönem | Kullanım |
|---|---|---|
| Train | 1 Ocak–31 Ağustos 2024 | Model fitting ve train-temelli istatistikler |
| Validation | 1 Eylül–31 Ekim 2024 | Model/calibration seçimi ve izinli tuning |
| ML test | 1–30 Kasım 2024 | Dondurulmuş ML değerlendirmesi |
| Blind replay | 1–31 Aralık 2024 | Uçtan uca ML + OR karar değerlendirmesi |

Aralık verisi Phase 5'ten önce feature, model, calibration, generator, seed, maliyet, objective, constraint veya vaka seçimi ayarlamak için kullanılamaz.

### 5.5 Ücretsiz çalışma ilkesi

- Ücretli API veya yönetilen servis zorunlu değildir.
- Çekirdek CPU-first yerel demo olarak çalışır.
- HiGHS zorunlu solver'dır.
- Hugging Face modelleri ve Ollama yalnızca Phase 8'de yerel inference için kullanılabilir.

### 5.6 Recovery case ve sentetik TL maliyet sınırı

- Bir `recovery_case`, tek bir kaynak uçuşu, tek bir origin–destination çifti ve bu uçuşa bağlı sentetik gönderileri kapsar.
- Projedeki “en fazla 10 destinasyon”, tek bir karma optimizasyon problemi değil, en fazla 10 bağımsız destinasyon case'i anlamına gelir.
- Recovery penceresi `prediction_cutoff_at` anında başlar ve tam 24 saat sürer; aday uçuşun planlanan varışı pencere içinde olmalıdır.
- Her gönderi bölünmeden tam bir aday uçuşa atanır veya açıkça `UNASSIGNED` kalır.
- Maliyet para birimi `TRY`, maliyet temeli `SYNTHETIC_NOMINAL_2024`'tür; KDV, enflasyon ve kur dönüşümü v1 kapsamı dışındadır.
- Bütün TL katsayıları kontrollü deney varsayımıdır; gerçek Turkish Cargo/THY maliyeti, fiyatı veya finansal etkisi değildir.

| Kargo sınıfı | Handling | Gecikme/saat | Aday uçuş aksama sonucu | Atanamama |
|---|---:|---:|---:|---:|
| `STANDARD` | ₺500 | ₺250 | ₺10.000 | ₺50.000 |
| `EXPRESS` | ₺750 | ₺750 | ₺30.000 | ₺150.000 |
| `PHARMA` | ₺1.250 | ₺1.250 | ₺50.000 | ₺250.000 |

Risk-blind MILP handling ve SLA gecikme maliyetini kullanır. ML-informed MILP aynı katsayılara yalnızca immutable prediction batch'ten gelen `p(severe_disruption) × disruption_consequence_try` terimini ekler. Gerçekleşmiş outcome yalnızca downstream blind replay değerlendirmesinde kullanılır; generator veya optimizasyon objective'ine girmez.

Prediction batch her aday için recovery kararında mevcut ceiling horizon forecast'ini taşır. Karar anından sonra üretilmiş prediction, iki stratejide de batch'i fail-closed geçersiz kılar.

### 5.7 OR çözüm ve doğrulama sınırı

- MILP kararları uygun shipment–flight çiftleri için binary assignment ve her shipment için binary `UNASSIGNED` değişkenidir.
- Risk-blind ve ML-informed aynı input snapshot, variable ve hard constraint setini kullanır; tek business-objective farkı expected disruption cost'tur.
- Bütün solver maliyet katsayıları `TRY × 100` ile tam sayı kuruşa çevrilir.
- HiGHS case başına 60 saniye time limit ve `0.001` relative MIP gap ile çalışır.
- Timeout `OPTIMAL` olarak sunulamaz; incumbent varsa `FEASIBLE_TIMEOUT`, yoksa `NO_SOLUTION_TIMEOUT` olur.
- Her yayımlanabilir plan Pyomo ve HiGHS state'ini okumayan bağımsız validator tarafından input snapshot üzerinden yeniden doğrulanır.
- Validator feasibility, maliyet ve hash bütünlüğünü kanıtlar; optimalite kanıtladığını iddia etmez.

### 5.8 Blind replay ve politika kararı sınırı

- Blind roster yalnızca Aralık 2024 schedule ve pre-outcome input eligibility ile seçilir; source/candidate outcome'u veya prediction probability'si ranking ve filtre olamaz.
- En fazla 10 dondurulmuş destination için destination başına en fazla 30 source case, `blind-roster-v1|20240831|destination|source_flight_id` SHA-256 rank'iyle seçilir; destination'lar arasında backfill yapılmaz.
- Aralık içindeki geçmiş outcome yalnızca as-of feature gateway üzerinden `label_available_at <= prediction_cutoff_at` koşuluyla rolling feature'a girebilir. Evaluation runner full outcome snapshot'ını pre-reveal freeze tamamlanmadan okuyamaz.
- Greedy, risk-blind MILP ve ML-informed MILP selected roster'ın tamamında aynı OR input hash'iyle full reveal öncesi çalıştırılır ve validate edilir.
- Reveal sonrasında yalnız source `severe_disruption == 1` case'ler triggered cohort olur. Bu, doğru veya dışarıdan verilmiş source alert'e koşullu recovery değerlendirmesidir; alert modelinin precision/recall ölçümü değildir.
- Realized cost, atanan candidate'ın binary severe-disruption outcome'u ile `cost-policy-try-v1` formülünden integer kuruş olarak yeniden hesaplanır; actual delay minutes ve source ortak sunk term'i paired farka girmez.
- Primary fark `D_i = Cost_ML_INFORMED,i - Cost_RISK_BLIND,i` olur; negatif değer ML-informed lehinedir.
- Mean paired fark için source `FlightDate` cluster bootstrap, `10.000` tekrar, seed `20240831` ve `%95` R-7 percentile interval kullanılır. Greedy karşılaştırmaları secondary descriptive'dir.
- ML-informed politika ancak en az 30 complete paired triggered case, 10 tarih, 5 destination, her strategy için `%95` valid-plan coverage, emitted planlarda `%100` validator pass, `%95` triggered paired coverage, iki MILP için `%90` `OPTIMAL`, en az `%5` aggregate improvement ve CI upper `< 0` kapılarının tamamıyla önerilebilir.
- Geçerli nötr/negatif veya yetersiz kanıt sonucunda risk-blind korunur. Deney bütünlüğü bozulursa politika kararı verilmez. Negatif sonuç proje başarısızlığı değildir.

### 5.9 Sensitivity analysis sınırı

- Sensitivity yalnız secondary, pre-registered ve non-release robustness analizidir; primary blind `run_status`, gate, CI veya `policy_decision` değerini değiştiremez.
- Primary baseline yeniden solve edilmez. Yalnız `RISK_BLIND_MILP` ve `ML_INFORMED_MILP` karşılaştırılır.
- Exact dört non-baseline OFAT scenario vardır: disruption consequence `×0.75/×1.25` ve available capacity `×0.90/×1.10`.
- Joint grid, adaptive search, outcome'a göre multiplier seçimi ve yeni strategy yasaktır.
- Scenario kataloğu full outcome reveal öncesi dondurulur. Triggered case listesi primary run'dan exact alınır.
- Sensitivity planner outcome okuyamaz; iki MILP'in scenario planları candidate outcome join'inden önce dondurulup bağımsız validator'dan geçer.
- Sonuçlar descriptive mean/median/aggregate fark, coverage, unassigned ve status dağılımıyla raporlanır; yeni bootstrap, CI, p-value veya adoption threshold üretilmez.

## 6. Sabit kapsam

| Boyut | Sınır |
|---|---:|
| Ana merkez | 1 |
| Destinasyon | En fazla 10 bağımsız case |
| Recovery penceresi | 24 saat |
| Aday uçuş | En fazla 30 |
| Gönderi | En fazla 500 |
| Rota | Yalnızca doğrudan |
| Gönderi bölme | Yok |
| Cargo türü | `STANDARD`, `EXPRESS`, `PHARMA` |
| ML problemi | Tek binary classification |
| Solver | HiGHS |

Kapsam değişikliği ADR, etki analizi ve açık insan onayı gerektirir.

## 7. Çekirdek kapsam içi

- Resmî BTS Reporting Carrier On-Time Performance verisinin sürümlü ingestion'ı
- Karar anı ve feature availability sözleşmesi
- As-of-time 7/30 günlük rolling feature'lar
- Dummy, Logistic Regression ve XGBoost karşılaştırması
- Olasılık kalibrasyonu ve MLflow deney kaydı
- Deterministik sentetik kargo, kapasite ve maliyet generator'ı
- Greedy, risk-blind MILP ve ML-informed MILP
- Ağırlık, hacim, destinasyon, hazır olma, SLA, öncelik ve soğuk zincir kısıtları
- Solver status, timeout, gap ve infeasibility yönetimi
- Pyomo state'inden bağımsız plan validator
- Aralık 2024 blind historical replay
- Paired bootstrap güven aralığı ve sensitivity analysis
- FastAPI, PostgreSQL, React, Docker Compose ve CI
- Model card, optimization report, backtest limitations ve demo

## 8. Phase 8 kapsamı

- Yalnızca kamuya açık, Türkçe, kaynak ve kullanım koşulu doğrulanabilir belgeler
- Sürümlü corpus ve ingestion manifesti
- BGE-M3 dense embedding
- PostgreSQL full-text + pgvector hybrid retrieval
- BGE multilingual reranking
- Ollama üzerinde yerel Qwen açıklama modeli
- Citation, abstention, conflict ve prompt-injection guardrail'leri
- Salt okunur Ops Copilot API ve UI
- Dondurulmuş Türkçe retrieval/grounding evaluation seti

Phase 8, Phase 7 çekirdek kabulü ve ayrı insan onayı olmadan başlayamaz.

## 9. Kesin kapsam dışı

- Fine-tuning veya LoRA
- LangGraph, application agent veya multi-agent
- LLM tool calling veya operasyonel mutation
- Reinforcement learning
- Dinamik fiyatlandırma
- Filo veya ekip çizelgeleme
- ULD 3D packing
- Ayrıntılı tehlikeli madde motoru
- Çok bacaklı network routing
- Split shipment
- Gerçek zamanlı streaming veya Kafka
- Mikroservis veya Kubernetes
- Zorunlu cloud deployment
- Gurobi veya CPLEX zorunluluğu
- Metaheuristic, formal stochastic veya robust optimization
- Mobil uygulama veya çok kiracılı SaaS
- Gerçek rezervasyon/cargo sistemine yazma
- Gerçek Turkish Cargo verisi, şirket içi belge veya finansal etki iddiası
- Sentetik RAG politika/prosedür belgeleri

Kapsam dışı bileşenler için kod, dependency, tablo, endpoint, UI, config, adapter veya placeholder oluşturulamaz.

## 10. Veri dürüstlüğü sınırı

- Uçuş verisi ABD iç hat yolcu uçuş performansını kapsayan resmî BTS verisidir; Turkish Cargo verisi değildir.
- Kargo manifestosu, uçuş kargo kapasitesi, handling maliyeti, SLA ve ceza verileri sentetiktir.
- TRY ile ifade edilen katsayılar `SYNTHETIC_NOMINAL_2024` deney parametreleridir; gerçek tarife veya maliyet değildir.
- Sentetik veri aynı config ve seed ile aynı sonucu vermelidir.
- Generator gerçek uçuş outcome alanlarını okuyamaz.
- RAG corpus'u yalnızca kamuya açık Türkçe kaynaklardan oluşur.
- Kamuya açıklık yeniden dağıtım hakkı sayılmaz; lisans/kullanım koşulu belge bazında kaydedilir.
- Proje gerçek operasyon deneyi veya nedensel etki çalışması değildir.

## 11. Araştırma ve başarı soruları

Birincil soru:

> Kalibre edilmiş uçuş riskini kullanan ML-informed MILP, aynı blind recovery vakalarında risk-blind MILP ve greedy baseline'a göre daha düşük gerçekleşen toplam maliyet sağlıyor mu?

İkincil sorular:

- Optimizasyon basit greedy yaklaşımdan daha iyi mi?
- ML olasılıkları yeterince kalibre mi?
- Üretilen bütün planlar constraint'leri ihlal etmeden doğrulanabiliyor mu?
- ML-informed yaklaşımın etkisi paired istatistiksel değerlendirmede güvenilir mi?
- Ops Copilot kaynaklı, sayısal olarak tutarlı ve gerektiğinde çekimser yanıt verebiliyor mu?

ML-informed yöntemin kazanması tamamlanma koşulu değildir. Kazanmazsa risk-blind MILP korunur ve negatif sonuç raporlanır.

## 12. Mimari ilkeler

- Modüler monolit
- Tek repository ve tek PostgreSQL instance
- Raw/processed analitik veri için Parquet
- Immutable snapshot ve versioned config
- Fail-closed veri, tahmin, solver ve validator davranışı
- Deterministik generator ve tie-break
- CPU-first yerel demo
- Çekirdek karar sisteminden ayrılmış downstream Copilot
- Dış sisteme gerçek mutation yok
- Faz kapısına kadar erken hazırlık yok

## 13. Yönetişim ve kaynakların önceliği

1. Güvenlik/veri bütünlüğü ve kullanıcının güncel açık kararı
2. `docs/phase-status.yaml`
3. Aktif onaylı görev sözleşmesi
4. Bu `PROJECT_SPEC.md`
5. Kabul edilmiş ADR'ler
6. `AGENTS.md`

Phase 0 contract kimliği, artifact yolu, owner component, implementation phase ve normative dependency kayıtları `docs/governance/CONTRACT_REGISTRY.yaml` içinde tutulur. Registry lifecycle status'ları `phase-0-to-1-transition-v1` ile `ACCEPTED` olmuştur. Contract değişikliği yeni görev/onay ile registry ve dependency DAG etki analizini de güncellemelidir.

Bu belgeyi etkileyen değişiklik:

- gerekçe ve etki analizi;
- ilgili ADR;
- veri/deney geriye uyumluluk değerlendirmesi;
- insan onayı

gerektirir.

## 14. Mevcut durum

- Tamamlanan fazlar: `PHASE_0 — COMPLETED/PASSED`, `PHASE_1 — COMPLETED/PASSED`
- Aktif faz: `PHASE_2 — data_and_domain`
- Tamamlanan görevler: `PH1-T01`, `PH1-T02`, `PH1-T03`, `PH1-T04`, `PH2-T01`
- Sonuçlanan görev: `PH2-T02 — BLOCKED/PROBE_SECURITY_ABORTED`; sonuç kabul edildi, source başarı iddiası kurulmadı
- Sonuçlanan retry görevi: `PH2-T02-R1 — BLOCKED/PROBE_SECURITY_ABORTED`; Extract `NOT_RUN`, cleanup `PASSED`
- Aktif görev: `PH2-T02-R2`; yalnız read-only hosted Discovery yürütülüyor
- Phase 1 sonucu: Local clean-room ve gerçek GitHub-hosted CI dahil bütün foundation kapıları geçti
- Onay kaydı: GitHub Actions, `ubuntu-24.04`, full-SHA checkout/setup-uv, read-only token, cache/secret/artifact yok
- Repository: `Slmnbal/cargoopt-recovery`; `main` ve GitHub Actions yazma/çalıştırma yetkisi doğrulandı
- Local sonuç: 13 package project graph + 6 package build graph; `0` vulnerability/adverse status; lisans envanteri PASS
- Phase 2 açılış hosted kanıtı: `Foundation` run `31876915844`, commit `44a5bfad2389a7efbfadecee82f6d9d256015055`, conclusion `success`
- PH2-T01 hosted kanıtı: `Foundation` run `31878673155`, commit `03181925cd10eb9c9dcd1b75152d35d39114b710`, job `94998027186`, conclusion `success`, artifact `0`
- Uygulanan foundation: Minimal package shell, exact lock ve local kalite/build gate'leri
- Sıradaki kapı: Data.gov/USA.gov haklar zinciri ve exact form sözleşmesinin fail-closed Discovery sonucu
- Runtime dependency sayısı: `0`
- Phase 2 implementation: Henüz yok; dependency kurulmadı ve veri indirilmedi
- Kilitli fazlar: `PHASE_3..PHASE_8`
- Faz disiplini: retry kapalı sonucu için güvenlik/haklar kararı verilmeden PH2-T03 planlanmaz
