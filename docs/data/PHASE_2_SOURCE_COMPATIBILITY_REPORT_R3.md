# Phase 2 Resmî Haklar Zinciri Discovery Raporu

| Alan | Değer |
|---|---|
| Belge kimliği | `phase-2-source-compatibility-report-r3` |
| Görev | `PH2-T02-R3` |
| Yürütme commit'i | `524550ee70f48b1492c89d073dcb0376077a90a9` |
| Discovery run/job | `31891212312` / `95027646385` |
| Foundation run/job | `31891212307` / `95027646222` |
| Kapalı sonuç | `RIGHTS_READY_FOR_EXTRACT_PLANNING` |
| Local analysis + attribution | `VERIFIED` |
| Raw redistribution | `DISABLED` |
| Extract | `NOT_RUN` |
| Artifact / data row | `0 / 0` |

## 1. Karar özeti

Data.gov'un kendi dataset sayfalarında yayımladığı iki immutable raw harvest
JSON kaydı GitHub-hosted runner üzerinden `200` ile alınmış ve standard-library
JSON parser ile yalnız allowlisted metadata alanları değerlendirilmiştir.

Primary `BTS Flight Data` kaydı şu zinciri mekanik olarak kanıtlamıştır:

1. `accessLevel = public`;
2. publisher `Bureau of Transportation Statistics`;
3. açıklama `carrier monthly on time performance`;
4. distribution `https://www.transtats.bts.gov`;
5. license `https://www.usa.gov/government-works`.

Marketing on-time kaydı ayrıca public access, BTS publisher ve USA.gov
public-domain label ile aynı veri ailesini corroborate etmiştir. USA.gov
government-works hedefi exact HTTPS path üzerinde `200` dönmüştür. Bu kanıtla
proje içi local analysis attribution şartıyla kullanılabilir; raw ZIP/CSV'nin
Git, release veya portfolio artifact olarak yeniden dağıtımı kapalı kalır.

## 2. Request ve güvenlik sınırı

| Kontrol | Sonuç |
|---|---|
| Runner | `ubuntu-24.04`, CPython `3.12.3`, Linux x86_64 |
| HTTP method | Yalnız `GET` |
| Request | `3 / 4` |
| Redirect | `0 / 1` |
| Retry | `0` |
| Max response | 1 MiB / endpoint |
| Checkout/action/dependency | Yok |
| Permission | `{}` |
| Secret/cache/artifact/OIDC | Yok |
| Extract/POST/ZIP/CSV/row | Hepsi `0` veya `NOT_RUN` |

## 3. Primary metadata kanıtı

| Alan | Değer |
|---|---|
| Title | `BTS Flight Data` |
| Identifier | `TSA-2025121705` |
| Access | `public` |
| Publisher | `Bureau of Transportation Statistics` |
| Distribution | `https://www.transtats.bts.gov` |
| License | `https://www.usa.gov/government-works` |
| Response byte | 651 |
| SHA-256 | `490a4869ef799e378ae61916b57816595c7e200d36000f11fe4095aa2debdb1c` |

## 4. Corroboration metadata kanıtı

| Alan | Değer |
|---|---|
| Title | `U.S. Marketing Air Carriers On-time Performance` |
| Identifier | `https://data.transportation.gov/api/views/56fa-sf82` |
| Access | `public` |
| Publisher | `Bureau of Transportation Statistics` |
| License label | `http://www.usa.gov/publicdomain/label/1.0/` |
| Response byte | 1.355 |
| SHA-256 | `bfb0ee31bd4d4e97951333442c75daa82776ad30b8ce0c0b535da9e56dd20a1d` |

HTTP license label yalnız metadata string'i olarak corroboration için
okunmuştur; HTTP target'a request gönderilmemiştir. Primary haklar kararı exact
HTTPS government-works zincirine dayanır.

## 5. USA.gov hedef kanıtı

`https://www.usa.gov/government-works` exact URL'si `200`, 521 byte ve
`b5128fd8bd0fbcb642b2cc21647a3352bfeea66030abe6221084b41db2cc1c71`
SHA-256 ile doğrulanmıştır. Redirect oluşmamıştır.

## 6. Form ve Extract sınırı

R2'de doğrulanan form contract SHA-256 değeri
`3d9227bf05af8dcf8f4fef99aef86ebbbcbe43561869ba43444079d913b3f8b0`
değiştirilmeden referans alınmıştır. R3 formu tekrar fetch etmemiştir.

- POST gönderilmedi.
- ZIP/CSV/header/data row okunmadı.
- Raw source byte kalıcılaştırılmadı.
- Workflow artifact yüklenmedi.
- Geçici R3 workflow'u result commit'inde silinir.

## 7. Hosted kanıt

Discovery workflow ve aynı commit'teki Foundation workflow `success` ile
tamamlanmış, ikisi de sıfır artifact üretmiştir. Result ve final closeout
commit/run kanıtları cleanup doğrulamasından sonra bu bölüme eklenir.

## 8. Downstream kapısı

Form ve haklar Discovery kapıları artık geçmiştir. Bu sonuç veri indirme yetkisi
vermez. Sonraki adım yalnız fresh form fingerprint equality, January 2024 exact
15-field request, en fazla bir geçici ZIP, header-only ve sıfır data-row
sınırındaki ayrı Extract güvenlik görevinin planlanması olabilir. `PH2-T03`,
Extract `SOURCE_COMPATIBLE` üretmeden açılamaz.
