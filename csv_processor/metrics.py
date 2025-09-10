from prometheus_client import Counter


django_errors_total = Counter(
    'django_errors_total',
    'Total number of errors in Django app',
    
     
)

# عداد عام للتطبيق
APP_ERRORS_TOTAL = Counter(
    'app_errors_total',
    'Total number of application errors',
    ['type'], 
)