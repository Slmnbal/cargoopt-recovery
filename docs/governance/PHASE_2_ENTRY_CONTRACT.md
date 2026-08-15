# Phase 2 Data ve Domain Giriş Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `phase-2-entry-v1` |
| Durum | Accepted — Phase 2 Active |
| Transition görevi | `PH1-T04` |
| Phase 2 adı | `data_and_domain` |

## 1. Amaç

Bu sözleşme Phase 2'nin güvenli açılışını, uygulanabilecek veri/domain temelini,
görev onay sırasını ve Phase 3+ sınırını tanımlar. Phase 2'nin amacı açık BTS
uçuş verisini sürümlü ve tekrar üretilebilir biçimde hazırlamak; karar anında
bilinen bilgi ile sonradan gerçekleşen outcome'u kesin ayırmak; deterministic
sentetik kargo/domain snapshot'larını üretmek ve leakage-safe feature
availability temelini kurmaktır.

Phase 2 model eğitimi, optimizasyon, servis/UI veya RAG fazı değildir.

## 2. Normatif Phase 2 contract'ları

Phase 2 implementation'ı aşağıdaki kabul edilmiş contract'lara uymalıdır:

| Contract ID | Artifact | Sorumluluk |
|---|---|---|
| `bts-reporting-otp-contract-v1` | `docs/data/BTS_DATA_CONTRACT.md` | Resmî BTS kaynak, sürüm ve ingestion sınırı |
| `cargoopt-data-quality-v2` | `docs/data/DATA_QUALITY_CONTRACT.md` | Fail-closed schema ve veri kalite kapıları |
| `cargo-domain-v1` | `docs/domain/CARGO_DOMAIN_CONTRACT.md` | Cargo domain varlıkları ve invariant'lar |
| `synthetic-cargo-v1` | `docs/data/SYNTHETIC_CARGO_CONTRACT.md` | Deterministik sentetik kargo üretimi |
| `flight-feature-availability-v2` | `docs/ml/FEATURE_AVAILABILITY.yaml` | As-of-time ve leakage-safe availability |

Registry lifecycle, contract ID, dependency veya semantik değişikliği bu fazda
kendiliğinden yapılamaz; ayrı governance görevi ve insan onayı gerekir.

## 3. Entry precondition'ları

Phase 2 ancak aşağıdakilerin tamamıyla açılabilir:

1. `PH1-T01..PH1-T03` görevleri `COMPLETED` olmalıdır.
2. Phase 1 gate değeri `READY_FOR_HUMAN_APPROVAL` olmalıdır.
3. Final `main` commit'i read-only hosted `Foundation` workflow'unda geçmelidir.
4. Phase 1 checkpoint SHA-256 ve ZIP bütünlüğü doğrulanmalıdır.
5. Proje sahibi Phase 1'i kapatıp Phase 2'yi açmak için ayrı açık onay vermelidir.
6. Transition mutation'ı yalnız ayrıca onaylanmış exact file planıyla yapılmalıdır.
7. İlk Phase 2 görevi yürütme başlamadan önce ayrıca açıkça onaylanmalıdır.

Faz geçiş onayı, PH2-T01 yürütme onayı değildir.

## 4. Transition sonrası zorunlu durum

```text
PHASE_1.status = COMPLETED
PHASE_1.gate = PASSED
PHASE_2.status = ACTIVE
PHASE_2.gate = PH2_T01_AWAITING_APPROVAL
active_phase = PHASE_2
active_task = PH2-T01
PHASE_3..PHASE_8.status = LOCKED
```

## 5. Phase 2 çalışma sırası ve onay modeli

### PH2-T01 — Official-source research ve exact implementation planı

Amaç; Phase 2 için kaynak erişimi, veri lisansı/kullanım koşulu, exact toolchain
adayları, dependency etkisi, veri provenance modeli, fail-closed test matrisi ve
dosya bazlı uygulama sırasını araştırıp tek bir onaylanabilir plan üretmektir.

Bu görev research/planning-only'dir. Dependency kurmaz, lock değiştirmez, veri
indirmez ve source/test implementation'ı yazmaz.

### Sonraki Phase 2 görevleri

PH2-T01 tamamlandıktan sonra her implementation görevi:

1. yalnız bir bounded sorumluluk taşımalı;
2. precondition, exact file allowlist, dependency/data yetkisi ve testleri yazmalı;
3. başlamadan önce ayrı insan onayı almalı;
4. önceki görev kapanmadan sonraki göreve ait dosya, dependency, placeholder,
   adapter, interface veya TODO oluşturmamalıdır.

PH2-T01 sonucu onaylanmadan sonraki görev kimlikleri ve dosya kapsamları nihai
kabul edilmez.

## 6. Phase 2 kapsam içi

- Yalnız resmî/açık BTS kaynağı için sürümlü acquisition ve provenance
- Raw byte hash, source metadata, immutable manifest ve tekrar üretilebilirlik
- Fail-closed schema, type, null, uniqueness, domain ve temporal quality gate'leri
- Schedule/input alanları ile outcome/label alanlarının fiziksel ve mantıksal ayrımı
- T-24/T-18/T-12/T-6 as-of availability kontrollerinin veri temeli
- Dondurulmuş train döneminden top-20 havalimanı evreni üretimi
- Deterministik cargo domain varlıkları, invariant'lar ve sentetik generator
- Seed/config/version/hash kontrollü cargo, kapasite ve maliyet snapshot'ları
- Unit, contract, property/invariant ve küçük fixture tabanlı integration testleri
- Veri sözlüğü, lineage, quality raporu ve Phase 2 exit kanıtı

## 7. Phase 2 kesin kapsam dışı

- Model fitting, calibration, MLflow experiment veya model registry
- XGBoost/Logistic Regression eğitimi ve Phase 3 inference implementation'ı
- Pyomo, HiGHS, MILP, assignment, validator veya OR implementation'ı
- Blind replay, outcome reveal, bootstrap veya sensitivity çalıştırması
- FastAPI, PostgreSQL, React, Docker Compose veya deployment
- RAG, embedding, reranker, Ollama, LLM veya Hugging Face inference
- Gerçek Turkish Cargo/THY rezervasyon, kapasite, fiyat veya operasyon verisi
- Ücretli API veya zorunlu managed/cloud servis
- Phase 3+ için erken dependency, interface, adapter, placeholder ya da TODO

## 8. Veri ve güvenlik ilkeleri

- Kaynak URL, erişim zamanı, kullanım koşulu, byte hash ve schema version kaydedilir.
- Ham veri overwrite edilmez; aynı kimlikte farklı byte görülürse fail-closed durulur.
- Outcome alanları feature/input yüzeyinden allowlist ile ayrılır.
- Bir alanın cutoff anında mevcut olduğu kanıtlanamıyorsa feature adayı olamaz.
- Sentetik cargo verisi açıkça `SYNTHETIC` etiketlenir ve gerçek şirket verisi gibi sunulmaz.
- Secret, kişisel veri, kullanıcıya özel absolute path veya dış sistem mutation'ı yoktur.
- Network kullanan acquisition ile offline transform/test adımları ayrılır.

## 9. Phase 2 exit kriterleri

Phase 2 ancak ayrıca planlanacak görevlerin tamamı kapandıktan ve şu kanıtlar
üretildikten sonra `READY_FOR_HUMAN_APPROVAL` olabilir:

- Resmî açık kaynak provenance ve immutable manifest doğrulanmış;
- raw/processed katmanları hash ve schema ile tekrar üretilebilir;
- fail-closed data quality ve leakage guard testleri geçiyor;
- schedule/outcome ayrımı mekanik olarak kanıtlanıyor;
- deterministic cargo/domain snapshot'ı aynı seed/config ile byte-stable;
- bütün Phase 2 contract/invariant testleri başarılı;
- Phase 3+ implementation veya dependency bulunmuyor;
- clean-room ve hosted CI kapıları başarılı;
- checkpoint bütünlüğü doğrulanmış.

Bu kriterlerin geçmesi Phase 3'ü otomatik açmaz. Ayrı exit raporu, exact
transition planı ve açık insan onayı gerekir.

## 10. Stop conditions

Phase 2 çalışması şu durumda durur:

- resmî kaynak, lisans/kullanım koşulu veya schema doğrulanamıyorsa;
- upstream veri beklenmedik biçimde değişmişse;
- label leakage veya schedule/outcome karışması görülürse;
- deterministic tekrar üretim sağlanamıyorsa;
- contract semantiği değişmeden implementation mümkün değilse;
- yeni dependency veya dosya onaylı task allowlist'inde değilse;
- Phase 3+ hazırlığı gerekirse;
- kalite kapısını geçirmek için kural veya test zayıflatmak gerekirse.

## 11. Değişiklik yönetimi

Phase 2 kapsamı, görev onay modeli, normatif contract listesi, veri kaynağı,
determinism/leakage ilkesi veya exit gate değişirse yeni sözleşme sürümü, etki
analizi ve açık insan onayı gerekir.
