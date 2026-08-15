# CargoOpt Recovery

CargoOpt Recovery, **Phase 1 repository foundation** kapılarını tamamladı ve
**Phase 2 data/domain** fazını açtı. Repository; exact Python/toolchain
sürümlerini, deterministic lock dosyasını, import edilebilir boş package
shell'ini, local clean-room kanıtlarını ve read-only GitHub Actions foundation
kapısını içerir.

`PH2-T01` yalnız official-source research ve exact uygulama planı görevi olarak
aktiftir; yürütülmesi ayrı insan onayı bekler. Data indirilmemiş, dependency
eklenmemiş ve cargo domain, ML, Operations Research, solver, API, database, UI,
Docker, RAG veya LLM davranışı uygulanmamıştır. Sonraki fazlara ait placeholder,
interface ya da erken dependency bulunmaz.

## Exact gereksinimler

- Standard GIL-enabled CPython `3.14.7`
- `uv 0.12.3`
- Linux x86_64 CPU-only referans ortamı

Project metadata, başka bir `uv` sürümüyle çalışmayı reddeder. Python runtime
gerekirse exact sürümle kurulur. Project ayarındaki `no-build-package` listesi,
yerel editable package build'ine izin verirken bütün beklenen üçüncü taraf
paketlerin yalnız wheel'den kurulmasını zorunlu kılar:

```bash
uv python install 3.14.7
```

## Local doğrulama

Aşağıdaki komutlar repository kökünden ve gösterilen sırayla çalıştırılır:

```bash
uv --version
uv python find 3.14.7 --managed-python
uv lock --check --python 3.14.7 --managed-python
uv sync --frozen --all-groups --python 3.14.7 --managed-python
uv run --frozen --no-sync python -c "import cargoopt_recovery; print(cargoopt_recovery.__version__)"
uv run --frozen --no-sync ruff format --check .
uv run --frozen --no-sync ruff check .
uv run --frozen --no-sync mypy src tests
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --frozen --no-sync pytest -q
```

Build çıktısı repository dışında geçici bir dizine alınır:

```bash
CARGOOPT_BUILD_PARENT="${TMPDIR:-/tmp}"
CARGOOPT_BUILD_TMP="$(mktemp -d "$CARGOOPT_BUILD_PARENT/cargoopt-build.XXXXXX")"
uv lock --check --python 3.14.7 --managed-python
uv build --no-sources --python 3.14.7 --managed-python --out-dir "$CARGOOPT_BUILD_TMP"
uv lock --check --python 3.14.7 --managed-python
```

## Faz kilidi

`PH1-T03` local clean-room, ikinci frozen sync, build, dependency/security,
CycloneDX, lisans ve gerçek hosted `Foundation` workflow kapılarını geçti.
`PH1-T04` Phase 1'i `COMPLETED/PASSED` kapattı ve Phase 2'yi atomik olarak açtı.
`PH2-T01` `ACTIVE` olsa da research/planning yürütmesi için ayrı açık onay
zorunludur. `PHASE_3..PHASE_8` kilitlidir; hiçbir sonraki görev veya faz otomatik
başlatılmaz.

Kalıcı kanıtlar `docs/foundation/CLEAN_ROOM_VERIFICATION_REPORT.md`,
`docs/foundation/DEPENDENCY_AUDIT_REPORT.md` ve
`docs/foundation/PHASE_1_EXIT_REPORT.md` dosyalarındadır. Raw venv, cache, build,
audit JSON veya SBOM repository'ye alınmaz.
