# Phase 2 POST-Only Transport R8 Raporu

R8 deterministic fresh GET profilini geri yüklemiş; form fingerprint, exact-four
default exclusion, January 2024, exact-15 ve submission contract kapılarının
tamamı geçmiştir. Bir POST gönderilmiş, fakat POST için açılan ikinci HTTPS
bağlantısı `10s` connect timeout'a düşmüştür. Sanitize sonuç
`UPSTREAM_UNAVAILABLE/TRANSPORT_TIMEOUT` olmuştur.

Run/job `31894769144/95036279609`, Foundation
`31894769137/95036279439`; ikisi de teknik `success` ve artifact `0`.
ZIP/header/data-row `0/0/0`, retry `0`, cleanup `true`.

R9 yeni connection veya retry açmaz. Fresh GET'in başarıyla kurulmuş ve body'si
tam okunmuş aynı allowlisted HTTPS bağlantısını exact aynı POST için bir kez
yeniden kullanır. Payload ve bütün veri güvenliği sözleşmeleri değişmez.
