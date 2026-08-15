# Phase 1 Exit Raporu

| Alan | Değer |
|---|---|
| Görev | `PH1-T03` |
| Rapor zamanı | `2026-08-15T09:00:30Z` |
| Phase 1 | `COMPLETED` |
| Phase 1 gate | `PASSED` |
| Phase 2 | `ACTIVE / PH2_T01_AWAITING_APPROVAL` |
| Phase 3–8 | `LOCKED` |
| Geçiş kaydı | `phase-1-to-2-transition-v1` / `PH1-T04` |

## 1. Kapı özeti

| Kapı | Sonuç | Kanıt |
|---|---|---|
| Approval/preflight | PASS | CI stack ve görev yürütme onayları; GitHub repository/yazma yetkisi doğrulandı |
| Clean snapshot | PASS | Repository dışı task-specific çalışma alanı |
| Exact runtime/toolchain | PASS | uv `0.12.3`, CPython `3.14.7`, GIL enabled |
| İki frozen exact sync | PASS | İkinci sync delta `0`; inventory/hash eşit |
| Import/format/lint/type/test | PASS | Bütün bağımsız kapılar exit code `0` |
| Wheel/sdist/isolated import | PASS | Metadata ve artifact hash'leri doğrulandı |
| Project/build audit | PASS | 19 audited graph entry; `0` vulnerability/adverse status |
| CycloneDX 1.5 | PASS | 13 ve 6 component SBOM; hash'ler kaydedildi |
| Full license inventory | PASS | 20 component; unknown/yasak/çözümsüz lisans yok |
| Minimal CI workflow | PASS | Approved SHA-pinned read-only workflow çalıştı |
| Hosted success commit | PASS | `d4cc97845b66d1ab97c8555d517f7075a966ca33` |
| Hosted run | PASS | `Foundation` run `31875871429`, attempt `1`, conclusion `success` |

## 2. Değişiklik ve kapsam kontrolü

PH1-T03 yalnız onaylı workflow ve foundation/status belgelerini değiştirir.
`pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `AGENTS.md`,
`src/**`, `tests/**`, Phase 0 sözleşmeleri ve bütün Phase 2+ yüzeyleri değişmez.
Runtime dependency sayısı `0` olarak kalır. Data, ML, OR, solver, API, UI, RAG
veya LLM davranışı eklenmemiştir.

Workflow yalnız `push`/`pull_request` → `main`, `ubuntu-24.04` ve
`permissions: contents: read` kullanır. Action referansları full SHA'dır; cache,
secret, artifact upload, publish, deployment ve repository write yoktur.

## 3. Hosted CI kanıtı

| Alan | Değer |
|---|---|
| Run URL | https://github.com/Slmnbal/cargoopt-recovery/actions/runs/31875871429 |
| Job | `Deterministic foundation gate` / `94991399025` |
| Runner | `ubuntu-24.04`, image `20260810.271.1` |
| Token | `contents: read`, `metadata: read` |
| Checkout SHA | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| setup-uv SHA | `ae62891fec2bb8e7d6c99fc78c9fec3a63790f8d` |
| Toolchain | uv `0.12.3`, managed CPython `3.14.7`, GIL enabled |
| Sync | İlk kurulum 13 environment entry; ikinci sync delta `0` |
| Kalite | format, lint, strict mypy ve 1 pytest PASS |
| Audit | Project 13 + build 6 package; `0` vulnerability/adverse status |
| Artifact upload | `0` |
| Sonuç | `success` |

İlk üç run; sırasıyla job-level context, managed Python bootstrap ve uv version
çıktısındaki platform suffix'i için fail-closed durdu. Her düzeltme ayrı insan
onayıyla, yalnız workflow allowlist'i içinde yapıldı. Başarılı run bütün kapıları
rule weakening olmadan geçti.

## 4. Checkpoint

Başarılı hosted commit state'i repository dışında
`CargoOpt_Recovery_PH1_T03_Hosted_Success.zip` olarak arşivlendi. ZIP integrity
testi geçti; SHA-256 değeri
`193fb70ecb7abbaa57afbc903f4f4928e1f7549712614cf39ceec0ce0f87326f`'tir.

## 5. Exit kararı

`PH1-T03` bütün foundation kapılarını tamamladı. Proje sahibinin ayrı faz geçiş
onayı ve ayrıca onaylanan PH1-T04 atomic planı sonrasında Phase 1
`COMPLETED/PASSED` kapatılmış, Phase 2 `ACTIVE` açılmıştır. `PH2-T01` yalnız
planning/research-only görev olarak aktive edilmiştir; yürütme onayı henüz
verilmemiştir. Phase 3–8 kilitli kalır.

Transition kanıtı `docs/governance/PHASE_1_TO_2_TRANSITION.md`, Phase 2 sınırları
ise `docs/governance/PHASE_2_ENTRY_CONTRACT.md` içinde tutulur.
