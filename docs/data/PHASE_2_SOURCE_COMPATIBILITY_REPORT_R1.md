# Phase 2 Kaynak Uyumluluk Güvenli Retry Raporu

| Alan | Değer |
|---|---|
| Belge kimliği | `phase-2-source-compatibility-report-r1` |
| Görev | `PH2-T02-R1` |
| Probe modu | `DISCOVERY` |
| Dönem hedefi | `2024-01` |
| Yürütme commit'i | `f8ce2cef29ac1d9e387ba0254e1eca8645fe3000` |
| Probe run/job | `31889912917` / `95024553029` |
| Foundation run/job | `31889912921` / `95024552833` |
| Kapalı sonuç | `PROBE_SECURITY_ABORTED` |
| Extract | `NOT_RUN` |
| Artifact | `0` |
| Okunan veri satırı | `0` |

## 1. Karar özeti

GitHub-hosted `ubuntu-24.04` runner üzerindeki standard-library Discovery probe'u
beş resmî sayfaya toplam beş `GET` isteği gönderdi. Redirect oluşmadı. Dataset
profili, alan sözlüğü, selected-field sayfası ve PREZIP index'i `200` döndü.
Selected-field sayfası alınabildi; fakat seçilen form action adayı exact HTTPS
host allowlist kontrolünü geçmedi. İstemci bu noktada action'ı izlememiş, POST
göndermemiş ve `URL_POLICY_VIOLATION` ile fail-closed durmuştur.

Haklar için onaylı NTL endpoint'i aynı runner'da `403` döndürmüştür. Bu nedenle
yerel analiz hakkı ve attribution koşulu approved source seti içinde ayrıca
kanıtlanamamıştır. Form sözleşmesi veya haklar kapısı geçmediği için Extract
workflow'u oluşturulmamış ve hiçbir ZIP/CSV byte'ı indirilmemiştir.

## 2. Yürütme sınırı

| Kontrol | Sonuç |
|---|---|
| Runner | `ubuntu-24.04`, Linux x86_64 |
| Python | `CPython 3.12.3` |
| Checkout/action/dependency | Kullanılmadı |
| Workflow permission | `{}` |
| Secret/cache/artifact/OIDC | Kullanılmadı |
| HTTP method | Yalnız `GET` |
| Request | `5 / 7` |
| Redirect | `0 / 5` |
| Otomatik retry | `0` |
| POST | `0` |
| Geçici ZIP | `0 / 1` |
| Data row | `0` |

## 3. Resmî endpoint sonuçları

| ID | HTTP | Byte | SHA-256 | Karar |
|---|---:|---:|---|---|
| Dataset profile | 200 | 128.037 | `ada4d8b12155b793e98662e613f1d435916ce5a6738f15c9dbb29687e37e2d3d` | Erişilebilir |
| Field dictionary | 200 | 151.048 | `54e1083cb1accca7b14dfc2ba46b4b496af7350a6b4273aa93625088bb864f43` | Erişilebilir |
| Selected-field form | 200 | 171.840 | `a0799e6cb2ae3e4944f1e3158bdc1a6b1277e767fd51414adfe765cc045b8c64` | Body alındı; action policy abort |
| PREZIP index | 200 | 163.180 | `683558005106b86f01f015e8f77712247a75e8c42f0cc716f83bed989e3c8d84` | Erişilebilir |
| NTL managing-rights | 403 | 412 | `51b23e5513c028c4daa48c0976bb69f75103f7607d541c8f9e149542d5dfff85` | Rights kanıtı alınamadı |

Response body, cookie değeri, hidden token, CSRF değeri veya HTML excerpt'i
rapora ya da artifact'a taşınmamıştır. Yalnız safe metadata, cookie adları ve
hash'ler sanitize edilmiş workflow JSON'unda tutulmuştur.

## 4. Form sözleşmesi kararı

Form sayfasının `200` olması exact request sözleşmesinin kanıtlandığı anlamına
gelmez. Action URL adayı scheme/host doğrulamasında durduğu için:

- action izlenmedi;
- year/month ve exact-15 mapping success olarak sunulmadı;
- form contract fingerprint success kanıtı üretilmedi;
- POST descriptor veya request fingerprint oluşturulmadı.

Bu durum scriptable exact-15 kaynağını olumlu kanıtlamaz.

## 5. Haklar kararı

Approved Discovery source setindeki NTL haklar sayfası hosted runner'a `403`
döndürdü. Genel bir DOT/BTS açıklaması exact Reporting Carrier On-Time
Performance tablosuna otomatik lisans olarak atanmadı. Raw redistribution
kapalı kalır; rights sonucu olumlu sayılmaz.

## 6. Extract ve cleanup

- `READY_FOR_EXTRACT` üretilmedi.
- Extract workflow'u oluşturulmadı.
- ZIP/CSV indirilmedi veya açılmadı.
- Header ve data row okunmadı.
- Workflow artifact yüklenmedi.
- Geçici Discovery workflow'u result commit'inde silinir.

## 7. Hosted kanıt

Discovery workflow run `31889912917` ve job `95024553029` `success` ile
tamamlandı. Bu başarı probe protokolünün kapalı sonuç ürettiğini gösterir;
source compatibility başarısı değildir. Aynı commit üzerindeki Foundation run
`31889912921`, job `95024552833` ile bütün 17 işlevsel adımda geçti. İki
workflow da sıfır artifact üretti.

Result ve final closeout commit/run kanıtları cleanup doğrulamasından sonra bu
bölüme eklenir.

## 8. Downstream kapısı

`PH2-T03` planlanamaz. İlerleme için action parsing/protocol düzeltmesini ve
resmî, erişilebilir, dataset ile ilişkilendirilebilir rights kaynağını birlikte
tanımlayan yeni, açıkça sınırlandırılmış bir güvenlik kararı gerekir. Mirror,
full-width silent projection veya raw redistribution otomatik fallback değildir.
