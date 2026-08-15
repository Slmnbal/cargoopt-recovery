# Phase 2 Exact-Set Bounded Extract R6 Raporu

| Alan | Değer |
|---|---|
| Görev | `PH2-T02-R6` |
| Bootstrap commit | `21bf5d2a39251aa83410c405d8c1a76c8728a57a` |
| Extract run/job | `31894279022` / `95035039898` |
| Foundation run/job | `31894279015` / `95035040020` |
| Kapalı sonuç | `PROBE_SECURITY_ABORTED` |
| Reason code | `UNEXPECTED_INTERNAL_EXCEPTION` |
| Request / POST | `2 / 1` |
| ZIP / header / data row | `0 / 0 / 0` |
| Cleanup | `PASSED` |

## 1. Geçen kapılar

- Fresh form fingerprint immutable R2/R4 hash'iyle exact eşleşti.
- R5'te tanımlanan dört default output-field checkbox seti exact eşleşti.
- January 2024, exact 15 distinct target field ve download submit sözleşmesi geçti.
- Submission contract SHA-256 değeri
  `2a0b2c2b5e4b1e538faa1bdd3a7629ed5147c158216ff3aa57f17f81ead42f2a`
  olarak kaydedildi.
- Exact payload ile bir POST gönderildi; retry yapılmadı.

## 2. Kapalı sonuç

POST sonrasında response header/ZIP kabul aşamasına ulaşılmadan standard-library
HTTP transport katmanında allowlist dışı bir exception oluşmuştur. R6 exception
mesajını loglamadığı için sonuç güvenli genel reason code
`UNEXPECTED_INTERNAL_EXCEPTION` ile kapanmıştır.

Geçici ZIP oluşturulmamış, header veya data row okunmamış, ortak cleanup yolu
`cleanup_path_absent = true` üretmiştir. Workflow teknik conclusion `success`
olsa da domain sonucu `PROBE_SECURITY_ABORTED` ve source henüz compatible
değildir.

## 3. R7 transport sınırı

R7 payload semantiğini değiştirmez. Yalnız tarayıcı navigation davranışına denk
same-origin `Origin`, `Referer`, fetch-mode ve browser Accept header'larını ekler;
transport exception'larını mesaj içermeyen allowlisted reason code'lara ayırır.
Fresh fingerprint, exact-four, exact-15, tek POST, tek ZIP, header-only, zero-row
ve mandatory cleanup kapıları aynı kalır.

R6 workflow'u R7 bootstrap commit'inde silinir. Her iki hosted run sıfır
artifact üretmiştir.
