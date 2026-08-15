# PH1-T03 Clean-room Doğrulama Raporu

| Alan | Sonuç |
|---|---|
| Görev | `PH1-T03` |
| Yürütme zamanı | `2026-08-14T18:16:02Z` |
| Durum | `LOCAL_PASS — HOSTED_CI_PASS` |
| Referans ortam | Linux x86_64, CPU-only, standard GIL-enabled CPython |
| Kaynak checkpoint | `CargoOpt_Recovery_PH1_T02_Completed.zip` |
| Checkpoint SHA-256 | `42013e718d7d07152de3364c6c8a713646f98a84f4bbc95cdf694a430446dd0d` |

## 1. İzolasyon ve değişmezlik

Doğrulama repository dışındaki tek kullanımlık bir çalışma alanında, önceki
project `.venv` veya repository cache'i taşınmadan yapıldı. `UV_CACHE_DIR`,
`UV_PYTHON_INSTALL_DIR` ve geçici build/audit yolları yalnız bu çalışmaya özel
dizinlere bağlandı. Alternate/private index, insecure host, credential, secret,
global site-package veya Phase 2+ artifact kullanılmadı.

| Dosya | Başlangıç SHA-256 | Bitiş SHA-256 | Sonuç |
|---|---|---|---|
| `pyproject.toml` | `db02c0b9ea47e128a595682da17c9176dac55b9052e900d5dc67084076bc9b6b` | aynı | PASS |
| `uv.lock` | `3f1fce29dd14fac81f56aaea1226131cd93d451c2c2ffe38730171e29e3697b4` | aynı | PASS |
| `src/cargoopt_recovery/__init__.py` | `64772bd814f916477a01504f11a4488a80774184b221fd62cfaa9691f79daabb` | aynı | PASS |
| `tests/test_package_import.py` | `fc2816402ce84ab6180374a793898d404d2ce68ce4cd759e804282e0df696afc` | aynı | PASS |

## 2. Exact toolchain

| Bileşen | Gözlenen değer | Sonuç |
|---|---|---|
| uv | `0.12.3` | PASS |
| Python | CPython `3.14.7` | PASS |
| ABI | `cpython-314`, GIL enabled | PASS |
| Mimari | Linux `x86_64` | PASS |
| Hatchling | `1.32.0` isolated build backend | PASS |
| Ruff | `0.16.3` | PASS |
| mypy | `2.3.0 (compiled: yes)` | PASS |
| pytest | `9.1.1` | PASS |

## 3. İki frozen exact sync

İki koşu da `uv sync --frozen --exact --all-groups` sözleşmesiyle yapıldı.
İlk koşu 12 registry package ile editable local project'i kurdu. İkinci koşu
aynı 13 environment entry'sini kontrol etti ve
ekleme, kaldırma veya güncelleme yapmadı.

| Ölçüm | İlk sync | İkinci sync | Sonuç |
|---|---:|---:|---|
| Süre | `6.001 s` | `3.451 s` | PASS |
| Environment entry | 13 | 13 | PASS |
| Registry package | 12 | 12 | PASS |
| Inventory SHA-256 | `2bdeac8aa53a65a1aab4fd98841a8686ac91298386bc5d97ef46a29146dbb21c` | aynı | PASS |
| Package delta | 13 initial install | `0` | PASS |
| `uv sync --check` | clean | clean | PASS |
| Metadata/lock mutation | yok | yok | PASS |

Aktif Linux envanteri: `ast-serialize 0.8.0`, `iniconfig 2.3.0`,
`librt 0.15.0`, `mypy 2.3.0`, `mypy-extensions 1.1.0`, `packaging 26.3`,
`pathspec 1.1.1`, `pluggy 1.6.0`, `Pygments 2.20.0`, `pytest 9.1.1`,
`ruff 0.16.3`, `typing-extensions 4.16.0` ve editable local project'tir.
Windows marker package'i `colorama 0.4.6` Linux ortamına kurulmadı.

## 4. Kalite ve test kapıları

| Kapı | Exit code | Süre | Sonuç |
|---|---:|---:|---|
| Package import/version | 0 | `0.026 s` | PASS |
| Ruff format | 0 | `0.023 s` | PASS — 35 file formatted |
| Ruff lint | 0 | `0.019 s` | PASS |
| mypy strict | 0 | `0.122 s` | PASS — 2 source file |
| pytest | 0 | `0.244 s` | PASS — 1 test |

Skip, xfail, ignore, suppression, auto-fix veya kalite kuralı zayıflatması
eklenmedi.

## 5. Build ve wheel smoke

Build repository dışına `uv build --no-sources` ile alındı. Üçüncü taraf
source build veya native compiler çağrısı gözlenmedi.

| Artifact | SHA-256 | Sonuç |
|---|---|---|
| `cargoopt_recovery-0.1.0-py3-none-any.whl` | `ef587410c5c6b26c6c90c7734c6786c28b293629d233b63324cc14d2d1ebe840` | PASS |
| `cargoopt_recovery-0.1.0.tar.gz` | `129657f9157d9c9b0a47e7eb29ff12c52da72ce9133ec4fd7852d55ad43e0211` | PASS |

Wheel metadata `cargoopt-recovery 0.1.0`, `Requires-Python: <3.15,>=3.14` ve
`cargoopt_recovery` top-level package değerleriyle eşleşti. Ayrı bir venv'e
yalnız wheel kuruldu ve import/version smoke başarılı oldu.

## 6. Platform sınırı

Bu rapor yalnız Linux x86_64 CPU-only referansını doğrular. Windows x86_64
metadata düzeyinde adaydır fakat yürütülmedi. macOS, ARM, GPU, container ve
free-threaded CPython doğrulanmış değildir.

Hosted parity `Foundation` run `31875871429` ile doğrulandı. Run,
`d4cc97845b66d1ab97c8555d517f7075a966ca33` commit'inde `ubuntu-24.04` image
`20260810.271.1` üzerinde bütün sync, kalite, build, audit, SBOM ve final
integrity adımlarını `success` sonucuyla tamamladı.
