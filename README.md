# CargoOpt Recovery

CargoOpt Recovery şu anda yalnızca **Phase 1 repository foundation**
aşamasındadır. Bu checkpoint; exact Python/toolchain sürümlerini, deterministic
lock dosyasını, import edilebilir boş package shell'ini, local clean-room
kanıtlarını ve read-only GitHub Actions foundation kapısını içerir.

Bu aşamada data, cargo domain, ML, Operations Research, solver, API, database,
UI, Docker, RAG veya LLM davranışı uygulanmamıştır. Sonraki fazlara ait
placeholder, interface ya da erken dependency de bulunmaz.

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
CycloneDX ve lisans kapılarını geçti. Nihai görev kapanışı için committed state'e
ait gerçek hosted `Foundation` workflow sonucunun `success` olması gerekir.
Phase 1 kapanışı ve Phase 2 açılışı bunun ardından bile yalnız ayrı insan
onayıyla yapılır; hiçbir sonraki görev veya faz otomatik başlatılmaz.

Kalıcı kanıtlar `docs/foundation/CLEAN_ROOM_VERIFICATION_REPORT.md`,
`docs/foundation/DEPENDENCY_AUDIT_REPORT.md` ve
`docs/foundation/PHASE_1_EXIT_REPORT.md` dosyalarındadır. Raw venv, cache, build,
audit JSON veya SBOM repository'ye alınmaz.
