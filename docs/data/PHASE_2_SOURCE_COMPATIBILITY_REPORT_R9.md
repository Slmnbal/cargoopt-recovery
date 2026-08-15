# Phase 2 Reused-Connection Extract R9 Raporu

R9 fresh GET bağlantısını same-host POST için yeniden kullanarak transport
engelini kaldırmıştır. POST `200`, response `application/zip`, byte count
`9.050.151`, SHA-256
`40f6c2863dc72472354251ea1945587bc1593d6ce8d5af26c5ad5d9b4825ca5b`.

Form fingerprint, exact-four exclusion, January 2024, exact-15 ve submission
contract kapıları geçmiştir. ZIP tek geçici path'e yazılmış; yalnız ilk CSV
record'u okunmuş, fakat literal `EXPECTED_FIELDS` sırası eşleşmediği için sonuç
`CONTRACT_SOURCE_MISMATCH/CSV_HEADER_EXACT_ORDER_MISMATCH` olmuştur. Data row
`0`, artifact `0`, fallback connection `0`, cleanup `true`.

R10 kaynak fiziksel sırasını formdaki target checkbox DOM sırasından POST öncesi
mekanik üretir. Header yalnız bu exact logical 15 sıra veya CSV serializer'ın
tek terminal boş token eklediği `logical15 + [""]` biçimindeyse compatible
olabilir. Boş token adlandırılmış bir kolon değildir; yalnız trailing delimiter
sentinel'idir. Başka kolon, eksik kolon, duplicate, farklı sıra veya transform
kabul edilmez.
