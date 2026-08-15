# Phase 2 Form ve Haklar Discovery Raporu

| Alan | Değer |
|---|---|
| Belge kimliği | `phase-2-source-compatibility-report-r2` |
| Görev | `PH2-T02-R2` |
| Yürütme commit'i | `52b636b6fc083615e690d40658eba5f8da7a5e8d` |
| Discovery run/job | `31890793103` / `95026641555` |
| Foundation run/job | `31890792970` / `95026640835` |
| Kapalı sonuç | `UPSTREAM_UNAVAILABLE` |
| Form sözleşmesi | `PASSED` |
| Haklar zinciri | `NOT_PROVEN` |
| Extract | `NOT_RUN` |
| Artifact / data row | `0 / 0` |

## 1. Karar özeti

Read-only R2 Discovery, R1'deki form parser belirsizliğini gidermiştir. Resmî
TranStats selected-field sayfasındaki exact `2024`, `January` ve normatif 15
alanın her biri tek bir kontrolle, aynı form içinde ve aynı sıradaki contract
listesine one-to-one eşlenmiştir. Form action'ı allowlisted HTTPS selected-field
URL'sidir, method `POST`'tur; login, CAPTCHA, password veya manual interaction
gereksinimi görülmemiştir.

Haklar tarafında kullanıcı tarafından onaylanan iki resmî Data.gov CKAN
`package_show` endpoint'i `404` döndürmüştür. USA.gov government-works sayfası
`200` dönmüş olsa da primary Data.gov metadata bridge alınamadığından BTS
flight data → TranStats distribution → government-works lisans zinciri
kanıtlanmamıştır. Bu yüzden sonuç `UPSTREAM_UNAVAILABLE` olmuş, rights success
iddiası kurulmamış ve Extract çalıştırılmamıştır.

## 2. Request ve güvenlik sınırı

| Kontrol | Sonuç |
|---|---|
| Runner | `ubuntu-24.04`, CPython `3.12.3`, Linux x86_64 |
| HTTP method | Yalnız `GET` |
| Request | `4 / 6` |
| Redirect | `0 / 2` |
| Retry | `0` |
| Checkout/action/dependency | Yok |
| Permission | `{}` |
| Secret/cache/artifact/OIDC | Yok |
| POST/ZIP/CSV | `0 / 0 / 0` |
| Data row | `0` |

## 3. Form sözleşmesi kanıtı

| Kontrol | Sonuç |
|---|---|
| Selected-field GET | `200`, 171.840 byte |
| Response SHA-256 | `e2f19af026bb40f7662ac159993f9e02fde8acaebddcd397bd7debe6d688acb7` |
| Action | Allowlisted HTTPS current selected-field URL |
| Method | `POST` |
| Yıl | Tek eşleşme: `cboYear=2024` |
| Ay | Tek eşleşme: `cboPeriod=1`, label `January` |
| Exact field mapping | `15 / 15`, one-to-one, aynı form |
| Default extra field | `0` |
| Login/CAPTCHA/manual/password | Hepsi `false` |
| Form contract SHA-256 | `3d9227bf05af8dcf8f4fef99aef86ebbbcbe43561869ba43444079d913b3f8b0` |

`OriginAirportID` ve `DestAirportID` upstream formda default checked'dir ve
normatif 15 alanın içinde oldukları için extra field sayılmamıştır. Diğer
13 normatif alan tek tek explicit seçilebilir durumdadır.

## 4. Exact alan mapping'i

| Contract alanı | Upstream control |
|---|---|
| `FlightDate` | `FL_DATE` |
| `Reporting_Airline` | `OP_UNIQUE_CARRIER` |
| `DOT_ID_Reporting_Airline` | `OP_CARRIER_AIRLINE_ID` |
| `Flight_Number_Reporting_Airline` | `OP_CARRIER_FL_NUM` |
| `OriginAirportID` | `ORIGIN_AIRPORT_ID` |
| `Origin` | `ORIGIN` |
| `DestAirportID` | `DEST_AIRPORT_ID` |
| `Dest` | `DEST` |
| `CRSDepTime` | `CRS_DEP_TIME` |
| `CRSArrTime` | `CRS_ARR_TIME` |
| `CRSElapsedTime` | `CRS_ELAPSED_TIME` |
| `Distance` | `DISTANCE` |
| `Cancelled` | `CANCELLED` |
| `Diverted` | `DIVERTED` |
| `ArrDelayMinutes` | `ARR_DELAY_NEW` |

## 5. Haklar endpoint sonuçları

| Endpoint | HTTP | Byte | SHA-256 | Karar |
|---|---:|---:|---|---|
| Data.gov `bts-flight-data` API | 404 | 36 | `8645212e2a6dda613ea2084ea24cf62a4e6aac2c3a34c74d1e219337d3a1f609` | Metadata bridge yok |
| Data.gov marketing on-time API | 404 | 36 | `8645212e2a6dda613ea2084ea24cf62a4e6aac2c3a34c74d1e219337d3a1f609` | Corroboration alınamadı |
| USA.gov government works | 200 | 521 | `b5128fd8bd0fbcb642b2cc21647a3352bfeea66030abe6221084b41db2cc1c71` | Primary catalog bridge olmadan yeterli değil |

Response body veya excerpt rapora yazılmamıştır. Sadece safe metadata ve
mekanik boolean kararları sanitize edilmiş result JSON'a alınmıştır.

## 6. Extract ve cleanup

- `DISCOVERY_READY_FOR_EXTRACT_PLANNING` üretilmedi.
- POST gönderilmedi.
- ZIP/CSV/header/data row okunmadı.
- Workflow artifact yüklenmedi.
- Geçici R2 workflow'u result commit'inde silinir.

## 7. Hosted kanıt

Discovery workflow ve aynı commit'teki Foundation workflow `success` ile
tamamlanmış, ikisi de sıfır artifact üretmiştir. Workflow success kapalı sonuç
protokolünün çalıştığını gösterir; rights veya source compatibility success
anlamına gelmez.

Result/cleanup commit'i `94246e865ae2882dd160ca39a65634b7bec3b3cf`
üzerindeki Foundation run `31890920119`, job `95026946209` ile başarıyla
tamamlandı ve sıfır artifact üretti. Aynı commit'te geçici R2 workflow yolunun
GitHub Contents API sonucu `404 Not Found` olarak doğrulandı.

Final closeout commit ve onun Foundation sonucu repository dışı hosted kanıt
olarak görev kapanışında doğrulanır; commit kendi SHA'sını öz-referanslı olarak
içeriğine yazmaz.

## 8. Downstream kapısı

Form belirsizliği çözülmüştür; kalan tek kaynak kapısı haklar metadata bridge
erişimidir. `PH2-T03` yine planlanamaz. Yeni görev, Data.gov'un erişilebilir
HTML sayfalarını veya resmî catalog metadata export'unu bounded read-only
olarak kullanmayı ayrıca tanımlamalıdır. Extract veya raw redistribution
otomatik fallback değildir.
