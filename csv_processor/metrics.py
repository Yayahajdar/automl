from prometheus_client import Counter


APP_ERRORS_TOTAL = Counter(
    'app_errors_total',
    'Total number of application errors',
    ['type']
)