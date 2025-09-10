from .metrics import django_errors_total

django_errors_total.labels(error_type='test').inc()
raise ValueError("Test error for Prometheus")