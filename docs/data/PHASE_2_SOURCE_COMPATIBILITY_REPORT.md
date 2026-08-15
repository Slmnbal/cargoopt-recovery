# Phase 2 Kaynak Uyumluluk Probe Raporu

| Alan | Değer |
|---|---|
| Belge kimliği | `phase-2-source-compatibility-report-v1` |
| Görev | `PH2-T02` |
| Dönem | `2024-01` |
| Başlangıç | `2026-08-15T13:44:10Z` |
| Bitiş | `2026-08-15T13:48:02Z` |
| Kapalı sonuç | `PROBE_SECURITY_ABORTED` |
| Reason code | `EXECUTION_ENVIRONMENT_CANNOT_ENFORCE_PROBE_TRANSPORT_CONTRACT` |
| Kalıcı kaynak byte'ı | `0` |
| Okunan veri satırı | `0` |

## 1. Karar özeti

Resmî BTS dataset kimliği, alan sözlüğü ve Ocak 2024 PREZIP kaydı
doğrulanabildi. Ancak onaylı standard-library probe istemcisi çalışma
ortamından resmî hosta DNS çözümleyemedi. Tanılama amaçlı resmî sayfa erişim
katmanı sayfaları gösterebildi; buna karşılık bu katman transport-level
concurrency, redirect zinciri, response header'ları, byte hash'i ve bounded
binary stream kontrollerini sunmadı.

Selected-field formu sabit URL, resmî `Download` bağlantısı ve izinli host
varyantı üzerinden deterministik biçimde alınamadı. Form action'ı ve hidden
control yapısı görülmediği için POST tahmin edilmedi. Ocak ZIP URL'sinin resmî
indexte varlığı ve içerik türü görüldü fakat artifact byte'ı indirilmedi;
dolayısıyla ZIP member ve exact-15 CSV header kontrolü yapılmadı.

Bu kanıtlarla `SOURCE_COMPATIBLE` veya kalıcı bir source mismatch iddiası
kurulamaz. Transport güvenlik sözleşmesi ispatlanamadığı için görev
`PROBE_SECURITY_ABORTED` ile fail-closed durmuştur.

## 2. Onay ve yürütme sınırı

| Kontrol | Sonuç |
|---|---|
| Exact yürütme onayı network öncesi kaydedildi | `PASSED` |
| Plan commit hosted Foundation CI | `PASSED` — run `31887820149` |
| İzinli scheme | Yalnız `https` |
| Kimlik doğrulama/secret/proxy | Kullanılmadı; direct client environment proxy'lerini kapattı |
| Kullanılan HTTP method | Yalnız `GET`; `HEAD` ve `POST` kullanılmadı |
| Strict direct-client request | `1` |
| Resmî sayfa tanılama operasyonu | `9` |
| Toplam mantıksal operasyon | `10 / 12` |
| Strict istemci concurrency | `1` |
| Tanılama katmanı transport concurrency/redirect kanıtı | Sunulmadı; success için kabul edilmedi |
| Toplam probe süresi | `232 / 600` saniye |
| Artifact | `0 / 1` |
| Kalıcı HTML/ZIP/CSV/cookie/token | `0` |
| Okunan veya parse edilen data row | `0` |

## 3. Resmî kaynak kanıtları

Bütün kaynaklar `2026-08-15` tarihinde yalnız task allowlist'indeki resmî
hostlardan incelendi.

| ID | Resmî URL | Gözlenen kanıt | Probe kararı |
|---|---|---|---|
| `BTS-01` | https://www.transtats.bts.gov/ontime/ | Airline On-Time Statistics kapsamı, veri mevcudiyeti ve local 24-hour time açıklaması görüldü | Dataset ailesi doğrulandı |
| `BTS-02` | https://transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFD | Reporting Carrier On-Time Performance tablosunun aylık, iç hat, uçuş-seviyesi download kapsamı görüldü | Dataset kimliği doğrulandı |
| `BTS-03` | https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ | Resmî sözlük 111 alan gösterdi; contract'taki 15 alanın tümü sözlükte bulundu | Field-name varlığı doğrulandı; output header doğrulanmadı |
| `BTS-04` | https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ | Sabit selected-field URL tanılama katmanında `Internal Error` üretti | Form/action/control contract'ı alınamadı |
| `BTS-05` | https://transtats.bts.gov/PREZIP/ | Ocak 2024 dosyası `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_1.zip`, listelenen boyut `27,573,265` byte | Artifact kimliği ve index boyutu doğrulandı |
| `BTS-06` | https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_1.zip | Tanılama istemcisi `application/x-zip-compressed` gördü fakat binary içeriği desteklemedi | Byte/hash/member/header kanıtı yok; artifact budget harcanmadı |
| `DOT-01` | https://ntl.bts.gov/ntl/public-access/managing-rights | DOT-funded research çıktıları için genel rights yaklaşımı ve CC-BY teşviki görüldü | Exact TranStats dataset lisansı olarak yorumlanmadı |

## 4. Request ve hata kanıtı

| Mantıksal operasyon | Hedef | Sonuç | Kalıcı byte |
|---:|---|---|---:|
| 1 | `BTS-01`, strict `urllib` GET | Response öncesi DNS failure: temporary name-resolution failure; `0.002` saniye; cookie sayısı `0` | 0 |
| 2 | `BTS-01`, resmî sayfa tanılaması | Sayfa metni erişilebilir | 0 |
| 3 | `BTS-02`, resmî sayfa tanılaması | Dataset profili erişilebilir | 0 |
| 4 | `BTS-03`, resmî sayfa tanılaması | Field dictionary erişilebilir | 0 |
| 5 | `BTS-05`, resmî index tanılaması | Ocak dosya adı ve listelenen boyut erişilebilir | 0 |
| 6 | `DOT-01`, resmî sayfa tanılaması | Rights sayfası erişilebilir | 0 |
| 7 | `BTS-04`, sabit selected-field URL | `Internal Error`; form gövdesi/action alınamadı | 0 |
| 8 | `BTS-03` içindeki resmî `Download` bağlantısı | `Internal Error`; form gövdesi/action alınamadı | 0 |
| 9 | `BTS-06`, Ocak ZIP URL | Binary content type görüldü; istemci desteklemedi, body alınmadı | 0 |
| 10 | `BTS-04`, izinli non-`www` host varyantı | Bounded fetch timeout | 0 |

İki local invalid-link denemesi URL resolve edilmeden reddedildiği ve bir URL
safety kontrolü network'e çıkmadan durduğu için request bütçesine katılmadı.
Hiçbir 3xx redirect zinciri diagnostic katmandan açıklanmadı; bu eksik kanıt
success yerine security abort gerekçesidir.

## 5. Exact-15 header kapısı

Beklenen header sırası:

```text
FlightDate
Reporting_Airline
DOT_ID_Reporting_Airline
Flight_Number_Reporting_Airline
OriginAirportID
Origin
DestAirportID
Dest
CRSDepTime
CRSArrTime
CRSElapsedTime
Distance
Cancelled
Diverted
ArrDelayMinutes
```

| Kontrol | Sonuç |
|---|---|
| 15 alanın resmî field dictionary'de varlığı | `PASSED` |
| Selected-field request fingerprint | `NOT_OBTAINED` |
| Response status/header/ETag/Last-Modified/byte SHA-256 | `NOT_OBTAINED` |
| ZIP member sayısı/adı/encryption/declared size | `NOT_RUN` |
| Raw CSV header | `NOT_OBTAINED` |
| Parsed header exact equality | `NOT_RUN` |
| BOM dışında trim/rename/reorder/projection | Uygulanmadı |
| Data rows read | `0` |

Field dictionary'de alanların bulunması, selected output header'ının exact ve
aynı sırada olduğunun kanıtı değildir.

## 6. Rights kararı

DOT Managing Rights sayfası genel public-access ve araştırma fonlama
koşullarını açıklar; exact TranStats flight archive için dataset-specific
license grant sunmaz. Bu yüzden:

- local analysis hakkı bu görevde doğrulanmış sayılmadı;
- raw redistribution kapalı kalır;
- DOT sayfasındaki CC-BY teşviki bu dataset'e CC-BY atanması için kullanılmaz;
- primary result transport security abort olduğu için ayrı bir ikinci closed
  result üretilmez, ancak rights kapısı da başarıyla geçmemiştir.

## 7. Cleanup ve kalıcılık kanıtı

- Strict network denemesi HTML, cookie veya artifact üretmedi.
- Diagnostic erişimler repository'ye page/archive byte'ı yazmadı.
- OS temporary cleanup guard marker ile çalıştırıldı; context çıkışından sonra
  temporary path'in yokluğu doğrulandı.
- Temporary path yalnız SHA-256 fingerprint ile kontrol edildi; absolute path
  rapora yazılmadı.
- Cookie, anti-CSRF, token, ZIP, CSV, header buffer veya source row kalmadı.
- `data/`, `artifacts/`, `configs/` veya cache dizini oluşturulmadı.

## 8. Downstream kapısı

`PH2-T03` planlanamaz. Retry, source-contract değişikliği veya başka bir
governance kararı kendiliğinden başlatılamaz. Güvenli retry için en az:

1. standard-library istemciden izinli resmî hostlara doğrudan HTTPS erişimi;
2. request/concurrency/redirect/timeout/byte kontrollerinin istemci tarafından
   uygulanması ve raporlanması;
3. selected-field form HTML/action/control yapısının public olarak alınması;
4. tek Ocak artifact'ının bounded binary stream ile alınabilmesi;
5. aynı exact task sınırı için yeni açık insan kararı

gerekir. Bu koşullar oluşmadan full-width PREZIP projection, mirror, manuel
browser, dependency kurulumu veya 12 aylık acquisition yapılmaz.

## 9. Repository ve hosted doğrulama

| Kontrol | Sonuç |
|---|---|
| Result commit | `4619dbda56a78f6deed74e21fa1602006590ecf6` |
| Değişen repository dosyaları | Yalnız task exact allowlist'indeki 4 dosya |
| Foundation run | `31888347851` |
| Foundation job | `95020802321` |
| Ana adımlar | `17 / 17 PASSED` |
| Workflow sonucu | `success` |
| Workflow artifact | `0` |

Bu hosted success yalnız repository bütünlüğünü doğrular; source compatibility
probe'unun `PROBE_SECURITY_ABORTED` sonucunu `SOURCE_COMPATIBLE` yapmaz.
