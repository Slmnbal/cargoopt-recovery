# Phase 2 Physical Header Discovery R10 Raporu

R10 run/job `31895258635/95037495467`, Foundation
`31895258632/95037495292`; artifact `0`. POST `200`, ZIP `1`, header record `1`,
data row `0`, cleanup `true`.

CSV tam 15 fiziksel BTS kolon kodu taşımıştır:

```text
FL_DATE,OP_UNIQUE_CARRIER,OP_CARRIER_AIRLINE_ID,OP_CARRIER_FL_NUM,
ORIGIN_AIRPORT_ID,ORIGIN,DEST_AIRPORT_ID,DEST,CRS_DEP_TIME,CRS_ARR_TIME,
ARR_DELAY_NEW,CANCELLED,DIVERTED,CRS_ELAPSED_TIME,DISTANCE
```

Ekstra, eksik, duplicate veya terminal boş kolon yoktur. Sıra, fresh formdaki
exact-15 target checkbox DOM sırasıyla aynıdır. Sonuç yalnız business-label
isimleri bekleyen R10 sözleşmesine göre mismatch'tir; fiziksel şema R2'de
kanıtlanan one-to-one field mapping ile tamamen açıklanmıştır.

R11 ağ veya veri erişimi yapmadan bu physical-to-canonical mapping'i veri ve
kalite sözleşmelerine exact allowlist olarak işler ve kanıtları uzlaştırır.
