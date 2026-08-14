# PH1-T03 CI Stack Kararı

| Alan | Değer |
|---|---|
| Karar kimliği | `foundation-ci-stack-v1` |
| Görev | `PH1-T03` |
| Durum | `APPROVED — IMPLEMENTED; HOSTED_RUN_PENDING` |
| Araştırma tarihi | 2026-08-13 |
| Onay tarihi | 2026-08-13 |
| Onay kaynağı | Proje sahibinin açık komutu |
| Onay metni | `PH1-T03 CI stack adayını onaylıyorum.` |
| Workflow hedefi | `.github/workflows/foundation.yml` |

## 1. Karar

Phase 1 foundation için onaylı CI sağlayıcısı **GitHub Actions**, tek referans job
ise **GitHub-hosted `ubuntu-24.04` x86_64** runner'dır. Workflow yalnız
`pull_request` ve `main` branch'ine `push` olaylarında çalışır.

Exact stack ve ayrı PH1-T03 yürütme onayı kayıtlıdır. Stack,
`.github/workflows/foundation.yml` içinde uygulanmıştır. Nihai kabul için final
committed state'e ait gerçek GitHub-hosted run kanıtı gerekir.

## 2. Exact onaylı stack

| Bileşen | Exact seçim | Bütünlük | Lisans | Amaç |
|---|---|---|---|---|
| Provider | GitHub Actions | GitHub-hosted fresh VM | Hizmet | Minimal portfolio CI |
| Runner | `ubuntu-24.04` | Sabit label; `latest` yok | Hizmet | Linux x86_64 referans ortam |
| Checkout | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | `v7.0.1` full SHA | MIT | Repository checkout |
| Runtime setup | `astral-sh/setup-uv@ae62891fec2bb8e7d6c99fc78c9fec3a63790f8d` | `v10.0.0` full SHA | MIT | Exact uv ve Python kurulumu |
| uv | `0.12.3` | Action input ile exact | MIT OR Apache-2.0 | Sync, kalite, build, audit, SBOM |
| Python | Standard GIL-enabled CPython `3.14.7` | Action input + runtime assertion | PSF-2.0 | Project runtime |

`actions/setup-python`, `actions/cache` ve `actions/upload-artifact` eklenmez.
`setup-uv`, exact Python sürümünü kurabildiği için ikinci bir setup action'ı
gereksizdir. Cache clean-room ispatını zayıflatmamak için kapalıdır. Phase 1
kalıcı artifact yükleme veya publish yapmaz.

## 3. Güvenlik sınırı

Workflow aşağıdaki exact politikanın dışına çıkamaz:

- top-level `permissions: contents: read`; belirtilmeyen tüm izinler `none`;
- secret, environment, OIDC, deployment veya external credential yok;
- `pull_request_target`, `workflow_run`, `release` ve `deployment` trigger'ı yok;
- yalnız full 40 karakter action commit SHA'sı; tag, branch veya kısa SHA yok;
- `persist-credentials: false` ve checkout sonrası Git write işlemi yok;
- `enable-cache: false`; restore/save cache yok;
- untrusted event alanı shell komutuna interpolate edilmez;
- workflow package publish, artifact upload, issue/comment veya repository write yapmaz;
- job timeout `15` dakikadır; başarısız veya cancelled step başarı sayılmaz.

GitHub, full commit SHA'larının immutable olduğunu ve üçüncü taraf action için
full SHA kullanılmasını önerir. Token izinleri de minimum yetkiyle explicit
tanımlanır.

## 4. Planlanan workflow topolojisi

Tek job, local clean-room sözleşmesiyle aynı sırayı izler:

1. Full-SHA checkout; credential persistence kapalı.
2. Full-SHA `setup-uv`; `uv 0.12.3`, Python `3.14.7`, cache kapalı.
3. Runner, architecture, uv, Python patch ve GIL doğrulaması.
4. `pyproject.toml` ve `uv.lock` başlangıç hash'i; `uv lock --check`.
5. İlk frozen exact all-groups sync; normalized package inventory.
6. İkinci aynı sync; inventory, lock ve metadata idempotency kontrolü.
7. Import; Ruff format; Ruff lint; mypy strict; pytest.
8. Repository dışındaki `$RUNNER_TEMP` altında wheel/sdist build ve metadata smoke.
9. `uv audit --frozen --output-format json`; ignore yok.
10. CycloneDX 1.5 export; SBOM hash ve component count log'u.
11. Repository transient path, forbidden path ve hash-stability kapanış kontrolü.

CI local raporun yerine geçmez; local ve hosted sonuçların ikisi de gereklidir.
Hosted sonuç da yalnız final commit SHA'sı, run URL/ID, runner image ve `success`
conclusion kaydedildiğinde kanıt sayılır.

## 5. Planlanan action girdileri

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
  with:
    persist-credentials: false

- uses: astral-sh/setup-uv@ae62891fec2bb8e7d6c99fc78c9fec3a63790f8d # v10.0.0
  with:
    version: "0.12.3"
    python-version: "3.14.7"
    enable-cache: false
```

Bu parça karar kanıtıdır; ayrı PH1-T03 yürütme onayından önce workflow
dosyasına yazılmaz.

## 6. Ücretsiz kullanım ve sınırlar

Public GitHub repository için standard GitHub-hosted runner kullanımı ücretsiz
ve GitHub dokümantasyonuna göre unlimited'dır. Private repository kullanımında
hesap planının ücretsiz dakika kotası geçerlidir. Proje ücretli runner, larger
runner, self-hosted runner veya managed third-party CI gerektirmez.

Sadece Linux sonucu üretilecektir. Windows uyumluluğu aday metadata üzerinden
görünse bile `Windows verified` iddiası kurulmayacaktır.

## 7. Onay ve değişiklik kuralı

Bir action release'i, SHA, runner, trigger, permission, cache veya secret
politikası değişirse bu karar otomatik geçerli olmaz. Belge revize edilir ve
yeni exact CI stack onayı istenir.

CI stack onayı 2026-08-13 tarihinde exact aday değişmeden kaydedilmiştir. Görev
hâlâ başlamamıştır. Sıradaki ayrı yürütme cümlesi:

> PH1-T03 planını onaylıyorum; başlat.

## 8. Resmî kaynaklar

| Kaynak | Erişim | Kanıt |
|---|---|---|
| https://docs.github.com/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job | 2026-08-13 | Fresh hosted runner ve `ubuntu-24.04` label |
| https://docs.github.com/actions/how-tos/write-workflows/choose-what-workflows-do/find-and-customize-actions | 2026-08-13 | Full SHA immutability ve pin önerisi |
| https://docs.github.com/actions/reference/workflows-and-actions/workflow-syntax | 2026-08-13 | Explicit minimum `permissions` davranışı |
| https://github.com/actions/checkout/releases/tag/v7.0.1 | 2026-08-13 | Checkout release ve signed commit |
| https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1 | 2026-08-13 | Exact full commit SHA |
| https://github.com/actions/checkout/blob/main/LICENSE | 2026-08-13 | MIT license |
| https://github.com/astral-sh/setup-uv | 2026-08-13 | Exact action SHA, inputs ve Python setup davranışı |
| https://github.com/astral-sh/setup-uv/blob/main/LICENSE | 2026-08-13 | MIT license |
