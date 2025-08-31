# import pandas as pd
# from sklearn.tree import DecisionTreeClassifier
# import joblib

# def train_cleaning_model():
#     # Synthetic dataset
#     data = {
#         'missing_values': [0.1, 0.5, 0.0, 0.8],
#         'data_type': ['numeric', 'categorical', 'numeric', 'categorical'],
#         'suggested_action': ['mean_impute', 'remove_duplicates', 'no_action', 'encoder']
#     }
    
#     df = pd.DataFrame(data)
    
#     # Features and target
#     X = df[['missing_values', 'data_type']]
#     y = df['suggested_action']
    
#     # Convert data types to numerical encoding
#     X_encoded = pd.get_dummies(X)
    
#     # Train model
#     model = DecisionTreeClassifier(max_depth=2)
#     model.fit(X_encoded, y)
    
#     # Save model
#     model_path = 'cleaning_model.pkl'
#     joblib.dump(model, model_path)
#     print("Model trained and saved")

# train_cleaning_model()

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

def train_cleaning_model(model_name='cleaning_model'):
    # Sample training data
    data = {
        'missing_values': [0.1, 0.8, 0.0, 0.3],
        'data_type_int64': [1, 0, 1, 0],
        'data_type_float64': [0, 0, 0, 0],
        'data_type_object': [0, 1, 0, 1],
        'suggested_action': ['fill_mean', 'remove_nulls', 'no_action', 'remove_duplicates']
    }
    df = pd.DataFrame(data)
    
    # Features and target
    X = df[['missing_values', 'data_type_int64', 'data_type_float64', 'data_type_object']]
    y = df['suggested_action']
    
    # Train and save the model
    model = DecisionTreeClassifier(max_depth=2)
    model.fit(X, y)
    model_path = f'{model_name}.pkl' if not model_name.endswith('.pkl') else model_name
    joblib.dump(model, model_path)
    print(f"Model trained and saved as {model_path}")
    return model

def test_model(model, test_data=None):
    if test_data is None:
        test_data = {
            'missing_values': 0.6,
            'data_type_int64': 0,
            'data_type_float64': 1,
            'data_type_object': 0
        }
    test_df = pd.DataFrame([test_data])
    prediction = model.predict(test_df)
    return prediction[0]

# Example usage
if __name__ == '__main__':
    model = train_cleaning_model('my_cleaning_model')
    test_result = test_model(model)
    print(f"Test prediction: {test_result}")