# پل دمای NVIDIA GTX 1080 Ti به HPE DL380 Gen9 از طریق OCSD و iLO 4

**نسخه:** `0.1.0-rc2`  
**وضعیت انتشار:** Experimental Release Candidate — برای Production تأیید نشده است  
**پلتفرم qualification:** فقط یک دستگاه HPE ProLiant DL380 Gen9 با iLO 4 نسخه 2.77 و GTX 1080 Ti Founders Edition

## هدف پروژه

Publisher دمای GPU را از طریق `nvidia-smi` روی Proxmox Host می‌خواند، Allocation مربوط به Option Card Sensor Data (OCSD) را از SMBIOS Type 229 کشف می‌کند و فقط رکورد سوم 160 بایتی را به‌روزرسانی می‌کند. iLO پس از ثبت سنسور، مقدار PCI را از طریق IPMI/Redfish نمایش می‌دهد و الگوریتم حرارتی خود HPE مسئول سیاست فن باقی می‌ماند.

این پروژه PWM فن‌ها را مستقیماً نمی‌نویسد، Firmware iLO را Patch نمی‌کند و هیچ Container، VM، Docker یا پردازش دیگری را مدیریت یا متوقف نمی‌کند.

## نتیجه‌های مشاهده‌شده روی میزبان آزمایش

- GPU: NVIDIA GeForce GTX 1080 Ti Founders Edition، BDF برابر `0000:0b:00.0`.
- Publisher دمای GPU را خوانده و رکورد اختصاصی OCSD را به‌روزرسانی کرده است.
- Allocation مشاهده‌شده OCSD برابر 16 KiB در آدرس فیزیکی `0x791f4000` بوده است. آدرس در Runtime کشف می‌شود و مقدار قابل‌تعمیم به Host دیگر نیست.
- پس از یک Reset پردازنده مدیریتی iLO، سنسور `22-PCI 2` به وضعیت `Enabled / OK` رسیده است.
- پنج نمونه هم‌زمان نشان دادند GPU بین 48 تا 49°C و سنسور iLO بین 63 تا 64°C بوده است. اختلاف مشاهده‌شده 14 تا 16°C و میانگین 15°C بوده است.
- در پایش 23 نمونه‌ای، Fan 5 موقتاً به 82% رسید؛ اما دمای GPU در همان بازه تقریباً ثابت و برابر 48 تا 49°C بود. بنابراین رابطه علت و معلولی GPU→Fan اثبات نشده است.

**مهم:** اختلاف 15°C یک مشاهده در یک نقطه کار است؛ در کد به‌عنوان Offset ثابت اعمال نمی‌شود و کالیبراسیون در بارها و دماهای مختلف نیست.

## پروفایل سخت‌افزار آزمایش‌شده

| مؤلفه | مقدار مشاهده‌شده |
|---|---|
| سرور | HPE ProLiant DL380 Gen9 |
| iLO | iLO 4 Firmware 2.77 |
| System ROM | P89، BIOS revision 2.76 |
| GPU | NVIDIA GeForce GTX 1080 Ti Founders Edition |
| GPU BDF | `0000:0b:00.0` |
| Proxmox VE | 9.2.2 |
| Kernel | `7.0.2-6-pve` |
| Python روی Host | 3.13.5 در زمان Export |
| NVIDIA-SMI | 580.196.07 در زمان Export |
| سنسور iLO مشاهده‌شده | `22-PCI 2` |

این مقادیر فقط پروفایل یک میزبان‌اند. BDF، آدرس فیزیکی، Bus/Device، layout، نام سنسور و رفتار Firmware را برای دستگاه دیگر ثابت فرض نکنید.

## تغییرات RC2

RC2 از سورس دقیق Exportشده از Host آغاز شده و سپس برای انتشار پاک‌سازی شده است:

- حذف توابع و متغیرهای بلااستفاده مدیریت Workload؛
- حذف `OCSD_WORKLOAD_UNITS` و وابستگی به EnvironmentFile قدیمی؛
- ساده‌سازی عملیات به `publish_record`؛
- حذف آستانه قدیمی توقف Workload و Offset/Tolerance بلااستفاده؛
- اصلاح نام‌گذاری‌های باقیمانده T4 به متن GPU عمومی؛
- افزودن 21 تست مستقل برای سورس نهایی RC2؛
- افزودن فایل MIT، Third-party Notices، CI، Service Unit نمونه و مستندات عملیات.

این کپی RC2 با فایل در حال اجرای Host بایت‌به‌بایت یکسان نیست. سورس Host با SHA-256 زیر مبنای پاک‌سازی بوده است:

`a92e6f87ab6037e76d4ba0f0e850bf0e422e9600b7dfddda602e8b2ab0b5178f`

SHA-256 سورس پاک‌سازی‌شده RC2:

`f6990a761e01ea95e3db51cd42cd6b0db980efe6a1807ad5a2239c8737ada940`

هیچ تغییری در سرویس فعال Host با ساخت این بسته انجام نشده است.

## ساختار بسته

- `src/`: Publisher نهایی RC2.
- `tests/`: تست‌های استاندارد Python بدون وابستگی خارجی.
- `systemd/`: Unit نمونه و manual-start-only.
- `config/`: توضیح تنظیمات و موارد منسوخ.
- `docs/`: معماری، وضعیت، زمان‌بندی رخدادها، روش استقرار، Release Gates و نتایج تست.
- `scripts/`: بررسی ایستای Candidate و Exporter اصلی Host.
- `validation/`: شواهد و مقادیر اندازه‌گیری‌شده.
- `legal/` و `LICENSE`: مجوز و انتساب‌ها.

## اجرای تست‌ها

نیاز به سخت‌افزار واقعی ندارد:

```bash
python3 -m py_compile src/gen9_t4_ocsd.py tests/test_publisher.py
python3 -m unittest discover -s tests -v
python3 scripts/verify_candidate.py .
systemd-analyze verify systemd/gen9-t4-ocsd.service
```

یا:

```bash
make check
```

تست‌ها فقط با حافظه مصنوعی و Mock کار می‌کنند و به `/dev/mem`، GPU، IPMI، Redfish، systemd یا Workload واقعی دسترسی ندارند.

## استقرار

این بسته Installer خودکار ندارد. Unit در `systemd/` یک نمونه دستی است؛ قبل از استفاده، مسیرها، Device Nodeها و تطابق سخت‌افزار را بررسی کنید. Unit هیچ `EnvironmentFile`، `ExecStop`، Guard یا `[Install]` ندارد و برای فعال‌سازی خودکار در Boot تنظیم نشده است.

شروع سرویس، عملیات تغییردهنده است: Publisher به `/dev/mem` دسترسی نوشتن می‌گیرد، رکورد سوم را claim می‌کند و Header device count را به‌روزرسانی می‌کند. راهنمای دقیق و Rollback در `docs/DEPLOYMENT_AND_OPERATIONS.md` است.

## محدودیت‌ها و بلوکه‌کننده‌ها

1. پروتکل OCSD عمومی و رسمی مستند نشده است. پروژه مرجع `conroy-cheers/ocsd` می‌گوید مهندسی معکوس آن روی یک ML350 Gen9 انجام شده و روی سخت‌افزارهای دیگر تست نشده است.
2. پروژه مرجع Ocean Media Now برای Tesla T4، iLO 4 v2.82 و High Performance fans qualification شده؛ این سیستم GTX 1080 Ti، iLO 2.77 و Standard fans دارد. سازگاری عمومی از آن نتیجه نمی‌شود.
3. Offset دما در پنج نمونه ثابت مشاهده شده، اما در محدوده دمایی مختلف کالیبره نشده است.
4. پایش فن 23 نمونه‌ای رابطه علت و معلولی GPU→Fan را اثبات نمی‌کند.
5. Soak test بلندمدت، پایداری پس از Boot، Watchdog recovery و failure injection روی سخت‌افزار انجام نشده‌اند.
6. Unit نمونه فقط در `systemd-analyze verify` بررسی شده است؛ هنوز روی Host جداگانه نصب و qualification نشده است.
7. هیچ Redfish client با TLS verification غیرفعال در بسته اجرایی RC2 وجود ندارد؛ نمونه‌های تشخیصی قدیمی گفتگو نباید به‌عنوان ابزار عمومی استفاده شوند.

## تصمیم انتشار

`0.1.0-rc2` فقط یک Experimental Release Candidate است. این نسخه برای بازبینی سورس، تست واحد و تکرارپذیری بسته مناسب است؛ اما برای Production، سازگاری عمومی HPE Gen9 یا اثبات کنترل فن از GPU تأیید نشده است.
