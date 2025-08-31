from django.urls import path
from .views import CSVUploadAPIView # Import your new APIView
from django.urls import path
from .views import CSVUploadAPIView
from . import views
from django.urls import include

urlpatterns = [
    path('api/upload-csv/', CSVUploadAPIView.as_view(), name='upload-csv'),
    path('simulate-error/', views.simulate_error, name='simulate_error'),
    path('', views.home, name='home'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('view/<int:pk>/', views.view_csv, name='view_csv'),
    path('delete/<int:pk>/', views.delete_csv, name='delete_csv'),
    path('clean/<int:pk>/', views.clean_data, name='clean_data'),
    path('column/<int:pk>/', views.column_operation, name='column_operation'),
    path('delete-row/<int:pk>/', views.delete_row, name='delete_row'),
    path('export/csv/<int:pk>/', views.export_csv, name='export_csv'),
    path('export/excel/<int:pk>/', views.export_excel, name='export_excel'),
    path('export/json/<int:pk>/', views.export_json, name='export_json'),
    path('csv/<int:pk>/ai-suggest/', views.ai_suggest_cleaning, name='ai_suggest_cleaning'),
    path('csv/<int:pk>/apply-ai/', views.apply_ai_suggestions, name='apply_ai_suggestions'),
    path('train-ml/<int:pk>/', views.train_ml_model, name='train_ml_model'),
    path('monitoring/<int:pk>/data/', views.get_monitoring_data, name='get_monitoring_data'),
    path('test-model/<int:pk>/<str:model_name>/', views.test_model, name='test_model'),
    path('monitoring/', views.monitoring_dashboard, name='monitoring_dashboard'),
    path('monitoring/metrics/', views.get_metrics, name='get_metrics'),
    path('mlflow/', views.mlflow_monitoring, name='mlflow_monitoring'),
    path('model/<int:pk>/<str:model_name>/', views.model_actions, name='model_actions'),
    path('model/<int:pk>/<str:model_name>/rename/', views.rename_model, name='rename_model'),
    path('model/<int:pk>/<str:model_name>/delete/', views.delete_model, name='delete_model'),
    path('api/upload/', CSVUploadAPIView.as_view(), name='api_upload_csv'),
    path('api/upload-csv/', CSVUploadAPIView.as_view(), name='upload-csv'),
    path('api/metrics/', views.get_metrics, name='get_metrics'),
    path("", include("django_prometheus.urls")),
   
   
]
