import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from csv_processor.models import CSVFile
import pandas as pd
import os
import shutil

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.fixture
def authenticated_client(client, user):
    client.login(username='testuser', password='testpass123')
    return client

@pytest.fixture
def sample_csv():
    data = {
        'name': ['John', 'Jane', 'Bob'],
        'age': [25, 30, 35],
        'city': ['Paris', 'Lyon', 'Nice']
    }
    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False).encode('utf-8')
    return SimpleUploadedFile(
        "test.csv",
        csv_content,
        content_type="text/csv"
    )

@pytest.fixture
def uploaded_csv_file(user, sample_csv):
    # Ensure media directories exist
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'csv_files'), exist_ok=True)
    
    # Create actual file on disk
    file_path = os.path.join(settings.MEDIA_ROOT, 'csv_files', 'test.csv')
    with open(file_path, 'wb') as f:
        f.write(sample_csv.read())
    
    # Reset file pointer
    sample_csv.seek(0)
    
    # Create database record
    csv_file = CSVFile.objects.create(
        user=user,
        title="test.csv",
        file="csv_files/test.csv",
        rows_count=3,
        columns_count=3
    )
    return csv_file

@pytest.fixture(autouse=True)
def cleanup_media():
    yield
    # Cleanup after test
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'csv_files')):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'csv_files'))

@pytest.mark.django_db
class TestViews:
    def test_home_view(self, authenticated_client):
        response = authenticated_client.get(reverse('home'))
        assert response.status_code == 200
        
    def test_upload_csv(self, authenticated_client, sample_csv):
        response = authenticated_client.post(
            reverse('upload_csv'),
            {'csv_file': sample_csv},
            format='multipart'
        )
        assert response.status_code == 302  # Redirect after successful upload
        assert CSVFile.objects.count() == 1
        
    def test_view_csv(self, authenticated_client, uploaded_csv_file):
        response = authenticated_client.get(
            reverse('view_csv', kwargs={'pk': uploaded_csv_file.pk})
        )
        assert response.status_code == 200
        
    def test_delete_row(self, authenticated_client, uploaded_csv_file):
        response = authenticated_client.post(
            reverse('delete_row', kwargs={'pk': uploaded_csv_file.pk}),
            {'row_number': 1}
        )
        assert response.status_code == 302  # Redirect after deletion
        
    def test_clean_data(self, authenticated_client, uploaded_csv_file):
        response = authenticated_client.post(
            reverse('clean_data', kwargs={'pk': uploaded_csv_file.pk}),
            {
                'operation': 'remove_duplicates',
                'columns': ['name']
            }
        )
        assert response.status_code == 302  # Redirect after cleaning
        
    def test_column_operation(self, authenticated_client, uploaded_csv_file):
        response = authenticated_client.post(
            reverse('column_operation', kwargs={'pk': uploaded_csv_file.pk}),
            {
                'operation': 'rename_column',
                'column': 'name',
                'new_name': 'full_name'
            }
        )
        assert response.status_code == 302  # Redirect after operation

    @pytest.fixture
    def trained_classification_model(self, uploaded_csv_file):
        # Create a simple classification dataset
        data = {
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [2, 4, 6, 8, 10],
            'target': ['A', 'B', 'A', 'B', 'A']
        }
        df = pd.DataFrame(data)
        model_path = uploaded_csv_file.file.path
        df.to_csv(model_path, index=False)
        
        # Train the model
        from sklearn.linear_model import LogisticRegression
        X = df[['feature1', 'feature2']]
        y = df['target']
        model = LogisticRegression(random_state=42)
        model.fit(X, y)
        
        # Save the model
        metrics = {
            'accuracy': 1.0,
            'classification_report': 'Test Report',
            'original_classes': ['A', 'B']
        }
        uploaded_csv_file.save_ml_model('test_classifier', model, ['feature1', 'feature2'], 'classification', metrics)
        return uploaded_csv_file

    def test_model_classification(self, authenticated_client, trained_classification_model):
        # Test GET request
        response = authenticated_client.get(
            reverse('test_model', kwargs={'pk': trained_classification_model.pk, 'model_name': 'test_classifier'})
        )
        assert response.status_code == 200

        # Test POST request with valid data
        response = authenticated_client.post(
            reverse('test_model', kwargs={'pk': trained_classification_model.pk, 'model_name': 'test_classifier'}),
            {'feature1': '1', 'feature2': '2'}
        )
        assert response.status_code == 200
        assert 'prediction' in response.context
        assert response.context['prediction'] in ['A', 'B']
        assert 'class_probabilities' in response.context

        # Test POST request with missing feature
        response = authenticated_client.post(
            reverse('test_model', kwargs={'pk': trained_classification_model.pk, 'model_name': 'test_classifier'}),
            {'feature1': '1'}
        )
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert any('Please enter a value for feature2' in str(message) for message in messages)

        # Test POST request with invalid data
        response = authenticated_client.post(
            reverse('test_model', kwargs={'pk': trained_classification_model.pk, 'model_name': 'test_classifier'}),
            {'feature1': 'invalid', 'feature2': '2'}
        )
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert any('Invalid value for feature1' in str(message) for message in messages)

        # Test with non-existent model
        response = authenticated_client.get(
            reverse('test_model', kwargs={'pk': trained_classification_model.pk, 'model_name': 'nonexistent_model'})
        )
        assert response.status_code == 302  # Redirects to view_csv

    @pytest.fixture
    def trained_regression_model(self, uploaded_csv_file):
        # Create a simple regression dataset
        data = {
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [2, 4, 6, 8, 10],
            'target': [10, 20, 30, 40, 50]
        }
        df = pd.DataFrame(data)
        model_path = uploaded_csv_file.file.path
        df.to_csv(model_path, index=False)
        
        # Train the model
        from sklearn.linear_model import LinearRegression
        X = df[['feature1', 'feature2']]
        y = df['target']
        model = LinearRegression()
        model.fit(X, y)
        
        # Save the model
        metrics = {
            'r2_score': 1.0,
            'mean_squared_error': 0.0
        }
        uploaded_csv_file.save_ml_model('test_regressor', model, ['feature1', 'feature2'], 'regression', metrics)
        return uploaded_csv_file

    def test_model_regression(self, authenticated_client, trained_regression_model):
        # Test GET request
        response = authenticated_client.get(
            reverse('test_model', kwargs={'pk': trained_regression_model.pk, 'model_name': 'test_regressor'})
        )
        assert response.status_code == 200

        # Test POST request with valid data
        response = authenticated_client.post(
            reverse('test_model', kwargs={'pk': trained_regression_model.pk, 'model_name': 'test_regressor'}),
            {'feature1': '1', 'feature2': '2'}
        )
        assert response.status_code == 200
        assert 'prediction' in response.context
        assert isinstance(float(response.context['prediction']), float)
        assert 'class_probabilities' not in response.context  # Regression models don't have class probabilities

        # Test POST request with missing feature
        response = authenticated_client.post(
            reverse('test_model', kwargs={'pk': trained_regression_model.pk, 'model_name': 'test_regressor'}),
            {'feature1': '1'}
        )
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert any('Please enter a value for feature2' in str(message) for message in messages)

        # Test POST request with invalid data
        response = authenticated_client.post(
            reverse('test_model', kwargs={'pk': trained_regression_model.pk, 'model_name': 'test_regressor'}),
            {'feature1': 'invalid', 'feature2': '2'}
        )
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert any('Invalid value for feature1' in str(message) for message in messages)
