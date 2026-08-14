# Phase 1 Repository Foundation Giriş Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `phase-1-entry-v1` |
| Durum | Accepted — Phase 1 Active |
| İlgili görev | `PH0-T06` |
| Phase 1 adı | `repository_foundation` |

## 1. Amaç

Bu sözleşme Phase 1'in ne zaman açılabileceğini ve repository foundation kapsamında hangi işlerin hangi sırayla yapılabileceğini tanımlar. Phase 1 ürün özelliği geliştirme fazı değildir; sonraki fazların güvenilir biçimde çalışacağı minimal, pinned ve test edilebilir geliştirme temelini kurar.

Bu belge Phase 1'i açmaz. `docs/phase-status.yaml` içinde Phase 1, ayrı açık insan onayı ve transition kaydı olmadan `LOCKED` kalır.

## 2. Entry precondition'ları

Phase 1 ancak aşağıdakilerin tamamıyla açılabilir:

1. `PH0-T01..PH0-T06` görevlerinin tamamı `COMPLETED` olmalıdır.
2. `PHASE_0` gate değeri `READY_FOR_HUMAN_APPROVAL` olmalıdır.
3. `PHASE_0_EXIT_AUDIT.md` içinde açık `BLOCKER` bulunmamalıdır.
4. Contract registry schema, path, reference ve DAG kontrolleri geçmelidir.
5. Son Phase 0 checkpoint ZIP'i bütünlük testinden geçmeli ve SHA-256 değeri transition kaydına yazılmalıdır.
6. Proje sahibi “Phase 0'ı kapat ve Phase 1'i aç” anlamına gelen ayrı, açık onay vermelidir.
7. Transition mutation'ı yalnızca ayrıca planlanmış ve izinli dosyaları belirlenmiş görevle yapılmalıdır.

“Devam”, bir önceki görevi onaylamak veya Phase 1 planını konuşmak tek başına phase transition onayı değildir.

## 3. Transition sonrası zorunlu faz durumu

Geçiş tek atomic governance değişikliği olarak şu sonucu üretmelidir:

```text
PHASE_0.status = COMPLETED
PHASE_0.gate = PASSED
PHASE_1.status = ACTIVE
PHASE_1.gate = NOT_READY
active_phase = PHASE_1
active_task = approved Phase 1 task ID
PHASE_2..PHASE_8.status = LOCKED
```

Partial durum, iki ACTIVE faz veya `active_task` olmadan implementation başlatmak yasaktır.

## 4. Phase 1 görev sırası

Phase 1 yalnız aşağıdaki sırayla planlanır. Her görev ayrıca dosya-bazlı plan ve insan onayı gerektirir.

### PH1-T01 — Runtime ve dependency karar dosyası

Amaç: Hiç dependency eklemeden uyumlu runtime/toolchain paketini kanıtlamak.

İzinli çıktı türleri:

- runtime ve package-manager karar ADR'si;
- dependency catalog ve lisans/maintenance tablosu;
- compatibility matrix;
- Phase 1 scaffold dosya planı;
- clean-environment verification komut sözleşmesi.

Bu görev `pyproject.toml`, lock file, source package veya CI dosyası oluşturmaz.

### PH1-T02 — Minimal Python repository scaffold

Önkoşul: PH1-T01 kararı ayrıca onaylanmış olmalıdır.

İzinli hedefler:

- `pyproject.toml` ve exact lock file;
- minimal `src` package;
- minimal test package ve import smoke testi;
- formatter/linter/type/test configuration;
- kısa local-development komutları.

Domain, data, ML, OR, API veya UI implementation'ı eklenmez.

### PH1-T03 — Clean-room kalite ve CI kapısı

Önkoşul: PH1-T02 local testleri geçmelidir.

İzinli hedefler:

- fresh environment frozen sync;
- lint, format-check, type-check ve unit-test gate'leri;
- aynı gate'leri çalıştıran minimal CI workflow;
- dependency/license audit raporu;
- repository foundation exit report.

CI sağlayıcısı, workflow permission'ları ve exact actions ayrıca onaylanmadan dosya eklenmez.

## 5. PH1-T01 dependency karar zorunlulukları

Her doğrudan dependency veya development tool için şu alanlar bulunmalıdır:

| Alan | Zorunluluk |
|---|---|
| Amaç | Tek cümlede hangi onaylı ihtiyacı karşılıyor |
| Alternatif | Standard library veya daha küçük alternatif neden yeterli/yetersiz |
| Official source | Resmî dokümantasyon veya package metadata bağlantısı |
| Exact candidate version | `latest` veya açık range değil |
| Runtime compatibility | Seçilen Python ve OS desteği |
| Transitive impact | Lock file'a eklenen paket sayısı ve kritik native dependency |
| License | SPDX kimliği ve proje kullanımına uygunluk |
| Maintenance | Release tarihi, destek durumu ve bilinen deprecation |
| Security | Bilinen kritik vulnerability kontrolü |
| Determinism | Lock/hash ve platform davranışı |
| Removal cost | Bağımlılığın ileride sökülme etkisi |

Version veya destek bilgisi belleğe dayanarak yazılamaz; Phase 1'in çalışıldığı tarihte official primary source üzerinden doğrulanır. Ücretli API veya managed service zorunlu dependency olamaz.

## 6. Minimal dependency ilkesi

- Sadece aktif Phase 1 kalite/scaffold ihtiyacı için dependency seçilir.
- Phase 2–8 ihtiyacı için erken paket eklenmez.
- Runtime dependency ile development-only dependency ayrılır.
- Aynı işi yapan iki framework eklenmez.
- Optional extra, plugin veya code generator varsayılan açılmaz.
- Exact top-level constraint ve tam lock birlikte commit edilir.
- Unsupported Python, yanked release veya pre-release varsayılan seçilemez.
- Git URL, unpinned branch veya editable external package yasaktır.

## 7. Clean-room verification sözleşmesi

PH1-T02/PH1-T03 aşağıdaki bağımsız kanıtları üretmelidir:

1. Boş bir virtual environment oluşturulur.
2. Yalnız committed project metadata ve lock file kullanılır.
3. Frozen sync lock değişikliğine izin vermeden tamamlanır.
4. İkinci frozen sync lock ve environment çözümünü değiştirmez.
5. Project package import smoke testi geçer.
6. Format check, lint, type check ve unit tests ayrı komutlarla geçer.
7. Build edilebilir artifact oluşturuluyorsa metadata okunur ve import edilir.
8. Test komutları repository kökünden ve belgelenmiş working directory'den çalışır.
9. Secret, kullanıcıya özel absolute path veya global interpreter state gerektirmez.
10. Lock diff, tool versions, OS/architecture ve command exit code'ları raporlanır.

Çalıştırılmamış platform “destekleniyor” diye iddia edilemez. Cross-platform hedef varsa her hedef ayrı CI job veya açık limitation gerektirir.

## 8. Phase 1 izinli repository sınırı

Phase 1 tamamlanana kadar yalnız foundation niteliğindeki şu alanlar açılabilir:

- project metadata ve lock;
- minimal importable package shell;
- quality tool configuration;
- foundation testleri;
- minimal CI;
- repository kullanım ve governance dokümantasyonu.

Minimal package shell business class, domain entity, adapter, interface veya gelecekte kullanılacağı varsayılan placeholder içeremez.

## 9. Phase 1 kesin kapsam dışı

- BTS download/ingestion veya data directory;
- cargo domain, generator veya cost implementation;
- feature engineering, model training, MLflow veya Hugging Face;
- Pyomo, HiGHS model/adapter veya validator implementation;
- PostgreSQL, pgvector, migration veya seed;
- FastAPI endpoint, React app veya UI;
- Docker Compose, deployment veya cloud resource;
- blind replay, sensitivity veya evaluation implementation;
- RAG, embedding, reranker, Ollama veya LLM;
- sample future-phase interface, empty adapter veya TODO placeholder.

Bir tool yalnız ileride gerekeceği için eklenemez.

## 10. Phase 1 exit kriterleri

Phase 1 ancak:

- PH1-T01 dependency kararı onaylı;
- PH1-T02 scaffold ve lock mevcut;
- PH1-T03 clean-room ve CI gate'leri başarılı;
- dependency/license/security raporu açık blocker içermiyor;
- minimal package import ediliyor;
- bütün committed test/lint/type komutları geçiyor;
- Phase 2+ implementation bulunmuyor;
- foundation checkpoint'i doğrulanmış;
- proje sahibi ayrı Phase 2 geçiş onayı vermiş

ise kapatılabilir.

## 11. Stop conditions

Phase 1 çalışması şu durumda durur:

- official compatibility veya lisans bilgisi doğrulanamıyorsa;
- dependency çözümü yalnız broad version range ile mümkünse;
- lock farklı clean run'larda değişiyorsa;
- native build tool veya OS dependency'si açıklanmamışsa;
- quality gate'i geçirmek için test/type/lint zayıflatmak gerekiyorsa;
- Phase 2+ dosyası ya da abstraction ihtiyacı doğuyorsa;
- onaylı task `files_allowed` sınırı aşılacaksa.

## 12. Değişiklik yönetimi

Phase 1 görev sırası, entry/exit gate, dependency approval standardı, izinli repository sınırı veya clean-room verification değişirse yeni contract sürümü, gerekçe ve açık insan onayı gerekir.
