# Runtime ve Toolchain Karar Dosyası

| Alan | Değer |
|---|---|
| Görev | `PH1-T01` |
| Araştırma tarihi | 2026-08-13 |
| Durum | `APPROVED — PH1-T02_EXECUTION_PENDING` |
| Kaynak politikası | Yalnız resmî primary source ve canonical PyPI metadata |
| Kurulum/lock durumu | Bu görevde çalıştırılmadı; `PH1-T02` öncesi yasak |
| Açık insan onayı | 2026-08-13 — exact toolchain onaylandı |
| Onay kaynağı | `explicit_user_exact_toolchain_approval` |

## 1. Tek öneri

CargoOpt Recovery repository foundation için tek aday toolchain aşağıdadır:

| Katman | Seçim | Exact sürüm | Repository bildirimi |
|---|---|---:|---|
| Runtime | Standard, GIL-enabled CPython | `3.14.7` | `.python-version = 3.14.7`; `requires-python = ">=3.14,<3.15"` |
| Project/package manager | uv | `0.12.3` | Repository dışı bootstrap aracı; sürüm yürütme başında doğrulanır |
| Build backend | Hatchling | `1.32.0` | `hatchling==1.32.0` |
| Formatter + linter + import sorter | Ruff | `0.16.3` | `ruff==0.16.3` development dependency |
| Static type checker | mypy | `2.3.0` | `mypy==2.3.0` development dependency |
| Test runner | pytest | `9.1.1` | `pytest==9.1.1` development dependency |

Uygulama runtime doğrudan dependency listesi bu fazda bilinçli olarak boştur. Python standard library dışında ürün davranışı sağlayan hiçbir paket seçilmemiştir.

## 2. Python kararı

`CPython 3.14.7` seçilmiştir çünkü:

- Python Developer's Guide, 3.14 dalını `bugfix` yani stable maintenance durumunda gösterir; 3.15 hâlâ pre-release'tir.
- 3.14.7, 5 Ağustos 2026 tarihli resmî maintenance sürümüdür; pre-release veya yanked değildir.
- 3.14 hattı yaklaşık Ekim 2030'a kadar güvenlik güncellemesi alacaktır.
- Seçilen beş foundation aracının tamamı Python 3.14 desteğini canonical metadata veya resmî proje sayfasında açıkça taşır.
- Exact patch `.python-version` ile tekrarlanabilir başlangıç sağlanırken `requires-python` minor hat üzerinde tutulur. Patch yükseltmesi otomatik değildir; ayrı dependency-change görevi ve clean-room doğrulaması gerektirir.

Free-threaded `3.14t`, experimental JIT veya source-build runtime seçilmemiştir. Referans runtime standard GIL-enabled CPython'dır; bu karar foundation aşamasında ABI ve native-wheel varyasyonunu azaltır.

## 3. Package manager kararı

`uv 0.12.3` tek project/package manager olarak seçilmiştir:

- Python runtime yönetimi, virtual environment, PEP 735 development group, universal lock, exact sync, build ve tool execution aynı araçta birleşir.
- `uv.lock` platformlar arası universal resolution taşır.
- `uv lock --check`, metadata ile lock uyumsuzsa hata verir.
- `uv sync --frozen`, mevcut lock'u source of truth kabul eder ve lock'u değiştirmez.
- `uv sync` varsayılan olarak exact sync yapar; lock dışında kalan extraneous paketleri kaldırır.
- `uv audit` bilinen vulnerability ve adverse package status kontrolünü yerleşik sağlar; ek security dependency gerekmez.

uv, project runtime veya development dependency değildir. Bootstrap executable olarak exact `0.12.3` kullanılır ve `uv --version` eşitliği her doğrulama başında kontrol edilir.

## 4. Build backend kararı

`Hatchling 1.32.0` seçilmiştir. Gerekçeler:

- PyPA packaging tutorial'ının varsayılan örnek backend'idir.
- PEP 517 uyumlu ve `src` layout için ek framework gerektirmeyen dar bir build backend'dir.
- Canonical metadata Python `>=3.10` ve Python 3.14 classifier'ı taşır.
- `hatchling.build` açık backend entry point'idir.
- Build frontend olarak ayrıca `build` paketi eklenmez; `uv build` kullanılır.

Hatch CLI seçilmemiştir. Yalnız build backend olan Hatchling kullanılacaktır; environment, script veya publishing yönetimi uv'de kalır.

## 5. Quality tool kararı

### Ruff 0.16.3

Tek araçla format check, lint ve import ordering sağlanır. Black, isort, Flake8, pyupgrade ve ayrı plugin paketi eklenmez. Ruff canonical sayfası Python 3.14 compatibility bildirir; PyPI paketi MIT lisanslıdır ve Python `>=3.7` ister.

### mypy 2.3.0

Strict static type gate için seçilmiştir. Canonical PyPI metadata Python `>=3.10`, Python 3.14 classifier'ı ve CPython 3.14 wheel'leri gösterir. Pyright veya ikinci type checker eklenmez; iki checker'ın farklı semantiklerini aynı foundation gate'inde yönetme maliyeti alınmaz.

### pytest 9.1.1

Minimal smoke/unit test runner olarak seçilmiştir. Canonical metadata Python `>=3.10`, Python 3.14 classifier'ı, MIT lisans ve mature/maintained proje sinyali taşır. Plugin, coverage veya parallel-runner eklenmez; bu özellikler aktif Phase 1 gereksinimi değildir.

## 6. Determinizm sözleşmesi

`PH1-T02` yalnız insan onayından sonra aşağıdaki kurallarla scaffold ve lock üretir:

1. Direct package bildirimleri `==` exact pin kullanır.
2. Runtime `.python-version` içinde `3.14.7` olarak pinlenir.
3. Project compatibility `>=3.14,<3.15` ile yalnız 3.14 minor hattına sınırlandırılır.
4. İlk resolution yalnız canonical PyPI index üzerinden, `2026-08-13T23:59:59Z` upload cutoff ile yapılır.
5. Git URL, branch, local path override, editable external dependency ve alternate untrusted index kullanılmaz.
6. `uv.lock` aynı görevde `pyproject.toml` ile birlikte üretilir ve commit edilir.
7. Normal doğrulama lock üretmez: önce `uv lock --check`, ardından `uv sync --frozen` çalışır.
8. Her `uv run` kalite komutu `--frozen --no-sync` ile çalışarak test sırasında metadata/lock/environment mutation'ını engeller.
9. Paket upgrade'i ancak ayrı onaylı görev, release/compatibility/license/security etki analizi ve yeniden clean-room gate ile yapılır.

## 7. Güvenlik ve supply-chain sınırı

Bu araştırma package indirip çözmediği için “lock graph güvenlidir” iddiası kurmaz. Doğrudan adayların canonical release metadata, lisans, supported Python ve proje security-policy yüzeyleri incelenmiştir. Executable sonuç `PH1-T03` içinde zorunludur:

- `uv audit --frozen` exit code `0`;
- ignore/allowlist olmaması;
- sync sırasında OSV tabanlı malware check'in açık olması;
- lock'taki bütün doğrudan ve transitive paketler için license inventory;
- yanked, deprecated, quarantined veya bilinen vulnerability bulgusunun blocker sayılması.

Bir finding sessizce ignore edilemez. Çözüm sürüm değişikliği gerektirirse mevcut task durur ve yeni dependency approval istenir.

## 8. Seçilmemiş alternatifler

| Alternatif | Seçilmeme nedeni |
|---|---|
| Python 3.15 pre-release | Stable değildir; giriş sözleşmesi pre-release'i yasaklar |
| Python 3.13 | Foundation araçları 3.14'ü açıkça destekler; 3.14 daha uzun maintenance/security ufku sunar |
| pip + venv + pip-tools | Runtime, resolver, lock ve environment görevlerini birden çok araca böler |
| Poetry/PDM | Foundation ihtiyacı için ikinci orchestration katmanı ve ek removal cost yaratır |
| setuptools | Hatchling'e göre legacy/fallback yüzeyi daha geniş; bu projede extension build ihtiyacı yok |
| Hatch CLI | uv ile environment/project management rolünü tekrarlar |
| Black + isort + Flake8 | Ruff'ın kapsadığı işleri üç ayrı dependency/config yüzeyine böler |
| Pyright/ty | myPy ile aynı rolü tekrarlar; ikinci checker aktif gereksinim değildir |
| unittest | Standard library avantajlıdır; ancak fixture/parametrization ve okunabilir test discovery standardı için pytest daha düşük proje içi boilerplate sunar |
| pytest-cov/coverage | Phase 1 exit sözleşmesinde coverage threshold yoktur; erken ek paket scope creep olur |
| pre-commit | Local hook kurulumu foundation kalite komutlarının correctness önkoşulu değildir |

## 9. Kesin kapsam dışı

Bu karar pandas, Polars, scikit-learn, XGBoost, MLflow, Pyomo, HiGHS, FastAPI, PostgreSQL, React, Docker, Hugging Face, embedding, RAG veya LLM paketi seçmez. Bu isimler dependency catalog veya scaffold'a eklenemez.

## 10. Kaynak kayıtları

| URL | Erişim | Desteklenen iddia |
|---|---|---|
| https://devguide.python.org/versions/ | 2026-08-13 | Python 3.14 bugfix/stable; 3.15 pre-release; EOL tarihleri |
| https://peps.python.org/pep-0745/ | 2026-08-13 | 3.14.7 release tarihi ve 3.14 lifecycle |
| https://www.python.org/downloads/release/python-3147/ | 2026-08-13 | Exact 3.14.7 maintenance release metadata |
| https://pypi.org/project/uv/ | 2026-08-13 | uv 0.12.3, release tarihi, lisans, Python ve platform metadata |
| https://docs.astral.sh/uv/concepts/projects/sync/ | 2026-08-13 | Lock check, frozen/locked ve exact sync semantiği |
| https://docs.astral.sh/uv/concepts/resolution/ | 2026-08-13 | Universal lock portability |
| https://docs.astral.sh/uv/reference/cli/ | 2026-08-13 | `uv audit`, `--frozen`, `--locked`, `--managed-python` davranışları |
| https://pypi.org/project/hatchling/ | 2026-08-13 | Hatchling 1.32.0, Python support, lisans, release metadata |
| https://github.com/pypa/hatch/blob/master/backend/pyproject.toml | 2026-08-13 | Hatchling canonical direct dependencies ve Python classifier'ları |
| https://packaging.python.org/en/latest/tutorials/packaging-projects/ | 2026-08-13 | PyPA build backend örneği ve Hatchling entry point |
| https://peps.python.org/pep-0517/ | 2026-08-13 | Isolated build backend modeli |
| https://pypi.org/project/ruff/ | 2026-08-13 | Ruff 0.16.3, lisans, Python gereksinimi ve release metadata |
| https://github.com/astral-sh/ruff | 2026-08-13 | Python 3.14 compatibility ve birleşik formatter/linter rolü |
| https://pypi.org/project/mypy/ | 2026-08-13 | mypy 2.3.0, lisans, Python 3.14 classifier ve wheel'ler |
| https://github.com/python/mypy/blob/master/pyproject.toml | 2026-08-13 | Canonical dependency marker'ları ve Python support |
| https://pypi.org/project/pytest/ | 2026-08-13 | pytest 9.1.1, lisans, Python gereksinimi ve release metadata |
| https://github.com/pytest-dev/pytest/blob/main/pyproject.toml | 2026-08-13 | Canonical dependency marker'ları ve Python 3.14 classifier |
| https://osv.dev/ | 2026-08-13 | Açık kaynak vulnerability veri tabanı; executable kontrol `uv audit` ile yapılacak |

## 11. Onay ve uygulama kapısı

Proje sahibi exact toolchain'i 2026-08-13 tarihinde açıkça onaylamıştır. Bu onay
`PH1-T01` kararını kapatır ve `PH1-T02` görev planının hazırlanmasına izin verir;
scaffold uygulamasını, dependency indirmeyi, environment oluşturmayı veya lock
üretmeyi tek başına yetkilendirmez. Bunlar ancak `PH1-T02` görev sözleşmesi için
ayrı ve açık execution onayından sonra yapılabilir.
