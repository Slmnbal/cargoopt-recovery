# Phase 2 Bounded Header-Only Extract Raporu

| Alan | Değer |
|---|---|
| Belge kimliği | `phase-2-source-compatibility-report-r4` |
| Görev | `PH2-T02-R4` |
| Yürütme commit'i | `d0088bb26bef7469512891901227e7315fb5c0ed` |
| Extract run/job | `31893089533` / `95032182552` |
| Foundation run/job | `31893089563` / `95032182592` |
| Kapalı sonuç | `CONTRACT_SOURCE_MISMATCH` |
| Reason code | `CHECKED_CONTROL_OUTSIDE_EXACT_15` |
| POST / geçici ZIP / data row | `0 / 0 / 0` |
| Cleanup | `PASSED` |

## 1. Karar özeti

Fresh selected-field formu GitHub-hosted runner üzerinden `200` ile alınmış ve
R2 parser/fingerprint sözleşmesi değiştirilmeden yeniden çalıştırılmıştır.
Fresh canonical form SHA-256 değeri
`3d9227bf05af8dcf8f4fef99aef86ebbbcbe43561869ba43444079d913b3f8b0`
olarak immutable R2 kanıtıyla tam eşleşmiştir. January 2024 ve exact 15 alan
eşlemesi de korunmuştur.

POST'tan önceki daha sıkı fail-closed kapı, seçilen formda exact 15 mapped alan
dışında varsayılan seçili bir checkbox veya radio kontrolü bulunduğunu
belirlemiştir. R4 sözleşmesi bu kontrolün etkisini sessizce varsaymaya veya onu
POST'a taşımaya izin vermediği için yürütme
`CHECKED_CONTROL_OUTSIDE_EXACT_15` reason code'u ile durmuştur.

Bu nedenle `SOURCE_COMPATIBLE` iddiası kurulmamış, POST gönderilmemiş, geçici
ZIP oluşturulmamış ve CSV header ya da data row okunmamıştır. Sonuç
`CONTRACT_SOURCE_MISMATCH` olarak kapalıdır.

## 2. Fresh form kanıtı

| Kontrol | Sonuç |
|---|---|
| GET status | `200` |
| Response byte | `171.840` |
| Response SHA-256 | `d579684eeb9e4529b817dce11c4585c6e36c9fb208baa87c5b70aabb63341164` |
| Redirect | `0` |
| Fresh contract SHA-256 | `3d9227bf05af8dcf8f4fef99aef86ebbbcbe43561869ba43444079d913b3f8b0` |
| Immutable R2 hash equality | `PASSED` |
| Year / month | `2024 / January` |
| Mapped field count | `15` |
| POST readiness | `BLOCKED` |

Raw HTML, hidden field değerleri, cookie değerleri ve form body loglanmamış veya
kalıcılaştırılmamıştır. Form response hash ve byte count dışında sonuç
artifact'ına girmemiştir.

## 3. Request ve Extract sınırı

| Kontrol | Sonuç |
|---|---|
| Runner | `ubuntu-24.04`, CPython `3.12.3`, Linux x86_64 |
| Request | `1 / 5` |
| POST | `0 / 1` |
| Redirect | `0 / 3` |
| Retry / rerun | `0 / 0` |
| Temporary ZIP | `0 / 1` |
| Header record | `0` |
| Data row | `0` |
| Persistent archive | `false` |
| Raw redistribution | `false` |
| Workflow artifact | `0` |

Workflow `permissions: {}` ile, checkout ve `uses` adımı olmadan, yalnız sistem
CPython standard library ile çalışmıştır. Secret, cache, OIDC veya artifact
mekanizması kullanılmamıştır.

## 4. Cleanup kanıtı

POST yapılmadığı için temporary path hiç oluşturulmamıştır. Buna rağmen ortak
`finally` cleanup yolu çalışmış ve `cleanup_path_absent = true` üretmiştir.
Absolute temporary path loglanmamış; temp path olmadığı için path hash'i de
`null` kalmıştır.

Geçici R4 workflow'u result commit'i
`4e601556000e7372570f071f3c2d9542df086c9c` içinde silinmiştir. Aynı commit
üzerindeki remote workflow path yokluğu GitHub Contents API üzerinden
`404 Not Found` ile doğrulanmıştır.

## 5. Hosted doğrulama

Bounded Extract workflow'u teknik olarak `success` conclusion üretmiştir; bu,
fail-closed result JSON'un güvenli biçimde üretildiğini gösterir ve veri kaynağı
uyumluluğu anlamına gelmez. Asıl domain sonucu sanitize edilmiş JSON içindeki
`CONTRACT_SOURCE_MISMATCH` değeridir.

Aynı bootstrap commit'indeki Foundation run da `success` olmuş; Extract ve
Foundation run'larının ikisi de sıfır artifact üretmiştir. Result/cleanup
commit'indeki Foundation run `31893270117`, job `95032611933` ile `success`
olmuş ve sıfır artifact üretmiştir. Remote workflow yokluğu aynı commit için
`404 Not Found` ile kanıtlanmıştır.

Final closeout commit ve onun Foundation sonucu repository dışı hosted kanıt
olarak görev kapanışında doğrulanır; commit kendi SHA'sını öz-referanslı olarak
içeriğine yazmaz.

## 6. Downstream kapısı

`PH2-T03` açılmamıştır ve `PHASE_3..PHASE_8` kilitlidir. Yeni bir retry ancak
exact-15 dışındaki seçili kontrolün güvenli, sanitize edilmiş ve mekanik olarak
tanımlandığı ayrı bir görev sözleşmesi ve yeni insan kararıyla planlanabilir.
Bu rapor otomatik retry, POST veya Extract yetkisi vermez.
