# Phase 1 → Phase 2 Atomic Transition Kaydı

| Alan | Değer |
|---|---|
| Transition ID | `phase-1-to-2-transition-v1` |
| Tarih | `2026-08-15` |
| Transition görevi | `PH1-T04` |
| Faz geçiş onayı | “Phase 1’i kapat ve Phase 2’yi aç” |
| Atomic plan onayı | “PH1-T04 atomic transition planını onaylıyorum; uygula.” |
| Kaynak main commit | `f4871063c5480c9b32ce004834f3ff2aa6373fcb` |
| Kaynak hosted run | `Foundation` / `31876120914` / `success` |
| Kaynak checkpoint | `CargoOpt_Recovery_PH1_T03_Hosted_Success.zip` |
| Kaynak checkpoint SHA-256 | `193fb70ecb7abbaa57afbc903f4f4928e1f7549712614cf39ceec0ce0f87326f` |
| Sonuç | `APPLIED` |

## 1. Precondition kanıtı

| Gate | Koşul | Sonuç |
|---|---|---|
| `TR-G01_PHASE1_TASKS` | `PH1-T01..PH1-T03` `COMPLETED` | PASS |
| `TR-G02_EXIT_GATE` | Phase 1 `READY_FOR_HUMAN_APPROVAL` | PASS |
| `TR-G03_HOSTED_CI` | Final main commit için hosted `Foundation` run başarılı | PASS |
| `TR-G04_CHECKPOINT_HASH` | PH1-T03 checkpoint SHA-256 exact eşleşti | PASS |
| `TR-G05_ARCHIVE_INTEGRITY` | Checkpoint ZIP bütünlük testini geçti | PASS |
| `TR-G06_PHASE_BOUNDARY` | Phase 2–8 implementation bulunmuyor | PASS |
| `TR-G07_TRANSITION_APPROVAL` | Ayrı Phase 1 close / Phase 2 open onayı mevcut | PASS |
| `TR-G08_ATOMIC_PLAN_APPROVAL` | PH1-T04 sekiz dosyalık planı ayrıca onaylandı | PASS |

## 2. Atomic state transition

Önce:

```text
active_phase = PHASE_1
active_task = null
PHASE_1 = ACTIVE / READY_FOR_HUMAN_APPROVAL
PHASE_2..PHASE_8 = LOCKED
```

Sonra:

```text
active_phase = PHASE_2
active_task = PH2-T01
PHASE_1 = COMPLETED / PASSED
PHASE_2 = ACTIVE / PH2_T01_AWAITING_APPROVAL
PHASE_3..PHASE_8 = LOCKED
```

İki `ACTIVE` faz, dangling task veya Phase 2'nin görev onayı olmadan yürütüldüğü
bir ara durum yayımlanmamıştır.

## 3. Phase 1 kapanış kanıtı

- Exact standard GIL-enabled CPython `3.14.7` ve `uv 0.12.3` foundation'ı kuruldu.
- Frozen lock ve ikinci sync idempotency kapıları geçti.
- Import, format, lint, strict type, test, isolated build ve wheel import kapıları geçti.
- Project/build dependency audit, SBOM ve full license inventory blocker üretmedi.
- Read-only, SHA-pinned GitHub Actions `Foundation` workflow'u gerçek hosted runner'da geçti.
- Runtime dependency sayısı `0` kaldı; Phase 2+ davranışı erken eklenmedi.

## 4. PH2-T01 aktivasyon sınırı

`PH2-T01` yalnız Phase 2 için official-source research ve exact uygulama planı
görevidir:

- status `ACTIVE`;
- `execution_requires_separate_human_approval = true`;
- execution approval `AWAITING_EXPLICIT_APPROVAL`;
- dependency install/lock, data download ve source implementation izni `false`;
- Phase 3+ model, solver, API/UI ve RAG işi yasak.

Bu transition PH2-T01 araştırmasını yürütmez, araç veya dependency seçmez, veri
indirmez ve implementation dosyası oluşturmaz.

## 5. Korumalar

- `PHASE_3..PHASE_8` kilitli kalır.
- Kabul edilmiş veri/domain/ML/OR/evaluation contract gövdeleri değişmez.
- `PH0-*` ve `PH1-T01..PH1-T03` görev kanıtları değiştirilmez.
- `pyproject.toml`, `uv.lock`, source, tests ve CI workflow byte-identical kalır.
- Her Phase 2 görevi exact file-by-file plan ve ayrı açık insan onayı gerektirir.
- Phase 2 exit sonucu Phase 3'ü otomatik açmaz.

## 6. Rollback politikası

Transition kaydı overwrite edilmez. Sonradan hata bulunursa faz durumu sessizce
geri alınmaz; yeni governance görevi, etki analizi, exact dosya planı ve açık
insan onayı gerekir. PH1-T03 checkpoint'i recoverable pre-transition referansı
olarak korunur.
