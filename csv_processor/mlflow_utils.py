"""
MLflow utilities for tracking machine learning experiments.
"""
import os
import mlflow
from mlflow.tracking import MlflowClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Default MLflow tracking URI (local)
DEFAULT_TRACKING_URI = "sqlite:///mlruns.db"

def setup_mlflow():
    """
    Set up MLflow tracking.

    This function configures MLflow to use either a local directory or a remote tracking server.
    """
    try:
        # Get tracking URI from settings or use default
        tracking_uri = getattr(settings, 'MLFLOW_TRACKING_URI', DEFAULT_TRACKING_URI)

        # Set the tracking URI
        mlflow.set_tracking_uri(tracking_uri)

        # Create experiment directory if using local filesystem
        if tracking_uri.startswith('file:'):
            experiment_dir = tracking_uri.replace('file:', '')
            os.makedirs(experiment_dir, exist_ok=True)

            # Ensure the directory structure is valid
            os.makedirs(os.path.join(experiment_dir, '.trash'), exist_ok=True)

        # Create SQLite database directory if using SQLite
        if tracking_uri.startswith('sqlite:'):
            # Extract the database path
            db_path = tracking_uri.replace('sqlite:///', '')
            # Create the directory for the database if it doesn't exist
            db_dir = os.path.dirname(os.path.abspath(db_path))
            if db_dir:  # Only create if there's a directory part
                os.makedirs(db_dir, exist_ok=True)

        logger.info(f"MLflow tracking URI set to: {tracking_uri}")
        return tracking_uri
    except Exception as e:
        logger.error(f"Error setting up MLflow: {e}")
        # Fallback to a local directory if there's an error
        fallback_uri = "file:./mlruns_fallback"
        os.makedirs("./mlruns_fallback", exist_ok=True)
        mlflow.set_tracking_uri(fallback_uri)
        logger.info(f"Using fallback MLflow tracking URI: {fallback_uri}")
        return fallback_uri

def get_or_create_experiment(experiment_name):
    """
    Get or create an MLflow experiment.

    Args:
        experiment_name (str): Name of the experiment

    Returns:
        str: Experiment ID
    """
    # Get experiment by name
    experiment = mlflow.get_experiment_by_name(experiment_name)

    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
        logger.info(f"Created new experiment: {experiment_name} with ID: {experiment_id}")
    else:
        experiment_id = experiment.experiment_id
        logger.info(f"Using existing experiment: {experiment_name} with ID: {experiment_id}")

    return experiment_id

def log_model_training(model_name, model, model_type, features, target, metrics):
    """
    Log a model training run to MLflow.

    Args:
        model_name (str): Name of the model
        model: The trained model object
        model_type (str): Type of model (classification or regression)
        features (list): List of feature names
        target (str): Target column name
        metrics (dict): Dictionary of metrics

    Returns:
        str: Run ID of the MLflow run
    """
    # Set up MLflow
    setup_mlflow()

    # Get or create experiment based on the dataset
    experiment_id = get_or_create_experiment(f"csv_analyzer_{model_type}")

    # Start an MLflow run
    with mlflow.start_run(experiment_id=experiment_id, run_name=model_name) as run:
        # Log parameters
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("target_column", target)
        mlflow.log_param("features_count", len(features))
        mlflow.log_param("features", ",".join(features))

        # Log algorithm-specific parameters
        if hasattr(model, 'get_params'):
            params = model.get_params()
            for param_name, param_value in params.items():
                if isinstance(param_value, (int, float, str, bool)):
                    mlflow.log_param(param_name, param_value)

        # Log metrics
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float)):
                mlflow.log_metric(metric_name, metric_value)

        # Log the model
        if model_type == 'classification':
            mlflow.sklearn.log_model(model, "model", registered_model_name=model_name)
        else:  # regression
            mlflow.sklearn.log_model(model, "model", registered_model_name=model_name)

        # Return the run ID
        return run.info.run_id

def get_mlflow_ui_url():
    """
    Get the URL for the MLflow UI.

    Returns:
        str: URL for the MLflow UI
    """
    tracking_uri = mlflow.get_tracking_uri()

    # If using a remote tracking server, return the URL
    if tracking_uri.startswith('http'):
        return tracking_uri

    # If using a local tracking server, return the local URL
    return "http://127.0.0.1:5000"

def get_experiment_runs(experiment_name, max_runs=100):
    """
    Get runs for a specific experiment.

    Args:
        experiment_name (str): Name of the experiment
        max_runs (int, optional): Maximum number of runs to return. Defaults to 100.

    Returns:
        list: List of run information dictionaries
    """
    try:
        # Set up MLflow
        setup_mlflow()

        # Get experiment
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            # Create the experiment if it doesn't exist
            experiment_id = mlflow.create_experiment(experiment_name)
            logger.info(f"Created new experiment: {experiment_name} with ID: {experiment_id}")
            return []  # No runs yet for a new experiment

        # Get runs
        client = MlflowClient()
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=max_runs,
            order_by=["attributes.start_time DESC"]
        )

        # Format run information
        run_info = []
        for run in runs:
            run_data = {
                'run_id': run.info.run_id,
                'name': run.data.tags.get('mlflow.runName', 'Unnamed'),
                'status': run.info.status,
                'start_time': run.info.start_time,
                'end_time': run.info.end_time,
                'params': run.data.params,
                'metrics': run.data.metrics,
                'experiment_id': experiment.experiment_id
            }
            run_info.append(run_data)

        return run_info
    except Exception as e:
        logger.error(f"Error getting experiment runs for {experiment_name}: {e}")
        return []

def get_model_details(model_name):
    """
    Get details for a specific model.

    Args:
        model_name (str): Name of the model

    Returns:
        dict: Model details
    """
    try:
        # Set up MLflow
        setup_mlflow()

        # Get model versions
        client = MlflowClient()
        model_versions = client.search_model_versions(f"name='{model_name}'")

        if not model_versions:
            logger.warning(f"No model versions found for model: {model_name}")
            return None

        # Get the latest version
        latest_version = sorted(model_versions, key=lambda x: x.version, reverse=True)[0]

        try:
            # Get run details
            run = client.get_run(latest_version.run_id)

            # Format model details
            model_details = {
                'name': model_name,
                'version': latest_version.version,
                'run_id': latest_version.run_id,
                'status': latest_version.status,
                'creation_time': latest_version.creation_timestamp,
                'params': run.data.params,
                'metrics': run.data.metrics,
            }

            return model_details
        except Exception as run_error:
            logger.error(f"Error getting run details for model {model_name}: {run_error}")
            # Return limited model details without run information
            return {
                'name': model_name,
                'version': latest_version.version,
                'run_id': latest_version.run_id,
                'status': latest_version.status,
                'creation_time': latest_version.creation_timestamp,
                'params': {},
                'metrics': {},
                'error': str(run_error)
            }
    except Exception as e:
        logger.error(f"Error getting model details for {model_name}: {e}")
        return None
