from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import joblib
import os
from django.conf import settings

class CSVFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    title = models.CharField(max_length=255, verbose_name='Titre')
    file = models.FileField(upload_to='csv_files/', verbose_name='Fichier')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de téléchargement')
    last_viewed = models.DateTimeField(null=True, blank=True, verbose_name='Dernière consultation')
    view_count = models.IntegerField(default=0, verbose_name='Nombre de vues')
    operations_log = models.JSONField(default=list, blank=True, verbose_name='Journal des opérations')
    rows_count = models.IntegerField(default=0, verbose_name='Nombre de lignes')
    columns_count = models.IntegerField(default=0, verbose_name='Nombre de colonnes')
    ml_models = models.JSONField(default=dict)

    def save_ml_model(self, model_name, model, features, model_type, metrics=None):
        """Sauvegarde un modèle ML avec ses métadonnées."""
        if not hasattr(self, 'ml_models'):
            self.ml_models = {}

        model_dir = os.path.join(settings.MEDIA_ROOT, 'ml_models', str(self.pk))
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, f'{model_name}.joblib')
        ml_model = MLModel(model, features, model_type, metrics)
        ml_model.save(model_path)
        
        self.ml_models[model_name] = {
            'path': os.path.relpath(model_path, settings.MEDIA_ROOT),
            'features': features,
            'model_type': model_type,
            'metrics': metrics or {}
        }
        self.save()
        return True

    def load_ml_model(self, model_name):
        """Charge un modèle ML et ses métadonnées."""
        if not self.ml_models or model_name not in self.ml_models:
            return None, None

        model_info = self.ml_models[model_name]
        model_path = os.path.join(settings.MEDIA_ROOT, model_info['path'])
        ml_model = MLModel.load(model_path)
        
        if ml_model is None:
            return None, None
        
        return ml_model.model, model_info

    class Meta:
        verbose_name = 'Fichier CSV'
        verbose_name_plural = 'Fichiers CSV'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        """
        Sauvegarde le fichier CSV et définit le titre s'il n'est pas spécifié
        """
        if not self.title:
            self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Supprime le fichier physique lors de la suppression de l'enregistrement
        """
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def log_operation(self, operation_type, details=None):
        """
        Enregistre une nouvelle opération dans le journal des opérations
        """
        if not self.operations_log:
            self.operations_log = []
        
        self.operations_log.append({
            'operation': operation_type,
            'details': details,
            'timestamp': timezone.now().isoformat()
        })
        self.save()

    def record_view(self):
        """
        Enregistre une nouvelle consultation du fichier
        """
        self.last_viewed = timezone.now()
        self.view_count += 1
        self.save()

class Operation(models.Model):
    csv_file = models.ForeignKey(CSVFile, on_delete=models.CASCADE, related_name='operations')
    operation_type = models.CharField(max_length=50)
    details = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.operation_type} on {self.csv_file.title} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class MLModel:
    def __init__(self, model, features, model_type, metrics=None):
        self.model = model
        self.features = features
        self.model_type = model_type
        self.metrics = metrics or {}

    def save(self, path):
        joblib.dump({
            'model': self.model,
            'features': self.features,
            'model_type': self.model_type,
            'metrics': self.metrics
        }, path)

    @classmethod
    def load(cls, path):
        if not os.path.exists(path):
            return None
        data = joblib.load(path)
        return cls(
            model=data['model'],
            features=data['features'],
            model_type=data['model_type'],
            metrics=data.get('metrics', {})
        )

def save_ml_model(self, model_name, model, features, model_type, metrics=None):
    """Sauvegarde un modèle ML avec ses métadonnées."""
    if not hasattr(self, 'ml_models'):
        self.ml_models = {}

    model_dir = os.path.join(settings.MEDIA_ROOT, 'ml_models', str(self.pk))
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, f'{model_name}.joblib')
    ml_model = MLModel(model, features, model_type, metrics)
    ml_model.save(model_path)
    
    self.ml_models[model_name] = {
        'path': os.path.relpath(model_path, settings.MEDIA_ROOT),
        'features': features,
        'model_type': model_type,
        'metrics': metrics or {}
    }
    self.save()
    return True

def load_ml_model(self, model_name):
    """Charge un modèle ML et ses métadonnées."""
    if not self.ml_models or model_name not in self.ml_models:
        return None, None

    model_info = self.ml_models[model_name]
    model_path = os.path.join(settings.MEDIA_ROOT, model_info['path'])
    ml_model = MLModel.load(model_path)
    
    if ml_model is None:
        return None, None
    
    return ml_model.model, model_info



from django.db import models

class FakeErrorLog(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Error: {self.message[:50]}"
        
    

