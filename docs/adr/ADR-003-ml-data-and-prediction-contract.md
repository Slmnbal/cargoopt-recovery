# ADR-003 — ML Veri, T-6 Availability ve Tahmin Sözleşmesi

| Alan | Değer |
|---|---|
| Durum | Accepted; T-6-only prediction kapsamı ADR-005 ile kısmen superseded |
| Tarih | 2026-08-13 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | PH0-T02 |

## Bağlam

> Tarihsel not: Bu ADR'nin kaynak uçuş için `T-6` karar anı korunur. Her target uçuşu yalnızca kendi T-6 anında score etme kararı, 24 saatlik recovery candidate penceresinde point-in-time leakage yarattığı için ADR-005 tarafından multi-horizon ladder ile genişletilmiştir. Feature/prediction v2 yeni yetkili sözleşmedir.

BTS Reporting Carrier On-Time Performance tablosu planlanan schedule alanlarıyla uçuş sonrası gerçekleşen sonuçları aynı kaynak satırında sunar. Bu yapı dikkatsiz bir pipeline'da target leakage yaratabilir. Ayrıca BTS gerçek-time outcome publication timestamp'i ve doğrudan timezone alanı sağlamaz. Random split, toplu rolling aggregate veya tüm yıl üzerinden havalimanı seçimi gerçek karar anında bilinmeyen bilgiyi modele taşıyabilir.

## Resmî dayanak

- [BTS Airline On-Time Performance database profile](https://transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFD)
- [Reporting Carrier On-Time Performance table profile](https://transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b0-gvzr&V0s1_b0yB=D&gnoyr_VQ=FGJ)
- [BTS Reporting Carrier field dictionary](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ)

BTS sözlüğüne göre `CRSDepTime`, `CRSArrTime` ve `CRSElapsedTime` planlanan schedule alanlarıdır; `DepTime`, `ArrTime`, `ArrDelayMinutes`, `Cancelled`, `Diverted` ve neden alanları uçuş sonucunu temsil eder. AirportID ve DOT Airline ID zaman içinde analiz için kalıcı kimliklerdir.

## Karar

### 1. Kapalı alan listesi

Pipeline yalnızca 15 alan ingest eder:

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

Her alan tam bir primary class taşır. Unlisted alan varsayılan `REJECT` olur ve schema drift snapshot'ı durdurur.

### 2. Schedule/outcome ayrımı

- Schedule/identity ve outcome ayrı immutable artifact'larda tutulur.
- Target outcome model matrix'e giremez.
- Outcome alanlarına imputasyon yapılmaz.
- Eksik veya çelişkili outcome label uydurmak yerine satırı karantinaya alır.

### 3. T-6 tahmin anı

```text
prediction_cutoff_at = scheduled_departure_at_utc - 6h
```

BTS yerel schedule zamanları, sürümlü AirportID–IANA timezone mapping ile UTC instant'a çevrilir. Mapping eksik veya DST çözümü belirsizse satır karantinaya alınır.

### 4. Konservatif label availability

```text
label_available_at = scheduled_arrival_at_utc + 24h
```

Historical outcome ancak `label_available_at <= prediction_cutoff_at` ise rolling feature'a girebilir. 24 saat BTS yayın SLA'sı değildir; offline kaynağın gerçek-time availability bilgisi olmadığı için seçilmiş konservatif deney varsayımıdır.

### 5. Label

```text
Cancelled == 1 OR Diverted == 1 OR ArrDelayMinutes >= 60
```

Diversion, planlanan destination'a ulaşma taahhüdünü bozduğu için ciddi aksama kabul edilir.

### 6. Havalimanı evreni

Top-20 AirportID yalnızca 1 Ocak–31 Ağustos TRAIN verisindeki toplam scheduled origin + destination operation sayısıyla seçilir. Sıralama `operations DESC, AirportID ASC` olur. Liste ve hash sonraki partition'lar için dondurulur.

### 7. Split ve warm-up

- TRAIN: `2024-01-01`–`2024-08-31`
- VALIDATION: `2024-09-01`–`2024-10-31`
- ML_TEST: `2024-11-01`–`2024-11-30`
- BLIND_REPLAY: `2024-12-01`–`2024-12-31`
- `2024-01-01`–`2024-01-31`, 30 günlük rolling history warm-up'tır.
- İlk model target tarihi `2024-02-01`'dir.

Validation/test/blind target'ları için geçmiş outcome yalnızca as-of availability sağlıyorsa feature'a girebilir; model yeniden fit edilmez.

### 8. Feature seti

Direct schedule/master-data feature'ları:

- takvim ayı ve ISO haftanın günü
- planlanan kalkış saati ve dört zaman bloğu
- origin, destination, route ve reporting carrier kimliği
- mesafe ve planlanan elapsed süre

Historical feature'lar:

- route, origin, destination ve carrier için 7/30 günlük history count
- aynı entity/pencere için prior-smoothed ciddi aksama oranı

Smoothing:

```text
(entity_events + 20 * global_asof_rate) / (entity_count + 20)
```

### 9. Model ve batch sınırı

- Dummy, Logistic Regression ve XGBoost dışında model yoktur.
- OR yalnızca kalibre edilmiş sürekli olasılığı tüketir.
- Eksik uçuş tahmini, NaN, range dışı değer veya snapshot mismatch durumunda OR başlamaz.
- Prediction batch immutable ve dataset/feature/model/calibration hash'leriyle bağlıdır.

## Gerekçe

- Kapalı whitelist ve default reject, yeni BTS alanının yanlışlıkla feature olmasını engeller.
- Schedule/outcome ayrımı direct leakage riskini azaltır.
- T-6 gerçek bir karar cutoff'u sağlar.
- 24 saat availability lag aynı kaynak satırındaki gelecekte bilinen sonucu erken kullanmayı engeller.
- Training döneminden top-20 seçimi test dağılımına önceden bakmayı önler.
- Time split, random split'ten daha gerçekçi deployment simülasyonudur.
- Count ile birlikte smoothed rate, az gözlemli route/entity oranlarının aşırı güven üretmesini azaltır.
- Probability calibration, OR objective'inde risk büyüklüğünün anlamlı kullanılmasını sağlar.

## Sonuçlar

Olumlu:

- Her feature için provenance ve availability kanıtı bulunur.
- Target ve historical outcome kullanımı ayrıştırılır.
- Test/blind döneminde walk-forward feature üretimi mümkündür.
- Data snapshot ve prediction batch tekrar üretilebilir olur.

Maliyet ve sınırlamalar:

- Timezone mapping ek bir açık veri artifact'ı ve kalite kontrolü gerektirir.
- İlk 31 gün target training satırı olarak kullanılamaz.
- 24 saat availability lag bazı gerçekte daha erken bilinen outcome'ları konservatif olarak dışarıda bırakır.
- Hava durumu gibi T-6 anında erişilebilir olabilecek dış veri v1'e dahil değildir.
- BTS passenger operation verisi cargo uçuş riskinin doğrudan karşılığı değildir.

## Reddedilen alternatifler

- Tüm 109 BTS alanını indirip sonradan seçmek
- Unclassified alanları otomatik kabul etmek
- `DepDelay`, `ArrDelay`, delay cause veya cancellation code'u feature yapmak
- Rastgele train/test split
- Tüm 2024 ile top-20 havalimanı seçmek
- Aynı satırın label'ını rolling aggregate'e dahil etmek
- Validation/test aggregate'ini bütün dönem üzerinden toplu hesaplamak
- Eksik completed outcome'u `0` kabul etmek
- Bilinmeyen risk için otomatik `0.5` yazmak
- Gerçek-time publication bilgisi yokken outcome'u uçuş biter bitmez biliniyor saymak

## Uygulama kapıları

Phase 2 ingestion başlamadan:

- kaynak alan listesi ve isimleri yeniden resmî sayfadan doğrulanır;
- AirportID–IANA timezone kaynağı için ayrı veri manifesti onaylanır;
- kalite fixture'ları ve quarantine reason code'ları hazırlanır.

Phase 3 ML başlamadan:

- feature availability testleri ve schema hash'i geçer;
- hiçbir target outcome feature matrix'te bulunmaz;
- rolling as-of invariant'ları otomatik testle kanıtlanır.

## Değişiklik koşulu

Alan, label, T-6, availability lag, top-20, split, warm-up, feature veya smoothing değişikliği yeni ADR, contract sürümü, leakage analizi ve insan onayı gerektirir. Blind sonuç görüldükten sonra v1 geriye dönük ayarlanamaz.
