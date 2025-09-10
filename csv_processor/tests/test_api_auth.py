# ... existing code ...
import os
import shutil
import io
import pytest
import pandas as pd
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from csv_processor.models import CSVFile

@pytest.fixture
def user(db):
    return User.objects.create_user(username='apitester', password='StrongPass123')

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(api_client, user):
    api_client.login(username='apitester', password='StrongPass123')
    return api_client

@pytest.fixture
def sample_csv_file():
    # ملف CSV بسيط للرفع عبر API
    df = pd.DataFrame({
        'feature1': [1, 2, 3],
        'feature2': [4, 5, 6],
        'target':   [7, 8, 9],
    })
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    return SimpleUploadedFile("sample.csv", csv_bytes, content_type="text/csv")

@pytest.fixture
def csv_record(db, user, tmp_path):
    # نتأكد من مجلد media/csv_files
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'csv_files'), exist_ok=True)
    file_path = os.path.join(settings.MEDIA_ROOT, 'csv_files', 'existing.csv')

    # ننشئ ملف فعلي على القرص
    df = pd.DataFrame({
        'feature1': [10, 11, 12],
        'feature2': [13, 14, 15],
        'target':   [1, 0, 1],
    })
    df.to_csv(file_path, index=False)

    # نسجل السجلّ في قاعدة البيانات ويرتبط بالمستخدم المصادق
    return CSVFile.objects.create(
        user=user,
        title="existing.csv",
        file="csv_files/existing.csv",
        rows_count=df.shape[0],
        columns_count=df.shape[1],
    )

@pytest.fixture(autouse=True)
def cleanup_media():
    # تنظيف بعد كل اختبار
    yield
    csv_dir = os.path.join(settings.MEDIA_ROOT, 'csv_files')
    if os.path.exists(csv_dir):
        shutil.rmtree(csv_dir, ignore_errors=True)

@pytest.mark.django_db
class TestAPIAuthProtection:

    def test_unauthenticated_returns_401(self, api_client, csv_record):
        # current_user
        resp = api_client.get(reverse('current_user'))
        assert resp.status_code == 401

        # metrics JSON
        resp = api_client.get(reverse('api_metrics'))
        assert resp.status_code == 401

        # prometheus metrics (text/plain)
        resp = api_client.get(reverse('api_prometheus_metrics'))
        assert resp.status_code == 401

        # export csv
        resp = api_client.get(reverse('api_export_csv', kwargs={'pk': csv_record.pk}))
        assert resp.status_code == 401

        # delete csv
        resp = api_client.post(reverse('api_delete_csv', kwargs={'pk': csv_record.pk}))
        assert resp.status_code == 401

    def test_authenticated_success_status(self, auth_client, csv_record, sample_csv_file):
        # current_user
        resp = auth_client.get(reverse('current_user'))
        assert resp.status_code == 200

        # metrics JSON
        resp = auth_client.get(reverse('api_metrics'))
        assert resp.status_code == 200
        assert isinstance(resp.json(), dict)

        # prometheus metrics
        resp = auth_client.get(reverse('api_prometheus_metrics'))
        assert resp.status_code == 200
        assert 'text/plain' in resp.headers.get('Content-Type', '')

        # upload csv (201 Created)
        resp = auth_client.post(
            reverse('upload-csv'),
            data={'file': sample_csv_file},
            format='multipart'
        )
        assert resp.status_code in (201, 200)  # 201 متوقعة، 200 مقبولة عند بعض الإعدادات
        # export csv
        resp = auth_client.get(reverse('api_export_csv', kwargs={'pk': csv_record.pk}))
        assert resp.status_code == 200
        # delete csv
        resp = auth_client.post(reverse('api_delete_csv', kwargs={'pk': csv_record.pk}))
        assert resp.status_code == 200
# ... existing code ...