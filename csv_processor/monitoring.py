import psutil
from datetime import datetime, timedelta
from collections import deque
import os
from django.conf import settings

class SystemMonitor:
    @staticmethod
    def get_system_metrics():
        try:
            # Récupération des métriques système
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': {
                    'total': memory.total,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk_usage': {
                    'total': disk.total,
                    'used': disk.used,
                    'percent': disk.percent
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

class UsageStatistics:
    _request_times = deque(maxlen=100)  # Garde les 100 dernières requêtes
    _last_cleanup = datetime.now()
    
    @classmethod
    def record_request_time(cls, processing_time):
        cls._request_times.append({
            'time': processing_time,
            'timestamp': datetime.now()
        })
    
    @classmethod
    def cleanup_old_requests(cls):
        now = datetime.now()
        if now - cls._last_cleanup > timedelta(minutes=5):
            threshold = now - timedelta(minutes=5)
            cls._request_times = deque(
                [r for r in cls._request_times if r['timestamp'] > threshold],
                maxlen=100
            )
            cls._last_cleanup = now
    
    @classmethod
    def get_usage_stats(cls):
        cls.cleanup_old_requests()
        
        try:
            # Calcul des statistiques d'utilisation
            if cls._request_times:
                avg_time = sum(r['time'] for r in cls._request_times) / len(cls._request_times)
                requests_last_minute = sum(
                    1 for r in cls._request_times
                    if r['timestamp'] > datetime.now() - timedelta(minutes=1)
                )
            else:
                avg_time = 0
                requests_last_minute = 0
            
            # Calcul de la taille totale des fichiers
            total_size = 0
            csv_files_dir = os.path.join(settings.MEDIA_ROOT, 'csv_files')
            if os.path.exists(csv_files_dir):
                for file in os.listdir(csv_files_dir):
                    file_path = os.path.join(csv_files_dir, file)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
            
            return {
                'avg_processing_time': avg_time,
                'requests_per_minute': requests_last_minute,
                'total_files_size': total_size,
                'total_operations': len(cls._request_times),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }