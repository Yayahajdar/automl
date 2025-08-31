#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Start MLflow UI server
mlflow ui --backend-store-uri sqlite:///mlruns.db --port 5000



# source venv/bin/activate && mlflow ui --backend-store-uri file:./mlruns --port 5000