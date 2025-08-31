from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('csv_processor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='csvfile',
            name='ml_models',
            field=models.JSONField(default=dict),
        ),
    ]