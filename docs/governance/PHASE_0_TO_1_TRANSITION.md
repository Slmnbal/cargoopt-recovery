# Phase 0 → Phase 1 Atomic Transition Kaydı

| Alan | Değer |
|---|---|
| Transition ID | `phase-0-to-1-transition-v1` |
| Tarih | `2026-08-13` |
| Transition görevi | `PH0-T07` |
| Açık insan onayı | “Phase 0’ı kapat ve Phase 1’i aç.” |
| Kaynak checkpoint | `CargoOpt_Recovery_PH0_T06.zip` |
| Kaynak checkpoint SHA-256 | `7ce28d7fc7a7ab127084bd3e7617359c07c0fc859d74b86ae10f9c171403211a` |
| Sonuç | `APPLIED` |

## 1. Precondition kanıtı

| Gate | Koşul | Sonuç |
|---|---|---|
| `TR-G01_CHECKPOINT_HASH` | PH0-T06 SHA-256 exact eşleşti | PASS |
| `TR-G02_ARCHIVE_INTEGRITY` | ZIP içindeki 37 dosya hatasız açıldı | PASS |
| `TR-G03_PHASE0_TASKS` | PH0-T01..PH0-T06 `COMPLETED`, validation sonuçları `PASSED` | PASS |
| `TR-G04_EXIT_GATE` | Phase 0 `READY_FOR_HUMAN_APPROVAL` | PASS |
| `TR-G05_OPEN_BLOCKERS` | Exit audit açık blocker sayısı `0` | PASS |
| `TR-G06_REGISTRY` | 18 benzersiz contract, çözülü referans ve acyclic DAG | PASS |
| `TR-G07_HUMAN_APPROVAL` | Exact phase close/open onayı mevcut | PASS |
| `TR-G08_TASK_PLAN_APPROVAL` | PH0-T07 dosya bazlı atomic plan onaylandı | PASS |

## 2. Atomic state transition

Önce:

```text
active_phase = PHASE_0
active_task = PH0-T07
PHASE_0 = ACTIVE / READY_FOR_HUMAN_APPROVAL
PHASE_1 = LOCKED / BLOCKED_BY_PHASE_0
PHASE_2..PHASE_8 = LOCKED
```

Sonra:

```text
active_phase = PHASE_1
active_task = PH1-T01
PHASE_0 = COMPLETED / PASSED
PHASE_1 = ACTIVE / NOT_READY
PHASE_2..PHASE_8 = LOCKED
```

İki ACTIVE faz veya task'siz ACTIVE Phase 1 ara durumu yayımlanmamıştır.

## 3. Contract lifecycle transition

`cargoopt-contract-registry-v1` içindeki 18 contract:

```text
CANDIDATE_PENDING_PHASE_0_TRANSITION → ACCEPTED
```

durumuna geçirilmiştir. Source artifact başlıkları registry ile mekanik olarak hizalanmıştır. Contract ID, version, owner, implementation phase, dependency, label, cost, constraint, solver, validation, blind replay, statistic, release ve sensitivity semantiği değiştirilmemiştir.

Status-only doğrulaması, PH0-T06 checkpoint gövdesinden status/lifecycle/transition metadata satırlarını normalize ederek semantic body equality kontrolüyle yapılır.

## 4. PH1-T01 aktivasyon sınırı

`PH1-T01` yalnız runtime ve dependency karar araştırması görevidir:

- status `ACTIVE`;
- `execution_requires_separate_human_approval = true`;
- execution approval `AWAITING_EXPLICIT_APPROVAL`;
- dependency ve migration izni `false`;
- `pyproject.toml`, lock, source, test ve CI yasak.

Bu transition PH1-T01 araştırmasını yürütmez ve herhangi bir araç/sürüm seçmez.

## 5. Korumalar

- PHASE_2–PHASE_8 kilitli kalır.
- Contract gövdeleri status dışında immutable kabul edilir.
- PH0-T01..PH0-T06 task kanıtları değiştirilmez.
- Exit audit değiştirilmez.
- Dependency, code, data, model, solver, database, API/UI ve RAG artifact'ı oluşturulmaz.
- PH1-T01 execution ayrı açık onay olmadan başlayamaz.

## 6. Rollback politikası

Transition kaydı overwrite edilmez. Sonradan hata bulunursa phase state sessizce geri alınmaz; yeni governance task'i, etki analizi ve açık insan onayı gerekir. PH0-T06 checkpoint'i recoverable pre-transition referansı olarak korunur.
