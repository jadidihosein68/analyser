import os
from flask import Flask
from common import Config, db, get_all_ohlcv_data
from training.data_processing import process_dataframe, add_technical_indicators
from training.labeling import add_future_close_and_multiclass_label
from training.model_training import train_and_save_models  # Updated function
from training.realtime_prediction import predict_realtime_data

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)  # Ensure you have a Config class in config.py

# Initialize the database
db.init_app(app)

# Paths for storing models
MODEL_DIR = "models/"
os.makedirs(MODEL_DIR, exist_ok=True)

if __name__ == "__main__":
    with app.app_context():
        # Step 1: Fetch Data
        db_data = get_all_ohlcv_data()
        if db_data is not None:
            # Step 2: Process Data
            processed_df = process_dataframe(db_data)
            if processed_df is not None:
                # Step 3: Add Technical Indicators
                df_with_indicators = add_technical_indicators(processed_df)
                if df_with_indicators is not None:
                    # Step 4: Label Data
                    df_with_labels = add_future_close_and_multiclass_label(df_with_indicators)
                    if df_with_labels is not None:
                        # Step 5: Train and Save Model
                        feature_columns = ["open", "high", "low", "close", "volume", "RSI_14", "MACD", "Signal_Line", "close_lag_1", "close_lag_2", "volume_lag_1", "volume_lag_2"]
                        
                        # Specify model types to train
                        model_types = ["random_forest", "logistic_regression", "svm", "xgboost"]
                        for model_type in model_types:
                            model_path = os.path.join(MODEL_DIR, f"{model_type}_model.joblib")
                            train_and_save_models(df_with_labels, feature_columns, MODEL_DIR, model_type=model_type)

                        # Step 6: Perform Real-Time Prediction
                        realtime_data = {"close": 105.5}
                        model_path = os.path.join(MODEL_DIR, "random_forest_model.joblib")  # Example model for prediction
                        prediction = predict_realtime_data(realtime_data, df_with_labels, model_path)
                        print(f"Real-time prediction: {prediction}")
