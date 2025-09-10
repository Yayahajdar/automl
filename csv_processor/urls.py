from django.urls import path, include
from . import views
from .views import (
    # API Views
    CSVUploadAPIView,
    DeleteCSVAPIView,
    ExportCSVAPIView,
    TrainMLAPIView,
    TestModelAPIView,
    MetricsAPIView,
    CurrentUserAPIView,
    UserCreateAPIView,
    PrometheusMetricsAPIView,
)
from django.urls import path
from django.contrib import admin    
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse

def metrics(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)

# تنظيم المسارات حسب النوع (API vs Web UI)
urlpatterns = [
    # API Endpoints
    path('api/upload-csv/', CSVUploadAPIView.as_view(), name='upload-csv'),
    path('api/delete/<int:pk>/', DeleteCSVAPIView.as_view(), name='api_delete_csv'),
    path('api/export/csv/<int:pk>/', ExportCSVAPIView.as_view(), name='api_export_csv'),
    path('api/train-ml/<int:pk>/', TrainMLAPIView.as_view(), name='api_train_ml'),
    path('api/test-model/<int:pk>/<str:model_name>/', TestModelAPIView.as_view(), name='api_test_model'),
    path('api/metrics/', MetricsAPIView.as_view(), name='api_metrics'),
    path('api/user/', CurrentUserAPIView.as_view(), name='current_user'),
    path('api/user/register/', UserCreateAPIView.as_view(), name='user_register'),
    path('api/monitoring/metrics/', PrometheusMetricsAPIView.as_view(), name='api_prometheus_metrics'),
    
    # Web UI Endpoints
    path('', views.home, name='home'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('view/<int:pk>/', views.view_csv, name='view_csv'),
    path('delete/<int:pk>/', views.delete_csv, name='delete_csv'),
    path('clean/<int:pk>/', views.clean_data, name='clean_data'),
    path('column/<int:pk>/', views.column_operation, name='column_operation'),
    path('delete-row/<int:pk>/', views.delete_row, name='delete_row'),
    path('feedback/', views.feedback, name='feedback'),
    path('admin/', admin.site.urls),
    
    # Export Endpoints
    path('export/csv/<int:pk>/', views.export_csv, name='export_csv'),
    path('export/excel/<int:pk>/', views.export_excel, name='export_excel'),
    path('export/json/<int:pk>/', views.export_json, name='export_json'),
    
    # AI & ML Endpoints
    path('csv/<int:pk>/ai-suggest/', views.ai_suggest_cleaning, name='ai_suggest_cleaning'),
    path('csv/<int:pk>/apply-ai/', views.apply_ai_suggestions, name='apply_ai_suggestions'),
    path('train-ml/<int:pk>/', views.train_ml_model, name='train_ml_model'),
    path('test-model/<int:pk>/<str:model_name>/', views.test_model, name='test_model'),
    path('model/<int:pk>/<str:model_name>/', views.model_actions, name='model_actions'),
    path('model/<int:pk>/<str:model_name>/rename/', views.rename_model, name='rename_model'),
    path('model/<int:pk>/<str:model_name>/delete/', views.delete_model, name='delete_model'),
    
    # Monitoring Endpoints
    path('monitoring/', views.monitoring_dashboard, name='monitoring_dashboard'),
    path('monitoring/<int:pk>/data/', views.get_monitoring_data, name='get_monitoring_data'),
    path('monitoring/metrics/', views.get_metrics, name='get_metrics'),
    path('mlflow/', views.mlflow_monitoring, name='mlflow_monitoring'),
    path('metrics/', metrics, name='metrics'),
    
    # Utility Endpoints
    path('simulate-error/', views.simulate_error, name='simulate_error'),
    
    # External Endpoints
    path("", include("django_prometheus.urls")),
]

