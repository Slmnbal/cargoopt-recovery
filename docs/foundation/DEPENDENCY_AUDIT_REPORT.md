# PH1-T03 Dependency, SBOM ve Lisans Raporu

| Alan | Sonuç |
|---|---|
| Görev | `PH1-T03` |
| Yürütme zamanı | `2026-08-14T18:16:02Z` |
| Durum | `LOCAL_PASS — HOSTED_CI_PASS` |
| Audit aracı | `uv 0.12.3` |
| Vulnerability ignore/allowlist | Yok |
| Alternate index/insecure host | Yok |

## 1. Güvenlik denetimi

| Graph | Audited package | Vulnerability | Adverse status | Sonuç |
|---|---:|---:|---:|---|
| Project lock | 13 | 0 | 0 | PASS |
| Isolated Hatchling build graph | 6 | 0 | 0 | PASS |

Project audit JSON SHA-256 değeri
`23651c21394194aeea9ad52c0020de94bc83fe588e157fd36c437c745a16bba5`,
build audit JSON SHA-256 değeri
`c567df537dc6254202f3f16bb96852eeaed45a44f8520ee0d92f20f3cb050425`'tir.
Project audit `4.985 s` içinde exit code `0` ile tamamlandı. `--ignore`,
`--ignore-until-fixed`, suppression veya sürüm override kullanılmadı.

## 2. Graph ve CycloneDX 1.5

Project tree 13 registry component içerir; tree kanıt SHA-256 değeri
`f07a16e96a26a0e4d7e124f8775d8d206129ce9ba852e09f3ed6aec72e095395`'tir.
Isolated build graph tam olarak `hatchling 1.32.0`, `packaging 26.3`,
`pathspec 1.1.1`, `pluggy 1.6.0`, `tomlkit 0.15.1` ve
`trove-classifiers 2026.6.1.19` bileşenlerinden oluşur. Temporary script lock
SHA-256 değeri
`c1624c7f81b38e4ede21857a22bf975bcfb02557f4a49fec0f484dc9ff217ccb`,
build tree kanıt SHA-256 değeri
`b1f7f50803e560f72ccc0dd8b3f030aa3a9a74032e8bb5341389e3aca161f072`'tir.

| SBOM | Spec | Component | SHA-256 | Sonuç |
|---|---|---:|---|---|
| Project | CycloneDX `1.5` | 13 | `3e4a2cc153fe58782e4847e4c712253f3052ea1e173de3f21d8c0f39690f2a44` | PASS |
| Build | CycloneDX `1.5` | 6 | `e7d98881183983b5781bf6e558e9c1d5b75d53c0ca32b0c9d9f6031b9d9981cb` | PASS |

Raw audit/SBOM dosyaları repository'ye alınmamıştır.

## 3. Tam lisans envanteri

`PASS` kararı, exact identity'nin installed metadata ve canonical lisans
kaynağıyla eşleştiğini; yasak veya çözümsüz bir koşul bulunmadığını gösterir.

| Component | Exact identity | Rol/marker | SPDX | Temel yükümlülük | Karar |
|---|---|---|---|---|---|
| CPython | `3.14.7` | runtime | `PSF-2.0` | Lisans ve bildirim metnini koru | PASS |
| uv | `0.12.3` | bootstrap tool | `MIT OR Apache-2.0` | Seçilen lisansın bildirimini koru | PASS |
| ast-serialize | `0.8.0` | Linux project transitive | `MIT` | Lisans/bildirim | PASS |
| colorama | `0.4.6` | Windows marker | `BSD-3-Clause` | Lisans/bildirim; endorsement yok | PASS |
| iniconfig | `2.3.0` | project transitive | `MIT` | Lisans/bildirim | PASS |
| librt | `0.15.0` | CPython 3.14 project transitive | `MIT` | Lisans/bildirim | PASS |
| mypy | `2.3.0` | direct dev | `MIT` | Lisans/bildirim | PASS |
| mypy-extensions | `1.1.0` | project transitive | `MIT` | Lisans/bildirim | PASS |
| packaging | `26.3` | project/build transitive | `Apache-2.0 OR BSD-2-Clause` | Lisans/bildirim; Apache seçilirse NOTICE/patent koşulları | PASS |
| pathspec | `1.1.1` | project/build transitive | `MPL-2.0` | Değiştirilen MPL dosyaları için source yükümlülüğü | PASS |
| pluggy | `1.6.0` | project/build transitive | `MIT` | Lisans/bildirim | PASS |
| Pygments | `2.20.0` | project transitive | `BSD-2-Clause` | Lisans/bildirim | PASS |
| pytest | `9.1.1` | direct dev | `MIT` | Lisans/bildirim | PASS |
| ruff | `0.16.3` | direct dev | `MIT` | Lisans/bildirim | PASS |
| typing-extensions | `4.16.0` | project transitive | `PSF-2.0` | Lisans/bildirim | PASS |
| hatchling | `1.32.0` | isolated build direct | `MIT` | Lisans/bildirim | PASS |
| tomlkit | `0.15.1` | build transitive | `MIT` | Lisans/bildirim | PASS |
| trove-classifiers | `2026.6.1.19` | build transitive | `Apache-2.0` | Lisans/NOTICE; patent koşulları | PASS |
| actions/checkout | `3d3c42e5aac5ba805825da76410c181273ba90b1` | CI action | `MIT` | Lisans/bildirim | PASS |
| astral-sh/setup-uv | `ae62891fec2bb8e7d6c99fc78c9fec3a63790f8d` | CI action | `MIT` | Lisans/bildirim | PASS |

Installed metadata envanterinin SHA-256 değeri
`131aa71532e34c307b56d4c531e83cee7bd02b602c0c52566fc23e2b11207065`'tir.
Unknown, proprietary, noncommercial, research-only, GPL/AGPL, SSPL, BSL veya
çözümsüz lisans girdisi yoktur.

## 4. Sonuç

Local dependency, adverse-status, malware configuration, SBOM ve lisans kapısı
`PASS` sonucundadır. Read-only hosted workflow run `31875871429` aynı project ve
build graph'larını sırasıyla 13 ve 6 package ile taradı; `0` vulnerability ve
`0` adverse status sonucu üretti. Hosted audit JSON hash'leri local audit
hash'leriyle eşleşti; artifact upload yapılmadı.
