# Phase 2 Resmî Kaynak Araştırması

| Alan | Değer |
|---|---|
| Belge kimliği | `phase-2-source-research-v1` |
| Görev | `PH2-T01` |
| Araştırma tarihi | `2026-08-15` |
| Kaynak politikası | Yalnız resmî birincil kaynak veya canonical paket metadata'sı |
| Veri indirme durumu | **Yapılmadı** |
| Sonuç | `CONDITIONAL_GO — SOURCE_COMPATIBILITY_PROBE_REQUIRED` |

## 1. Karar özeti

Phase 2 için resmî uçuş kaynağı, U.S. Department of Transportation Bureau of
Transportation Statistics (BTS) **Reporting Carrier On-Time Performance
(1987–present)** tablosunun 2024 aylık verileridir. Kaynak açıktır, aylık
arşivleri resmî `transtats.bts.gov` alanında yayımlanır ve gerekli uçuş,
schedule, iptal, diversion ve gecikme alanlarını tanımlar.

Ancak implementation başlamadan önce çözülmesi gereken iki fail-closed kapı
vardır:

1. Kabul edilmiş contract tam olarak 15 seçili kolon bekler. Resmî PREZIP
   arşivleri geniş tabloyu sunabilir; seçili-alan web formunun 15 kolonluk
   çıktıyı tekrarlanabilir ve otomasyona uygun biçimde verip vermediği henüz
   byte seviyesinde doğrulanmamıştır.
2. TranStats tablo sayfalarında erişim açıktır; fakat bu exact uçuş tablosunun
   yeniden dağıtım lisansı araştırılan sayfalarda açık bir SPDX/Creative
   Commons ifadesiyle verilmemiştir. Kamu erişimi, otomatik olarak raw arşivi
   repository içinde yeniden dağıtma hakkı sayılmayacaktır.

Bu nedenle 12 aylık acquisition'a geçilmez. Sıradaki bounded görev yalnız
resmî kaynak arayüzü, kullanım koşulu ve bir aylık header uyumluluğunu inceler.
Sonuç kesinleşmeden dependency, ingestion kodu veya kalıcı veri oluşturulmaz.

## 2. Resmî kaynak kayıtları

| ID | Resmî URL | Erişim | Desteklediği gerçek | Kullanım notu |
|---|---|---:|---|---|
| `BTS-01` | https://www.transtats.bts.gov/ontime/ | 2026-08-15 | On-time verisinin güncelliği; saatlerin yerel ve 24 saat formatında olduğu | Veri kapsamını tanımlar; acquisition endpoint'i değildir |
| `BTS-02` | https://transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFD | 2026-08-15 | Reporting carrier iç hat aktarmasız uçuşları; schedule/actual zaman, cancellation, diversion, delay cause ve distance; aylık veri | Dataset kimliği ve kapsam kaynağı |
| `BTS-03` | https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ | 2026-08-15 | Reporting Carrier tablosunun field dictionary'si ve geniş kaynak şeması | Contract alan adlarını upstream sözlükle eşleştirme kaynağı |
| `BTS-04` | https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ | 2026-08-15 | Yıl/dönem/alan seçimi yapan resmî download formu | Exact 15-field extract için aday; otomasyon davranışı probe edilmedi |
| `BTS-05` | https://transtats.bts.gov/PREZIP/ | 2026-08-15 | `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_1.zip` … `_12.zip` aylık arşivlerinin varlığı | Stabil resmî archive adları; field kapsamı probe edilmeden kullanılamaz |
| `DOT-01` | https://ntl.bts.gov/ntl/public-access/managing-rights | 2026-08-15 | DOT'un araştırma çıktıları için CC-BY teşviki ve hak yönetimi yaklaşımı | Exact TranStats tablosuna özel lisans vermez |
| `PY-01` | https://docs.python.org/3/library/zoneinfo.html | 2026-08-15 | `zoneinfo` sistem tzdb'sini veya first-party `tzdata` paketini kullanır | Cross-platform determinism için exact `tzdata` pin'i gerekir |
| `AIRPORT-01` | https://pypi.org/project/airportsdata/ | 2026-08-15 | IATA/ICAO/FAA keyed airport metadata ve IANA-compatible `tz`; `20260803` release metadata'sı | BTS AirportID'yi doğrudan anahtar olarak sunmaz |
| `AIRPORT-02` | https://github.com/mborsetti/airportsdata | 2026-08-15 | Paket veri alanları, köken açıklaması ve MIT lisansı | Güncel airport dataset'idir; tarihsel master-data iddiası yoktur |

## 3. Kaynak ve sözleşme uyumluluğu

### 3.1 Hedef upstream artifact'ları

2024 için beklenen resmî aylık ad şablonu:

```text
https://transtats.bts.gov/PREZIP/
On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_{month}.zip
```

`month` tam sayı `1..12` olur. Liste sayfasında on iki artifact görülmüştür;
bu araştırmada hiçbir ZIP veya CSV indirilmemiştir. Dosya boyutu, member adı,
header, content hash, ETag ve Last-Modified değerleri henüz `UNKNOWN`'dur.

### 3.2 Exact 15-field kapısı

Normatif `bts-reporting-otp-contract-v1`, yalnız şu 15 alanı kabul eder:

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

`cargoopt-data-quality-v2` ayrıca kaynak kolon setinin bu listeye **tam eşit**
olmasını ister. Bu iki sonucu doğurur:

- PREZIP full-width header gelirse pipeline'ın kod içinde 15 kolon seçip devam
  etmesi mevcut contract'a göre yasaktır.
- Resmî selected-field formu exact 15 kolon üretiyorsa request parametreleri,
  response URL'si, form token/cookie gereksinimi ve byte hash tekrarlanabilir
  biçimde kaydedilmelidir.

PH2-T02 sonuç durumları:

| Durum | Koşul | Sonraki davranış |
|---|---|---|
| `SOURCE_COMPATIBLE` | Resmî arayüz exact 15 kolonluk, scriptable ve tekrarlanabilir artifact sağlar; kullanım koşulu kaydedilir | Dependency/toolchain görevi ayrıca planlanabilir |
| `CONTRACT_SOURCE_MISMATCH` | Yalnız full-width arşiv otomasyona uygundur veya exact extract kararlı değildir | Dur; ingestion yazma; ayrı governance/contract değişikliği iste |
| `RIGHTS_UNRESOLVED` | Exact tablo için kullanım/yerel işleme koşulu güvenle kaydedilemez | Dur; raw veri indirme ve saklama yapma |
| `UPSTREAM_UNAVAILABLE` | Resmî endpoint güvenli ve bounded probe sırasında doğrulanamaz | Dur; mirror veya üçüncü taraf dataset'e düşme |

Kaggle, Hugging Face dataset repository'si, GitHub mirror'u veya başka bir
yeniden paketlenmiş kaynak otomatik fallback değildir.

## 4. Kullanım hakkı ve yeniden dağıtım politikası

Araştırma sonucu exact TranStats flight archive için açık bir dataset-specific
license expression bulunmamıştır. Bu nedenle proje aşağıdaki muhafazakâr
politikayı uygular:

- Sınıflandırma: `US_GOVERNMENT_PUBLIC_DATA — EXACT_REUSE_TERMS_PENDING`.
- Proje içi attribution zorunludur: BTS, tablo adı, resmi URL ve erişim tarihi.
- Raw ZIP/CSV Git'e, release artifact'ına veya portfolio download'una konmaz.
- Raw byte'lar yalnız açıkça onaylanmış acquisition görevinde local ignored
  data alanında tutulabilir.
- Hash, provenance, schema ve aggregate quality report yayımlanabilir; raw byte
  yeniden dağıtımı exact hak doğrulamasına kadar kapalıdır.
- DOT `Managing Rights` sayfasının CC-BY teşviki bu tablo için license grant'i
  gibi sunulmaz.
- PH2-T02 resmî sayfadaki güncel policy/rights bağlantılarını kaydeder. Belirsiz
  sonuç `RIGHTS_UNRESOLVED` olur; varsayım yapılmaz.

## 5. Bounded source-compatibility probe tasarımı

PH2-T02 için önerilen maksimum yetki:

1. Yalnız `transtats.bts.gov`, `www.transtats.bts.gov`, `bts.gov` ve
   `transportation.gov` alanlarına read-only HTTPS istekleri.
2. Önce HEAD/metadata/form incelemesi; GET yalnız gerekiyorsa.
3. En fazla Ocak 2024 tek arşivi veya exact 15-field eşdeğerini OS temporary
   dizinine indirme.
4. En fazla ZIP central directory, member adı ve CSV header'ını inceleme;
   full dataset transform etme veya repository içine taşıma yok.
5. Probe sonunda raw temporary byte'ları silme; yalnız URL, response metadata,
   boyut, SHA-256, header ve karar kaydı tutma.
6. Redirect final host allowlist dışında kalırsa, HTTPS düşerse, byte sınırı
   aşılırsa, ZIP birden çok/beklenmeyen member taşırsa veya header exact değilse
   fail-closed durma.

Bu yetkiler PH2-T01 onayından doğmaz. PH2-T02 task dosyası ve ayrı yürütme
onayı olmadan network probe yapılmaz.

## 6. Acquisition güvenlik ve provenance modeli

Gelecekteki acquisition implementation'ı Python standard library ile şu
kontrolleri taşır:

- HTTPS-only ve exact host allowlist;
- açık connect/read timeout, bounded retry ve exponential backoff;
- kullanıcı tanımlı URL, proxy, credential, cookie export veya secret yok;
- final redirect host/scheme doğrulaması;
- `Content-Length` varsa indirmeden önce, yoksa streaming sırasında max-byte
  kontrolü;
- streaming SHA-256 ve byte count;
- OS temporary dosyasına yazma, fsync ve yalnız doğrulamadan sonra atomic rename;
- ZIP path traversal, absolute member, symlink, duplicate member, CRC ve
  compression-ratio/expanded-size kontrolleri;
- aynı artifact ID altında farklı hash görülürse `UPSTREAM_MUTATION`;
- retry yalnız transient network/5xx için; schema, rights ve hash hataları retry
  ile gizlenmez.

Her source artifact manifest kaydı en az şunları taşır:

```json
{
  "artifact_id": "bts-reporting-otp-2024-01",
  "dataset_contract_id": "bts-reporting-otp-contract-v1",
  "source_url": "https://transtats.bts.gov/...",
  "requested_at_utc": "RFC3339",
  "final_url": "https://transtats.bts.gov/...",
  "http_status": 200,
  "etag": null,
  "last_modified": null,
  "content_length_header": null,
  "downloaded_bytes": 0,
  "sha256": "64-lowercase-hex",
  "archive_members": ["exact-member.csv"],
  "source_header": ["exact-15-fields"],
  "rights_status": "VERIFIED_OR_STOP",
  "acquisition_implementation_version": "semver",
  "manifest_schema_version": 1
}
```

Timestamp manifest kimliğine veya processed snapshot hash materyaline katılmaz.
Canonical JSON; UTF-8, LF, sorted keys ve trailing newline ile üretilir.

## 7. Timezone master-data kararı

BTS schedule saatleri airport-local `hhmm` olduğundan UTC normalizasyonu için
iki ayrı kaynak gerekir:

- `airportsdata==20260803`: IATA display code → IANA timezone adayı;
- `tzdata==2026.3`: Python `zoneinfo` için dondurulmuş IANA ruleset.

`airportsdata`, BTS `AirportID` anahtarını doğrudan taşımaz. Eşleme şu şekilde
üretilir ve dondurulur:

```text
BTS OriginAirportID + Origin display code
BTS DestAirportID   + Dest display code
        -> airportsdata IATA record
        -> IANA timezone name
        -> ZoneInfo(tz_name) validation
```

Aktivasyon kuralları:

1. Aynı BTS AirportID 2024 içinde birden fazla display code'a map olamaz.
2. Her display code `airportsdata` içinde tek record'a resolve olmalıdır.
3. Record `tz` alanı boş olamaz ve pinned `tzdata` ile `ZoneInfo` açılmalıdır.
4. Dondurulmuş mapping; AirportID, display code, IANA zone, airportsdata
   version, tzdata version ve canonical hash taşır.
5. Paket güncel master-data olduğundan 2024 için doğrulama sonucu eksiksiz ve
   one-to-one değilse tarihsel doğruluk varsayılmaz; snapshot aktive edilmez.

Eksik/ambiguous mapping otomatik UTC offset, koordinat tahmini veya başka web
kaynağıyla sessizce tamamlanmaz.

## 8. Veri katmanları ve trust-zone ayrımı

| Katman | İçerik | Mutable | Network | Model girdisi |
|---|---|---:|---:|---:|
| `raw` | Resmî source archive byte'ı + source manifest | Hayır | Yalnız acquisition | Hayır |
| `staged` | Exact 15 kolon; orijinal metin değerleri + source locator | Hayır | Hayır | Hayır |
| `quarantine` | Reddedilen satır, reason code, source locator; outcome taşıyabilir | Hayır | Hayır | Hayır |
| `processed/schedule` | Identity, schedule, audit ve izinli feature source alanları | Hayır | Hayır | Evet, allowlist ile |
| `processed/outcome` | `Cancelled`, `Diverted`, `ArrDelayMinutes`, label ve availability | Hayır | Hayır | Doğrudan hayır |
| `processed/features` | Horizon-cutoff'lu leakage-safe feature snapshot | Hayır | Hayır | Evet |
| `domain` | Açıkça `SYNTHETIC` cargo/capacity snapshot'ı | Hayır | Hayır | OR fazında |

Schedule ve outcome aynı Parquet dosyasında, aynı view'da veya wildcard scan
surface'inde bulunmaz. Join yalnız explicit outcome/label işinde, canonical
`flight_instance_id` ile yapılır. Feature builder'ın filesystem allowlist'i
outcome path'ini içermez.

## 9. Açık riskler ve stop conditions

| Risk | Etki | Kontrol |
|---|---|---|
| Selected-field form session veya insan etkileşimi istiyor | Reproducibility kaybı | PH2-T02 probe; başarısızsa `CONTRACT_SOURCE_MISMATCH` |
| PREZIP full-width source | Exact-15 quality contract ihlali | Silent projection yok; governance kararı gerekir |
| Exact reuse terms belirsiz | Raw redistribution riski | Raw Git/release dışı; rights gate fail-closed |
| Upstream archive byte'ı sonradan değişir | Snapshot lineage bozulur | URL + byte count + SHA-256; aynı ID/farklı hash fatal |
| Airport code güncel dataset ile eşleşmez | UTC cutoff hatası | One-to-one frozen mapping; eksikse aktivasyon yok |
| DST ambiguous/nonexistent local time | Yanlış instant | `zoneinfo` round-trip ve fold policy testleri; çözümsüz satır quarantine |
| Outcome schedule yüzeyine sızar | Label leakage | Ayrı path/schema/reader; forbidden-column tests |

## 10. PH2-T01 sonucu

Resmî kaynak gerçek, ücretsiz ve proje amacına uygundur; fakat exact-15 source
interface ve exact rights kaydı data acquisition öncesi doğrulanmalıdır.
Dolayısıyla PH2-T01 kaynak kararı koşullu `GO` verir; bir sonraki iş yalnız
PH2-T02 source compatibility probe'unu **planlamak** olabilir. Probe
onaylanmadan veri indirme, package kurulumu veya implementation yoktur.
