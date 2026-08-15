# Phase 2 Default Field Control Discovery Raporu

| Alan | Değer |
|---|---|
| Görev | `PH2-T02-R5` |
| Bootstrap commit | `a953617b0591fd310ceea4c20ba750bd5355e3ef` |
| Discovery run/job | `31894069584` / `95034532975` |
| Foundation run/job | `31894069749` / `95034533391` |
| Workflow sonucu | `CONTROL_NOT_UNAMBIGUOUS` |
| Reason code | `OUTSIDE_CHECKED_CONTROL_COUNT_NOT_ONE` |
| Güvenli sınıflandırma | Dört bağımsız default output-field checkbox'ı |
| POST / ZIP / header / row | `0 / 0 / 0 / 0` |

## 1. Sonuç

R4'te tek bir bilinmeyen kontrol olduğu varsayımı doğru çıkmamıştır. Fresh form
fingerprint yeniden exact geçmiş ve exact-15 dışında dört checked kontrol
sanitize edilmiş public form metadata'sıyla ayrı ayrı tanımlanmıştır:

| Name / ID | Label | Type | Disabled | Exact-15 selector ile aynı name |
|---|---|---|---|---|
| `ORIGIN_AIRPORT_SEQ_ID` | `OriginAirportSeqID` | checkbox | false | false |
| `ORIGIN_CITY_MARKET_ID` | `OriginCityMarketID` | checkbox | false | false |
| `DEST_AIRPORT_SEQ_ID` | `DestAirportSeqID` | checkbox | false | false |
| `DEST_CITY_MARKET_ID` | `DestCityMarketID` | checkbox | false | false |

Workflow'un `CONTROL_NOT_UNAMBIGUOUS` sonucu kontrollerin kimliğinin belirsiz
olduğunu değil, görevdeki exact-one cardinality varsayımının yanlış olduğunu
gösterir. Dört kontrol de hidden state veya submit düğmesi değil; bağımsız,
enabled ve etiketli output-field checkbox'larıdır.

## 2. R6 için mekanik karar

R6 şu exact seti fresh form üzerinde yeniden görmek zorundadır. Set artar,
azalır veya kimliklerden biri değişirse POST yapılmaz. Set tam eşleşirse bu dört
opsiyonel field checkbox'ını form payload'ına koymamak, tarayıcıda onları
unchecked bırakmakla eşdeğerdir. Exact hedef 15 checkbox ise açıkça payload'a
eklenir.

Bu karar hiçbir hidden değer veya server state'i düşürmez. Hidden başarılı form
kontrolleri fresh değerleriyle taşınmaya devam eder; yalnız dört açık output
field seçimi dışarıda bırakılır.

## 3. Güvenlik kanıtı

- Fresh GET: `1`; redirect: `0`; retry: `0`.
- Form contract SHA-256: `3d9227bf05af8dcf8f4fef99aef86ebbbcbe43561869ba43444079d913b3f8b0`.
- Raw HTML, hidden değer, cookie değeri veya response body loglanmadı.
- POST, ZIP, CSV header ve data row erişimi yapılmadı.
- Discovery ve Foundation run'ları `success`, artifact sayıları `0`.

Geçici R5 workflow'u R6 bootstrap commit'inde silinir ve remote yokluğu kapanış
kanıtında doğrulanır.
