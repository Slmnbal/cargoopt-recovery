# ADR-007 — Outcome-Blind Roster, Cluster Bootstrap ve Politika Kapısı

| Alan | Değer |
|---|---|
| Durum | Accepted |
| Tarih | 2026-08-13 |
| Karar sahipleri | Proje sahibi ve Codex |
| İlgili görev | `PH0-T05` |

## Bağlam

CargoOpt Recovery'nin temel portföy iddiası kalibre edilmiş uçuş riskinin recovery optimizasyonuna karar katkısını göstermektir. Model/OR tasarımı Aralık outcome'ları görüldükten sonra değişirse elde edilen sonuç blind değildir. Yalnızca gerçekte aksayan source flight'ları önceden seçmek source outcome leakage yaratır; yalnızca başarılı planları analize almak ise survivorship bias üretir.

Aralık tamamen outcome erişimsiz işlenirse başka bir hata oluşur: ayın daha erken günlerinde tamamlanıp konservatif availability zamanını geçen uçuşlar, gerçek bir sonraki karar anında bilinebilecek olmasına rağmen rolling feature'lardan çıkarılır. Bu nedenle feature üretiminin kontrollü point-in-time outcome erişimi ile evaluation runner'ın full reveal erişimi birbirinden ayrılmalıdır.

MILP'ler aynı gün birden fazla case üretebilir. Case'leri bağımsız kabul eden row bootstrap güven aralığını yapay daraltabilir. Ayrıca “ML daha iyi görünüyor” ifadesi, örnek büyüklüğü, plan coverage, validator başarısı ve solver optimalite guardrail'leri olmadan politika benimsemek için yeterli değildir.

## Karar

### 1. Outcome-blind roster

- Blind partition `1–31 Aralık 2024` olarak kalır.
- Source roster yalnızca schedule ve pre-outcome input eligibility ile kurulur.
- Source/candidate outcome ve prediction probability'si ranking veya filtre olamaz.
- En fazla 10 dondurulmuş destination için destination başına en fazla 30 source case seçilir.
- Rank `SHA-256("blind-roster-v1|20240831|destination_airport_id|source_flight_instance_id")` ile belirlenir.
- Destination kotası başka destination'a taşınmaz ve global backfill yapılmaz.

### 2. Walk-forward outcome erişimi

As-of feature builder yalnızca:

```text
history.label_available_at <= target.prediction_cutoff_at
history.flight_instance_id != target.flight_instance_id
```

koşuluyla geçmiş outcome aggregate'i kullanabilir. Bu erişim gateway ve immutable ledger üzerinden yapılır. Prediction, OR ve evaluation runner raw outcome göremez. Evaluation runner full snapshot'ı ancak freeze sonrası yetkili reveal ile okur.

### 3. Plan-before-reveal

Selected roster'ın tamamı için greedy, risk-blind MILP ve ML-informed MILP aynı OR input hash'i üzerinde full reveal öncesi çalışır ve validate edilir. Error/no-plan/invalid sonuçları audit'te tutulur. Source outcome açıldıktan sonra yalnızca `severe_disruption == 1` case'ler triggered cohort olur; planlar yeniden çalıştırılmaz.

Bu tasarım source alert'i exogenous/doğru kabul ederek recovery karar katkısını ölçer. Alert modelinin precision/recall veya end-to-end trigger performansı bu deneyden çıkarılamaz.

### 4. Realized cost ve pairing

- Realized cost `cost-policy-try-v1` formülünü candidate `severe_disruption` outcome'u ile integer kuruş olarak yeniden hesaplar.
- Actual delay minutes yeni maliyet terimi değildir.
- Source event ortak sunk term olarak paired farkın dışındadır.
- Primary case yalnızca üç valid plan ve atanan candidate'lar için tam outcome olduğunda complete paired olur.
- Eksik ve başarısız case'ler reason code ve attrition funnel ile raporlanır.

### 5. Primary istatistik

Primary difference:

```text
D_i = Cost_ML_INFORMED,i - Cost_RISK_BLIND,i
```

Negatif değer ML-informed lehinedir. Mean fark için source `FlightDate` cluster bootstrap kullanılır:

- `10.000` replicate;
- seed `20240831`;
- SHA-256 first-64-bit rejection sampling;
- `%95` R-7 percentile interval;
- case-weighted replicate mean;
- p-value yok.

Greedy karşılaştırmaları secondary descriptive'dir.

### 6. Üç katmanlı karar

Karar sırası:

1. Experiment integrity geçmezse `INVALID_EXPERIMENT / NO_DECISION_INVALID_EXPERIMENT`.
2. Integrity geçer fakat örnek/coverage/validator/optimalite kapıları geçmezse `INSUFFICIENT_EVIDENCE / RETAIN_RISK_BLIND`.
3. Bütün yeterlilik kapıları ve hem en az `%5` aggregate mean improvement hem CI upper `< 0` geçerse `VALID_POSITIVE / ADOPT_ML_INFORMED`.
4. Diğer geçerli sonuçlar `VALID_NEUTRAL_OR_NEGATIVE / RETAIN_RISK_BLIND`.

Positive öneri için en az 30 paired triggered case, 10 source tarihi, 5 destination, her strategy için en az `%95` valid-plan coverage, emitted planlarda `%100` validator pass, triggered paired coverage en az `%95` ve iki MILP için en az `%90` `OPTIMAL` oranı gerekir.

Policy artifact'ı başlangıçta insan onayı bekler; evaluation engine sistemi otomatik değiştirmez.

## Gerekçe

- Outcome-blind roster, yalnızca gerçekleşmiş aksama vakalarını sonradan seçme yanlılığını önler.
- Bütün roster'ı reveal öncesi planlamak triggered cohort'taki plan availability'nin source outcome'a bağlı olmasını engeller.
- Ayrı as-of gateway hem point-in-time doğruluğu hem outcome erişim denetimini korur.
- Aynı immutable input üç strateji arasındaki kontrollü farkı korur.
- Integer-kuruş realized cost OR ve validator hesaplarıyla exact reconciliation sağlar.
- Date-cluster bootstrap ortak gün etkisini row-independent bootstrap'tan daha dürüst ele alır.
- Önceden kayıtlı threshold'lar sonuç sonrası başarı tanımını değiştirmeyi engeller.
- Negative veya neutral sonuç risk-blind politikanın korunmasını sağlayan değerli bir mühendislik bulgusudur.

## Sonuçlar

Olumlu:

- Blind iddiası artifact freeze ve reveal kanıtına bağlanır.
- Case selection, missingness ve solver failure görünür hale gelir.
- ML katkısı risk-blind MILP'e karşı exact paired farkla ölçülür.
- İstatistiksel etki ile sistem güvenilirliği aynı politika kapısında fakat ayrı gate ailelerinde izlenir.
- Mülakatta iddia sınırı savunulabilir olur.

Maliyet ve sınırlamalar:

- Bütün selected roster için üç strategy outcome reveal öncesi çalıştırılır.
- Outcome vault, erişim gateway'i ve ledger ek implementation disiplini gerektirir.
- Triggered case sayısı 30'un altında kalabilir ve sonuç `INSUFFICIENT_EVIDENCE` olabilir.
- `%90` optimalite ve `%95` coverage kapıları ML etkisi olumlu görünse bile benimsemeyi durdurabilir.
- Deney exogenous source alert'e koşulludur ve gerçek cargo SLA/finans etkisini ölçmez.

## Reddedilen alternatifler

- Aralık outcome'larını açıp yalnızca ciddi aksayan source flight'ları planlamak
- Source risk probability'sine göre blind roster seçmek
- Destination kotasını outcome veya başarıya göre backfill etmek
- Aralık içindeki bütün geçmiş outcome'ları feature'lardan koşulsuz kaldırmak
- Evaluation runner'a pre-reveal raw outcome erişimi vermek
- Üç strateji için farklı candidate, shipment veya OR input kullanmak
- Missing/invalid case'leri raporlamadan complete cases göstermek
- Case-level bağımsız bootstrap kullanmak
- Random library varsayılan RNG davranışına güvenmek
- CI sıfırı içerirken yalnız point estimate ile ML'i benimsemek
- Yetersiz veya negatif sonucu proje başarısızlığı saymak
- Blind outcome sonrası threshold, cost, model veya bootstrap kuralı ayarlamak

## Uygulama kapıları

Phase 5 başlamadan önce en az şu testler bulunmalıdır:

- outcome kolonları verildiğinde roster output'unun değişmediğini kanıtlayan metamorphic test;
- destination quota, no-backfill ve rank golden testleri;
- cutoff sınırında as-of availability ve raw outcome access denial testleri;
- üç strategy input hash equality testi;
- incomplete freeze ile reveal'in reddi;
- post-reveal mutation detection;
- realized-cost golden case'leri ve integer-kuruş reconciliation;
- pairing exclusion reason ve attrition reconciliation testleri;
- bootstrap golden vector, rejection ve R-7 quantile testleri;
- gate boundary testleri: `29/30`, `9/10`, `4/5`, `0.949/0.95`, `0.899/0.90`, `0.049/0.05`, CI upper `0/-epsilon`;
- run status ve policy precedence truth table testi.

Bu ADR kod, veri, outcome reveal, model/solver çalıştırma, dependency veya sonraki faz hazırlığı başlatmaz.

## Değişiklik koşulu

Roster, outcome access, freeze/reveal, pairing, realized cost, bootstrap, threshold, status veya policy mapping değişirse yeni ADR, contract sürümü, leakage/istatistik/operasyon etki analizi ve açık insan onayı gerekir. Outcome görüldükten sonra bu karar geriye dönük değiştirilemez.
