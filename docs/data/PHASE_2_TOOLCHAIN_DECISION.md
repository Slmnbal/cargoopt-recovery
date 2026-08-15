# Phase 2 Exact Toolchain Kararı

| Alan | Değer |
|---|---|
| Belge kimliği | `phase-2-toolchain-decision-v1` |
| Görev | `PH2-T01` |
| Karar tarihi | `2026-08-15` |
| Durum | `APPROVED — NOT INSTALLED` |
| Onay | `2026-08-15` — explicit user command |
| Hedef runtime | Standard GIL-enabled `CPython 3.14.7`, Linux x86_64, CPU-only |
| Maliyet | Ücretsiz; managed servis, token veya secret yok |
| Bu görevde kurulum | **Yok** |

## 1. Seçilen minimal stack

| Rol | Exact seçim | Scope | Gerekçe |
|---|---|---|---|
| Analitik motor | `duckdb==1.5.5` | Runtime | CSV/Parquet, explicit schema, SQL window/ASOF ve larger-than-memory işleme tek in-process dependency'de |
| Airport timezone metadata | `airportsdata==20260803` | Runtime | IATA-keyed airport kaydında IANA-compatible `tz`; pure Python data package |
| IANA timezone rules | `tzdata==2026.3` | Runtime | `zoneinfo` davranışını işletim sistemi tzdb'sinden bağımsız dondurur |
| Property/invariant test | `hypothesis==6.165.9` | Development | Generator ve data-quality invariant'larını edge-case üreterek sınar |
| Hypothesis transitive pin | `sortedcontainers==2.4.0` | Development | Hypothesis'in tek mandatory Python-library dependency'sini exact ve audit edilebilir yapar |
| HTTP/download | Python `urllib.request` | Standard library | Bu dar read-only acquisition için üçüncü HTTP stack'i gerektirmez |
| Archive/hash/atomic I/O | `zipfile`, `hashlib`, `tempfile`, `pathlib`, `os` | Standard library | Bounded archive doğrulaması ve provenance için yeterli |
| Zaman | `datetime`, `zoneinfo` | Standard library | UTC/local normalizasyon; pinned `tzdata` ile |
| Canonical domain | `dataclasses`, `enum`, `decimal`, `json` | Standard library | Strict domain value ve byte-stable JSON; Phase 2'de Pydantic gerektirmez |
| Test runner | Mevcut `pytest==9.1.1` | Development | Foundation'da zaten exact pinli |

Bu karar `PH2-T01 toolchain ve uygulama planını onaylıyorum; PH2-T02 görevini
planla.` komutuyla kabul edildi. Onay yalnız PH2-T02 task planının oluşturulmasına
izin verir; `pyproject.toml`, `uv.lock` veya environment değişmez. Dependency
çözmek için PH2-T02 başarıyla kapanmalı, PH2-T03 ayrıca planlanmalı ve ayrıca
exact yürütme onayı almalıdır.

## 2. Canonical metadata kanıtı

| Paket | Canonical kaynak | Exact sürüm / yayın | Python 3.14.7 + Linux x86_64 | Lisans | Maintenance/provenance |
|---|---|---|---|---|---|
| DuckDB | https://pypi.org/project/duckdb/ | `1.5.5`, 2026-07-22 | `cp314` manylinux x86_64 wheel; Python `>=3.10` | MIT | Production/Stable; DuckDB Foundation; trusted publishing + attestation |
| airportsdata | https://pypi.org/project/airportsdata/ | `20260803`, 2026-08-03 | `py3-none-any`; classifier 3.14; Python `>=3.11` | MIT | Production/Stable; trusted publishing + attestation |
| tzdata | https://pypi.org/project/tzdata/ | `2026.3`, 2026-07-10 | `py2.py3-none-any` | Apache-2.0 | Python Software Foundation first-party tzdb; trusted publishing + attestation |
| Hypothesis | https://pypi.org/project/hypothesis/ | `6.165.9`, 2026-08-15 | Python `>=3.10`; classifier/wheel 3.14 | MPL-2.0 | Production/Stable; aktif release; typed |
| sortedcontainers | https://pypi.org/project/sortedcontainers/ | `2.4.0`, 2021-05-16 | `py2.py3-none-any` | Apache-2.0 | Production/Stable fakat release yaşı yüksek; lock/audit gate zorunlu |

Ek resmî teknik kaynaklar:

- DuckDB Python/CSV/Parquet dokümantasyonu:
  https://duckdb.org/docs/stable/clients/python/overview,
  https://duckdb.org/docs/stable/data/csv/overview,
  https://duckdb.org/docs/stable/data/parquet/overview
- DuckDB SQL `FROM`/ASOF semantiği:
  https://duckdb.org/docs/stable/sql/query_syntax/from
- Python `zoneinfo`: https://docs.python.org/3/library/zoneinfo.html
- Hypothesis packaging/dependency açıklaması:
  https://hypothesis.readthedocs.io/en/latest/packaging.html

## 3. Neden DuckDB seçildi

Phase 2'nin ihtiyacı genel amaçlı dataframe notebook deneyimi değil;
tekrarlanabilir, explicit-schema, disk üzerinde Parquet üreten ve as-of zaman
mantığını deterministik olarak çalıştıran bir batch data engine'dir.

DuckDB bu ihtiyaçları şu tek sorumlulukta birleştirir:

- CSV parse sırasında kolon adlarını ve tiplerini açık vermek;
- Parquet'i ek Python Arrow dependency'si olmadan okumak/yazmak;
- schedule/outcome katmanlarını ayrı tablolar ve ayrı dosya yollarında tutmak;
- range window ve ASOF join ile 7/30 günlük geçmiş feature temelini kurmak;
- projection/filter pushdown ve larger-than-memory execution;
- server, daemon, port, credential veya managed database gerektirmemek.

Uygulama kuralları:

1. CSV auto-detection contract doğrulaması için kullanılmaz; header önce exact
   karşılaştırılır ve tipler explicit verilir.
2. SQL değerleri string interpolation ile kurulmaz; değer parametreleri bind
   edilir, identifier'lar internal closed allowlist'ten gelir.
3. Remote HTTP/S3 access veya community extension kurulumu kullanılmaz.
4. `INSTALL`, `LOAD`, `ATTACH` ve user-provided path/SQL üretimi application
   surface'ine açılmaz.
5. Connection process içinde ve bounded olur; permanent `.duckdb` database
   proje truth source'u değildir. Truth source immutable Parquet + manifest'tir.
6. Her materialization explicit `ORDER BY` ile canonical row order üretir.

## 4. Değerlendirilen alternatifler

| Aday | Exact sürüm | Sonuç | Gerekçe | Removal/replace cost |
|---|---:|---|---|---|
| DuckDB | `1.5.5` | **SELECTED** | Tek native wheel; zero external Python dependency; CSV/Parquet/window/ASOF | Orta: SQL/data-engine adapter katmanı değişir; contracts etkilenmez |
| Polars | `1.43.2` | REJECTED | Güçlü lazy/streaming API; ancak runtime meta + native runtime graph'ı ve Python expression bağımlılığı seçilen tek-engine ihtiyacında ek değer sağlamıyor | Orta-yüksek: bütün transform expression'ları değişir |
| PyArrow | `25.0.1` | REJECTED | Parquet interoperability güçlü; DuckDB zaten native Parquet sunarken ikinci büyük native stack olur | Orta: serialization adapter'ları değişir |

Şu kategoriler Phase 2 adayı değildir:

- `pandas`/NumPy: ikinci dataframe stack'i ve duplicate memory model;
- Pandera: data-quality contract'ları explicit validator + DuckDB schema ile
  uygulanabilirken ek framework yüzeyi;
- Pydantic: API fazından önce domain için dataclass/Enum/Decimal yeterli;
- requests/httpx: dört resmî hosta bounded read-only acquisition için standard
  library yeterli;
- Spark/Dask/Ray: 2024 tek yıllık bounded dataset ve local CPU hedefi için
  distributed runtime scope creep'i;
- cloud warehouse/object storage: ücretsiz local reproducibility ve no-secret
  ilkesine aykırı;
- Hugging Face: Phase 2 data/domain işi değildir; yalnız Phase 8 için kilitli.

Tek analitik motor kuralı geçerlidir: DuckDB seçiliyken Polars, pandas veya
PyArrow doğrudan dependency olarak eklenmez. Daha sonraki gerçek ve ölçülmüş bir
interop gereksinimi ayrı ADR/task/onay ister.

## 5. Proposed dependency graph

```text
cargoopt-recovery runtime
├── duckdb==1.5.5
├── airportsdata==20260803
└── tzdata==2026.3

cargoopt-recovery development
├── existing foundation groups
│   ├── pytest==9.1.1
│   ├── ruff==0.16.3
│   └── mypy==2.3.0
├── hypothesis==6.165.9
└── sortedcontainers==2.4.0
```

Expected Python-package impact:

- runtime: 3 yeni direct, 0 beklenen Python transitive;
- development: 2 yeni exact package; `sortedcontainers` Hypothesis'in mandatory
  dependency'sidir ve bilinçli direct constraint olarak pinlenir;
- optional extras: hiçbiri;
- service/container/OS package: hiçbiri;
- GPU: hiçbiri.

Bu grafik **kurulmuş veya lock edilmiş değildir**. PH2 dependency task'ında
`uv lock` sonucu farklı ek transitive, sdist-only build, yanked release veya
marker sürprizi üretirse görev başarısız olur; plan sessizce güncellenmez.

## 6. Security ve supply-chain kabul kapısı

Dependency task'ı ayrı onayla şu sırayı uygular:

1. Canonical PyPI index ve foundation'daki `exclude-newer`/pre-release politikası.
2. Exact direct constraint'lerle lock çözümü.
3. `uv sync --frozen --all-groups` clean environment.
4. Actual lock graph ile proposed graph farkı; beklenmeyen package fatal.
5. Python 3.14.7 Linux x86_64 wheel availability; zorunlu sdist build fatal.
6. `uv audit` ile vulnerability, deprecation ve quarantine kontrolü.
7. Direct + transitive SPDX inventory; yalnız kabul edilmiş lisans policy'si.
8. Wheel metadata, package version import ve minimal smoke.
9. İki frozen sync sonrası normalized inventory idempotency.
10. Lock ve `pyproject.toml` diff'i yalnız task exact allowlist'inde.

Security durumu PH2-T01'de “temiz” olarak iddia edilmez; kurulum yapılmadan
vulnerability sonucu üretilemez. Kabul, future task'taki actual resolved lock ve
audit kanıtına bağlıdır. Bulguyu ignore/suppress/allowlist ile geçmek yasaktır.

## 7. Removal cost ve isolation tasarımı

| Seçim | İzole edilecek sınır | Kaldırma etkisi |
|---|---|---|
| DuckDB | `data/engine.py` tek adapter; domain katmanı SQL bilmez | Adapter ve transform query'leri; manifest/contracts değişmez |
| airportsdata | `data/timezones.py` loader; frozen mapping output'u package object'i taşımaz | Başka approved master-data loader; mapping yeniden version/hash alır |
| tzdata | Standard `zoneinfo`; manifestte exact ruleset version | OS tzdb'ye dönüş reproducibility'yi düşürür; yeni snapshot version gerekir |
| Hypothesis | Yalnız `tests/property/`; production import yasak | Property testleri deterministic parametrik testlere çevrilir; runtime etkilenmez |

Dependency modülleri immutable snapshot veya public domain modeline sızdırılmaz.
Bu sayede sonraki bir package değişikliği contract kimliklerini gereksiz yere
bozmaz; fakat byte-level output değişirse yeni implementation/snapshot version
zorunludur.

## 8. Determinism kuralları

- DuckDB version manifestte yazılır; query çıktısı explicit order olmadan
  serialize edilmez.
- Thread sayısı ve memory/temp sınırı config'te açık verilir; test/golden run
  tek-thread canonical materialization kullanır.
- Float aggregate, domain para/ağırlık/hacim kaynağı olamaz; domain katmanı
  `Decimal` ve contract hassasiyetini kullanır.
- Parquet file hash tek başına semantic snapshot kimliği değildir. Canonical
  logical manifest; schema, ordered row digest, engine version ve source hash
  taşır. Engine upgrade yeniden doğrulama gerektirir.
- Hypothesis testleri CI'da fixed profile, deadline policy ve example database
  kapalı/temporary olarak çalışır; başarısız örnek loglanır. Golden determinism
  yalnız Hypothesis randomness'ine bırakılmaz.

## 9. Karar kapısı

Exact stack teknik olarak onaylanmıştır fakat **kurulmamış ve lock
edilmemiştir**. `PH2-T01 toolchain ve uygulama planını onaylıyorum; PH2-T02
görevini planla.` komutu kaydedilmiş, PH2-T02 bounded source compatibility
probe görevi planlanmıştır.

Bir sonraki geçerli insan komutu:

> `PH2-T02 source compatibility probe planını onaylıyorum; başlat.`

Bu komut yalnız PH2-T02'de tanımlanan bounded resmî kaynak probe'unu başlatır.
Dependency kurulumu/lock, tam 2024 veri edinimi, source implementation veya
PH2-T03 planlaması için yetki vermez.
