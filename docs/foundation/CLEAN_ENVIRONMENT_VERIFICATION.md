# Clean Environment Verification Sözleşmesi

| Alan | Değer |
|---|---|
| İlk üreten görev | `PH1-T01` |
| Revize eden görev | `PH1-T03` planlaması |
| Yürütme sahibi | `PH1-T03` |
| Durum | `EXECUTED — LOCAL_PASS — HOSTED_CI_PASS` |
| Primary ortam | Fresh Linux x86_64, CPU-only |
| Onaylı CI stack | GitHub-hosted `ubuntu-24.04` |

## 1. Amaç ve kanıt sınırı

Bu akış repository foundation'ın global Python state, eski `.venv`, kullanıcı
cache'i, secret, özel index veya makineye özgü path olmadan yalnız committed
metadata ve lock ile kurulabildiğini kanıtlar.

İki bağımsız kanıt zorunludur:

1. Repository dışında oluşturulan yerel clean-room snapshot'ı.
2. GitHub Actions içindeki gerçek fresh hosted runner run'ı.

Yerel kopya hosted CI yerine, hosted CI de yerel ayrıntılı audit/lisans raporu
yerine geçmez. Mevcut workspace bir Git checkout değilse yerel sonuç “fresh
checkout” olarak adlandırılmaz; yalnız “isolated repository snapshot” kanıtıdır.

## 2. Önkoşullar

- `PH1-T02` `COMPLETED` ve checkpoint SHA-256 doğrulanmış olmalıdır.
- CI stack ve `PH1-T03` yürütmesi ayrı ayrı açıkça onaylanmış olmalıdır.
- Exact araçlar `uv 0.12.3` ve standard GIL-enabled CPython `3.14.7` olmalıdır.
- Clean-room repository dışında OS temporary parent altında oluşturulmalıdır.
- Başlangıçta `.venv`, build output ve repository cache bulunmamalıdır.
- Yalnız canonical PyPI kullanılmalı; Git, path, alternate index ve
  `--allow-insecure-host` yasak olmalıdır.
- `UV_INDEX*`, `PIP_INDEX*`, `PYTHONPATH`, `VIRTUAL_ENV` ve credential taşıyan
  custom environment değişkenleri temizlenmelidir. Yalnız task'ta açıkça
  tanımlanan `UV_PYTHON`, `UV_MALWARE_CHECK`, `UV_CACHE_DIR` ve test kontrol
  değişkenleri kullanılabilir.
- Security ignore/allowlist, audit suppression ve secret kullanılamaz.

## 3. Başlangıç kanıtı

Clean-room source şu bilgileri kaydeder:

- sorted relative file manifest ve her dosyanın SHA-256 değeri;
- source snapshot oluşturma yöntemi ve UTC timestamp;
- OS, kernel, architecture, libc ve CPU bilgisi;
- repository dışında kullanılan temporary parent;
- `pyproject.toml` başlangıç SHA-256:
  `db02c0b9ea47e128a595682da17c9176dac55b9052e900d5dc67084076bc9b6b`;
- `uv.lock` başlangıç SHA-256:
  `3f1fce29dd14fac81f56aaea1226131cd93d451c2c2ffe38730171e29e3697b4`;
- Phase 2+ implementation artifact ve secret taraması sonucu.

Snapshot yalnız repository dosyalarını içerir. `.git`, `.venv`, cache, build,
test result ve önceki audit artifact'ları taşınmaz.

## 4. Exact doğrulama sırası

Komutlar clean-room kökünde fail-fast shell ile ve ayrı exit code/süre kaydıyla
çalıştırılır. Komutlar tek bir sonucu saklayan composite gate'e dönüştürülmez.

### A. Bootstrap ve runtime

```bash
uv --version
uv python install 3.14.7
uv python find 3.14.7 --managed-python
uv run --python 3.14.7 --managed-python --no-project python -c "import platform, sys; assert platform.python_implementation() == 'CPython'; assert sys.version_info[:3] == (3, 14, 7); assert sys._is_gil_enabled(); assert sys.implementation.cache_tag == 'cpython-314'"
```

İlk çıktı exact `uv 0.12.3` değilse veya runtime assertion'lardan biri
başarısızsa görev durur.

### B. Metadata-lock bütünlüğü

```bash
uv lock --check --python 3.14.7 --managed-python
sha256sum pyproject.toml uv.lock
```

`uv lock --check` lock'u değiştirmemelidir. Başlangıç hash'leri PH1-T02
precondition değerleriyle eşleşmelidir.

### C. Birinci frozen exact sync

```bash
UV_MALWARE_CHECK=1 uv sync --frozen --exact --all-groups --python 3.14.7 --managed-python
uv sync --check --all-groups --python 3.14.7 --managed-python
```

Sync `.venv` dosyasını clean-room içinde ilk kez oluşturur. Local editable
project build'ine izin verilir; bütün üçüncü taraf paketler için mevcut
`no-build-package` policy uygulanır. Üçüncü taraf sdist, C/Rust compiler veya
alternate index kullanımı blocker'dır.

Birinci sync sonrasında standard-library `importlib.metadata` ile package adı
ve version alanlarından normalize, sıralı bir JSON inventory üretilir. Bu
inventory repository dışında tutulur.

### D. İkinci frozen exact sync ve idempotency

```bash
UV_MALWARE_CHECK=1 uv sync --frozen --exact --all-groups --python 3.14.7 --managed-python
uv sync --check --all-groups --python 3.14.7 --managed-python
sha256sum pyproject.toml uv.lock
```

İkinci sync sonrasında aynı normalized inventory tekrar üretilir. `PASS` için:

- ikinci sync sıfır package add/remove/update göstermeli;
- inventory-1 ile inventory-2 byte-identical olmalı;
- başlangıç ve bitiş `pyproject.toml`/`uv.lock` hash'leri eşit olmalı;
- extraneous package kalmamalıdır.

### E. Import ve tool version smoke

```bash
uv run --frozen --no-sync python -c "import cargoopt_recovery; assert cargoopt_recovery.__version__ == '0.1.0'"
uv run --frozen --no-sync ruff --version
uv run --frozen --no-sync mypy --version
uv run --frozen --no-sync pytest --version
```

Tool çıktıları exact `ruff 0.16.3`, `mypy 2.3.0` ve `pytest 9.1.1` olmalıdır.

### F. Bağımsız kalite gate'leri

```bash
uv run --frozen --no-sync ruff format --check .
uv run --frozen --no-sync ruff check .
uv run --frozen --no-sync mypy src tests
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --frozen --no-sync pytest -q
```

Her komutun exit code ve süresi ayrı kaydedilir. `fix`, `ignore`, `skip`,
`xfail`, suppression veya config zayıflatma kullanılamaz.

### G. Build ve artifact smoke

Build output repository dışındaki yeni bir temporary directory'ye yazılır:

```bash
uv lock --check --python 3.14.7 --managed-python
uv build --no-sources --python 3.14.7 --managed-python --out-dir "$CARGOOPT_BUILD_OUTPUT"
uv lock --check --python 3.14.7 --managed-python
sha256sum pyproject.toml uv.lock
```

`uv 0.12.3` için `uv build --frozen` geçerli bir komut değildir; bu sözleşmede
kullanılmaz. Build determinism sınırı, sabit source/metadata, `--no-sources`,
repository dışı output ve build öncesi/sonrası lock/hash eşitliğiyle uygulanır.

Wheel ve sdist için filename, SHA-256, package name, version ve
`Requires-Python` okunur. Wheel ikinci bir isolated temporary environment'a
kurulur ve `cargoopt_recovery==0.1.0` import edilir. Artifact'lar commit edilmez.

### H. Project security, graph ve SBOM gate

```bash
uv audit --frozen --output-format json
uv tree --frozen
uv export --frozen --all-groups --format cyclonedx1.5 --output-file "$CARGOOPT_PROJECT_SBOM"
```

`uv audit` varsayılan olarak bütün extras ve groups alanlarını tarar. Exit code
`0` olmalı; vulnerability yanında deprecation ve quarantine/adverse status da
bulunmamalıdır. `--ignore` ve `--ignore-until-fixed` yasaktır.

CycloneDX dosyası repository dışında tutulur. SHA-256, component count ve graph
özeti permanent audit raporuna yazılır; raw SBOM ayrı onay olmadan commit edilmez.

### I. Isolated build graph audit

Project `uv.lock`, PEP 517 build-system transitiflerini içermez. Bu nedenle full
audit yalnız project lock ile tamamlanmış sayılmaz.

1. Verbose isolated build kanıtından Hatchling `1.32.0` ve gerçek transitive
   build graph çıkarılır.
2. Repository dışında temporary PEP 723 script oluşturulur; tek direct
   dependency `hatchling==1.32.0`, Python `3.14.7` ve aynı
   `exclude-newer=2026-08-13T23:59:59Z` sınırı kullanılır.
3. Script lock'u temporary alanda oluşturulur; graph, build sırasında observed
   graph ile exact karşılaştırılır.
4. Eşleşen script lock `uv audit --script ... --frozen` ile taranır ve
   CycloneDX 1.5 olarak export edilir.

Graph eşleşmezse, build dependency audit'i eksik kalır ve görev durur. Project
metadata'ya constraint veya dependency sessizce eklenmez.

### J. Full license inventory

License inventory şu beş yüzeyi kapsar:

1. CPython runtime;
2. uv bootstrap tool;
3. project lock içindeki bütün direct/transitive ve platform-marker package'ları;
4. observed isolated build graph;
5. workflow'da kullanılan GitHub Actions.

Her satırda component, exact version/SHA, role, source, marker, SPDX expression,
canonical license URL, yükümlülük ve karar bulunur. Installed metadata tek başına
belirsizse canonical project `LICENSE`/PyPI metadata ile cross-check edilir.
`UNKNOWN`, missing, proprietary, noncommercial, research-only, SSPL, BSL, GPL,
AGPL veya unresolved conflict Phase 1 exit blocker'ıdır.

## 5. GitHub Actions parity gate

CI dosyası yalnız `CI_STACK_DECISION.md` exact adayı onaylandıktan sonra
oluşturulabilir. Zorunlu sınırlar:

- `runs-on: ubuntu-24.04`;
- `permissions: contents: read` ve başka izin yok;
- `actions/checkout` ve `astral-sh/setup-uv` full 40 karakter SHA ile pinned;
- `uv 0.12.3`, Python `3.14.7`, `enable-cache: false`;
- secret, write, artifact upload, publish ve deployment yok;
- local A–H kapıları aynı sırayla çalışır;
- final commit SHA'sına ait gerçek hosted run `success` olmalıdır.

CI file syntax'ının local olarak parse edilmesi gerçek GitHub run'ı yerine
geçmez. GitHub remote/run yetkisi yoksa görev
`BLOCKED_EXTERNAL_CI_EVIDENCE` durumunda durur.

## 6. Zorunlu permanent raporlar

`PH1-T03` başarıyla yürütülürse yalnız şu raporlar commit edilir:

- `CLEAN_ROOM_VERIFICATION_REPORT.md`;
- `DEPENDENCY_AUDIT_REPORT.md`;
- `PHASE_1_EXIT_REPORT.md`.

Raporlar UTC timestamp, bütün exact sürümler, before/after hash'ler, package
inventory özeti, bütün command exit code/süreleri, audit/SBOM hash'leri, license
kararları, build artifact hash'leri, runner image ve final CI run URL/ID'sini
içerir. Raw `.venv`, cache, build, SBOM ve audit JSON checkpoint'e alınmaz.

## 7. PASS/FAIL kuralları

`PASS` için A–J ve gerçek hosted CI gate'inin tamamı başarılı olmalıdır.
Aşağıdakiler doğrudan `FAIL/BLOCKER`dır:

- exact uv/Python/action mismatch veya kanıtlanamayan provenance;
- stale/mutated lock ya da değişen metadata hash'i;
- ikinci sync environment graph değişikliği;
- third-party source build veya native compiler gereksinimi;
- import, format, lint, type, test, build veya installed-wheel hatası;
- rule/strictness azaltma ihtiyacı;
- vulnerability, deprecation, quarantine, malware veya adverse finding;
- audit ignore, insecure host, alternate index veya override ihtiyacı;
- project/build graph audit eksikliği;
- unknown, prohibited veya unresolved license;
- CI permission/action/runner/trigger drift'i;
- final commit'e ait gerçek hosted `success` kanıtının olmaması;
- user-specific path, secret, global interpreter veya Phase 2+ artifact bağımlılığı.

Failure durumunda fallback, broad constraint, yeni dependency veya suppression
eklenmez. Task son doğrulanmış gate'te durur ve yeni insan kararı ister.

## 8. Platform iddia sınırı

Bu görev yalnız Linux x86_64 CPU-only referansını kanıtlar. Canonical metadata
Windows desteği gösterse bile Windows'ta aynı akış çalıştırılmadan “Windows
verified” denemez. macOS, ARM, free-threaded Python, GPU ve container da
unverified kalır.

## 9. Resmî davranış kaynakları

| URL | Erişim | Claim |
|---|---|---|
| https://docs.astral.sh/uv/concepts/projects/sync/ | 2026-08-13 | Lock check, frozen/exact sync ve group davranışı |
| https://docs.astral.sh/uv/reference/cli/ | 2026-08-13 | Sync, audit, export, build ve managed Python seçenekleri |
| https://docs.astral.sh/uv/concepts/python-versions/ | 2026-08-13 | Exact patch request ve managed Python |
| https://docs.astral.sh/uv/concepts/resolution/ | 2026-08-13 | Universal lock ve dependency constraint sınırı |
| https://docs.astral.sh/uv/concepts/projects/dependencies/ | 2026-08-13 | PEP 518 build dependency davranışı |
| https://docs.astral.sh/uv/reference/settings/ | 2026-08-13 | Build-constraint davranışı |
| https://peps.python.org/pep-0517/ | 2026-08-13 | Isolated frontend/backend build modeli |
| https://cyclonedx.org/specification/overview/ | 2026-08-13 | CycloneDX SBOM modeli |
