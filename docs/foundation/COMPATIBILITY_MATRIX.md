# Foundation Compatibility Matrix

| Alan | Değer |
|---|---|
| Görev | `PH1-T01`, `PH1-T02`, `PH1-T03` |
| Araştırma tarihi | 2026-08-13 |
| Durum | PH1-T03 Linux clean-room ve GitHub-hosted CI dahil bütün foundation kapıları geçti |
| Primary reference | Linux x86_64, CPU-only, standard GIL-enabled CPython |

## 1. Ortak runtime matrisi

| Bileşen | Exact sürüm | Canonical Python sınırı | Python 3.14 kanıtı | Linux x86_64 | Windows x86_64 | Belgesel sonuç |
|---|---:|---|---|---|---|---|
| CPython | `3.14.7` | `3.14.x` | Resmî maintenance release | Resmî source; uv-managed distribution hedefi | Resmî 64-bit installer | PASS |
| uv | `0.12.3` | PyPI install için `>=3.8` | PyPI classifier `3.14` | manylinux wheel/standalone binary | win_amd64 wheel/standalone binary | PASS |
| Hatchling | `1.32.0` | `>=3.10` | PyPI classifier `3.14` | OS independent | OS independent | PASS |
| Ruff | `0.16.3` | `>=3.7` | Proje README'si açık 3.14 compatibility bildirir | Platform wheel | Platform wheel | PASS |
| mypy | `2.3.0` | `>=3.10` | PyPI classifier ve `cp314` wheel'ler | cp314 manylinux wheel | cp314 win_amd64 wheel | PASS |
| pytest | `9.1.1` | `>=3.10` | Canonical classifier `3.14` | POSIX/Linux classifier; pure Python wheel | Windows classifier; pure Python wheel | PASS |

Ortak kesişim `CPython 3.14`'tür. Seçilen exact patch `3.14.7` bu kesişim içindedir. Hiçbir doğrudan araç pre-release Python veya unsupported interpreter istemez.

## 2. Referans environment kararı

| Boyut | Karar | Gerekçe |
|---|---|---|
| Interpreter | Standard CPython `3.14.7` | Tek ABI hattı; free-threaded varyant yok |
| Primary OS | Linux x86_64 | CPU-first local/CI referansı ve en dar başlangıç yüzeyi |
| Secondary OS | Windows x86_64 | Aday araçların canonical desteği var; yürütülmüş destek iddiası ancak ayrı T03 job sonucu ile kurulur |
| CPU/GPU | CPU-only | Foundation aracı GPU istemez; CUDA/driver kapsam dışıdır |
| Package index | Canonical PyPI | Alternate/private index veya Git dependency yok |
| Build isolation | PEP 517 default isolation | Build dependency'nin global interpreter'dan sızmasını engeller |
| Native compiler | Beklenmiyor | Supported wheels kullanılır; sdist fallback veya local Rust/C build blocker'dır |

## 3. Marker ve transitive davranış

İlk tablo PH1-T01 ön analizini, ikinci tablo PH1-T02 gözlenen project lock
sonucunu gösterir. PEP 517 build dependency'leri project lock'a dahil olmadığı
için Hatchling graph'ı isolated build smoke sırasında ayrıca doğrulanacaktır.

| Kaynak | Python 3.14 Linux'ta beklenen marker sonucu | Windows farkı | Lock doğrulama kuralı |
|---|---|---|---|
| Hatchling | `tomli` dışarıda; `packaging`, `pathspec`, `pluggy`, `tomlkit`, `trove-classifiers` içeride | Beklenen fark yok | PH1-T02 graph ile exact doğrula |
| mypy | `tomli` dışarıda; `typing_extensions`, `mypy_extensions`, `pathspec`, `librt`, `ast-serialize` içeride | Platform wheel değişir | cp314 wheel seçilmeli; local compiler olmamalı |
| pytest | `exceptiongroup`, `tomli`, `colorama` dışarıda; dört pure-Python dependency içeride | `colorama` eklenir | Universal lock marker'ı korumalı |
| Ruff | Python transitive dependency beklenmiyor | Platform wheel değişir | Rust source build'e düşülmemeli |
| uv | Project lock'a girmez | Bootstrap binary değişir | Her OS'te executable sürümü exact kontrol edilir |

### PH1-T02 gözlenen project lock

| Ölçüm | Sonuç |
|---|---|
| Resolver/runtime | `uv 0.12.3` / standard GIL-enabled `CPython 3.14.7` |
| Lock hash | `3f1fce29dd14fac81f56aaea1226131cd93d451c2c2ffe38730171e29e3697b4` |
| Toplam entry | 14: 1 local project + 13 canonical PyPI package |
| Direct dev package | `mypy 2.3.0`, `pytest 9.1.1`, `ruff 0.16.3` |
| Linux aktif transitive | 9 |
| Universal Windows marker farkı | `colorama 0.4.6` |
| Source policy | Git, URL, path dependency veya alternate index yok |
| Pre-release/yanked | Pre-release yok; resolver yanked uyarısı yok |
| Linux CPython 3.14 wheel | Bütün aktif registry package'ları için uyumlu wheel mevcut |
| Compiler fallback | Beklenmiyor; gerçek sonuç frozen `--no-build` sync ile doğrulanacak |

## 4. Uyum kapıları

Belgesel `PASS`, paketin gerçekten kurulup çalıştığı anlamına gelmez. Aşağıdaki sonuçların tamamı `PH1-T02/PH1-T03` içinde gözlenmeden Phase 1 exit olamaz:

1. `PASS` — `uv 0.12.3` exact executable doğrulaması.
2. `PASS` — uv-managed standard CPython `3.14.7`; GIL açık ve cache tag `cpython-314`.
3. `PASS` — `uv lock --check`; lock hash mutation yok.
4. `PASS` — Linux x86_64 fresh environment'ta iki frozen exact sync.
5. `PASS` — Lock ve environment'ın ikinci sync'te değişmemesi; package delta `0`.
6. `PASS` — Local editable project dışında üçüncü taraf source build veya native compiler yok.
7. `PASS` — Import, Ruff format/lint, mypy strict, pytest ve isolated wheel import.
8. `PASS` — Project/build graph audit, CycloneDX 1.5 ve full license inventory.
9. `PENDING/UNVERIFIED` — Windows x86_64 clean job.

Bir transitive dependency Python 3.14 ile çözülemezse broad range, override veya test zayıflatma yapılmaz; task durur ve toolchain kararı revize edilir.

## 5. Kaynaklar

| Kaynak | Erişim | Kullanım |
|---|---|---|
| https://www.python.org/downloads/release/python-3147/ | 2026-08-13 | CPython exact release ve platform artifact'ları |
| https://devguide.python.org/versions/ | 2026-08-13 | Stable branch durumu |
| https://pypi.org/project/uv/ | 2026-08-13 | uv version/Python/platform metadata |
| https://pypi.org/project/hatchling/ | 2026-08-13 | Hatchling Python ve OS metadata |
| https://pypi.org/project/ruff/ | 2026-08-13 | Ruff Python ve wheel metadata |
| https://github.com/astral-sh/ruff | 2026-08-13 | Açık Python 3.14 compatibility bildirimi |
| https://pypi.org/project/mypy/ | 2026-08-13 | mypy Python classifier ve cp314 wheels |
| https://pypi.org/project/pytest/ | 2026-08-13 | pytest Python/OS metadata |
| https://docs.astral.sh/uv/concepts/resolution/ | 2026-08-13 | Universal resolution ve platform marker davranışı |
| https://peps.python.org/pep-0517/ | 2026-08-13 | Isolated build environment modeli |
