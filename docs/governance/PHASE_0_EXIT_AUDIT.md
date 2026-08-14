# Phase 0 Exit Audit

| Alan | Değer |
|---|---|
| Audit ID | `phase-0-exit-audit-v1` |
| İlgili görev | `PH0-T06` |
| Audit tarihi | `2026-08-13` |
| İncelenen başlangıç checkpoint'i | `CargoOpt_Recovery_PH0_T05.zip` |
| Başlangıç checkpoint SHA-256 | `01229c9d03e7d0aecaf927d9f995f56853ea6711c8bdc192113204d32180b4ad` |
| Sonuç | `READY_FOR_HUMAN_APPROVAL` |
| Açık blocker | `0` |

## 1. Karar özeti

Phase 0'ın specification ve governance amacı karşılanmıştır. Ürün sınırı, veri/label/feature zamanı, sentetik kargo, maliyet, ML prediction, OR formülü, solver, bağımsız validator, blind replay, istatistik, release ve ikincil sensitivity sınırları implementation öncesinde ölçülebilir sözleşmelere bağlanmıştır.

Bu audit:

- Phase 0'ı kendiliğinden `COMPLETED` yapmaz;
- Phase 1'i açmaz;
- contract header'larını kendiliğinden `Accepted` durumuna yükseltmez;
- kod veya dependency yetkisi vermez.

Yalnızca ayrı phase transition onayına sunulabilirlik kararı verir.

## 2. Audit kapsamı ve yöntem

Başlangıçta PH0-T05 checkpoint'indeki 31 dosya incelendi:

| Artifact sınıfı | Adet |
|---|---:|
| Core governance (`AGENTS`, project spec, phase status) | 3 |
| Tamamlanmış task contract (`PH0-T01..T05`) | 5 |
| Accepted ADR (`ADR-001..ADR-007`) | 7 |
| Data/domain/ML/OR/evaluation normative artifact | 16 |
| Toplam | 31 |

PH0-T06 şu yöntemleri uyguladı:

1. Task completion ve validation result envanteri.
2. Scope içi/dışı maddelerin Project Spec ve AGENTS ile karşılaştırılması.
3. Contract ID, artifact path, owner, implementation phase ve dependency registry'si.
4. Directed dependency graph cycle ve unresolved reference kontrolü.
5. Veri → ML → OR → validator → evaluation boyunca exact invariant izleme.
6. Blind leakage, outcome access, post-reveal mutation ve claim-boundary kontrolü.
7. Project Spec'te adı olup contract'ı olmayan sensitivity analizinin kapatılması.
8. Locked-phase ve forbidden implementation path kontrolü.
9. Phase 1 için dependency-first, clean-room entry kapısının tanımlanması.

## 3. Task completion audit'i

| Task | Konu | Durum | Validation kaydı | Sonuç |
|---|---|---|---:|---|
| `PH0-T01` | Proje kapsamı ve faz yönetişimi | `COMPLETED` | 5 | PASS |
| `PH0-T02` | BTS veri sözleşmesi | `COMPLETED` | 8 | PASS |
| `PH0-T03` | Domain, sentetik cargo, ML ve OR input | `COMPLETED` | 14 | PASS |
| `PH0-T04` | OR model, solver ve validator | `COMPLETED` | 17 | PASS |
| `PH0-T05` | Blind replay, istatistik ve release | `COMPLETED` | 15 | PASS |
| `PH0-T06` | Exit audit, sensitivity ve Phase 1 entry | Kapanışta `COMPLETED` | Kapanış kaydı | PASS koşullu tamamlandı |

Task ID dizisi ardışıktır. Aynı anda birden fazla aktif task veya faz yoktur.

## 4. Contract registry sonucu

`CONTRACT_REGISTRY.yaml` içinde:

| Kontrol | Sonuç |
|---|---|
| Registry contract sayısı | 18 |
| Benzersiz contract ID | PASS |
| Benzersiz ve mevcut artifact path | PASS |
| Her contract için tek owner component | PASS |
| Her contract için implementation phase | PASS |
| Normative dependency referansları | PASS |
| Informational reference çözümü | PASS |
| Superseded identifier çözümü | PASS |
| Directed graph cycle | Yok — PASS |

Registry lifecycle status'ları transition onayına kadar `CANDIDATE_PENDING_PHASE_0_TRANSITION` olarak kalır. Bu, kaynak belgelerdeki `Accepted Candidate` ifadeleriyle uyumludur.

## 5. Uçtan uca invariant audit'i

| Invariant ID | Kilit karar | Normative kaynaklar | Implementation kapısı | Sonuç |
|---|---|---|---|---|
| `INV-001` | Tek binary label: cancellation/diversion/arrival delay ≥60 | BTS, feature, prediction | Phase 2/3 label golden tests | PASS |
| `INV-002` | Source recovery kararı T-6 | Project Spec, prediction, domain | Phase 2/3 cutoff tests | PASS |
| `INV-003` | Candidate forecast ceiling horizon 24/18/12/6 | Feature, prediction, OR input | Phase 3 boundary tests | PASS |
| `INV-004` | Target outcome feature/plan girdisi olamaz | BTS, data quality, prediction, blind replay | Leakage/metamorphic tests | PASS |
| `INV-005` | Partition train/validation/test/blind takvim bazlı ve immutable | BTS, prediction, blind replay | Snapshot/split tests | PASS |
| `INV-006` | Cargo, capacity, SLA ve TRY maliyet sentetik | Domain, synthetic cargo, cost policy | Generator/cost golden tests | PASS |
| `INV-007` | Split shipment yok; exact assignment veya UNASSIGNED | Domain, OR input, math | OR/validator mutation tests | PASS |
| `INV-008` | İki MILP aynı set/constraint/input; yalnız risk terimi farklı | Cost, math, OR output | Objective-diff test | PASS |
| `INV-009` | Solver maliyeti integer kuruş | Cost, math, solver, validator | Exact reconciliation tests | PASS |
| `INV-010` | Timeout optimal değildir; no incumbent no plan | Solver, OR output, validator | Status mapping tests | PASS |
| `INV-011` | Validator solver/Pyomo state'inden bağımsız | Validator, ADR-006 | Import boundary/mutation tests | PASS |
| `INV-012` | Roster outcome ve probability ile seçilemez | Blind replay, ADR-007 | Roster metamorphic tests | PASS |
| `INV-013` | Bütün primary planlar full reveal öncesi dondurulur | Blind replay, release gate | Freeze/reveal tests | PASS |
| `INV-014` | Primary fark ML minus risk-blind; negative ML lehine | Metrics, evaluation output | Formula/golden tests | PASS |
| `INV-015` | Date-cluster bootstrap 10.000/seed 20240831/R-7 | Metrics, evaluation output | Golden vector/quantile tests | PASS |
| `INV-016` | ML adoption bütün integrity/evidence/impact gate'lerine bağlı | Release gate, evaluation output | Boundary truth-table tests | PASS |
| `INV-017` | Sensitivity secondary ve primary policy'yi değiştiremez | Sensitivity, ADR-008 | Isolation/output-schema tests | PASS |
| `INV-018` | RAG salt okunur ve yalnız Phase 8 | AGENTS, Project Spec | Phase 8 entry gate | PASS |

Her invariant tekil ID'ye ve ileride çalıştırılacak en az bir test ailesine sahiptir.

## 6. Scope traceability matrisi

| Requirement ID | Project ihtiyacı | Normative artifact | Uygulama fazı | Exit sonucu |
|---|---|---|---|---|
| `REQ-001` | Resmî açık uçuş kaynağı ve provenance | BTS contract | Phase 2 | COVERED |
| `REQ-002` | Fail-closed veri kalitesi | Data quality contract | Phase 2 | COVERED |
| `REQ-003` | Sentetik cargo/domain dürüstlüğü | Cargo domain + synthetic cargo | Phase 2 | COVERED |
| `REQ-004` | As-of leakage-free feature | Feature availability | Phase 2 | COVERED |
| `REQ-005` | Kalibre multi-horizon risk olasılığı | Prediction contract | Phase 3 | COVERED |
| `REQ-006` | Sentetik nominal TRY maliyeti | Cost policy | Phase 4 | COVERED |
| `REQ-007` | Greedy ve iki MILP karşılaştırması | Math contract | Phase 4 | COVERED |
| `REQ-008` | HiGHS timeout/gap/status dürüstlüğü | Solver contract | Phase 4 | COVERED |
| `REQ-009` | Bağımsız feasibility/cost validator | Validator contract | Phase 4 | COVERED |
| `REQ-010` | Immutable plan/output artifact | OR output schema | Phase 4 | COVERED |
| `REQ-011` | Outcome-blind historical replay | Blind replay contract | Phase 5 | COVERED |
| `REQ-012` | Paired istatistiksel değerlendirme | Metrics/statistics contract | Phase 5 | COVERED |
| `REQ-013` | Önceden tanımlı policy release kararı | Release gate + evaluation schema | Phase 5 | COVERED |
| `REQ-014` | Scope-controlled robustness analizi | Sensitivity contract | Phase 5 | COVERED |
| `REQ-015` | Güvenilir repository başlangıcı | Phase 1 entry contract | Phase 1 | COVERED |
| `REQ-016` | API/UI ile doğrulanmış karar sunumu | Project Spec responsibility boundary | Phase 6 | DEFERRED_BY_PHASE_LOCK |
| `REQ-017` | Hardening ve portfolio evidence | Project Spec phase boundary | Phase 7 | DEFERRED_BY_PHASE_LOCK |
| `REQ-018` | Salt okunur Türkçe RAG + LLM Copilot | AGENTS + Project Spec Phase 8 boundary | Phase 8 | DEFERRED_BY_PHASE_LOCK |

`DEFERRED_BY_PHASE_LOCK`, eksik implementation değildir; erken klasör, dependency veya placeholder üretimini önleyen bilinçli governance kararıdır.

## 7. Sensitivity gap çözümü

Başlangıç audit'inde Project Spec kapsamındaki “sensitivity analysis” için exact scenario, strategy ve primary-policy ayrımı bulunmadığı görüldü. Bu, sonuç sonrası grid seçimi ve scope creep riskiydi.

`evaluation-sensitivity-v1` ile:

- yalnız iki MILP;
- exact dört non-baseline OFAT scenario;
- disruption consequence `0.75/1.25`;
- available capacity `0.90/1.10`;
- joint grid ve adaptive search yasağı;
- planner/outcome ayrımı;
- scenario plan freeze öncesi outcome join yasağı;
- descriptive metrikler ve primary policy immutable kuralı

kilitlendi. Gap `RESOLVED` durumundadır.

## 8. Phase 1 readiness sonucu

`phase-1-entry-v1` şu profesyonel başlangıç sırasını kilitler:

1. Runtime/dependency kararı ve official compatibility/license kanıtı — dependency eklemeden.
2. Onaylanan exact sürümlerle minimal scaffold ve lock.
3. Fresh-environment frozen sync, import, lint, type, test ve minimal CI kapısı.

Phase 1'de data, ML, OR, API, UI, database, Docker veya RAG placeholder'ı yasaktır. Bu nedenle Phase 1 entry tasarımı sonraki faz implementation'ını erkenden başlatmaz.

## 9. Finding kaydı

| Finding ID | Seviye | Bulgu | Karar/owner | Durum |
|---|---|---|---|---|
| `F-001` | BLOCKER | Sensitivity scenario sınırı yoktu | PH0-T06 sensitivity contract | RESOLVED |
| `F-002` | OBSERVATION | Data quality ve prediction başlığında explicit status satırı yok | Registry lifecycle alanı; transition task'ta mekanik hizalama önerilir | OPEN_NON_BLOCKING |
| `F-003` | OBSERVATION | Contract header'ları candidate durumda | Human Phase 0 transition öncesi beklenen durum | EXPECTED |
| `F-004` | DEFERRED | Exact Python/package sürümleri seçilmedi | PH1-T01 official-source compatibility kararı | CONTROLLED_DEFERRED |
| `F-005` | DEFERRED | BTS source availability ve gerçek row quality henüz yürütülmedi | Phase 2 ingestion gate | CONTROLLED_DEFERRED |
| `F-006` | DEFERRED | Blind triggered sample büyüklüğü bilinmiyor | Phase 5 insufficient-evidence policy | CONTROLLED_DEFERRED |
| `F-007` | DEFERRED | RAG teknik contract'ı oluşturulmadı | Yalnız Phase 8 entry sonrası | CONTROLLED_DEFERRED |

Audit sonunda açık `BLOCKER = 0`'dır. Observation ve controlled-deferred maddeler Phase 0 çıkışını engellemez; sahipleri ve uygulanacak fazları bellidir.

## 10. Forbidden-path ve erken uygulama kontrolü

Phase 0 sonunda aşağıdakiler bulunmamalıdır:

```text
pyproject.toml
uv.lock
docker-compose.yml
src/
tests/
frontend/
migrations/
knowledge/
```

Dependency, model, data, solver, database, API/UI veya RAG artifact'ı oluşturulmamıştır. Bu kontrol checkpoint kapanışında tekrar çalıştırılır.

## 11. Exit gate kontrol listesi

| Gate | Koşul | Sonuç |
|---|---|---|
| `P0-G01_TASKS_COMPLETE` | PH0-T01..T06 tamamlandı | PASS |
| `P0-G02_SCOPE_FROZEN` | Kapsam içi/dışı sınırlar ölçülebilir | PASS |
| `P0-G03_CONTRACT_REGISTRY` | ID/path/owner/phase kayıtlı | PASS |
| `P0-G04_DEPENDENCY_DAG` | Referans çözülü, cycle yok | PASS |
| `P0-G05_DATA_ML_OR_COHERENCE` | Label/time/cost/input invariant'ları tutarlı | PASS |
| `P0-G06_BLIND_INTEGRITY` | Roster/freeze/reveal/missingness kilitli | PASS |
| `P0-G07_STATISTICAL_POLICY` | Primary metric/bootstrap/release kapısı kilitli | PASS |
| `P0-G08_SENSITIVITY_BOUNDARY` | Secondary OFAT sınırı kilitli | PASS |
| `P0-G09_PHASE1_ENTRY` | Dependency-first clean-room kapısı tanımlı | PASS |
| `P0-G10_LOCKED_PHASES` | Phase 1–8 kilitli ve erken artifact yok | PASS |
| `P0-G11_OPEN_BLOCKERS` | Açık blocker sayısı sıfır | PASS |
| `P0-G12_CHECKPOINT_INTEGRITY` | PH0-T06 ZIP test/hash başarılı | PASS |

`P0-G12`, checkpoint oluşturma ve test sonucunun PH0-T06 task validation kaydına yazılmasıyla kapanmıştır.

## 12. Phase transition için gereken ayrı karar

Audit sonucu yalnız şunu önerir:

> Phase 0, proje sahibinin ayrı açık onayına sunulmaya hazırdır.

Onay verilirse transition görevi en az:

- Phase 0'ı `COMPLETED/PASSED`;
- Phase 1'i `ACTIVE/NOT_READY`;
- registry lifecycle'ını `ACCEPTED`;
- candidate contract header'larını tutarlı final duruma;
- active task'i onaylanan ilk Phase 1 görevine

getirmeli ve yeni checkpoint üretmelidir.

Bu audit o mutation'ı gerçekleştirmez.

## 13. Nihai sınırlamalar

- Belge tutarlılığı implementation doğruluğunun yerine geçmez; sonraki faz testleri zorunludur.
- Açık BTS verisi ABD iç hat yolcu operasyonlarını temsil eder, Turkish Cargo değildir.
- Cargo, capacity, SLA ve maliyetler sentetiktir.
- Üretilecek sistem canlı operasyon sistemi veya production-ready ürün değildir; production-oriented prototype'tır.
- Phase 8 RAG katmanı çekirdek karar yetkisi kazanamaz.

## 14. Audit değişiklik yönetimi

Phase 0 kapsamı veya registry'deki normative contract'lardan biri transition öncesi değişirse bu audit yeniden çalıştırılır ve sonuç hash'i yenilenir. Açık blocker ortaya çıkarsa gate tekrar `NOT_READY` veya `BLOCKED` olur; başarı eşiği zayıflatılamaz.
