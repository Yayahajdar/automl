from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
import pandas as pd
import numpy as np
import json
import os
import time
import plotly.graph_objects as go
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
from .monitoring import SystemMonitor, UsageStatistics
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CSVFile
from .forms import CSVUploadForm, DataCleaningForm, ColumnOperationForm
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, r2_score, mean_squared_error, classification_report
from sklearn.preprocessing import LabelEncoder
from .mlflow_utils import get_mlflow_ui_url
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64
import joblib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CSVUploadSerializer, TrainMLRequestSerializer, TestModelRequestSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import TrainMLRequestSerializer, TestModelRequestSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, UserCreateSerializer
from prometheus_client import generate_latest
from .metrics import APP_ERRORS_TOTAL


@login_required
def train_model(request, pk):
    """Train a machine learning model on the dataset."""
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    try:
        # Load the dataset
        delimiter = detect_delimiter(csv_file.file.path)
        df = pd.read_csv(csv_file.file.path, delimiter=delimiter)

        # Prepare the data
        X = df.select_dtypes(include=['int64', 'float64'])
        if X.empty:
            messages.error(request, 'No numeric features found in the dataset.')
            return redirect('view_csv', pk=pk)

        y = df.iloc[:, -1]  # Assuming the target is the last column
        le = LabelEncoder()
        original_classes = None
        if not pd.api.types.is_numeric_dtype(y):
            original_classes = list(y.unique())
            y = le.fit_transform(y)

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Determine the problem type and train appropriate models
        models = {}
        if len(np.unique(y)) <= 10:  # Classification
            models = {
                'logistic_regression': LogisticRegression(random_state=42),
                'decision_tree': DecisionTreeClassifier(random_state=42),
                'random_forest': RandomForestClassifier(random_state=42)
            }
        else:  # Regression
            models = {
                'linear_regression': LinearRegression(),
                'decision_tree': DecisionTreeRegressor(random_state=42),
                'random_forest': RandomForestRegressor(random_state=42)
            }

        # Train and evaluate models
        results = {}
        for name, model in models.items():
            # Train the model
            model.fit(X_train, y_train)

            # Make predictions
            y_pred = model.predict(X_test)

            # Calculate metrics
            if isinstance(model, (LogisticRegression, DecisionTreeClassifier, RandomForestClassifier)):
                accuracy = accuracy_score(y_test, y_pred)
                report = classification_report(y_test, y_pred)
                results[name] = {
                    'accuracy': accuracy,
                    'classification_report': report,
                    'original_classes': original_classes
                }
            else:
                r2 = r2_score(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                results[name] = {
                    'r2_score': r2,
                    'mean_squared_error': mse
                }

            # Save the model using MLModel class
            metrics = results[name]
            csv_file.save_ml_model(name, model, list(X.columns), 'classification' if len(np.unique(y)) <= 10 else 'regression', metrics)

        # Store results in session for display
        request.session[f'model_training_results_{pk}'] = results
        messages.success(request, 'Model training completed successfully!')

    except Exception as e:
        messages.error(request, f'Error training models: {str(e)}')

    return redirect('view_csv', pk=pk)

@login_required
def test_model(request, pk, model_name):
    """Test a trained machine learning model with manually entered values."""
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    try:
        # Load the trained model using MLModel class
        model, model_info = csv_file.load_ml_model(model_name)
        if model is None:
            messages.error(request, f'Model "{model_name}" not found. Please train the model first.')
            return redirect('view_csv', pk=pk)

        # Check if model_info has the required keys
        if 'features' not in model_info:
            messages.error(request, f'Model "{model_name}" is missing feature information. Please retrain the model.')
            return redirect('view_csv', pk=pk)

        if 'model_type' not in model_info:
            messages.error(request, f'Model "{model_name}" is missing type information. Please retrain the model.')
            return redirect('view_csv', pk=pk)

        # Prepare context with model information
        context = {
            'features': model_info['features'],
            'pk': pk,
            'model_name': model_name,
            'model_type': model_info['model_type'],
            'metrics': model_info.get('metrics', {})
        }

        if request.method == 'POST':
            # Get feature values from the form
            feature_values = {}
            has_errors = False

            for feature in model_info['features']:
                value = request.POST.get(feature, '').strip()
                if not value:
                    messages.error(request, f'Please enter a value for {feature}.')
                    has_errors = True
                    continue

                # Ne pas convertir en float pour les variables catégorielles
                if feature in model_info.get('metrics', {}).get('label_encoders', {}):
                    feature_values[feature] = value  # Garder comme chaîne de caractères
                else:
                    try:
                        feature_values[feature] = float(value)
                    except ValueError:
                        messages.error(request, f'Invalid value for {feature}. Please enter a valid number.')
                        has_errors = True

            if has_errors:
                return render(request, 'csv_processor/test_model.html', context)

            try:
                # Create input array for prediction
                X_test = pd.DataFrame([feature_values])

                # Ensure all required features are present
                missing_features = set(model_info['features']) - set(X_test.columns)
                if missing_features:
                    messages.error(request, f'Missing features: {", ".join(missing_features)}')
                    return render(request, 'csv_processor/test_model.html', context)

                # Reorder columns to match training data
                try:
                    X_test = X_test[model_info['features']]
                except KeyError as e:
                    messages.error(request, f'Error accessing feature: {str(e)}. Please ensure all features are provided.')
                    return render(request, 'csv_processor/test_model.html', context)
                
                # Appliquer les encodeurs aux variables catégorielles
                label_encoders = model_info.get('metrics', {}).get('label_encoders', {})
                if label_encoders:
                    for col in X_test.columns:
                        if col in label_encoders:
                            try:
                                # Reconstruire l'encodeur à partir du dictionnaire
                                from sklearn.preprocessing import LabelEncoder
                                import numpy as np
                                le = LabelEncoder()
                                le.classes_ = np.array(label_encoders[col]['classes_'])
                                X_test[col] = le.transform(X_test[col].astype(str))
                            except Exception as e:
                                messages.warning(request, f"Erreur lors de l'encodage de {col}: {str(e)}. Utilisation de la valeur telle quelle.")

                # Make prediction
                try:
                    prediction = model.predict(X_test)
                except Exception as e:
                    messages.error(request, f'Error making prediction: {str(e)}. The model might be corrupted or incompatible.')
                    return render(request, 'csv_processor/test_model.html', context)

                # Normalize model_type to handle legacy models where target column name was used as model_type
                normalized_model_type = model_info['model_type'].lower()
                if normalized_model_type not in ['classification', 'regression']:
                    # Check if the model is a classifier or regressor based on its class
                    if isinstance(model, (LogisticRegression, DecisionTreeClassifier, RandomForestClassifier)):
                        normalized_model_type = 'classification'
                    elif isinstance(model, (LinearRegression, DecisionTreeRegressor, RandomForestRegressor)):
                        normalized_model_type = 'regression'
                    else:
                        # Try to infer from the number of unique values in the prediction
                        if hasattr(model, 'classes_') and len(model.classes_) <= 10:
                            normalized_model_type = 'classification'
                        else:
                            # Default to regression for continuous values
                            normalized_model_type = 'regression'

                    # Log that we had to normalize the model type
                    messages.info(request, f'Model type "{model_info["model_type"]}" was normalized to "{normalized_model_type}"')

                # Format prediction message based on normalized model type
                if normalized_model_type == 'classification':
                    # For classification models
                    # Get prediction probabilities if the model supports it
                    try:
                        probabilities = model.predict_proba(X_test)[0]
                        # Get class labels if available
                        original_classes = model_info['metrics'].get('original_classes')
                        if original_classes:
                            # Create a list of class probabilities with original class labels
                            class_probs = [{'class': str(original_classes[i]), 'probability': probabilities[i]}
                                          for i in range(len(probabilities))]
                        else:
                            # Fallback to numeric classes if original labels not available
                            classes = model.classes_
                            class_probs = [{'class': str(classes[i]), 'probability': probabilities[i]}
                                          for i in range(len(probabilities))]
                        context['class_probabilities'] = class_probs
                    except (AttributeError, NotImplementedError):
                        # Some models might not support probability prediction
                        pass

                    # Convert numeric prediction to original class label if available
                    try:
                        original_classes = model_info['metrics'].get('original_classes')

                        # Debug information
                        if original_classes:
                            messages.info(request, f'Original classes found: {original_classes}')
                        else:
                            messages.info(request, 'No original classes found in model metrics')

                        if hasattr(model, 'classes_'):
                            messages.info(request, f'Model classes: {model.classes_}')
                            messages.info(request, f'Raw prediction: {prediction[0]}')

                        # Try to map the prediction to a class label
                        if original_classes and isinstance(prediction[0], (int, np.integer)) and prediction[0] < len(original_classes):
                            # If we have original classes and the prediction is an index
                            prediction_message = str(original_classes[prediction[0]])
                        elif hasattr(model, 'classes_'):
                            # If the model has classes_ attribute
                            if isinstance(prediction[0], (int, np.integer)):
                                # If prediction is an integer, use it as an index
                                if prediction[0] < len(model.classes_):
                                    prediction_message = str(model.classes_[prediction[0]])
                                else:
                                    prediction_message = str(prediction[0])
                                    messages.warning(request, f'Prediction index {prediction[0]} out of range for model classes')
                            else:
                                # If prediction is not an integer, find it in the classes array
                                try:
                                    pred_idx = np.where(model.classes_ == prediction[0])[0][0]
                                    prediction_message = str(model.classes_[pred_idx])
                                except (IndexError, ValueError):
                                    # If we can't find the prediction in the classes array
                                    prediction_message = str(prediction[0])
                                    messages.warning(request, f'Could not find prediction {prediction[0]} in model classes')
                        else:
                            # If we don't have original classes or model.classes_
                            prediction_message = str(prediction[0])
                            messages.warning(request, 'No class mapping available')
                    except (IndexError, TypeError) as e:
                        # Fallback if there's an issue with class mapping
                        prediction_message = str(prediction[0])
                        messages.warning(request, f'Warning: Could not map prediction to class label: {str(e)}')

                elif normalized_model_type == 'regression':
                    # For regression models - format as a floating point number
                    try:
                        # Try to convert to float and format with 4 decimal places
                        prediction_value = float(prediction[0])
                        prediction_message = f'{prediction_value:.4f}'
                    except (ValueError, TypeError):
                        # Fallback if conversion fails
                        prediction_message = str(prediction[0])
                else:
                    # This should never happen due to normalization above
                    prediction_message = str(prediction[0])
                    messages.warning(request, f'Unknown model type: {model_info["model_type"]}')

                context['prediction'] = prediction_message
                context['input_values'] = feature_values  # Keep form values
                context['model_type'] = normalized_model_type  # Use the normalized model type
                messages.success(request, 'Prediction generated successfully!')

            except Exception as e:
                messages.error(request, f'Error making prediction: {str(e)}')

            return render(request, 'csv_processor/test_model.html', context)

        # GET request - show the form
        return render(request, 'csv_processor/test_model.html', context)

    except Exception as e:
        messages.error(request, f'Error testing model: {str(e)}')
        return redirect('view_csv', pk=pk)

def detect_delimiter(file_path):
    possible_delimiters = [',', ';', '\t', '|', '_', '-']
    with open(file_path, 'r', encoding='utf-8') as file:
        first_line = file.readline()
        delimiter_counts = {delimiter: first_line.count(delimiter) for delimiter in possible_delimiters}
        max_delimiter = max(delimiter_counts.items(), key=lambda x: x[1])
        return max_delimiter[0] if max_delimiter[1] > 0 else ','

def ensure_media_dirs():
    media_root = settings.MEDIA_ROOT
    os.makedirs(media_root, exist_ok=True)
    csv_dir = os.path.join(media_root, 'csv_files')
    export_dir = os.path.join(media_root, 'exports')
    temp_dir = os.path.join(media_root, 'temp')
    for directory in [csv_dir, export_dir, temp_dir]:
        os.makedirs(directory, exist_ok=True)
    return csv_dir, export_dir, temp_dir

def generate_ai_suggestions(df):
    """Analyze DataFrame and generate cleaning suggestions."""
    suggestions = []

    # Check for missing values
    for column in df.columns:
        null_count = df[column].isnull().sum()
        if null_count > 0:
            if pd.api.types.is_numeric_dtype(df[column]):
                suggestions.append({
                    'column': column,
                    'action': 'fill_mean',
                    'reason': f'{null_count} valeurs manquantes dans la colonne numérique "{column}".'
                })
            else:
                suggestions.append({
                    'column': column,
                    'action': 'fill_mode',
                    'reason': f'{null_count} valeurs manquantes dans la colonne catégorielle "{column}".'
                })

    # Check for duplicates
    duplicate_rows = len(df) - len(df.drop_duplicates())
    if duplicate_rows > 0:
        suggestions.append({
            'action': 'remove_duplicates',
            'reason': f'{duplicate_rows} lignes dupliquées détectées.'
        })

    # Check for outliers
    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            outlier_count = ((df[column] < (Q1 - 1.5 * IQR)) | (df[column] > (Q3 + 1.5 * IQR))).sum()
            if outlier_count > 0:
                suggestions.append({
                    'column': column,
                    'action': 'remove_outliers',
                    'reason': f'{outlier_count} valeurs aberrantes dans la colonne "{column}".'
                })
    return suggestions

@login_required
@require_POST
def ai_suggest_cleaning(request, pk):
    """Generate AI suggestions and store them in the session."""
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    try:
        delimiter = detect_delimiter(csv_file.file.path)
        df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        suggestions = generate_ai_suggestions(df)
        request.session[f'ai_suggestions_{pk}'] = suggestions
        messages.success(request, f'{len(suggestions)} suggestions générées.')
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'analyse : {str(e)}')
    return redirect('view_csv', pk=pk)

@login_required
@require_POST
def apply_ai_suggestions(request, pk):
    """Apply all AI-generated suggestions."""
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    suggestions = request.session.get(f'ai_suggestions_{pk}', [])

    if not suggestions:
        messages.error(request, "Aucune suggestion à appliquer.")
        return redirect('view_csv', pk=pk)

    try:
        delimiter = detect_delimiter(csv_file.file.path)
        df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        operations_log = []

        for suggestion in suggestions:
            action = suggestion['action']
            column = suggestion.get('column')

            if action == 'fill_mean':
                mean_val = df[column].mean()
                df[column].fillna(mean_val, inplace=True)
                operations_log.append(f"Remplissage des valeurs manquantes avec la moyenne ({mean_val:.2f}) dans {column}.")

            elif action == 'fill_mode':
                mode_val = df[column].mode()[0]
                df[column].fillna(mode_val, inplace=True)
                operations_log.append(f"Remplissage des valeurs manquantes avec le mode ({mode_val}) dans {column}.")

            elif action == 'remove_duplicates':
                initial_rows = len(df)
                df = df.drop_duplicates()
                removed = initial_rows - len(df)
                operations_log.append(f"Suppression de {removed} lignes dupliquées.")

            elif action == 'remove_outliers':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                initial_rows = len(df)
                df = df[~((df[column] < (Q1 - 1.5 * IQR)) | (df[column] > (Q3 + 1.5 * IQR)))]
                removed = initial_rows - len(df)
                operations_log.append(f"Suppression de {removed} valeurs aberrantes dans {column}.")

        # Save cleaned file
        base_name = os.path.splitext(csv_file.title)[0]
        new_filename = f'ai_clean_{base_name}_{datetime.now().strftime("%Y%m%d%H%M")}.csv'
        new_path = os.path.join(settings.MEDIA_ROOT, 'csv_files', new_filename)
        df.to_csv(new_path, index=False, sep=detect_delimiter(csv_file.file.path))

        # Create new CSVFile record
        new_csv = CSVFile.objects.create(
            user=request.user,
            title=new_filename,
            file=f'csv_files/{new_filename}',
            rows_count=len(df),
            columns_count=len(df.columns)
        )
        new_csv.log_operation('ai_clean', ' | '.join(operations_log))
        messages.success(request, "Suggestions appliquées avec succès!")
        return redirect('view_csv', pk=new_csv.pk)

    except Exception as e:
        messages.error(request, f'Erreur lors de l\'application : {str(e)}')
        return redirect('view_csv', pk=pk)

@login_required
@require_http_methods(['GET'])
def get_monitoring_data(request, pk):
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)

    # Get system metrics
    system_metrics = SystemMonitor.get_system_metrics()

    # Get usage statistics
    usage_stats = UsageStatistics.get_usage_stats()

    # Combine metrics
    monitoring_data = {
        'system_metrics': system_metrics,
        'usage_stats': usage_stats,
        'file_info': {
            'title': csv_file.title,
            'rows': csv_file.rows_count,
            'columns': csv_file.columns_count,
            'last_viewed': csv_file.last_viewed.isoformat() if csv_file.last_viewed else None,
            'view_count': csv_file.view_count
        }
    }

    return JsonResponse(monitoring_data)

@login_required
def home(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['file']
            timestamp = datetime.now().strftime('%Y-%m-%d_%Hh%M')
            safe_title = "".join(c for c in uploaded_file.name if c.isalnum() or c in (' ', '_', '-'))
            filename = f'upload_{safe_title}_{timestamp}.csv'
            filepath = os.path.join(settings.MEDIA_ROOT, 'csv_files', filename)
            with open(filepath, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            csv_file = CSVFile.objects.create(
                user=request.user,
                title=uploaded_file.name,
                file=f'csv_files/{filename}'
            )
            messages.success(request, 'Le fichier a été téléchargé avec succès !')
            return redirect('view_csv', pk=csv_file.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors du téléchargement du fichier : {str(e)}')
    csv_files = CSVFile.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'csv_processor/home.html', {
        'csv_files': csv_files,
        'form': CSVUploadForm()
    })

@login_required
def upload_csv(request):
    if request.method == 'POST':
        try:
            csv_file = request.FILES.get('csv_file')
            if not csv_file or not csv_file.name.endswith('.csv'):
                messages.error(request, 'Aucun fichier n\'a été sélectionné ou ce n\'est pas un fichier CSV')
                return redirect('home')
            ensure_media_dirs()
            file_path = os.path.join(settings.MEDIA_ROOT, 'csv_files', csv_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in csv_file.chunks():
                    destination.write(chunk)
            delimiter = detect_delimiter(file_path)
            df = pd.read_csv(file_path, delimiter=delimiter)
            relative_path = os.path.join('csv_files', csv_file.name)
            csv_record = CSVFile.objects.create(
                user=request.user,
                title=csv_file.name,
                file=relative_path,
                rows_count=len(df),
                columns_count=len(df.columns)
            )
            messages.success(request, 'Fichier CSV téléchargé avec succès')
            return redirect('view_csv', pk=csv_record.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors du téléchargement : {str(e)}')
    return redirect('home')

@login_required
def view_csv(request, pk):
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    ai_suggestions = request.session.get(f'ai_suggestions_{pk}', [])
    try:
        delimiter = detect_delimiter(csv_file.file.path)
        df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        cleaning_form = DataCleaningForm(list(df.columns))
        column_form = ColumnOperationForm(list(df.columns))
        summary = {
            'rows': len(df),
            'columns': len(df.columns),
            'null_cells': df.isna().sum().sum(),
            'duplicate_rows': len(df) - len(df.drop_duplicates()),
            'memory_usage': f'{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB'
        }
        column_stats = {}
        for column in df.columns:
            stats = {
                'name': column,
                'type': str(df[column].dtype),
                'null_count': df[column].isnull().sum(),
                'unique_count': df[column].nunique()
            }
            if pd.api.types.is_numeric_dtype(df[column]):
                stats.update({
                    'min': f"{df[column].min():.2f}",
                    'max': f"{df[column].max():.2f}",
                    'mean': f"{df[column].mean():.2f}",
                    'median': f"{df[column].median():.2f}"
                })
            column_stats[column] = stats
        plots = []
        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=df[column].dropna(), name=column))
                fig.update_layout(
                    title=f'Distribution de {column}',
                    xaxis_title=column,
                    yaxis_title='Fréquence',
                    showlegend=False,
                    template='plotly_white',
                    height=400,
                    margin=dict(l=50, r=50, t=50, b=50)
                )
                plots.append(fig.to_json())
            elif df[column].nunique() <= 10:
                value_counts = df[column].value_counts()
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=value_counts.index.astype(str).tolist(),
                    y=value_counts.values.tolist(),
                    name=column
                ))
                fig.update_layout(
                    title=f'Distribution de {column}',
                    xaxis_title=column,
                    yaxis_title='Nombre',
                    showlegend=False,
                    template='plotly_white',
                    height=400,
                    margin=dict(l=50, r=50, t=50, b=50)
                )
                plots.append(fig.to_json())
        data = df.replace({np.nan: None}).values.tolist()
        page = request.GET.get('page', 1)
        paginator = Paginator(data, 50)
        try:
            current_page = paginator.page(page)
        except PageNotAnInteger:
            current_page = paginator.page(1)
        except EmptyPage:
            current_page = paginator.page(paginator.num_pages)
        csv_file.record_view()
        # Get system monitoring data
        system_metrics = SystemMonitor.get_system_metrics()
        usage_stats = UsageStatistics.get_usage_stats()

        # Prepare trained models list for display
        trained_models = []

        # Debug: Print ml_models to console
        print(f"DEBUG - CSV File ID: {csv_file.pk}")
        print(f"DEBUG - ML Models: {csv_file.ml_models}")

        if hasattr(csv_file, 'ml_models') and csv_file.ml_models:
            print(f"DEBUG - Has ml_models attribute and it's not empty")
            for model_name, model_info in csv_file.ml_models.items():
                print(f"DEBUG - Processing model: {model_name}")
                # Get score based on model type
                score = 0
                if model_info.get('metrics'):
                    if model_info.get('model_type') == 'classification':
                        score = model_info['metrics'].get('cv_scores_mean', 0)
                    else:  # regression
                        score = model_info['metrics'].get('cv_scores_mean', 0)

                # Get creation time from metrics if available, otherwise use current time
                created_at = model_info.get('metrics', {}).get('created_at', timezone.now().isoformat())

                model_entry = {
                    'name': model_name,
                    'type': model_info.get('model_type', 'unknown'),
                    'score': score,
                    'created_at': created_at,  # Use stored creation time
                    'id': model_name  # Use model name as ID
                }

                trained_models.append(model_entry)
                print(f"DEBUG - Added model to trained_models: {model_entry}")

        print(f"DEBUG - Final trained_models list: {trained_models}")

        context = {
            'csv_file': csv_file,
            'ai_suggestions': ai_suggestions,
            'columns': df.columns.tolist(),
            'cleaning_form': cleaning_form,
            'column_form': column_form,
            'summary': summary,
            'column_stats': column_stats,
            'plots': plots,
            'pagination': {
                'page': current_page,
                'total_pages': paginator.num_pages,
                'total_rows': len(df),
                'start_index': current_page.start_index(),
                'end_index': current_page.end_index()
            },
            'operations_log': csv_file.operations_log,
            # Add monitoring data to context
            'cpu_usage': system_metrics['cpu_usage'],
            'memory_usage': system_metrics['memory_usage'],
            'disk_usage': system_metrics['disk_usage'],
            'avg_processing_time': usage_stats['avg_processing_time'],
            'requests_per_minute': usage_stats['requests_per_minute'],
            'total_files_size': usage_stats['total_files_size'],
            'total_operations': usage_stats['total_operations'],
            # Add trained models to context
            'trained_models': trained_models
        }
        return render(request, 'csv_processor/view.html', context)
    except Exception as e:
        messages.error(request, f'Erreur lors de la lecture du fichier : {str(e)}')
        return redirect('home')

@login_required
def delete_csv(request, pk):
    try:
        csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
        csv_file.file.delete()
        csv_file.delete()
        messages.success(request, 'Le fichier a été supprimé avec succès')
    except Exception as e:
        messages.error(request, f'Erreur lors de la suppression du fichier : {str(e)}')
    return redirect('home')

@login_required
def clean_data(request, pk):
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    if request.method == 'POST':
        delimiter = detect_delimiter(csv_file.file.path)
        df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        form = DataCleaningForm(list(df.columns), request.POST)
        if form.is_valid():
            try:
                column = form.cleaned_data['column']
                action = form.cleaned_data['action']
                if action == 'remove_nulls':
                    original_count = len(df)
                    df = df.dropna(subset=[column])
                    removed_count = original_count - len(df)
                    operation_details = f'{removed_count} lignes contenant des valeurs vides ont été supprimées de la colonne {column}'
                elif action == 'fill_mean' and pd.api.types.is_numeric_dtype(df[column]):
                    mean_value = df[column].mean()
                    df[column] = df[column].fillna(mean_value)
                    operation_details = f'Les valeurs vides ont été remplies avec la moyenne ({mean_value:.2f}) dans la colonne {column}'
                elif action == 'fill_median' and pd.api.types.is_numeric_dtype(df[column]):
                    median_value = df[column].median()
                    df[column] = df[column].fillna(median_value)
                    operation_details = f'Les valeurs vides ont été remplies avec la médiane ({median_value:.2f}) dans la colonne {column}'
                elif action == 'fill_mode':
                    mode_value = df[column].mode()[0]
                    df[column] = df[column].fillna(mode_value)
                    operation_details = f'Les valeurs vides ont été remplies avec la valeur la plus fréquente ({mode_value}) dans la colonne {column}'
                elif action == 'remove_duplicates':
                    original_count = len(df)
                    df = df.drop_duplicates(subset=[column])
                    removed_count = original_count - len(df)
                    operation_details = f'{removed_count} lignes en double ont été supprimées dans la colonne {column}'
                elif action == 'remove_outliers' and pd.api.types.is_numeric_dtype(df[column]):
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    original_count = len(df)
                    df = df[~((df[column] < (Q1 - 1.5 * IQR)) | (df[column] > (Q3 + 1.5 * IQR)))]
                    removed_count = original_count - len(df)
                    operation_details = f'{removed_count} valeurs aberrantes ont été supprimées de la colonne {column}'
                else:
                    messages.error(request, 'Action invalide ou colonne non numérique')
                    return redirect('view_csv', pk=pk)
                ensure_media_dirs()
                base_name = os.path.splitext(csv_file.title)[0]
                new_filename = f'cleaned_{base_name}.csv'
                new_file_path = os.path.join(settings.MEDIA_ROOT, 'csv_files', new_filename)
                df.to_csv(new_file_path, index=False, sep=delimiter)
                relative_path = os.path.join('csv_files', new_filename)
                new_csv = CSVFile.objects.create(
                    user=request.user,
                    title=new_filename,
                    file=relative_path,
                    rows_count=len(df),
                    columns_count=len(df.columns)
                )
                new_csv.log_operation('clean_data', operation_details)
                messages.success(request, operation_details)
                return redirect('view_csv', pk=new_csv.pk)
            except Exception as e:
                messages.error(request, f'Erreur lors du nettoyage des données : {str(e)}')
                return redirect('view_csv', pk=pk)
    return redirect('view_csv', pk=pk)

@login_required
def column_operation(request, pk):
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    if request.method == 'POST':
        delimiter = detect_delimiter(csv_file.file.path)
        df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        form = ColumnOperationForm(list(df.columns), request.POST)
        if form.is_valid():
            try:
                column = form.cleaned_data['column']
                operation = form.cleaned_data['operation']
                new_name = form.cleaned_data.get('new_name')
                old_value = form.cleaned_data.get('old_value')
                new_value = form.cleaned_data.get('new_value')
                if operation == 'rename':
                    if new_name and new_name not in df.columns:
                        df = df.rename(columns={column: new_name})
                        operation_details = f'La colonne {column} a été renommée en {new_name}'
                    else:
                        messages.error(request, 'Nouveau nom de colonne invalide')
                        return redirect('view_csv', pk=pk)
                elif operation == 'delete':
                    if len(df.columns) > 1:
                        df = df.drop(columns=[column])
                        operation_details = f'La colonne {column} a été supprimée'
                    else:
                        messages.error(request, 'Impossible de supprimer la seule colonne du fichier')
                        return redirect('view_csv', pk=pk)
                elif operation == 'convert_numeric':
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                    nan_count = df[column].isna().sum() - df[column].isna().sum().shift(1, fill_value=0)
                    operation_details = f'La colonne {column} a été convertie en nombres ({nan_count} valeurs non convertibles)'
                elif operation == 'convert_datetime':
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                    nan_count = df[column].isna().sum() - df[column].isna().sum().shift(1, fill_value=0)
                    operation_details = f'La colonne {column} a été convertie en dates ({nan_count} valeurs non convertibles)'
                elif operation == 'replace_values':
                    if old_value is not None and new_value is not None:
                        mask = df[column].astype(str).str.replace(',', '.') == str(old_value)
                        count_before = mask.sum()
                        df.loc[mask, column] = new_value
                        operation_details = f'{count_before} valeurs ont été changées de {old_value} à {new_value} dans la colonne {column}'
                    else:
                        messages.error(request, 'Vous devez spécifier la valeur ancienne et la valeur nouvelle')
                        return redirect('view_csv', pk=pk)
                ensure_media_dirs()
                base_name = os.path.splitext(csv_file.title)[0]
                new_filename = f'modified_{base_name}.csv'
                new_file_path = os.path.join(settings.MEDIA_ROOT, 'csv_files', new_filename)
                df.to_csv(new_file_path, index=False, sep=delimiter)
                relative_path = os.path.join('csv_files', new_filename)
                new_csv = CSVFile.objects.create(
                    user=request.user,
                    title=new_filename,
                    file=relative_path,
                    rows_count=len(df),
                    columns_count=len(df.columns)
                )
                new_csv.log_operation('column_operation', operation_details)
                messages.success(request, operation_details)
                return redirect('view_csv', pk=new_csv.pk)
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'opération sur la colonne : {str(e)}')
                return redirect('view_csv', pk=pk)
    return redirect('view_csv', pk=pk)

@login_required
def delete_row(request, pk):
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    if request.method == 'POST':
        try:
            row_number = int(request.POST.get('row_number', 0))
            delimiter = detect_delimiter(csv_file.file.path)
            df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
            if row_number < 0 or row_number >= len(df):
                messages.error(request, f'Numéro de ligne invalide. Doit être entre 0 et {len(df)-1}')
                return redirect('view_csv', pk=pk)
            df = df.drop(index=row_number)
            ensure_media_dirs()
            base_name = os.path.splitext(csv_file.title)[0]
            new_filename = f'modified_{base_name}.csv'
            new_file_path = os.path.join(settings.MEDIA_ROOT, 'csv_files', new_filename)
            df.to_csv(new_file_path, index=False, sep=delimiter)
            relative_path = os.path.join('csv_files', new_filename)
            new_csv = CSVFile.objects.create(
                user=request.user,
                title=new_filename,
                file=relative_path,
                rows_count=len(df),
                columns_count=len(df.columns)
            )
            operation_details = f'La ligne {row_number} a été supprimée'
            new_csv.log_operation('delete_row', operation_details)
            messages.success(request, operation_details)
            return redirect('view_csv', pk=new_csv.pk)
        except ValueError:
            messages.error(request, 'Veuillez entrer un numéro de ligne valide')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression de la ligne : {str(e)}')
    return redirect('view_csv', pk=pk)

@login_required
def export_csv(request, pk):
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    try:
        ensure_media_dirs()
        timestamp = datetime.now().strftime('%Y-%m-%d_%Hh%M')
        safe_title = "".join(c for c in csv_file.title if c.isalnum() or c in (' ', '_', '-'))
        export_filename = f'export_{safe_title}_{timestamp}.csv'
        export_path = os.path.join(settings.MEDIA_ROOT, 'exports', export_filename)
        delimiter = detect_delimiter(csv_file.file.path)
        df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        df.to_csv(export_path, index=False)
        with open(export_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{export_filename}"'
        os.remove(export_path)
        return response
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'exportation du fichier : {str(e)}')
        return redirect('view_csv', pk=pk)

@login_required
def export_excel(request, pk):
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    try:
        ensure_media_dirs()
        timestamp = datetime.now().strftime('%Y-%m-%d_%Hh%M')
        safe_title = "".join(c for c in csv_file.title if c.isalnum() or c in (' ', '_', '-'))
        export_filename = f'export_{safe_title}_{timestamp}.xlsx'
        export_path = os.path.join(settings.MEDIA_ROOT, 'exports', export_filename)
        delimiter = detect_delimiter(csv_file.file.path)
        df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
        with open(export_path, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{export_filename}"'
        os.remove(export_path)
        return response
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'exportation du fichier : {str(e)}')
        return redirect('view_csv', pk=pk)

@login_required
def export_json(request, pk):
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    try:
        ensure_media_dirs()
        timestamp = datetime.now().strftime('%Y-%m-%d_%Hh%M')
        safe_title = "".join(c for c in csv_file.title if c.isalnum() or c in (' ', '_', '-'))
        export_filename = f'export_{safe_title}_{timestamp}.json'
        export_path = os.path.join(settings.MEDIA_ROOT, 'exports', export_filename)
        delimiter = detect_delimiter(csv_file.file.path)
        df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        df.to_json(export_path, orient='records', force_ascii=False)
        with open(export_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        os.remove(export_path)
        response = HttpResponse(file_content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{export_filename}"'
        return response
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'exportation du fichier : {str(e)}')
        return redirect('view_csv', pk=pk)

@login_required
def train_ml_model(request, pk):
    """Train a machine learning model on the selected features with improved error handling and data validation."""
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)

    try:
        # Read the CSV file with error handling
        try:
            delimiter = detect_delimiter(csv_file.file.path)
            df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        except Exception as e:
            messages.error(request, f'Erreur lors de la lecture du fichier CSV : {str(e)}')
            return redirect('view_csv', pk=pk)

        if request.method == 'POST':
            # Validate input parameters
            features = request.POST.getlist('features')
            target = request.POST.get('target')
            model_type = request.POST.get('model_type')
            model_name = request.POST.get('model_name')

            # Validation des paramètres
            if not all([features, target, model_type, model_name]):
                messages.error(request, 'Tous les champs sont requis (caractéristiques, cible, type de modèle et nom du modèle).')
                return redirect('view_csv', pk=pk)

            if target in features:
                messages.error(request, 'La variable cible ne peut pas être incluse dans les caractéristiques.')
                return redirect('view_csv', pk=pk)

            # Vérifier la qualité des données
            if df[features + [target]].isnull().any().any():
                messages.warning(request, 'Attention : Les données contiennent des valeurs manquantes qui seront traitées automatiquement.')
                # Remplir uniquement les colonnes numériques par leur moyenne pour éviter l’erreur int+str
                df = df.fillna(df.mean(numeric_only=True))
                # Remplir les colonnes catégorielles par la valeur la plus fréquente (mode)
                for col in df.select_dtypes(include=['object']).columns:
                    if df[col].isnull().any():
                        mode = df[col].mode()
                        df[col] = df[col].fillna(mode.iloc[0] if not mode.empty else '')

            # Prepare the data
            try:
                X = df[features]
                y = df[target]
            except KeyError as e:
                messages.error(request, f'Colonne non trouvée dans le dataset : {str(e)}')
                return redirect('view_csv', pk=pk)

            # Handle categorical variables in features with error handling
            categorical_cols = X.select_dtypes(include=['object']).columns
            label_encoders = {}
            try:
                for col in categorical_cols:
                    le = LabelEncoder()
                    X[col] = le.fit_transform(X[col])
                    # Convertir LabelEncoder en dictionnaire sérialisable
                    label_encoders[col] = {'classes_': le.classes_.tolist()}

                # Encode target if necessary
                original_classes = None
                if not pd.api.types.is_numeric_dtype(y):
                    if model_type == 'regression':
                        messages.error(request, 'La régression nécessite une variable cible numérique.')
                        return redirect('view_csv', pk=pk)
                    # Store original class labels before encoding
                    original_classes = list(y.unique())
                    le = LabelEncoder()
                    y = le.fit_transform(y)
            except Exception as e:
                messages.error(request, f'Erreur lors du prétraitement des données : {str(e)}')
                return redirect('view_csv', pk=pk)

            # Split the data
            try:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            except Exception as e:
                messages.error(request, f'Erreur lors de la séparation des données : {str(e)}')
                return redirect('view_csv', pk=pk)

            # Train the model based on type with validation
            try:
                # Get the algorithm type from the form
                algorithm_type = request.POST.get('algorithm_type', 'random_forest')

                # Select the appropriate algorithm based on model type and algorithm type
                if model_type == 'regression':
                    if algorithm_type == 'linear':
                        model = LinearRegression()
                        algorithm_name = 'Linear Regression'
                    elif algorithm_type == 'decision_tree':
                        model = DecisionTreeRegressor(random_state=42)
                        algorithm_name = 'Decision Tree'
                    else:  # random_forest
                        model = RandomForestRegressor(random_state=42)
                        algorithm_name = 'Random Forest'

                    metric_name = 'R2 Score'
                    scoring = 'r2'
                else:  # classification
                    if algorithm_type == 'logistic':
                        model = LogisticRegression(random_state=42, max_iter=1000)
                        algorithm_name = 'Logistic Regression'
                    elif algorithm_type == 'decision_tree':
                        model = DecisionTreeClassifier(random_state=42)
                        algorithm_name = 'Decision Tree'
                    else:  # random_forest
                        model = RandomForestClassifier(random_state=42)
                        algorithm_name = 'Random Forest'

                    metric_name = 'Accuracy'
                    scoring = 'accuracy'

                results = []
                plots = []

                # Calculer le nombre minimum d'échantillons par classe pour la validation croisée
                from collections import Counter
                class_counts = Counter(y_train)
                min_samples_per_class = min(class_counts.values())
                
                # Validation croisée - s'assurer que cv est au moins 2 et pas plus grand que min_samples_per_class
                cv_value = max(2, min(5, min_samples_per_class))
                
                # Si min_samples_per_class est 1, utiliser KFold au lieu de StratifiedKFold
                if min_samples_per_class == 1:
                    from sklearn.model_selection import KFold
                    cv = KFold(n_splits=2)
                    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring=scoring)
                else:
                    cv_scores = cross_val_score(model, X_train, y_train, cv=cv_value, scoring=scoring)

                if cv_scores.mean() < 0.5:  # Seuil de performance minimal
                    messages.warning(request, f'Le modèle {model_name} présente des performances faibles (score moyen : {cv_scores.mean():.2f})')

                # Entraînement final et sauvegarde
                model.fit(X_train, y_train)

                try:
                    # Create metrics dictionary with target column and cross-validation scores
                    metrics_dict = {
                        'target_column': target,
                        'cv_scores_mean': float(cv_scores.mean()),
                        'cv_scores_std': float(cv_scores.std()),
                        'algorithm': algorithm_name,  # Store the algorithm type
                        'created_at': timezone.now().isoformat()  # Store creation timestamp
                    }

                    # Add original class labels for classification models
                    if model_type == 'classification' and original_classes is not None:
                        metrics_dict['original_classes'] = original_classes

                    # Add label encoders to metrics dictionary
                    metrics_dict['label_encoders'] = label_encoders
                    
                    # Save the model with the user-provided name, correct model type and metrics
                    csv_file.save_ml_model(model_name, model, features, model_type, metrics=metrics_dict)

                    # Log the model to MLflow
                    try:
                        # Evaluate on test set for additional metrics
                        y_pred = model.predict(X_test)

                        # Add evaluation metrics
                        if model_type == 'classification':
                            metrics_dict['accuracy'] = float(accuracy_score(y_test, y_pred))
                            # Convert classification report to dict
                            report = classification_report(y_test, y_pred, output_dict=True)
                            for class_name, metrics in report.items():
                                if isinstance(metrics, dict):
                                    for metric_name, value in metrics.items():
                                        if isinstance(value, (int, float)):
                                            metrics_dict[f'{class_name}_{metric_name}'] = float(value)
                        else:  # regression
                            metrics_dict['r2_score'] = float(r2_score(y_test, y_pred))
                            metrics_dict['mean_squared_error'] = float(mean_squared_error(y_test, y_pred))

                        # Log to MLflow
                        from .mlflow_utils import log_model_training
                        run_id = log_model_training(
                            model_name=model_name,
                            model=model,
                            model_type=model_type,
                            features=features,
                            target=target,
                            metrics=metrics_dict
                        )

                        if run_id:
                            # Add MLflow run ID to metrics
                            metrics_dict['mlflow_run_id'] = run_id

                            # Update the model with MLflow information
                            csv_file.save_ml_model(model_name, model, features, model_type, metrics=metrics_dict)

                            messages.success(request, f'Modèle {model_name} enregistré dans MLflow (Run ID: {run_id})')
                        else:
                            messages.warning(request, f'Avertissement: Échec de l\'enregistrement dans MLflow')
                    except Exception as e:
                        # Don't fail if MLflow logging fails
                        messages.warning(request, f'Avertissement: Échec de l\'enregistrement dans MLflow: {str(e)}')
                except Exception as e:
                    messages.error(request, f'Erreur lors de la sauvegarde du modèle {model_name} : {str(e)}')
                    return redirect('view_csv', pk=pk)

            except Exception as e:
                messages.error(request, f'Erreur lors de l\'entraînement des modèles : {str(e)}')
                return redirect('view_csv', pk=pk)

            # Evaluate the model on the test set
            y_pred = model.predict(X_test)

            if model_type == 'regression':
                score = r2_score(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                results.append({
                    'name': model_name,
                    'score': f'{score:.4f}',
                    'mse': f'{mse:.4f}'
                })

                # Regression plot: actual vs predicted
                plt.figure(figsize=(8, 6))
                plt.scatter(y_test, y_pred, alpha=0.5)
                plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
                plt.xlabel('Valeurs réelles')
                plt.ylabel('Valeurs prédites')
                plt.title(f'{model_name} - Réel vs Prédit')
            else:
                score = accuracy_score(y_test, y_pred)
                results.append({
                    'name': model_name,
                    'score': f'{score:.4f}'
                })

                # Classification plot: confusion matrix
                cm = pd.crosstab(y_test, y_pred)
                plt.figure(figsize=(8, 6))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
                plt.xlabel('Prédit')
                plt.ylabel('Réel')
                plt.title(f'{model_name} - Matrice de confusion')

            # Save the plot to a base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            graphic = base64.b64encode(image_png).decode('utf-8')
            plots.append({'name': model_name, 'plot': graphic})
            plt.close()

            # Feature importance plot for tree-based models
            if isinstance(model, (RandomForestClassifier, RandomForestRegressor, DecisionTreeClassifier, DecisionTreeRegressor)):
                importance = pd.DataFrame({
                    'feature': features,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)

                plt.figure(figsize=(10, 6))
                sns.barplot(data=importance, x='importance', y='feature')
                plt.title('Importance des caractéristiques')
                plt.xlabel('Score d\'importance')

                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()
                feature_importance_plot = base64.b64encode(image_png).decode('utf-8')
                plt.close()
            else:
                feature_importance_plot = None

            return render(request, 'csv_processor/ml_results.html', {
                'results': results,
                'plots': plots,
                'feature_importance_plot': feature_importance_plot,
                'metric_name': metric_name,
                'features': features,
                'target': target,
                'model_type': model_type,
                'csv_file': csv_file
            })

        # GET request: show ML training form (separate UI)
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        all_columns = df.columns.tolist()

        return render(request, 'csv_processor/train_ml.html', {
            'numeric_columns': numeric_columns,
            'categorical_columns': categorical_columns,
            'all_columns': all_columns,
            'csv_file': csv_file
        })

    except Exception as e:
        messages.error(request, f'Erreur lors de l\'entraînement du modèle : {str(e)}')
        return redirect('view_csv', pk=pk)


@login_required
def monitoring_dashboard(request):
    """Display system monitoring dashboard with metrics and usage statistics."""
    # Get system metrics
    system_metrics = SystemMonitor.get_system_metrics()

    # Get usage statistics
    usage_stats = UsageStatistics.get_usage_stats()

    context = {
        'system_metrics': system_metrics,
        'usage_stats': usage_stats,
        'page_title': 'System Monitoring Dashboard'
    }

    return render(request, 'csv_processor/monitoring_dashboard.html', context)

@login_required
def get_monitoring_data(request, pk):
    """Return system metrics and usage statistics for monitoring."""
    try:
        csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)

        # We don't need to check for ML models here, as we're just getting monitoring data
        # Remove the condition that was causing issues

        # Get system metrics
        system_metrics = SystemMonitor.get_system_metrics()

        # Get usage statistics
        usage_stats = UsageStatistics.get_usage_stats()

        # Combine metrics with file-specific information
        monitoring_data = {
            'system_metrics': system_metrics,
            'usage_stats': usage_stats,
            'file_info': {
                'title': csv_file.title,
                'rows': csv_file.rows_count,
                'columns': csv_file.columns_count,
                'last_viewed': csv_file.last_viewed.isoformat() if csv_file.last_viewed else None,
                'view_count': csv_file.view_count,
                'operations_count': len(csv_file.operations_log) if hasattr(csv_file, 'operations_log') and csv_file.operations_log else 0
            }
        }

        return JsonResponse(monitoring_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_metrics(request):
    """Get system metrics and usage statistics for monitoring dashboard."""
    try:
        # Record this request for usage statistics
        start_time = time.time()

        # Get system metrics
        system_metrics = SystemMonitor.get_system_metrics()

        # Get usage statistics
        usage_stats = UsageStatistics.get_usage_stats()

        # Record the processing time for this request
        processing_time = time.time() - start_time
        UsageStatistics.record_request_time(processing_time)

        # Combine metrics
        monitoring_data = {
            'system_metrics': system_metrics,
            'usage_stats': usage_stats,
            'timestamp': datetime.now().isoformat(),
            'request_info': {
                'method': request.method,
                'path': request.path,
                'processing_time': processing_time
            }
        }

        return JsonResponse(monitoring_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def model_actions(request, pk, model_name):
    """Display and handle model management actions (rename, delete, etc.)."""
    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)

    # Load the model information
    _, model_info = csv_file.load_ml_model(model_name)
    if model_info is None:
        messages.error(request, f"Le modèle '{model_name}' n'a pas été trouvé.")
        return redirect('view_csv', pk=pk)

    context = {
        'csv_file': csv_file,
        'model_name': model_name,
        'model_info': model_info,
    }

    return render(request, 'csv_processor/model_actions.html', context)

@login_required
def rename_model(request, pk, model_name):
    """Rename an existing ML model."""
    if request.method != 'POST':
        return redirect('model_actions', pk=pk, model_name=model_name)

    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
    new_name = request.POST.get('new_name', '').strip()

    if not new_name:
        messages.error(request, "Le nouveau nom ne peut pas être vide.")
        return redirect('model_actions', pk=pk, model_name=model_name)

    if new_name == model_name:
        messages.info(request, "Le nouveau nom est identique à l'ancien nom.")
        return redirect('model_actions', pk=pk, model_name=model_name)

    if new_name in csv_file.ml_models:
        messages.error(request, f"Un modèle avec le nom '{new_name}' existe déjà.")
        return redirect('model_actions', pk=pk, model_name=model_name)

    try:
        # Get the model info
        if model_name not in csv_file.ml_models:
            messages.error(request, f"Le modèle '{model_name}' n'a pas été trouvé.")
            return redirect('view_csv', pk=pk)

        model_info = csv_file.ml_models[model_name]

        # Rename the model file
        old_path = os.path.join(settings.MEDIA_ROOT, model_info['path'])
        new_path = os.path.join(os.path.dirname(old_path), f"{new_name}.joblib")

        if os.path.exists(old_path):
            os.rename(old_path, new_path)

        # Update the model info
        model_info['path'] = os.path.relpath(new_path, settings.MEDIA_ROOT)

        # Update the ml_models dictionary
        csv_file.ml_models[new_name] = model_info
        del csv_file.ml_models[model_name]
        csv_file.save()

        # Log the operation
        csv_file.log_operation('rename_model', {
            'old_name': model_name,
            'new_name': new_name
        })

        messages.success(request, f"Le modèle '{model_name}' a été renommé en '{new_name}'.")
        return redirect('model_actions', pk=pk, model_name=new_name)

    except Exception as e:
        messages.error(request, f"Erreur lors du renommage du modèle: {str(e)}")
        return redirect('model_actions', pk=pk, model_name=model_name)

@login_required
def delete_model(request, pk, model_name):
    """Delete an existing ML model."""
    if request.method != 'POST':
        return redirect('model_actions', pk=pk, model_name=model_name)

    csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)

    try:
        # Get the model info
        if model_name not in csv_file.ml_models:
            messages.error(request, f"Le modèle '{model_name}' n'a pas été trouvé.")
            return redirect('view_csv', pk=pk)

        model_info = csv_file.ml_models[model_name]

        # Delete the model file
        model_path = os.path.join(settings.MEDIA_ROOT, model_info['path'])
        if os.path.exists(model_path):
            os.remove(model_path)

        # Remove the model from the ml_models dictionary
        del csv_file.ml_models[model_name]
        csv_file.save()

        # Log the operation
        csv_file.log_operation('delete_model', {
            'model_name': model_name,
            'model_type': model_info.get('model_type', 'unknown')
        })

        messages.success(request, f"Le modèle '{model_name}' a été supprimé avec succès.")
        return redirect('view_csv', pk=pk)

    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression du modèle: {str(e)}")
        return redirect('model_actions', pk=pk, model_name=model_name)

@login_required
def mlflow_monitoring(request):
    """Display MLflow monitoring dashboard with model metrics and experiments."""
    from .mlflow_utils import setup_mlflow, get_experiment_runs, get_mlflow_ui_url
    import json
    from django.conf import settings

    try:
        # Set up MLflow
        tracking_uri = setup_mlflow()

        # Get MLflow UI URL
        mlflow_ui_url = get_mlflow_ui_url()

        # Get experiment names from settings
        experiment_names = getattr(settings, 'MLFLOW_EXPERIMENT_NAMES', {
            'classification': 'csv_analyzer_classification',
            'regression': 'csv_analyzer_regression'
        })

        # Get classification and regression runs
        classification_runs = get_experiment_runs(experiment_names['classification'], max_runs=10)
        regression_runs = get_experiment_runs(experiment_names['regression'], max_runs=10)

        # Combine recent runs from both experiments
        all_runs = classification_runs + regression_runs
        all_runs.sort(key=lambda x: x.get('start_time', 0) if x.get('start_time') else 0, reverse=True)
        recent_runs = all_runs[:10]  # Get 10 most recent runs

        # Prepare model comparison data for Plotly
        model_comparison_data = []

        # Classification models (accuracy)
        if classification_runs:
            classification_trace = {
                'x': [run['name'] for run in classification_runs],
                'y': [run['metrics'].get('accuracy', 0) for run in classification_runs],
                'type': 'bar',
                'name': 'Accuracy'
            }
            model_comparison_data.append(classification_trace)

        # Regression models (R² score)
        if regression_runs:
            regression_trace = {
                'x': [run['name'] for run in regression_runs],
                'y': [run['metrics'].get('r2_score', 0) for run in regression_runs],
                'type': 'bar',
                'name': 'R² Score'
            }
            model_comparison_data.append(regression_trace)

        context = {
            'mlflow_ui_url': mlflow_ui_url,
            'classification_runs': classification_runs,
            'regression_runs': regression_runs,
            'recent_runs': recent_runs,
            'model_comparison_data': json.dumps(model_comparison_data),
            'page_title': 'MLflow Monitoring',
            'tracking_uri': tracking_uri
        }

        return render(request, 'csv_processor/mlflow_monitoring.html', context)
    except Exception as e:
        messages.error(request, f"Error loading MLflow monitoring: {str(e)}")
        context = {
            'mlflow_ui_url': get_mlflow_ui_url(),
            'classification_runs': [],
            'regression_runs': [],
            'recent_runs': [],
            'model_comparison_data': json.dumps([]),
            'page_title': 'MLflow Monitoring',
            'error': str(e)
        }
        return render(request, 'csv_processor/mlflow_monitoring.html', context)
@extend_schema(
    request=CSVUploadSerializer,
    responses=CSVUploadSerializer,
    summary="Upload a CSV file via API"
)
class CSVUploadAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CSVUploadSerializer(data=request.data)
        if serializer.is_valid():
            
             return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    summary="Delete a CSV file by ID",
    responses={200: OpenApiTypes.OBJECT}
)
class DeleteCSVAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
            if csv_file.file:
                csv_file.file.delete()
            csv_file.delete()
            return Response({"detail": "CSV deleted successfully", "id": pk}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        return self.post(request, pk)
# ... existing code ...

@extend_schema(
    summary="Export CSV file by ID",
    responses={200: OpenApiTypes.BINARY}
)
class ExportCSVAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
            ensure_media_dirs()
            timestamp = datetime.now().strftime('%Y-%m-%d_%Hh%M')
            safe_title = "".join(c for c in csv_file.title if c.isalnum() or c in (' ', '_', '-'))
            export_filename = f'export_{safe_title}_{timestamp}.csv'
            export_path = os.path.join(settings.MEDIA_ROOT, 'exports', export_filename)
            delimiter = detect_delimiter(csv_file.file.path)
            df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
            df.to_csv(export_path, index=False)
            with open(export_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{export_filename}"'
            os.remove(export_path)
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    summary="Train a ML model",
    request=TrainMLRequestSerializer,
    responses={200: OpenApiTypes.OBJECT}
)
class TrainMLAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
        try:
            delimiter = detect_delimiter(csv_file.file.path)
            df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
        except Exception as e:
            return Response({"error": f"Erreur lecture CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        features = data.get('features') or []
        target = data.get('target')
        model_type = data.get('model_type')
        model_name = data.get('model_name')
        algorithm_type = data.get('algorithm_type', 'random_forest')

        if not all([features, target, model_type, model_name]):
            return Response({"error": "features, target, model_type, model_name are required"}, status=status.HTTP_400_BAD_REQUEST)
        if target in features:
            return Response({"error": "target cannot be part of features"}, status=status.HTTP_400_BAD_REQUEST)

        if df[features + [target]].isnull().any().any():
            df = df.fillna(df.mean(numeric_only=True))
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].isnull().any():
                    mode = df[col].mode()
                    df[col] = df[col].fillna(mode.iloc[0] if not mode.empty else '')

        try:
            X = df[features].copy()
            y = df[target].copy()
        except KeyError as e:
            return Response({"error": f"Missing column: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        categorical_cols = X.select_dtypes(include=['object']).columns
        label_encoders = {}
        try:
            for col in categorical_cols:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                label_encoders[col] = le

            original_classes = None
            if not pd.api.types.is_numeric_dtype(y):
                if model_type == 'regression':
                    return Response({"error": "Regression requires numeric target"}, status=status.HTTP_400_BAD_REQUEST)
                original_classes = list(y.unique())
                le_y = LabelEncoder()
                y = le_y.fit_transform(y.astype(str))
        except Exception as e:
            return Response({"error": f"Preprocessing error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        except Exception as e:
            return Response({"error": f"Train/test split error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if model_type == 'regression':
                if algorithm_type == 'linear':
                    model = LinearRegression()
                    algorithm_name = 'Linear Regression'
                elif algorithm_type == 'decision_tree':
                    model = DecisionTreeRegressor(random_state=42)
                    algorithm_name = 'Decision Tree'
                else:
                    model = RandomForestRegressor(random_state=42)
                    algorithm_name = 'Random Forest'
                scoring = 'r2'
            else:
                if algorithm_type == 'logistic':
                    model = LogisticRegression(random_state=42, max_iter=1000)
                    algorithm_name = 'Logistic Regression'
                elif algorithm_type == 'decision_tree':
                    model = DecisionTreeClassifier(random_state=42)
                    algorithm_name = 'Decision Tree'
                else:
                    model = RandomForestClassifier(random_state=42)
                    algorithm_name = 'Random Forest'
                scoring = 'accuracy'

            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring=scoring)
            model.fit(X_train, y_train)

            metrics_dict = {
                'target_column': target,
                'cv_scores_mean': float(cv_scores.mean()),
                'cv_scores_std': float(cv_scores.std()),
                'algorithm': algorithm_name,
                'created_at': timezone.now().isoformat()
            }
            if model_type == 'classification' and original_classes is not None:
                metrics_dict['original_classes'] = original_classes

            csv_file.save_ml_model(model_name, model, features, model_type, metrics=metrics_dict)

            try:
                y_pred = model.predict(X_test)
                if model_type == 'classification':
                    metrics_dict['accuracy'] = float(accuracy_score(y_test, y_pred))
                    report = classification_report(y_test, y_pred, output_dict=True)
                    for class_name, ms in report.items():
                        if isinstance(ms, dict):
                            for metric_name, value in ms.items():
                                if isinstance(value, (int, float)):
                                    metrics_dict[f'{class_name}_{metric_name}'] = float(value)
                else:
                    metrics_dict['r2_score'] = float(r2_score(y_test, y_pred))
                    metrics_dict['mean_squared_error'] = float(mean_squared_error(y_test, y_pred))

                from .mlflow_utils import log_model_training
                run_id = log_model_training(
                    model_name=model_name,
                    model=model,
                    model_type=model_type,
                    features=features,
                    target=target,
                    metrics=metrics_dict
                )
                if run_id:
                    metrics_dict['mlflow_run_id'] = run_id
                    csv_file.save_ml_model(model_name, model, features, model_type, metrics=metrics_dict)
            except Exception as e:
                # لا نفشل الـ API إذا فشل تسجيل MLflow
                pass

            return Response({
                "message": "Model trained and saved",
                "csv_id": pk,
                "model_name": model_name,
                "model_type": model_type,
                "algorithm": algorithm_name,
                "metrics": metrics_dict
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Training error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
# ... existing code ...

@extend_schema(
    summary="Get monitoring metrics (JSON)",
    responses={200: OpenApiTypes.OBJECT}
)
class MetricsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            start_time = time.time()
            system_metrics = SystemMonitor.get_system_metrics()
            usage_stats = UsageStatistics.get_usage_stats()
            processing_time = time.time() - start_time
            UsageStatistics.record_request_time(processing_time)

            monitoring_data = {
                'system_metrics': system_metrics,
                'usage_stats': usage_stats,
                'timestamp': datetime.now().isoformat(),
                'request_info': {
                    'method': request.method,
                    'path': request.path,
                    'processing_time': processing_time
                }
            }
            return Response(monitoring_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    request=CSVUploadSerializer,
    responses={201: OpenApiTypes.OBJECT},
    summary="Upload a CSV file via API"
)
class CSVUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CSVUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        csv_file = CSVFile(user=request.user, file=file)
        csv_file.save()

        try:
            delimiter = detect_delimiter(csv_file.file.path)
            df = pd.read_csv(csv_file.file.path, delimiter=delimiter)
            columns = list(df.columns)
            csv_file.rows_count = int(df.shape[0])
            csv_file.columns_count = int(df.shape[1])
            csv_file.save()
        except Exception as e:
            csv_file.delete()
            return Response({"error": f"Erreur lecture CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "id": csv_file.pk,
            "name": csv_file.title,
            "path": csv_file.file.url if hasattr(csv_file.file, "url") else csv_file.file.name,
            "columns": columns
        }, status=status.HTTP_201_CREATED)

@extend_schema(
    summary="Test a trained ML model",
    request=TestModelRequestSerializer,
    responses={200: OpenApiTypes.OBJECT}
)
class TestModelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, model_name):
        csv_file = get_object_or_404(CSVFile, pk=pk, user=request.user)
        try:
            # Validate input data
            serializer = TestModelRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Load the model
            model, model_info = csv_file.load_ml_model(model_name)
            if model is None:
                return Response({"error": f"Model '{model_name}' not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get feature values from request
            inputs = serializer.validated_data['inputs']
            
            # Ensure all required features are present
            if 'features' not in model_info:
                return Response({"error": "Model is missing feature information"}, status=status.HTTP_400_BAD_REQUEST)
            
            missing_features = set(model_info['features']) - set(inputs.keys())
            if missing_features:
                return Response({"error": f"Missing features: {', '.join(missing_features)}"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Create input DataFrame with proper feature order
            X_test = pd.DataFrame([inputs])
            try:
                X_test = X_test[model_info['features']]
            except KeyError as e:
                return Response({"error": f"Error accessing feature: {str(e)}"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Measure prediction latency
            start_time = time.time()
            prediction = model.predict(X_test)
            latency_ms = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Format the prediction result
            prediction_value = prediction[0]
            
            return Response({
                "prediction": float(prediction_value) if isinstance(prediction_value, (int, float, np.number)) else str(prediction_value),
                "latency_ms": round(latency_ms, 2)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé avec succès ! Vous pouvez maintenant vous connecter')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')

@extend_schema(
    summary="Opérations sur l'utilisateur actuel",
    description="Permet de récupérer ou modifier les informations de l'utilisateur connecté",
    responses=UserSerializer
)
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Récupère les informations de l'utilisateur connecté"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Met à jour les informations de l'utilisateur connecté"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    summary="Création d'un nouvel utilisateur",
    description="Permet de créer un nouvel utilisateur",
    responses=UserCreateSerializer
)
class UserCreateAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Crée un nouvel utilisateur"""
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Utilisateur créé avec succès',
                'username': serializer.validated_data['username']
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    summary="Get Prometheus metrics (text/plain)",
    responses={200: OpenApiTypes.BINARY}
)
class PrometheusMetricsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            metrics_data = generate_latest()
            return HttpResponse(
                metrics_data,
                content_type="text/plain; version=0.0.4"
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
def simulate_error(request):
     
    APP_ERRORS_TOTAL.labels(type='simulated').inc()
    return HttpResponse('Simulated error', status=500)


