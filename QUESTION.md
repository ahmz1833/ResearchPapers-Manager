 # سیستم مدیریت مقالات تحقیقاتی دانشگاه


این سوال از شما می‌خواهد که یک **سیستم مدیریت مقالات تحقیقاتی دانشگاه** را برای مدیریت مقالات تحقیقاتی پیاده‌سازی کنید. سیستم از **MongoDB** برای ذخیره‌سازی دائمی پروفایل کاربران، متادیتا مقالات، و روابط استنادی، و از **Redis** برای کش کردن نتایج جستجو، ردیابی تعداد بازدیدهای بی‌درنگ مقالات، و پیاده‌سازی جدول هش برای بررسی در دسترس بودن نام کاربری به صورت بی‌درنگ در زمان ثبت‌نام استفاده می‌کند. این سوال روی ورکفلو دیتابیس شامل طراحی اسکیما، ایندکس‌گذاری، کوئری‌نویسی، و ادغام Redis برای بهینه‌سازی عملکرد تمرکز دارد. احراز هویت کاربران مینیمال است و فقط شامل ثبت‌نام و ورود با نام کاربری یکتا می‌شود.

## الزامات سیستم

### الزامات عملکردی

1.  **مدیریت کاربران**:
	+ **ثبت‌نام**: کاربران با نام کاربری یکتا، نام، ایمیل، رمز عبور، و دپارتمان ثبت‌نام می‌کنند.
		+ بررسی در دسترس بودن نام کاربری به صورت بی‌درنگ با استفاده از جدول هش Redis.
		+ اگر نام کاربری قبلاً گرفته شده باشد، خطا برگردانده شود؛ در غیر این صورت، کاربر ذخیره شده و نام کاربری به عنوان گرفته شده علامت‌گذاری شود.
	+ **ورود**: کاربران با نام کاربری و رمز عبور وارد سیستم شده و شناسه کاربر (user ID) برای ردیابی سشن دریافت می‌کنند.
	+ احراز هویت مینیمال است و فقط برای وصل کردن مقالات به کاربران استفاده می‌شود.

2.  **مدیریت مقالات**:
	+ کاربران احراز هویت شده می‌توانند مقالات را با متادیتا زیر آپلود کنند:
		+ `title`: رشته (اجباری، حداکثر 200 کاراکتر)
		+ `authors`: لیست (1 تا 5 رشته، هر کدام حداکثر 100 کاراکتر)
		+ `abstract`: رشته (اجباری، حداکثر 1000 کاراکتر)
		+ `publication_date`: رشته تاریخ ISO (مثال: &quot;2023-05-15&quot;)
		+ `journal_conference`: رشته (حداکثر 200 کاراکتر)
		+ `keywords`: لیست (1 تا 5 رشته، هر کدام حداکثر 50 کاراکتر)
		+ `citations`: لیست (0 تا 5 شناسه مقاله معتبر از مجموعه Papers)
	+ مقالات به شناسه کاربر آپلودکننده مرتبط می‌شوند.

3.  **قابلیت جستجو**:
	+ جستجوی متنی در عنوان، چکیده، و کلمات کلیدی با استفاده از جستجوی متنی MongoDB.
	+ پشتیبانی از مرتب‌سازی بر اساس تاریخ انتشار (صعودی یا نزولی) یا relevance (امتیاز متنی).
	+ بازگشت تمام نتایج منطبق (بدون صفحه‌بندی).
	+ کش کردن نتایج جستجو در Redis برای کاهش لود MongoDB.

4.  **مدیریت استنادها**:
	+ ذخیره روابط استنادی (مقاله A به مقاله B ارجاع می‌دهد) در یک مجموعه اختصاصی.
	+ محاسبه تعداد استنادها برای هر مقاله (تعداد مقالاتی که به آن ارجاع داده‌اند).

5.  **متریک‌های بی‌درنگ**:
	+ ردیابی تعداد بازدیدهای مقالات در Redis، افزایش در هر بازدید.
	+ سینک کردن تعداد بازدیدها با MongoDB هر 10 دقیقه.

6.  **وارد کردن داده‌ها**:
	+ ارائه اسکریپتی برای پر کردن MongoDB با:
		+ 100 کاربر با نام‌های کاربری یکتا، نام، ایمیل، رمزهای عبور هش‌شده، و دپارتمان‌ها.
		+ 1,000 مقاله با متادیتا تصادفی و شناسه‌های بارگذارنده.
		+ استنادهای تصادفی (0 تا 5 برای هر مقاله) که به مقالات دیگر ارجاع دارند.

7.  **APIها**:
	+ پیاده‌سازی پنج endpoint RESTful برای ثبت‌نام، ورود، آپلود مقاله، جستجو، و جزئیات مقاله، با تعاملات دیتابیس مشخص.

## استک تکنولوژی

+ **دیتابیس**: MongoDB (نسخه 7.0 یا بالاتر) برای ذخیره‌ دائمی. استفاده از [PyMongo](https://pymongo.readthedocs.io/) (Python) یا [Mongoose](https://mongoosejs.com/) (Node.js).
+ **کش**: Redis (نسخه 7.2 یا بالاتر) برای کش، تعداد بازدیدها، و جدول هش نام کاربری. استفاده از [redis-py](https://redis-py.readthedocs.io/) (Python) یا [ioredis](https://github.com/redis/ioredis) (Node.js).
+ **زبان برنامه‌نویسی**: Python (با Flask) یا Node.js (با Express.js). Python توصیه می‌شود.
+ **فریم‌ورک وب**: استفاده از [Flask](https://flask.palletsprojects.com/) (Python) یا [Express.js](https://expressjs.com/) (Node.js) برای APIها.
+ **احراز هویت**: احراز هویت ساده مبتنی بر سشن (بازگشت شناسه کاربر در ورود، استفاده در هدر `X-User-ID`).
+ **تولید داده**: استفاده از [Faker](https://faker.readthedocs.io/) (Python، نسخه 22.0.0) یا [faker-js](https://fakerjs.dev/) (Node.js، نسخه 8.4.1).
+ **هش رمز عبور**: استفاده از [bcrypt](https://pypi.org/project/bcrypt/) (Python، نسخه 4.1.2) یا [bcryptjs](https://www.npmjs.com/package/bcryptjs) (Node.js، نسخه 2.4.3).

**توجه: استفاده از دیگر زبان‌های برنامه‌نویسی و باقی فریم‌ورک‌ها مجاز است.**

## اسکیمای دیتابیس

### مجموعه‌های MongoDB

1.  **Users**:
	+ `_id`: ObjectId (شناسه یکتا)
	+ `username`: String (یکتا، 3–20 کاراکتر، حروف و اعداد با زیرخط)
	+ `name`: String (حداکثر 100 کاراکتر)
	+ `email`: String (حداکثر 100 کاراکتر، فرمت ایمیل معتبر)
	+ `password`: String (هش‌شده با bcrypt)
	+ `department`: String (حداکثر 100 کاراکتر)
	+ **Indexes**:
		+ ایندکس یکتا روی `username`: `db.users.createIndex({ &quot;username&quot;: 1 }, { unique: true })`

2.  **Papers**:
	+ `_id`: ObjectId (شناسه یکتا)
	+ `title`: String (اجباری، حداکثر 200 کاراکتر)
	+ `authors`: [String] (1–5 رشته، هر کدام حداکثر 100 کاراکتر)
	+ `abstract`: String (اجباری، حداکثر 1000 کاراکتر)
	+ `publication_date`: Date (فرمت ISO، مثال: ISODate(&quot;2023-05-15&quot;))
	+ `journal_conference`: String (حداکثر 200 کاراکتر)
	+ `keywords`: [String] (1–5 رشته، هر کدام حداکثر 50 کاراکتر)
	+ `uploaded_by`: ObjectId (ارجاع به مجموعه Users)
	+ `views`: Number (پیش‌فرض 0، همگام‌سازی از Redis)
	+ **Indexes**:
		+ ایندکس متنی روی `title`, `abstract`, `keywords`: `db.papers.createIndex({ &quot;title&quot;: &quot;text&quot;, &quot;abstract&quot;: &quot;text&quot;, &quot;keywords&quot;: &quot;text&quot; })`

3.  **Citations**:
	+ `_id`: ObjectId (شناسه یکتا)
	+ `paper_id`: ObjectId (مقاله ارجاع‌دهنده، ارجاع به Papers)
	+ `cited_paper_id`: ObjectId (مقاله ارجاع‌شده، ارجاع به Papers)
	+ **Indexes**:
		+ ایندکس روی `cited_paper_id`: `db.citations.createIndex({ &quot;cited_paper_id&quot;: 1 })`

### استفاده از Redis

1.  **جدول هش نام‌های کاربری**:
	+ **کلید**: `usernames`
	+ **ساختار**: هش که فیلد آن `username` و مقدار آن `1` (نشانه گرفته شدن) است.
	+ **مثال**: `HSET usernames johndoe123 1`
	+ **عملیات**:
		+ بررسی در دسترس بودن: `HEXISTS usernames &lt;username&gt;`
		+ اگر `0` باشد، نام کاربری در دسترس است؛ کاربر را درج کرده و `HSET usernames &lt;username&gt; 1` را تنظیم کنید.
		+ اگر `1` باشد، خطای 409 برگردانید (&quot;نام کاربری گرفته شده است&quot;).

2.  **کش نتایج جستجو**:
	+ **فرمت کلید**: `search:&lt;search_term&gt;:&lt;sort_by&gt;:&lt;order&gt;`
	+ **مثال**: `search:machine learning:publication_date:desc`
	+ **TTL**: 300 ثانیه (5 دقیقه)
	+ **داده**: رشته JSON از نتایج جستجو (آرایه‌ای از اشیاء مقاله)
	+ **عملیات**:
		+ بررسی کلید با `GET`.
		+ اگر وجود دارد، JSON را تجزیه کرده و برگردانید.
		+ اگر وجود ندارد، MongoDB را کوئری کرده، JSON را با `SETEX` ذخیره کنید، و برگردانید.

3.  **تعداد بازدیدهای مقاله**:
	+ **فرمت کلید**: `paper_views:&lt;paper_id&gt;`
	+ **مثال**: `paper_views:507f1f77bcf86cd799439011`
	+ **عملیات**:
		+ افزایش با `INCR` در هر بازدید.
		+ بازیابی با `GET` برای نمایش.
	+ **همگام‌سازی**: هر 10 دقیقه، `views` در مجموعه Papers را به‌روزرسانی کرده و کلید Redis را به 0 ریست کنید.

## اندپوینت‌های API
### `/signup`

- **Method**: POST

- **Description**: ثبت‌نام کاربر با نام کاربری یکتا

- **Headers**: None

- **Body**: `{ &quot;username&quot;: string, &quot;name&quot;: string, &quot;email&quot;: string, &quot;password&quot;: string, &quot;department&quot;: string }`

- **Response**: `201 Created`, `{ &quot;message&quot;: &quot;User registered&quot;, &quot;user_id&quot;: string }`

- **Status Codes**: 201, 400, 409

### `/login`

- **Method**: POST

- **Description**: ورود و بازگشت شناسه کاربر

- **Headers**: None

- **Body**: `{ &quot;username&quot;: string, &quot;password&quot;: string }`

- **Response**: `200 OK`, `{ &quot;message&quot;: &quot;Login successful&quot;, &quot;user_id&quot;: string }`

- **Status Codes**: 200, 400, 401

### `/papers` (POST)

- **Method**: POST

- **Description**: بارگذاری مقاله جدید

- **Headers**: `X-User-ID: &lt;user_id&gt;`

- **Body**: `{ &quot;title&quot;: string, &quot;authors&quot;: [string], &quot;abstract&quot;: string, &quot;publication_date&quot;: string, &quot;journal_conference&quot;: string, &quot;keywords&quot;: [string], &quot;citations&quot;: [string] }`

- **Response**: `201 Created`, `{ &quot;message&quot;: &quot;Paper uploaded&quot;, &quot;paper_id&quot;: string }`

- **Status Codes**: 201, 400, 401, 404

### `/papers` (GET)

- **Method**: GET

- **Description**: جستجوی مقالات بر اساس پرس‌وجو

- **Headers**: None

- **Body**: Query params: `?search=string`, `?sort_by=string` (publication_date یا relevance), `?order=asc|desc`

- **Response**: `200 OK`, `{ &quot;papers&quot;: [ { &quot;id&quot;: string, &quot;title&quot;: string, &quot;authors&quot;: [string], &quot;publication_date&quot;: string, &quot;journal_conference&quot;: string, &quot;keywords&quot;: [string] } ] }`

- **Status Codes**: 200, 400

### `/papers/{paper_id}`

- **Method**: GET

- **Description**: دریافت جزئیات مقاله با استنادها و بازدیدها

- **Headers**: None

- **Body**: None

- **Response**: `200 OK`, `{ &quot;id&quot;: string, &quot;title&quot;: string, &quot;authors&quot;: [string], &quot;abstract&quot;: string, &quot;publication_date&quot;: string, &quot;journal_conference&quot;: string, &quot;keywords&quot;: [string], &quot;citation_count&quot;: int, &quot;views&quot;: int }`

- **Status Codes**: 200, 404

### ورک‌فلو دیتابیس API

1.  **POST /signup**:
	+ **اعتبارسنجی ورودی**:
		+ `username`: 3–20 کاراکتر، حروف و اعداد با زیرخط.
		+ `name`, `email`, `department`: غیرخالی، در محدوده طول.
		+ `password`: حداقل 8 کاراکتر.
	+ **بررسی Redis**: `HEXISTS usernames &lt;username&gt;`
		+ اگر `1` باشد، خطای 409 برگردانید (&quot;نام کاربری گرفته شده است&quot;).
		+ اگر `0` باشد، ادامه دهید.
	+ **عملیات پایگاه داده**:
		+ هش کردن رمز عبور با bcrypt.
		+ درج در مجموعه Users.
		+ تنظیم در Redis: `HSET usernames &lt;username&gt; 1`.
	+ **پاسخ**: بازگشت 201 با `{ &quot;message&quot;: &quot;User registered&quot;, &quot;user_id&quot;: &quot;&lt;_id&gt;&quot; }`.
	+ **خطاها**: 400 (ورودی نامعتبر)، 409 (نام کاربری تکراری).

2.  **POST /login**:
	+ **اعتبارسنجی ورودی**: `username` و `password` غیرخالی.
	+ **عملیات پایگاه داده**:
		+ کوئری Users با `username`.
		+ تأیید رمز عبور با bcrypt.
	+ **پاسخ**: بازگشت 200 با `{ &quot;message&quot;: &quot;Login successful&quot;, &quot;user_id&quot;: &quot;&lt;_id&gt;&quot; }`.
	+ **خطاها**: 400 (ورودی نامعتبر)، 401 (اعتبارنامه نامعتبر).

3.  **POST /papers**:
	+ **اعتبارسنجی هدر**: بررسی `X-User-ID` با کوئری در Users.
	+ **اعتبارسنجی ورودی**:
		+ `title`, `abstract`: غیرخالی، در محدوده طول.
		+ `authors`, `keywords`: 1–5 آیتم، در محدوده طول.
		+ `publication_date`: تاریخ ISO معتبر.
		+ `citations`: 0–5 شناسه مقاله معتبر (بررسی در مجموعه Papers).
	+ **عملیات پایگاه داده**:
		+ درج مقاله در Papers با `uploaded_by` برابر با `_id` کاربر و `views: 0`.
		+ برای هر شناسه استناد، درج `{ paper_id: new_paper_id, cited_paper_id: cited_id }` در Citations.
	+ **پاسخ**: بازگشت 201 با `{ &quot;message&quot;: &quot;Paper uploaded&quot;, &quot;paper_id&quot;: &quot;&lt;_id&gt;&quot; }`.
	+ **خطاها**: 400 (ورودی نامعتبر)، 401 (شناسه کاربر نامعتبر)، 404 (شناسه استناد نامعتبر).

4.  **GET /papers**:
	+ **اعتبارسنجی پارامترهای کوئری**:
		+ `search`: رشته اختیاری (پیش‌فرض خالی).
		+ `sort_by`: `publication_date` یا `relevance` (پیش‌فرض `relevance`).
		+ `order`: `asc` یا `desc` (پیش‌فرض `desc`).
	+ **عملیات Redis**: بررسی کلید `search:&lt;search_term&gt;:&lt;sort_by&gt;:&lt;order&gt;` با `GET`.
		+ اگر وجود دارد، JSON را تجزیه کرده و بازگشت 200 با `{ &quot;papers&quot;: [...] }`.
	+ **عملیات MongoDB**:
		+ کوئری Papers با `$text: { $search: search_term }`.
		+ مرتب‌سازی بر اساس `textScore` (اگر `relevance`) یا `publication_date`.
	+ **عملیات Redis**: ذخیره نتایج در Redis با `SETEX search:&lt;search_term&gt;:&lt;sort_by&gt;:&lt;order&gt; 300 &lt;JSON&gt;`.
	+ **پاسخ**: بازگشت 200 با `{ &quot;papers&quot;: [...] }`.
	+ **خطاها**: 400 (پارامترهای کوئری نامعتبر).

5.  **GET /papers/{paper_id}**:
	+ **عملیات MongoDB**:
		+ کوئری Papers با `_id`.
		+ شمارش اسناد در Citations که `cited_paper_id` برابر با `paper_id` است.
	+ **عملیات Redis**:
		+ افزایش `paper_views:&lt;paper_id&gt;` با `INCR`.
		+ بازیابی تعداد بازدید با `GET` (پیش‌فرض 0 اگر وجود ندارد).
	+ **پاسخ**: بازگشت 200 با جزئیات مقاله، `citation_count`، و `views`.
	+ **خطاها**: 404 (مقاله یافت نشد).

### تسک پس‌زمینه

+ **هدف**: همگام‌سازی تعداد بازدیدهای Redis با MongoDB هر 10 دقیقه.
+ **پیاده‌سازی**:
	+ بازیابی تمام کلیدهای `paper_views:*` (استفاده از `KEYS paper_views:*` یا ردیابی شناسه‌های مقالات).
	+ برای هر کلید، تعداد را با `GET` بازیابی کنید، فیلد `views` در Papers را با `$inc: { views: count }` به‌روزرسانی کنید، و کلید Redis را با `SET &lt;key&gt; 0` بازنشانی کنید.
+ **زمان‌بند**: استفاده از [APScheduler](https://apscheduler.readthedocs.io/) (Python، نسخه 3.10.1) یا [node-cron](https://www.npmjs.com/package/node-cron) (Node.js، نسخه 3.0.2).

## اسکریپت تولید و وارد کردن دادۀ جعلی
+ **الزامات**:
	+ تولید 100 کاربر:
		+ `username`: یکتا، 3–20 کاراکتر، حروف و اعداد با زیرخط.
		+ `name`: تصادفی (حداکثر 100 کاراکتر).
		+ `email`: ایمیل معتبر تصادفی (حداکثر 100 کاراکتر).
		+ `password`: هش‌شده با bcrypt، تصادفی 8–12 کاراکتر.
		+ `department`: تصادفی (حداکثر 100 کاراکتر).
	+ تولید 1,000 مقاله:
		+ `title`: جمله تصادفی (6–10 کلمه، حداکثر 200 کاراکتر).
		+ `authors`: 1–5 نام تصادفی (هر کدام حداکثر 100 کاراکتر).
		+ `abstract`: پاراگراف تصادفی (حداکثر 1000 کاراکتر).
		+ `publication_date`: تاریخ تصادفی بین 2015-06-05 و 2025-06-05.
		+ `journal_conference`: نام تصادفی (حداکثر 200 کاراکتر).
		+ `keywords`: 1–5 کلمه تصادفی (هر کدام حداکثر 50 کاراکتر).
		+ `uploaded_by`: شناسه کاربر تصادفی از Users.
		+ `views`: 0.
	+ تولید استنادها:
		+ برای هر مقاله، 0–5 مقاله دیگر به صورت تصادفی انتخاب کنید (بدون خود-استناد).
		+ درج در مجموعه Citations.
	+ به‌روزرسانی جدول هش Redis `usernames` با تمام نام‌های کاربری (`HSET usernames &lt;username&gt; 1`).
+ **کتابخانه**: استفاده از [Faker](https://faker.readthedocs.io/) (Python، نسخه 22.0.0) یا [faker-js](https://fakerjs.dev/) (Node.js، نسخه 8.4.1).

## فرمت سابمیت نهایی

+ ارسال کل سورس کد
+ ارسال ویدیو دمو از پروژه به همراه توضیح مختصر از کدها
+ نوشتن کوئری‌های مونگو بدون استفاده از ORM