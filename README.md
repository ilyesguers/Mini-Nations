# Mini-Nations — Linebet Analytics Bot

بوت Telegram خاص بمستخدم واحد لتسجيل وتحليل السجل التاريخي للعبتي Aviator وApple على Linebet.

> **تنبيه:** هذا المشروع أداة لتسجيل البيانات وتحليلها إحصائياً، وليس وسيلة مضمونة للفوز أو التنبؤ بنتائج الألعاب العشوائية. لا توجد في النسخة الحالية آلية اتصال رسمية بـ Linebet؛ الإدخال اليدوي هو مصدر البيانات المعتمد إلى أن يتم التحقق من واجهة موثوقة ومسموح باستخدامها.

## المزايا الحالية

- وصول محصور بمعرّف Telegram واحد (`OWNER_ID`).
- أوامر تسجيل نتائج Aviator وApple.
- إحصائيات وصفية للسجل: عدد الجولات، الفوز والخسارة، نسبة الفوز المسجلة، ومتوسط/وسيط/أعلى مضاعف متاح.
- تصدير السجل إلى CSV.
- PostgreSQL مع SQLAlchemy async.
- مخطط قاعدة بيانات مُدار بواسطة Alembic.
- تشغيل طويل الأمد مناسب لخدمة Worker على Railway.

## المتطلبات

- Python 3.12+
- Telegram bot token من BotFather
- PostgreSQL database (مثل Railway PostgreSQL)

## الإعداد المحلي

1. أنشئ بوتاً عبر `@BotFather` واحصل على التوكن.
2. انسخ `.env.example` إلى `.env` واملأ القيم:

| المتغير | الوصف |
|---|---|
| `BOT_TOKEN` | توكن بوت Telegram |
| `OWNER_ID` | معرّف Telegram الرقمي المسموح له |
| `DATABASE_URL` | رابط PostgreSQL |
| `LOG_LEVEL` | مستوى السجلات، افتراضياً `INFO` |

3. ثبّت الاعتماديات وشغّل الترحيلات والبوت:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app
```

على Windows PowerShell استخدم `.venv\Scripts\Activate.ps1` لتفعيل البيئة.

## الأوامر

- `/start` — القائمة الرئيسية.
- `/help` — المساعدة.
- `/dashboard` — ملخص كل الألعاب.
- `/record_aviator 2.35 win ملاحظة` — تسجيل مضاعف ونتيجة Aviator.
- `/record_apple win ملاحظة` — تسجيل نتيجة Apple.
- `/stats_aviator` — إحصائيات Aviator.
- `/stats_apple` — إحصائيات Apple.
- `/export` — تنزيل سجل النتائج CSV.

تقبل نتيجة الجولة `win` أو `loss`. في Aviator يجب أن يكون المضاعف رقماً موجباً. لا تسجل معلومات دخول Linebet أو كلمات المرور أو مفاتيح الجلسات في البوت.

## النشر على Railway

1. أنشئ خدمة PostgreSQL في مشروع Railway.
2. اربط المستودع بخدمة Worker.
3. أضف `BOT_TOKEN` و`OWNER_ID` و`DATABASE_URL` إلى متغيرات الخدمة. استخدم متغير اتصال PostgreSQL الذي يوفره Railway.
4. سيشغّل أمر البدء `alembic upgrade head` ثم `python -m app`.
5. لا تضع ملف `.env` أو التوكن داخل GitHub.

استخدم نسخة احتياطية دورية لقاعدة البيانات قبل أي ترقية كبيرة.

## الاختبارات

```bash
pytest -q
```

## حدود التكامل

أي تكامل آلي مع Linebet يجب أن يعتمد على API رسمي أو مصدر بيانات موثوق ومسموح به. لا يتضمن المشروع كشطاً للموقع أو تجاوز حماية أو تسجيل دخول آلي. التحليلات تصف البيانات المسجلة ولا تستنتج نتيجة الجولة القادمة.
