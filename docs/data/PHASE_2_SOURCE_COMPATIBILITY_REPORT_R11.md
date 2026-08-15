# PH2-T02-R11 Offline Fiziksel Header Uzlaştırma Raporu

| Alan | Değer |
|---|---|
| Görev | `PH2-T02-R11` |
| Tarih | `2026-08-15` |
| Sonuç | `SOURCE_COMPATIBLE` |
| Reason code | `EXACT_PHYSICAL_TO_CANONICAL_MAPPING_CONFIRMED` |
| Network request | `0` |
| Yeni/okunan data row | `0` |
| Kalıcı source byte | `0` |

## Kanıt zinciri

- `PH2-T02-R3`: resmî public government-works metadata zinciriyle attribution
  zorunlu local analysis doğrulandı; raw redistribution kapalı kaldı.
- `PH2-T02-R2`: 15 selected-field control için business label ve fiziksel
  kaynak kodu exact mapping'i kanıtlandı.
- `PH2-T02-R10`: Ocak 2024 exact selected-field POST `200` döndü; tek güvenli
  ZIP member'ın yalnız header satırı okundu.
- R10 raw header: 15 kolon; extra `0`, missing `0`, duplicate `0`, empty `0`.
- R10 data row read invariant: `0`.
- R10 geçici ZIP cleanup: `PASSED`.

## Dondurulan mapping

| Sıra | Fiziksel kaynak | Canonical alan |
|---:|---|---|
| 1 | `FL_DATE` | `FlightDate` |
| 2 | `OP_UNIQUE_CARRIER` | `Reporting_Airline` |
| 3 | `OP_CARRIER_AIRLINE_ID` | `DOT_ID_Reporting_Airline` |
| 4 | `OP_CARRIER_FL_NUM` | `Flight_Number_Reporting_Airline` |
| 5 | `ORIGIN_AIRPORT_ID` | `OriginAirportID` |
| 6 | `ORIGIN` | `Origin` |
| 7 | `DEST_AIRPORT_ID` | `DestAirportID` |
| 8 | `DEST` | `Dest` |
| 9 | `CRS_DEP_TIME` | `CRSDepTime` |
| 10 | `CRS_ARR_TIME` | `CRSArrTime` |
| 11 | `ARR_DELAY_NEW` | `ArrDelayMinutes` |
| 12 | `CANCELLED` | `Cancelled` |
| 13 | `DIVERTED` | `Diverted` |
| 14 | `CRS_ELAPSED_TIME` | `CRSElapsedTime` |
| 15 | `DISTANCE` | `Distance` |

## Mekanik doğrulama sonucu

| Kontrol | Sonuç |
|---|---|
| Fiziksel kolon sayısı | `15 — PASSED` |
| Canonical kolon sayısı | `15 — PASSED` |
| Fiziksel uniqueness | `15/15 — PASSED` |
| Canonical uniqueness | `15/15 — PASSED` |
| R10 raw order equality | `PASSED` |
| R2 mapping equality | `PASSED` |
| Canonical accepted set equality | `PASSED` |
| Fuzzy/alias/fallback kuralı | `0 — PASSED` |

Canonical iş sözleşmesinde `CRSElapsedTime` ve `Distance`, outcome alanlarından
önce tutulur. Fiziksel CSV'de bu iki kolon sonda gelir. Bu fark yalnız yukarıdaki
exact mapping sonrası deterministik canonical reorder ile çözülür; kaynak raw
sırası değiştirilmiş kabul edilmez.

## Normatif değişiklikler

- `BTS_DATA_CONTRACT.md`: exact raw fiziksel header ve closed mapping eklendi.
- `DATA_QUALITY_CONTRACT.md`: raw ve post-map iki ayrı `SNAPSHOT_FATAL` şema
  kapısı eklendi.
- `ADR-010`: karar, alternatifler ve downstream sonuçlar kabul edildi.

## Kapanış

`PH2-T02` toplam görevi `COMPLETED/SOURCE_COMPATIBLE` durumundadır. Phase 2
aktif kalır; sıradaki izinli iş yalnız `PH2-T03` görevini planlamaktır.
`PH2-T03` oluşturulmamış, ingestion implementation başlatılmamış ve 12 aylık
veri acquisition yapılmamıştır.
