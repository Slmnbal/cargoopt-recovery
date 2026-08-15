# BTS Uçuş Verisi Sözleşmesi

| Alan | Değer |
|---|---|
| Contract ID | `bts-reporting-otp-contract-v1` |
| Şema sürümü | `bts-flight-schema-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T02`; multi-horizon ek: `PH0-T03` |
| Veri dönemi | 2024-01-01 — 2024-12-31 |

## 1. Amaç ve sınır

Bu sözleşme CargoOpt Recovery'nin uçuş risk modeli ve historical replay'i için kullanılacak resmî uçuş performans verisinin kaynağını, alanlarını, kimliğini, zaman anlamını ve katmanlar arası ayrımını tanımlar.

Veri:

- ABD iç hat, duraksız yolcu uçuş performansını temsil eder;
- Turkish Cargo veya THY operasyon verisi değildir;
- gerçek cargo booking, kapasite, SLA veya finansal maliyet içermez;
- kargo tarafı için nedensel veya finansal etki kanıtı olarak sunulamaz.

## 2. Resmî kaynak

Kaynak kuruluş: U.S. Department of Transportation, Bureau of Transportation Statistics — Office of Airline Information.

Seçilen tablo: **Reporting Carrier On-Time Performance (1987-present)**.

- [BTS database profile](https://transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFD)
- [Reporting Carrier tablo profili](https://transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b0-gvzr&V0s1_b0yB=D&gnoyr_VQ=FGJ)
- [Resmî alan sözlüğü](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ)

BTS bu tabloyu raporlayan taşıyıcıların işlettiği duraksız ABD iç hat uçuşları için aylık olarak yayımlar. Tablo; planlanan/gerçekleşen kalkış-varış zamanlarını, iptal ve diversion sonuçlarını, gecikmeleri ve mesafeyi içerir.

Kaggle, Hugging Face Dataset Hub veya üçüncü taraf kopyası ana veri kaynağı olamaz. Böyle bir kopya yalnızca resmî BTS dosyasıyla byte/row düzeyinde doğrulanırsa geçici aktarım aracı olarak ayrıca onaylanabilir; v1'de planlanmamıştır.

## 3. Snapshot kapsamı

```yaml
dataset_id: bts-reporting-otp-2024-top20-v1
source_table: Reporting Carrier On-Time Performance
period_start: 2024-01-01
period_end: 2024-12-31
source_frequency: monthly
expected_months: 12
airport_universe_method: train_period_total_operations_top20
raw_immutable: true
processed_format: parquet
```

Her ay ayrı kaynak artifact olarak indirilir. Phase 2'de kaynak arşivleri değiştirilemez biçimde saklanır; her arşivin URL'si, indirme zamanı, byte boyutu ve SHA-256 değeri manifestte bulunur.

## 4. Alan sınıfları

Her ingest edilen BTS alanı tam bir `primary_class` taşır:

| Sınıf | Anlamı | Model girdisi olabilir mi? |
|---|---|---:|
| `IDENTITY` | Satır/flight instance kimliği ve provenance | Doğrudan hayır; açıkça tanımlanmış türevi olabilir |
| `FEATURE_SOURCE` | İzinli T-24/T-18/T-12/T-6 cutoff'larında mevcut schedule/master-data kaynağı | Yalnızca feature allowlist üzerinden |
| `LABEL_OUTCOME` | Uçuş gerçekleştikten sonra bilinen hedef/sonuç | Hayır |
| `AUDIT_ONLY` | İnsan okunabilirlik ve tutarlılık kontrolü | Hayır |
| `REJECTED` | İndirilmeyen veya pipeline girişinde reddedilen alan | Hayır |

Bir kaynak alan birden fazla `primary_class` taşıyamaz. Alanın teknik uçuş anahtarında kullanılması, sınıfını model girdisine dönüştürmez.

## 5. Kapalı ingest alan listesi

Yalnızca aşağıdaki 15 BTS alanı indirme seçimine alınır:

| BTS alanı | Primary class | Null | Kullanım |
|---|---|---:|---|
| `FlightDate` | `IDENTITY` | Yasak | Uçuş tarihi, split ve takvim türevleri |
| `Reporting_Airline` | `AUDIT_ONLY` | Yasak | İnsan okunabilir unique carrier code |
| `DOT_ID_Reporting_Airline` | `FEATURE_SOURCE` | Yasak | Kalıcı taşıyıcı kimliği ve carrier feature |
| `Flight_Number_Reporting_Airline` | `IDENTITY` | Yasak | Flight instance doğal anahtarı; feature değil |
| `OriginAirportID` | `FEATURE_SOURCE` | Yasak | Kalıcı origin kimliği |
| `Origin` | `AUDIT_ONLY` | Yasak | İnsan okunabilir origin kodu |
| `DestAirportID` | `FEATURE_SOURCE` | Yasak | Kalıcı destination kimliği |
| `Dest` | `AUDIT_ONLY` | Yasak | İnsan okunabilir destination kodu |
| `CRSDepTime` | `FEATURE_SOURCE` | Yasak | Planlanan yerel kalkış saati |
| `CRSArrTime` | `AUDIT_ONLY` | Yasak | Planlanan yerel varış tutarlılık kontrolü |
| `CRSElapsedTime` | `FEATURE_SOURCE` | Yasak | Planlanan gate-to-gate süre, dakika |
| `Distance` | `FEATURE_SOURCE` | Yasak | Duraksız mesafe, mil |
| `Cancelled` | `LABEL_OUTCOME` | Yasak | İptal hedef bileşeni |
| `Diverted` | `LABEL_OUTCOME` | Yasak | Diversion hedef bileşeni |
| `ArrDelayMinutes` | `LABEL_OUTCOME` | Koşullu | Gerçek pozitif varış gecikmesi, dakika |

Bu liste dışında gelen her BTS alanı için varsayılan politika `REJECT_UNCLASSIFIED_FIELD` olur. Schema drift pipeline'ı fail-closed durdurur; yeni alan otomatik kabul edilmez.

### 5.1 Fiziksel CSV header ve exact canonical mapping

BTS selected-field formundaki iş alanı adları ile indirilen CSV'nin fiziksel
kolon kodları aynı identifier değildir. Kaynak archive kabul edilmeden önce raw
CSV header aşağıdaki sıraya **tam eşit** olmalıdır:

```text
FL_DATE
OP_UNIQUE_CARRIER
OP_CARRIER_AIRLINE_ID
OP_CARRIER_FL_NUM
ORIGIN_AIRPORT_ID
ORIGIN
DEST_AIRPORT_ID
DEST
CRS_DEP_TIME
CRS_ARR_TIME
ARR_DELAY_NEW
CANCELLED
DIVERTED
CRS_ELAPSED_TIME
DISTANCE
```

İzin verilen tek fiziksel-to-canonical dönüşüm aşağıdaki kapalı eşlemedir:

| Sıra | Fiziksel kaynak kolonu | Canonical iş alanı |
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

Bu eşleme `PH2-T02-R2` form-control kanıtı ile `PH2-T02-R10` raw header
kanıtının exact birleşimidir. Fuzzy match, case-fold tabanlı tahmin, alias
keşfi, eksik/fazla kolon toleransı veya sessiz projection yasaktır. Pipeline
önce raw header sırasını doğrular, sonra bu tabloyla rename eder ve canonical
15 alanı Bölüm 5'teki sözleşme sırasına yeniden dizer. Herhangi bir drift
`SNAPSHOT_FATAL` olur.

## 6. Uçuş kimliği ve duplicate politikası

Canonical doğal anahtar:

```text
FlightDate
+ DOT_ID_Reporting_Airline
+ Flight_Number_Reporting_Airline
+ OriginAirportID
+ DestAirportID
+ normalized_CRSDepTime
```

Sistem kimliği:

```text
flight_instance_id = SHA-256(canonical natural key)
```

Kurallar:

- Aynı doğal anahtara ve aynı 15 alan değerine sahip tam kopyalar exact duplicate sayılır.
- Exact duplicate tek kayda indirilebilir; kaynak satır sayısı ve kaldırılan kopya sayısı manifestte tutulur.
- Aynı doğal anahtar altında farklı alan değerleri varsa conflicting duplicate oluşur ve aylık snapshot aktive edilmez.
- Flight number tek başına kimlik değildir ve feature olamaz.

## 7. Saat ve zaman dilimi normalizasyonu

BTS `CRSDepTime` ve `CRSArrTime` alanlarını havalimanının yerel `hhmm` saati olarak verir. Tahmin cutoff'u timezone-aware bir instant olmak zorundadır.

Phase 2 normalizasyonu şu sözleşmeye uyar:

1. `OriginAirportID` ve `DestAirportID`, sürümlü bir `AirportID -> IANA timezone` eşlemesine bağlanır.
2. Eşlemenin açık kaynağı, sürümü ve hash'i ayrı manifestte tutulur.
3. `FlightDate + CRSDepTime + origin timezone` ile `scheduled_departure_at_utc` üretilir.
4. `CRSDepTime == 2400`, sonraki yerel gün `00:00` olarak normalize edilir.
5. Diğer değerlerde saat `00..23`, dakika `00..59` olmalıdır.
6. DST nedeniyle olmayan veya iki anlama gelen yerel zaman fail-closed karantinaya alınır; sessiz düzeltme yapılmaz.
7. `scheduled_arrival_at_utc = scheduled_departure_at_utc + CRSElapsedTime` olarak hesaplanır.
8. `CRSArrTime`, destination local saate çevrilen hesaplanmış varışla audit amaçlı karşılaştırılır; model girdisi olmaz.

Timezone eşlemesi bulunmayan havalimanı model evrenine alınamaz.

## 8. Outcome ve label kullanılabilirlik zamanı

BTS aylık ve tarihsel bir kaynaktır; gerçek operasyon outcome publication timestamp'i sağlamaz. Backtest'in gelecek bilgisi görmesini önlemek için konservatif bir simülasyon zamanı kullanılır:

```text
label_available_at = scheduled_arrival_at_utc + 24 hours
```

Bir geçmiş uçuşun outcome'u rolling feature'a ancak:

```text
label_available_at <= target_prediction_cutoff_at
```

koşulunda girebilir. Bu 24 saatlik gecikme gerçek BTS yayın SLA'sı iddiası değil, leakage önleyici proje varsayımıdır.

## 9. Hedef alanlarının null politikası

Label:

```text
severe_disruption = 1
if Cancelled == 1
   OR Diverted == 1
   OR ArrDelayMinutes >= 60
else 0
```

Kurallar:

- `Cancelled` ve `Diverted` yalnızca `0` veya `1` olabilir.
- İkisi aynı satırda `1` olamaz; olursa conflicting outcome olarak karantinaya alınır.
- `Cancelled == 1` veya `Diverted == 1` ise `ArrDelayMinutes` null olabilir ve label yine `1` olur.
- Her ikisi de `0` ise `ArrDelayMinutes` zorunlu, sonlu ve `>= 0` olmalıdır.
- Her ikisi `0` iken gecikme eksikse label uydurulmaz; satır model/evaluation evreninden karantinaya alınır.
- Outcome alanlarına imputasyon yapılmaz.

## 10. En yoğun 20 havalimanı algoritması

Havalimanı seçimi yalnızca `2024-01-01 <= FlightDate <= 2024-08-31` eğitim partition'ından yapılır.

Algoritma:

1. Structural validation ve exact dedup tamamlanır.
2. İptal/diversion dahil her planlanmış uçuş tutulur.
3. Her `OriginAirportID` bir kalkış operasyonu, her `DestAirportID` bir varış operasyonu olarak sayılır.
4. `total_operations = origin_count + destination_count` hesaplanır.
5. Azalan `total_operations`, eşitlikte artan `AirportID` sıralaması uygulanır.
6. İlk 20 AirportID dondurulur.
7. `top20_airport_set_id = SHA-256(sorted AirportID list)` üretilir.
8. ML evreninde hem origin hem destination bu dondurulmuş kümede olmalıdır.

Eylül–Aralık verisi sıralamayı veya tie-break'i etkileyemez. 20 geçerli havalimanı oluşmazsa snapshot başarısızdır.

## 11. Zaman partition'ları

| Partition | Hedef uçuş tarihi | Kullanım |
|---|---|---|
| `TRAIN` | 2024-01-01 — 2024-08-31 | Feature warm-up ve model fitting |
| `VALIDATION` | 2024-09-01 — 2024-10-31 | Model/calibration seçimi |
| `ML_TEST` | 2024-11-01 — 2024-11-30 | Dondurulmuş ML testi |
| `BLIND_REPLAY` | 2024-12-01 — 2024-12-31 | Uçtan uca ML + OR değerlendirmesi |

30 günlük rolling feature için 1–31 Ocak warm-up olarak tutulur. İlk model-fitting hedef tarihi `2024-02-01` olur. Bu, Ocak verisinin TRAIN partition'ında olmasını değiştirmez; Ocak satırları geçmiş feature üretir fakat yeterli lookback bulunmadan model hedef satırı olmaz.

Validation, test ve blind dönemde geçmiş günlerin outcome'u yalnızca Bölüm 8'deki availability kuralı sağlanıyorsa rolling feature'a girebilir. Model yeniden fit edilmez. Aralık outcome'u Phase 5 outcome-reveal adımından önce performans hesabı veya tuning için açılamaz.

## 12. Veri katmanları

| Katman | İçerik | Mutation | Outcome görünürlüğü |
|---|---|---:|---:|
| `raw` | Kaynaktan indirilen aylık archive | Yasak | Kaynakta mevcut |
| `staging` | Tip dönüşümü ve doğrulama sonucu | Yeniden üretilebilir | Erişim kontrollü |
| `processed/schedule` | Kimlik, schedule ve master-data alanları | Immutable snapshot | Yok |
| `processed/outcome` | Cancelled, Diverted, ArrDelayMinutes, label | Immutable snapshot | Yalnızca label/evaluation hattı |
| `features` | T-24/T-18/T-12/T-6 as-of feature matrix | Immutable snapshot | Yok |
| `evaluation` | Dondurulmuş prediction ve sonradan açılan outcome | Immutable run | Kontrollü reveal |

Schedule ve outcome fiziksel/lojik olarak ayrı artifact'larda tutulur. Feature pipeline outcome tablosuna doğrudan serbest join yapamaz; yalnızca as-of feature builder sözleşmesi üzerinden erişir.

Önerilen artifact isimleri yalnızca sözleşmedir; Phase 2'den önce dizinleri oluşturulmaz:

```text
data/raw/bts/year=2024/month=MM/
data/processed/schedule/year=2024/month=MM/
data/processed/outcome/year=2024/month=MM/
artifacts/features/{feature_snapshot_id}/
artifacts/evaluation/{evaluation_run_id}/
```

## 13. Dataset manifesti

Her aktive edilen dataset snapshot en az şu alanları taşır:

```yaml
dataset_id: bts-reporting-otp-2024-top20-v1
schema_version: bts-flight-schema-v1
source_table: Reporting Carrier On-Time Performance
source_urls: []
period_start: 2024-01-01
period_end: 2024-12-31
selected_fields: []
monthly_artifacts:
  - month: 2024-01
    byte_size: 0
    raw_sha256: ""
    raw_row_count: 0
processed_row_count: 0
quarantined_row_count: 0
exact_duplicate_count: 0
top20_airport_ids: []
top20_airport_set_id: ""
timezone_mapping_id: ""
processed_schedule_sha256: ""
processed_outcome_sha256: ""
pipeline_git_sha: ""
created_at: ""
status: CANDIDATE
```

`status` yalnızca bütün kalite kapıları geçince `ACTIVE` olabilir. Hash veya kaynak bilgisi eksik snapshot model eğitiminde kullanılamaz.

## 14. Sözleşmenin değişmesi

Alan listesi, label, multi-horizon cutoff seti, source T-6 decision, top-20 algoritması, partition sınırı, availability lag veya null politikası değişikliği:

- yeni schema/contract sürümü;
- ADR;
- leakage ve geriye uyumluluk analizi;
- mevcut deneylerin tekrar üretilebilirlik etkisi;
- açık insan onayı

gerektirir. Blind replay görüldükten sonra v1 üzerinde geriye dönük değişiklik yapılamaz.
