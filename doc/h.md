ة Trello لمشروع CSV Analyzer، مقسمة إلى قوائم (Lists) وبطاقات (Cards) داخل كل قائمة:

القائمة 1: التخطيط والتحليل (Planning & Analysis)

- البطاقات:
  - مراجعة وثيقة متطلبات المنتج `E4power.md`
  - مراجعة وثيقة التصميم التقني (إذا وجدت)
  - تحديد نطاق المشروع والميزات الأساسية
  - إعداد بيئة التطوير المحلية
القائمة 2: إعداد البنية التحتية (Infrastructure Setup)

- البطاقات:
  - تكوين Docker Compose لـ Prometheus و Grafana `docker-compose.yml`
  - تكوين Prometheus لمراقبة التطبيق `prometheus.yml`
  - إعداد Grafana ولوحات المعلومات (Dashboards) `csv_analyzer.json`
  - تثبيت المتطلبات الأساسية للمشروع `requirements.txt`
القائمة 3: تطوير الميزات الأساسية (Core Feature Development)

- البطاقات:
  - تطوير نماذج قاعدة البيانات (Models) `models.py`
  - إنشاء طرق العرض (Views) لتحميل ومعالجة ملفات CSV `views.py`
  - تطوير واجهات برمجة التطبيقات (APIs) باستخدام Django REST Framework `serializers.py`
  - تطبيق منطق معالجة البيانات وتحليلها
  - تضمين ميزات التعلم الآلي (ML) `mlflow_utils.py`
القائمة 4: المراقبة والمقاييس (Monitoring & Metrics)

- البطاقات:
  - تعريف المقاييس المخصصة (Custom Metrics) `metrics.py`
  - دمج Prometheus مع التطبيق `monitoring.py`
  - إنشاء لوحات معلومات Grafana للمراقبة `csv_analyzer.json`
  - إعداد تنبيهات Grafana (Alerts) `Edit rule - Alert rules - Alerting - Grafana.html`
القائمة 5: التكامل المستمر والنشر المستمر (CI/CD)

- البطاقات:
  - إعداد سير عمل CI/CD باستخدام GitHub Actions `ci.yml`
  - كتابة اختبارات الوحدة (Unit Tests) `test_models.py` و `test_views.py`
  - ضمان جودة الكود (Code Quality) باستخدام Flake8 `.flake8`
  - أتمتة عمليات النشر (Deployment Automation)
القائمة 6: التوثيق (Documentation)

- البطاقات:
  - تحديث ملف README.md `README.md`
  - كتابة دليل المستخدم `user_guide.md`
  - توثيق نقاط النهاية (API Endpoints) باستخدام DRF Spectacular `schema.yml`
القائمة 7: تحسينات وأداء (Improvements & Performance)

- البطاقات:
  - تحسين أداء معالجة ملفات CSV
  - تحسين استجابة واجهة المستخدم (UI Responsiveness)
  - مراجعة وتحسين الكود (Code Refactoring)
القائمة 8: الاختبار (Testing)

- البطاقات:
  - إجراء اختبارات التكامل (Integration Tests)
  - إجراء اختبارات الأداء (Performance Tests)
  - اختبار مسار محاكاة الأخطاء `simulate_error` عبر URL