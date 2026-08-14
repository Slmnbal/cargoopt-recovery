# Sentetik Kargo ve Kapasite Üretim Sözleşmesi

| Alan | Değer |
|---|---|
| Sözleşme kimliği | `synthetic-cargo-v1` |
| Durum | Accepted |
| İlgili görev | `PH0-T03` |
| Varsayılan master seed | `20240831` |
| Varsayılan gönderi sayısı | `200` |
| İzinli gönderi sayısı | `50..500` |
| Kapasite modu | `BALANCED_110` |

## 1. Amaç

Bu sözleşme, gerçek kargo verisi kullanmadan tekrar üretilebilir shipment manifestosu ve aday uçuş kapasitesi üretme kurallarını kilitler. Generator gerçek bir havayolunun dağılımını taklit ettiği iddiasında değildir; kontrollü ML + OR karşılaştırması için sentetik deney girdisi üretir.

## 2. İzinli generator girdileri

Generator yalnızca şunları okuyabilir:

- `generator_contract_version`
- `master_seed`
- `case_id` ve doğal case anahtarı
- `shipment_count`
- kaynak uçuşun schedule alanları
- önceden eligibility filtresinden geçmiş aday uçuş schedule alanları
- bu sözleşmedeki cargo oranları, aralıklar ve kapasite modu

Generator şunları okuyamaz:

- `severe_disruption_probability`
- `prediction_batch_id`, model veya calibration sonucu
- `Cancelled`
- `Diverted`
- `ArrDelayMinutes`
- gerçekleşmiş `severe_disruption`
- delay cause veya uçuş sonrası herhangi bir alan
- solver sonucu, objective değeri veya önceki assignment
- blind replay metriği

Yasak alanlardan biri generator input şemasında görülürse üretim `GENERATOR_INPUT_REJECTED` ile durur.

## 3. Deterministik uniform üretimi

Her rastgele görünen değer stateless SHA-256 ile üretilir. Ortak bir ilerleyen PRNG state'i kullanılmaz.

```text
material = "cargoopt|synthetic-cargo-v1|{master_seed}|{case_id}|{entity}|{entity_id}|{attribute}"
digest = SHA256(UTF8(material))
integer53 = integer value of first 13 hex characters
u = integer53 / 2^52
```

`u`, `[0,1)` aralığındadır. Attribute adları küçük snake_case ve bu belgede yazıldığı şekliyle sabittir. Bu yöntem sayesinde satır sırası veya paralel çalışma sayısı sonucu değiştirmez.

### 3.1 Canonical ID'ler

Gönderi sıra numarası `000001` ile başlar:

```text
shipment_id = "SHP-" + first_16_hex(SHA256(case_id + "|" + zero_padded_index))
```

Liste her zaman `shipment_id` artan sıralanır. Aday uçuşlar `flight_id` artan sıralanır.

## 4. Cargo sınıfı dağılımı

| Cargo | Oran |
|---|---:|
| `STANDARD` | `0.70` |
| `EXPRESS` | `0.20` |
| `PHARMA` | `0.10` |

Oran toplamı tam `1.00`'dır.

Her sınıfın adedi `shipment_count × ratio` için largest-remainder yöntemiyle belirlenir:

1. Her sınıf için floor alınır.
2. Kalan adet, kesir kısmı büyük sınıftan küçüğe dağıtılır.
3. Kesir eşitse enum sırası `STANDARD`, `EXPRESS`, `PHARMA` kullanılır.
4. Gönderiler `cargo_type_rank` uniform'una göre artan sıralanır ve kotalara atanır.

Bu nedenle varsayılan 200 gönderide tam 140 STANDARD, 40 EXPRESS ve 20 PHARMA bulunur.

## 5. Ağırlık ve hacim

| Cargo | Min–max ağırlık | Min–max yoğunluk |
|---|---:|---:|
| `STANDARD` | `20.0..1000.0 kg` | `120..300 kg/m3` |
| `EXPRESS` | `1.0..250.0 kg` | `80..220 kg/m3` |
| `PHARMA` | `5.0..500.0 kg` | `100..250 kg/m3` |

Küçük gönderilerin daha sık olması için:

```text
weight_raw = weight_min + (u_weight ^ 2) × (weight_max - weight_min)
weight_kg = round_half_up(weight_raw, 1)
density = density_min + u_density × (density_max - density_min)
volume_m3 = max(0.001, round_half_up(weight_kg / density, 3))
```

Hacim ağırlıktan türetildiği için iki değişken bağımsız değildir. IEEE float sonucu doğrudan snapshot'a yazılmaz; belirtilen hassasiyette decimal string olarak canonical serialize edilir.

## 6. Hazır olma ve SLA

Ready offset, recovery window başlangıcından itibaren üretilir:

| Cargo | Ready offset | Handling | SLA slack |
|---|---:|---:|---:|
| `STANDARD` | `0..300 dk` | `60 dk` | `12 saat` |
| `EXPRESS` | `120..330 dk` | `45 dk` | `4 saat` |
| `PHARMA` | `0..240 dk` | `90 dk` | `2 saat` |

```text
ready_offset_minutes = floor(min + u_ready × (max - min + 1))
ready_at_utc = prediction_cutoff_at + ready_offset_minutes
delivery_due_at_utc = source_scheduled_arrival_at_utc + sla_slack
```

`requires_cold_chain`, yalnızca `cargo_type == PHARMA` olduğunda `true` olur.

## 7. Aday uçuş kapasitesi

Kapasite schedule veya gerçek havayolu kapasitesi değildir; case shipment talebine göre sentetik oluşturulur.

Varsayılan `BALANCED_110` modu:

```text
network_weight_capacity = total_shipment_weight × 1.10
network_volume_capacity = total_shipment_volume × 1.10
raw_weight_share[f] = 0.5 + u_capacity_weight[f]
raw_volume_share[f] = 0.5 + u_capacity_volume[f]
normalized_share = raw_share / sum(raw_share)
```

- Ağırlık kapasitesi `0.1 kg`, hacim kapasitesi `0.001 m3` hassasiyetinde largest-remainder ile uçuşlara dağıtılır.
- Yuvarlama kalanı, ilgili raw pay kesri büyük uçuşa; eşitlikte küçük `flight_id`'ye verilir.
- Dağıtım sonrası uçuş kapasitelerinin toplamı canonical network kapasitesine tam eşit olmalıdır.
- Her uçuş kapasitesi pozitif olmalıdır.
- Bu kapasite modu gerçek kargo kapasitesi iddiası değildir.

### 7.1 Cold-chain

```text
cold_chain_capable = u_cold_chain < 0.35
```

PHARMA gönderisi varken hiçbir aday cold-chain uyumlu değilse `cold_chain_rank` değeri en küçük uçuş deterministik olarak `true` yapılır. Bu garanti yalnızca en az bir teknik aday yaratır; kapasite yetersizliği veya zaman uyumsuzluğu nedeniyle PHARMA yine `UNASSIGNED` kalabilir.

## 8. Case kabul kuralları

- Input schedule filtresinden sonra 2–30 aday uçuş olmalıdır.
- Candidate schedule listesi duplicate `flight_id` içeremez.
- Source flight candidate listesine giremez.
- Source ve candidate timestamp'leri UTC olmalıdır.
- Bütün aday varışları recovery window içinde olmalıdır.
- `shipment_count` integer ve `50..500` olmalıdır.
- Master seed signed 64-bit non-negative integer olmalıdır.
- Bilinmeyen config alanı fail-closed reddedilir.
- NaN, infinity, sıfır veya negatif weight/volume/capacity üretilemez.

## 9. Snapshot ve manifest

Generator çıktısı, key sıralaması açık, listeleri canonical ID artan, UTF-8, LF newline ve whitespace-normalized JSON olarak serialize edilir.

Manifest en az şunları taşır:

- `generator_contract_version`
- `generator_implementation_version`
- `master_seed`
- `case_id`
- `shipment_count`
- `candidate_flight_count`
- cargo sınıf adetleri
- toplam shipment ağırlık ve hacmi
- toplam candidate kapasite ağırlık ve hacmi
- `source_schedule_snapshot_id`
- canonical input SHA-256
- canonical output SHA-256
- üretim timestamp'i

Timestamp hash materyaline katılmaz. Aynı sözleşme, implementation, seed ve canonical input aynı output SHA-256'yı vermelidir.

## 10. Blind bütünlüğü

- `synthetic-cargo-v1`, `master_seed = 20240831`, oranlar, aralıklar ve `BALANCED_110` blind sonuç görülmeden dondurulur.
- Blind outcome görüldükten sonra seed, kapasite, cargo mix, SLA veya cost katsayısı geriye dönük değiştirilemez.
- Sensitivity çalışması yapılırsa yeni, açık config kimliği taşır ve birincil frozen sonucu değiştirmez.

## 11. Uygulama kapısı

İleride generator kodlanmadan önce golden fixture'lar bu sözleşmeden üretilecek ve en az şu özellikler test edilecektir:

- aynı input iki çalıştırmada byte-identical canonical çıktı verir;
- input satır sırası değişse de çıktı hash'i değişmez;
- 200 gönderide sınıf adetleri `140/40/20` olur;
- weight, density, volume ve time sınırları aşılmaz;
- generator erişim logunda prediction veya outcome alanı bulunmaz;
- capacity toplamları exact reconciliation sağlar.

Bu testlerin kendisi PH0-T03 kapsamında yazılmaz.
