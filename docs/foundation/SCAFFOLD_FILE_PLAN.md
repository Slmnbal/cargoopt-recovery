# PH1-T02 Minimal Scaffold Dosya Planı

| Alan | Değer |
|---|---|
| Üreten görev | `PH1-T01` |
| Hedef görev | `PH1-T02` |
| Durum | `COMPLETED — PH1_T02_LOCAL_GATE_PASSED` |
| Temel ilke | Yalnız import edilebilir ve kalite kapıları çalışabilir minimal package shell |

## 1. Uygulama sırası

Exact toolchain 2026-08-13 tarihinde onaylanmıştır. `PH1-T02`, ayrı dosya
allowlist'li görev sözleşmesi için açık execution onayı verildikten sonra
aşağıdaki sırayla yürütülür:

1. Runtime ve metadata dosyaları.
2. Exact dependency bildirimleri.
3. Tek lock resolution.
4. Minimal `src` package shell.
5. Tek import smoke testi.
6. Local format/lint/type/test/build kontrolleri.
7. Task validation ve checkpoint.

Bir adım geçmeden sonraki adım başlatılmaz. Lock çözülemezse source/test oluşturulmaz; package import geçmezse yeni test veya config genişletilmez.

## 2. Exact dosya planı

| Sıra | Path | İşlem | Minimal içerik | Yasak içerik |
|---:|---|---|---|---|
| 1 | `.python-version` | Create | Yalnız `3.14.7` | Başka runtime, floating minor |
| 2 | `.gitignore` | Create | `.venv`, caches, build artifacts, editor/OS-local artifacts | Data, model, secret veya future-phase path tasarımı |
| 3 | `pyproject.toml` | Create | Project metadata, `>=3.14,<3.15`, Hatchling exact build pin, exact dev group, Ruff/mypy/pytest minimal config, uv audit malware check | Ürün dependency'si, entry point, plugin, future interface |
| 4 | `uv.lock` | Generate once | Canonical PyPI, exact direct pins, upload cutoff `2026-08-13T23:59:59Z` | Git/path dependency, unlocked source, manual edit |
| 5 | `src/cargoopt_recovery/__init__.py` | Create | Docstring ve sabit package version metadata dışında davranış yok | Domain class, adapter, service, TODO, placeholder interface |
| 6 | `tests/test_package_import.py` | Create | Package spec/import smoke testi | Data fixture, business assertion, mock external service |
| 7 | `README.md` | Create | Scope, foundation-only durum, exact local commands ve phase-lock uyarısı | Ürün özelliği varmış gibi iddia, future API/UI/RAG kullanım talimatı |

`tests/__init__.py`, CLI, config module, logging setup, environment loader, Makefile, task runner, Dockerfile, CI workflow veya empty future directories oluşturulmaz. Bunlardan biri gerekli görünürse current task durur ve yeni plan/onay istenir.

## 3. `pyproject.toml` karar şeması

Bu bölüm uygulanacak semantiği tanımlar; mevcut görevde gerçek dosya oluşturmaz.

| Bölüm | Karar |
|---|---|
| `[build-system]` | `requires = ["hatchling==1.32.0"]`; backend `hatchling.build` |
| `[project]` | Static name/version/description; `requires-python = ">=3.14,<3.15"`; `dependencies = []` |
| `[dependency-groups] dev` | Yalnız `ruff==0.16.3`, `mypy==2.3.0`, `pytest==9.1.1` |
| `[tool.uv]` | Upload cutoff sabit; default dev group; alternate source yok |
| `[tool.uv.audit]` | Malware check açık; ignore listesi yok |
| `[tool.hatch.build.targets.wheel]` | Yalnız `src/cargoopt_recovery` package |
| `[tool.ruff]` | Python 3.14 target; tek line-length; src/tests kapsamı |
| `[tool.ruff.lint]` | Dar fakat hata yakalayan explicit rule set; autofix gate'te kapalı |
| `[tool.mypy]` | Python 3.14; strict; implicit optional ve untyped defs yasak |
| `[tool.pytest.ini_options]` | Yalnız `tests`; deterministic discovery; plugin requirement yok |

Project version için dynamic VCS plugin kullanılmaz. Tek static başlangıç version'ı kullanılır; `setuptools-scm`, Hatch version plugin'i veya Git tag dependency'si eklenmez.

## 4. Lock üretim sözleşmesi

`PH1-T02` içinde ilk ve tek intentional lock mutation aşağıdaki koşullarla yapılır:

```text
uv version == 0.12.3
python request == 3.14.7
default index == canonical PyPI
exclude newer == 2026-08-13T23:59:59Z
prerelease == disallow
resolution == highest compatible within exact direct pins
```

Lock üretildikten sonra:

- direct ve transitive graph catalog estimate'iyle karşılaştırılır;
- unexpected package, sdist fallback veya native compiler ihtiyacı blocker olur;
- yanked/adverse release bulunursa task durur;
- `pyproject.toml` ve `uv.lock` aynı değişiklik setinde kalır;
- sonraki bütün komutlar locked/frozen çalışır.

## 5. PH1-T02 acceptance

Task ancak aşağıdakilerin tamamıyla tamamlanabilir:

- allowlist dışı dosya yok;
- runtime ve direct pins karar dosyasıyla exact aynı;
- project runtime dependency sayısı `0`;
- package import edilebilir;
- Ruff format check ve lint geçer;
- mypy strict geçer;
- pytest smoke test geçer;
- build metadata okunabilir;
- lock check geçer;
- Phase 2+ path, dependency, abstraction veya placeholder yok;
- local validation sırasında test/type/lint kuralı zayıflatılmamış.

CI workflow `PH1-T02` kapsamında değildir. Minimal CI ancak local scaffold başarıyla tamamlandıktan sonra ayrı `PH1-T03` plan/onayıyla oluşturulabilir.

## 6. PH1-T02 gerçekleşen sonuç

| Kapı | Sonuç |
|---|---|
| Exact runtime | Standard GIL-enabled `CPython 3.14.7` — PASS |
| Exact manager | `uv 0.12.3` — PASS |
| Project lock | 14 entry; canonical source policy ve hash stability — PASS |
| Runtime dependency | `0` — PASS |
| Minimal package | Tek `__init__.py`, tek import/version testi — PASS |
| Frozen sync | Linux x86_64 local exact sync — PASS |
| Quality | Import, Ruff format/lint, mypy strict, pytest — PASS |
| Build | sdist, wheel metadata ve isolated wheel import — PASS |
| Phase sınırı | Phase 2–8 LOCKED; CI ve clean-room işi başlatılmadı — PASS |

Fresh-environment ikinci sync, security/license audit ve minimal CI ayrı
`PH1-T03` planı ve açık execution onayı gerektirir.
