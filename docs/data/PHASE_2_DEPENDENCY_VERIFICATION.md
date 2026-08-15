# Phase 2 Dependency Verification

## Karar

PH2-T03 exact dependency candidate, onaylı beş paket dışında dependency eklemeden ve
mevcut 13 external lock package'ının çözüm semantiğini değiştirmeden hosted doğrulama
kapılarından geçti. Doğrulanmış `pyproject.toml` ve `uv.lock` repository'ye alınmıştır.

Bu belge yalnız sanitize edilmiş dependency ve supply-chain kanıtını taşır. BTS veri
isteği yapılmamış, ZIP/CSV indirilmemiş ve hiçbir data row okunmamıştır.

## Sabit ortam

| Alan | Değer |
|---|---|
| Runner | `ubuntu-24.04`, Linux x86_64 |
| Python | CPython `3.14.7`, standard GIL |
| Paket yöneticisi | `uv 0.12.3` |
| Index | `https://pypi.org/simple` |
| Global cutoff | `2026-08-13T23:59:59Z` |
| Hypothesis cutoff | `2026-08-15T23:59:59Z` |
| Resolver run/job | `31897450532` / `95042846510` |
| Resolver sonucu | `success`; bütün adımlar ve zorunlu cleanup geçti |
| Workflow artifact | `0` |

## Exact graph sonucu

| Paket | Sürüm | Grup | Lisans | Yanked |
|---|---:|---|---|---|
| `airportsdata` | `20260803` | runtime | MIT | Hayır |
| `duckdb` | `1.5.5` | runtime | MIT | Hayır |
| `tzdata` | `2026.3` | runtime | Apache-2.0 | Hayır |
| `hypothesis` | `6.165.9` | dev | MPL-2.0 | Hayır |
| `sortedcontainers` | `2.4.0` | dev | Apache-2.0 | Hayır |

- External lock graph `13` paketten `18` pakete çıktı; exact fark yalnız yukarıdaki
  beş pakettir.
- Mevcut 13 external package'ın name, version, source, marker ve hash içeren parsed
  package kayıtları eşit kaldı.
- CPython 3.14.7 Linux x86_64 üzerinde `no-build-package` politikasıyla frozen kurulum
  geçti; source build yapılmadı.
- İki bağımsız clean-room kurulumu `17` aktif external package üretti ve normalized
  inventory SHA-256 değeri iki odada da
  `c439a8a7aeaef5ee2f881c3dbe0aef711fa6eacea4c24c553b5e762fcb523ec5` oldu.

## Supply-chain kapıları

| Kapı | Gözlenen sonuç |
|---|---|
| Direct import/version | 5/5 exact eşleşme |
| Yanked release | 0 |
| Vulnerability | 0 |
| Adverse status / malware | 0 |
| Audit edilen package | 18 |
| CycloneDX 1.5 component | 18 |
| Artifact | 0 |
| Data request/download/row | 0 / 0 / 0 |

## Bütünlük

| Dosya | SHA-256 |
|---|---|
| `pyproject.toml` | `d355df0f044febbad6bf54dbc7af6b03fa14cc5a1aee9660e4e9b3ba15475722` |
| `uv.lock` | `af33afda49ad0f295a9f76de42c4b3a48cd0c4e39c73a4fda9d2626e0a17acd7` |

Geçici resolver workflow'u, clean-room dizinleri, uv cache, audit JSON ve SBOM bytes'ları
result commit öncesinde kaldırılmıştır. Kalıcı Foundation workflow'unda yalnız yeni
gözlenen Linux inventory (`17`), audit (`18`) ve SBOM (`18`) integer assertion'ları
güncellenmiştir; build graph sayacı ve diğer komutlar değiştirilmemiştir.

## Kapanış kuralı

Bu candidate commit'in hosted Foundation sonucu `success` ve artifact sayısı `0`
olmadan PH2-T03 tamamlanmış sayılmaz ve PH2-T04 dosyası oluşturulmaz.
