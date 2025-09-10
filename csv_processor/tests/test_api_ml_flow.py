import os
import io
import shutil
import pytest
import pandas as pd
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient


@pytest.fixture
def user(db):
    return User.objects.create_user(username='mltester', password='StrongPass123')


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.login(username='mltester', password='StrongPass123')
    return api_client


@pytest.fixture
def cleanup_media():
    # تنظيف مجلد ملفات CSV بعد كل اختبار
    yield
    csv_dir = os.path.join(settings.MEDIA_ROOT, 'csv_files')
    if os.path.exists(csv_dir):
        shutil.rmtree(csv_dir, ignore_errors=True)


def make_simple_uploaded_csv(df: pd.DataFrame, name="data.csv"):
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    return SimpleUploadedFile(name, csv_bytes, content_type="text/csv")


@pytest.mark.django_db
def test_full_ml_flow_regression(auth_client, cleanup_media):
    # 1) إنشاء CSV كافٍ للـ cv=5 (>= 10 صفوف مفضل)
    rows = 20
    df = pd.DataFrame({
        "feature1": list(range(rows)),
        "feature2": [x * 2 for x in range(rows)],
        "target":   [x * 3 + 1 for x in range(rows)],  # خطي بسيط
    })
    file = make_simple_uploaded_csv(df, name="train.csv")

    # 2) رفع CSV
    resp = auth_client.post(reverse('upload-csv'), data={'file': file}, format='multipart')
    assert resp.status_code in (200, 201), resp.content
    csv_id = resp.json()['id']

    # 3) تدريب نموذج Regression (RandomForest كافٍ لاجتياز الاختبارات)
    train_payload = {
        "features": ["feature1", "feature2"],
        "target": "target",
        "model_type": "regression",
        "model_name": "rf_model",
        "algorithm_type": "random_forest"
    }
    resp = auth_client.post(
        reverse('api_train_ml', kwargs={'pk': csv_id}),
        data=train_payload,
        format='json'
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body.get("message") == "Model trained and saved"
    assert body.get("model_type") == "regression"
    assert body.get("model_name") == "rf_model"
    assert "metrics" in body and isinstance(body["metrics"], dict)

    # 4) اختبار التنبؤ عبر /api/test-model/<pk>/<model_name>/
    test_payload = {
        "inputs": {"feature1": 5.0, "feature2": 10.0}
    }
    resp = auth_client.post(
        reverse('api_test_model', kwargs={'pk': csv_id, 'model_name': 'rf_model'}),
        data=test_payload,
        format='json'
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert "prediction" in body
    assert "latency_ms" in body

    # 5) تصدير CSV عبر API
    resp = auth_client.get(reverse('api_export_csv', kwargs={'pk': csv_id}))
    assert resp.status_code == 200
    assert 'text/csv' in resp.headers.get('Content-Type', '')
    assert 'attachment;' in resp.headers.get('Content-Disposition', '')


@pytest.mark.django_db
def test_regression_with_non_numeric_feature_returns_422(auth_client, cleanup_media):
    # CSV يحتوي على عمود نصي ضمن الخصائص
    rows = 12
    df = pd.DataFrame({
        "feature1": list(range(rows)),
        "category": ["A" if i % 2 == 0 else "B" for i in range(rows)],
        "target":   [i * 2 for i in range(rows)],
    })
    file = make_simple_uploaded_csv(df, name="bad_regression.csv")

    # رفع CSV
    resp = auth_client.post(reverse('upload-csv'), data={'file': file}, format='multipart')
    assert resp.status_code in (200, 201), resp.content
    csv_id = resp.json()['id']

    # محاولة تدريب Regression مع عمود نصّي ضمن features ⇒ يجب أن يرجع 422
    train_payload = {
        "features": ["feature1", "category"],  # category نصّي
        "target": "target",
        "model_type": "regression",
        "model_name": "bad_reg",
        "algorithm_type": "linear"
    }
    resp = auth_client.post(
        reverse('api_train_ml', kwargs={'pk': csv_id}),
        data=train_payload,
        format='json'
    )
    assert resp.status_code == 422, resp.content
    body = resp.json()
    assert body.get("error_code") == "NON_NUMERIC_FEATURES_REGRESSION"
    assert "non_numeric_features" in body