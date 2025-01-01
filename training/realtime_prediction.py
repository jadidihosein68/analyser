import os  
from joblib import load
import pandas as pd
from training.data_processing import add_technical_indicators

def predict_realtime_data(realtime_data, historical_data, model_path):
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        model = load(model_path)

        last_row = historical_data.iloc[-1].copy()
        last_row["close"] = realtime_data["close"]
        last_row["high"] = max(last_row["high"], realtime_data["close"])
        last_row["low"] = min(last_row["low"], realtime_data["close"])

        historical_data = pd.concat([historical_data, pd.DataFrame([last_row])], ignore_index=True)
        historical_data = add_technical_indicators(historical_data)

        latest_features = historical_data.iloc[[-1]]
        feature_columns = ["open", "high", "low", "close", "volume", "RSI_14", "MACD", "Signal_Line", "close_lag_1", "close_lag_2", "volume_lag_1", "volume_lag_2"]
        X_realtime = latest_features[feature_columns]

        prediction = model.predict(X_realtime)
        return prediction[0]

    except Exception as e:
        print(f"Error in real-time prediction: {e}")
        return None
