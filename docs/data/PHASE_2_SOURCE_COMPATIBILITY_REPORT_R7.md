# Phase 2 Browser-Equivalent Transport R7 Raporu

R7 workflow run `31894598315`, job `95035849388` teknik olarak `success`, domain
sonucu `CONTRACT_SOURCE_MISMATCH/FRESH_FORM_FINGERPRINT_MISMATCH` olmuştur.
Browser User-Agent ve navigation header'ları fresh GET'e de uygulandığı için BTS
171.840 byte yerine 174.887 byte'lık UA-dependent form varyantı döndürmüş ve
canonical contract hash `6a2b89d8...c49c31` olmuştur.

Fail-closed kapı POST'tan önce çalışmıştır: request `1`, POST `0`, ZIP `0`,
header `0`, data row `0`, cleanup `true`, artifact `0`. Foundation run
`31894598316`, job `95035849222` başarıyla tamamlanmıştır.

R8 yalnız uygulama hatasını düzeltir: GET header profili R6'daki deterministic
değerlere byte-for-byte döner; browser-equivalent header'lar yalnız POST branch'i
içinde kurulur. Form/payload/exact-four/exact-15/ZIP/header/cleanup semantiği
değişmez.
