# ADR-009 — Runtime ve Repository Foundation Toolchain

| Alan | Değer |
|---|---|
| Durum | Accepted |
| Tarih | 2026-08-13 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | `PH1-T01` |
| Açık insan onayı | 2026-08-13 — exact toolchain onaylandı |
| Sonraki görev | `PH1-T02` — execution onayı bekliyor |

## Bağlam

Phase 1 yalnız güvenilir repository foundation kurar. Doğrudan `pyproject.toml` ve lock üretmek; unsupported runtime, yanked/pre-release paket, lisans belirsizliği, gereksiz future-phase dependency veya clean machine'de çözülemeyen graph riski taşır. Bu nedenle PH1-T01 hiçbir paket indirmeden exact runtime, package manager, build backend ve yalnız foundation kalite araçlarını resmî kaynaklardan seçmekle sınırlandırılmıştır.

Karar aynı zamanda şu sınırları korumalıdır:

- Phase 2–8 dependency veya placeholder'ı yok;
- uygulama runtime dependency'si yok;
- tek package manager ve tek quality role sahibi;
- exact top-level pins ve committed universal lock;
- Linux CPU-first clean-room kurulabilirlik;
- güvenlik/lisans sonucu gözlenmeden Phase 1 exit yok.

## Karar

Onaylanan tek toolchain:

- standard GIL-enabled `CPython 3.14.7`;
- project/package/runtime manager `uv 0.12.3`;
- PEP 517 build backend `Hatchling 1.32.0`;
- formatter/linter/import sorter `Ruff 0.16.3`;
- strict static checker `mypy 2.3.0`;
- test runner `pytest 9.1.1`.

Project metadata minor runtime hattını `>=3.14,<3.15`, developer interpreter pin'ini `3.14.7` olarak taşır. Uygulama `dependencies` listesi boş, development group yalnız Ruff, mypy ve pytest'ten oluşur. Hatch CLI, Black, isort, Flake8, ikinci type checker, pytest plugin, coverage tool, pre-commit ve future-phase paketleri eklenmez.

uv project lock'u canonical PyPI üzerinde upload cutoff ile bir kez çözer. Sonraki doğrulamalar `uv lock --check`, iki `uv sync --frozen`, `uv run --frozen --no-sync`, `uv audit --frozen` ve standard build smoke ile mutation olmadan yapılır.

## Gerekçe

- Python 3.14 current stable bugfix hattıdır; 3.14.7 exact maintenance release'tir ve güvenlik ufku Ekim 2030'dur.
- Bütün foundation araçları Python 3.14 uyumluluğunu canonical metadata ile taşır.
- uv runtime/venv/lock/sync/build/audit işlerini tek araçta birleştirir ve universal lock üretir.
- Hatchling dar, standard-compliant build backend rolünde kalır; project manager rolünü uv ile paylaşmaz.
- Ruff üç ayrı style tool'unu tek dependency/config yüzeyine indirir.
- mypy ve pytest production-stable/mature, Python 3.14 uyumlu ve görev sözleşmesindeki bağımsız type/test gate'lerini karşılar.
- Exact direct pins, upload cutoff ve committed lock çözüm zamanını; frozen/no-sync komutları doğrulama zamanını deterministik sınırlar.
- Yerleşik uv audit yeni bir security scanner dependency'si eklemeden OSV tabanlı gate sağlar.

## Sonuçlar

Olumlu:

- Repository başlangıcı altı exact version ile tekrarlanabilir.
- Runtime application dependency sayısı sıfır kalır.
- Style/type/test sorumlulukları çakışmaz.
- Global interpreter ve extraneous package sızıntısı clean-room exact sync ile yakalanır.
- Phase 2+ teknoloji kararları erkenden verilmez.

Maliyet ve sınırlamalar:

- uv workflow ve lock formatına geçiş maliyeti yüksektir; bu bilinçli tek-tool tercihidir.
- Python 3.14 patch upgrade'i otomatik yapılmaz; ayrı kontrollü bakım işi gerekir.
- Ruff 0.x sürüm hattında bulunduğundan exact pin ve explicit config zorunludur.
- Canonical compatibility yürütülmüş clean-room sonucu değildir; PH1-T02/T03 geçmeden “verified” denemez.
- Direct package metadata incelemesi transitive vulnerability/license kanıtı değildir; lock sonrası audit zorunludur.
- Windows canonical target'tır fakat ayrı runner geçmeden yalnız Linux verified claim kurulabilir.

## Reddedilen alternatifler

- Python 3.15 pre-release kullanmak
- Python 3.13'te kalmak; daha kısa support ufku ve 3.14 foundation compatibility kanıtına rağmen eski minor seçmek
- pip, venv ve pip-tools'u ayrı ayrı pinlemek
- Poetry/PDM veya Hatch CLI ile uv rolünü tekrar etmek
- setuptools fallback'ine dayanmak
- Black + isort + Flake8 kombinasyonu
- mypy yanında Pyright/ty çalıştırmak
- pytest yerine sadece unittest ile daha fazla repository boilerplate'i üretmek
- “sonra gerekir” gerekçesiyle coverage, pre-commit, CI plugin veya future-phase dependency eklemek
- broad version range, `latest`, Git branch veya unpinned source kullanmak

## Uygulama kapıları

Bu ADR 2026-08-13 tarihinde `Accepted` olmuştur. Kabul doğrudan implementation
yetkisi oluşturmaz; PH1-T02 ayrı file-by-file task ve açık execution onayı
gerektirir.

PH1-T02:

1. Exact scaffold allowlist'i onaylatır.
2. `pyproject.toml` ve `uv.lock` aynı görevde üretir.
3. Unexpected graph/native build bulgusunda durur.
4. Minimal package/import/quality local gate'lerini geçirir.

PH1-T03:

1. Fresh Linux environment'ta iki frozen sync ve lock idempotency kanıtlar.
2. Import, format, lint, strict type, test ve build gate'lerini geçirir.
3. Security audit ve full license inventory üretir.
4. Ayrı onaylı minimal CI ile aynı komutları tekrarlar.

## Değişiklik koşulu

Runtime minor/patch, package manager, build backend, direct dev tool, exact pin, source index, upload cutoff, dependency group veya clean-room gate değişirse yeni dependency impact analizi, ADR revizyonu ve açık insan onayı gerekir. Phase 2+ ihtiyaçları bu ADR'yi sessizce genişletemez.
