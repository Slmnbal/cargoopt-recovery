# ADR-008 — Phase 0 Exit, Sensitivity Sınırı ve Phase 1 Giriş Kararı

| Alan | Değer |
|---|---|
| Durum | Accepted |
| Tarih | 2026-08-13 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | `PH0-T06` |

## Bağlam

PH0-T01..PH0-T05 proje kapsamını, açık BTS veri sınırını, leakage-free multi-horizon ML tahminini, sentetik cargo/TRY maliyetini, OR/solver/validator sözleşmelerini ve primary blind replay release kararını tanımladı. Phase 1'e geçmeden önce bu artifact'ların kimlik, dependency ve faz sahipliği açısından tek registry'de doğrulanması gerekmektedir.

Project Spec ayrıca “sensitivity analysis” içeriyordu; fakat PH0-T05 bilinçli olarak scenario grid'i tanımlamadı. Scenario'ların outcome görüldükten sonra serbestçe seçilmesi primary sonuca uygun robustness anlatısı üretme ve scope creep riski taşır. Buna karşılık bütün maliyet/capacity kombinasyonlarını primary reveal öncesi solve etmek compute kapsamını gereksiz büyütür.

Phase 1 başlangıcında doğrudan dependency kurmak da runtime/package uyumsuzluğu, yanked release, lisans belirsizliği ve gereksiz gelecek-faz paketleri riskini yaratır. Kullanıcının “faz bitmeden diğer faz işi yapılmaması” kararı nedeniyle entry sırası koddan önce sınırlandırılmalıdır.

## Karar

### 1. Contract registry

Phase 0 normative artifact'ları `cargoopt-contract-registry-v1` içinde:

- benzersiz contract ID;
- mevcut ve benzersiz artifact path;
- tek owner component;
- implementation phase;
- task origin;
- supersedes ilişkisi;
- normative dependency;
- informational reference;
- lifecycle status

ile kaydedilir. Normative dependency graph cycle içeremez. Informational iki yönlü reference, implementation ordering dependency'si sayılmaz.

Contract'lar açık phase transition onayına kadar `CANDIDATE_PENDING_PHASE_0_TRANSITION` kalır.

### 2. Phase 0 exit audit

Audit:

- tamamlanmış task ve validation kayıtlarını;
- Project Spec kapsam traceability'sini;
- data → ML → OR → validator → evaluation invariant'larını;
- registry path/reference/DAG bütünlüğünü;
- locked-phase ve forbidden-path durumunu;
- açık blocker ve controlled-deferred riskleri

kontrol eder.

Açık blocker sıfırsa Phase 0 gate `READY_FOR_HUMAN_APPROVAL` olabilir. Bu status Phase 0'ı tamamlamaz veya Phase 1'i açmaz.

### 3. Sensitivity tasarımı

Sensitivity `evaluation-sensitivity-v1` ile secondary, pre-registered ve non-release çalışmadır.

Yalnız iki MILP çalışır ve exact dört non-baseline OFAT scenario vardır:

```text
disruption consequence × 0.75
disruption consequence × 1.25
available capacity × 0.90
available capacity × 1.10
```

- Primary baseline yeniden solve edilmez.
- Joint grid, adaptive search ve ek multiplier yasaktır.
- Scenario kataloğu primary reveal öncesi dondurulur.
- Triggered cohort primary run'dan exact alınır.
- Sensitivity planner yalnız case authorization ve immutable planning artifact'larını okuyabilir; outcome okuyamaz.
- İki MILP aynı adjusted input üzerinde plan üretir ve bağımsız validate edilir.
- Scenario plan manifesti candidate outcome join'inden önce dondurulur.
- Metrikler descriptive'dir; bootstrap, CI, p-value veya release threshold yoktur.
- Primary run status, gate ve policy decision immutable kalır.

### 4. Phase 1 entry sırası

Phase 1 ancak ayrı açık transition onayıyla açılır. İlk görev sırası:

1. `PH1-T01`: Official-source runtime/dependency/compatibility/license kararı; dependency eklemez.
2. `PH1-T02`: Onaylanan exact sürümlerle minimal scaffold ve lock.
3. `PH1-T03`: Clean-room frozen sync, import, lint, type, test ve minimal CI gate'i.

Phase 1 içinde Phase 2+ domain/data/ML/OR/API/UI/RAG placeholder'ı oluşturulamaz.

## Gerekçe

- Registry sözleşmelerin dosya adlarından bağımsız tekil kimlik ve implementation order'ını görünür yapar.
- DAG kontrolü circular build sorumluluğunu implementation öncesi yakalar.
- Exit audit belge yazmayı “faz tamamlandı” sanmak yerine ölçülebilir geçiş kapısı oluşturur.
- Dört OFAT scenario, ML risk maliyetinin ve kapasite varsayımının yön etkisini gösterirken combinatorial grid scope creep'ini önler.
- Outcome-isolated planner, post-reveal sensitivity'nin outcome'u optimization girdisine taşımasını engeller.
- Sensitivity'nin release yetkisi olmaması cherry-picked robustness sonucunun primary kararı değiştirmesini önler.
- Dependency-first Phase 1 sırası, hatalı başlangıç riskini kod oluşturmadan azaltır.
- Separate transition approval, “bir görevi onaylamak bütün fazı onaylamak değildir” kuralını korur.

## Sonuçlar

Olumlu:

- Phase 0 kararları 18 contract üzerinden izlenebilir.
- Her contract'ın implementation fazı ve dependency yönü bellidir.
- Project Spec'teki sensitivity kapsamı ölçülebilir ve sınırlı hale gelir.
- Primary blind iddia sensitivity'den etkilenmez.
- Phase 1 dependency hataları resmi uyumluluk kanıtı ve clean-room testleriyle erken yakalanır.
- Phase 1–8 PH0-T06 boyunca kilitli kalır.

Maliyet ve sınırlamalar:

- Phase transition için ayrı küçük governance adımı gerekir.
- Sensitivity yalnız iki factor ailesini kapsar; bütün ekonomik belirsizlikleri taramaz.
- Post-reveal triggered cohort sensitivity'si primary blind experiment değildir.
- Exact runtime ve paket sürümleri Phase 1 çalışma tarihine bırakılmıştır; bugün bellekten sabitlenmez.
- Belge DAG'inin acyclic olması runtime bug bulunmayacağını garanti etmez.

## Reddedilen alternatifler

- Contract'ları registry olmadan yalnız dosya adlarıyla yönetmek
- Source document içindeki her cross-reference'ı normative dependency sayıp yapay cycle üretmek
- Phase 0 task onayıyla Phase 1'i otomatik açmak
- Phase 1 açılır açılmaz pyproject ve dependency kurmak
- Gelecek data/ML/OR paketlerini “sonra lazım olur” diye Phase 1'e eklemek
- Outcome sonrası serbest sensitivity multiplier seçmek
- Bütün factor'ların Cartesian grid'ini çalıştırmak
- Sensitivity sonucunu primary release gate'e üçüncü etki kapısı yapmak
- Sensitivity'de greedy ve yeni heuristic eklemek
- Sensitivity planner'a candidate outcome erişimi vermek
- Contract header'larını phase transition onayı olmadan final `Accepted` yapmak

## Uygulama kapıları

Phase transition öncesi:

- PH0-T01..T06 completion kayıtları;
- registry unique ID/path/reference/DAG testleri;
- sensitivity exact scenario catalog ve no-joint-grid testleri;
- sensitivity output'ta primary policy mutation alanı bulunmaması;
- locked phase ve forbidden path kontrolü;
- PH0-T06 checkpoint bütünlük testi

geçmelidir.

Phase 1 başladıktan sonra PH1-T01 exact runtime/dependency kararını official sources ile yeniden doğrular. Bu ADR dependency seçmez veya kurmaz.

## Değişiklik koşulu

Registry lifecycle, Phase 0 exit gate, sensitivity factor/multiplier/strategy, primary-policy isolation, Phase 1 task sırası veya dependency approval standardı değişirse yeni ADR, scope/compute/integrity analizi ve açık insan onayı gerekir.
