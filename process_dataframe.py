import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from joblib import dump, load  # For saving and loading models
from common import Config, db, get_all_ohlcv_data
from flask import Flask

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)  # Ensure you have a Config class in config.py

# Initialize the database
db.init_app(app)

# Paths for storing models
MODEL_DIR = "models/"
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "trading_model.joblib")

# Step 1: Clean or Prepare Data
def process_dataframe(df):
    """
    Process a DataFrame with the following steps:
      - Convert open_time and close_time to datetime.
      - Convert numerical columns (open, high, low, close, volume) to float.
      - Handle missing values by dropping rows with NaNs.
      - Sort the DataFrame by open_time in ascending order.

    Args:
        df (pd.DataFrame): Input DataFrame with columns [open_time, open, high, low, close, volume, close_time].

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    try:
        required_columns = ["open_time", "open", "high", "low", "close", "volume", "close_time"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Input DataFrame must contain the columns: {', '.join(required_columns)}")

        df = df.copy()
        df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
        df["close_time"] = pd.to_datetime(df["close_time"], unit='ms')

        numerical_columns = ["open", "high", "low", "close", "volume"]
        for col in numerical_columns:
            df[col] = df[col].astype(float)

        df = df.dropna()
        df = df.sort_values(by="open_time", ascending=True)

        return df

    except Exception as e:
        print(f"Error processing DataFrame: {e}")
        return None

# Step 2: Add Technical Indicators
def add_technical_indicators(df):
    """
    Adds technical indicators: RSI(14), MACD, and lag features.

    Args:
        df (pd.DataFrame): Input DataFrame with columns ['open', 'high', 'low', 'close', 'volume'].

    Returns:
        pd.DataFrame: DataFrame with added technical indicators.
    """
    try:
        df = df.copy()

        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=14, min_periods=14).mean()
        avg_loss = loss.rolling(window=14, min_periods=14).mean()

        rs = avg_gain / avg_loss
        df['RSI_14'] = 100 - (100 / (1 + rs))

        short_ema = df['close'].ewm(span=12, adjust=False).mean()
        long_ema = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = short_ema - long_ema
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        df['close_lag_1'] = df['close'].shift(1)
        df['close_lag_2'] = df['close'].shift(2)
        df['volume_lag_1'] = df['volume'].shift(1)
        df['volume_lag_2'] = df['volume'].shift(2)

        df = df.dropna()

        return df

    except Exception as e:
        print(f"Error adding technical indicators: {e}")
        return None

# Step 3: Add Labels
def add_future_close_and_multiclass_label(df):
    """
    Adds a 'future_close' column which is the next bar's close (shifted by -1),
    and a 'label' column with three classes:
      - 0 (Sell) if future_close <= close - 0.2% of close
      - 2 (Buy) if future_close >= close + 0.2% of close
      - 1 (Hold) otherwise

    Args:
        df (pd.DataFrame): Input DataFrame with a 'close' column.

    Returns:
        pd.DataFrame: DataFrame with future_close and label columns added.
    """
    try:
        df = df.copy()
        df['future_close'] = df['close'].shift(-1)
        df['pct_change'] = (df['future_close'] - df['close']) / df['close'] * 100

        df['label'] = df['pct_change'].apply(lambda x: 2 if x >= 0.09 else (0 if x <= -0.09 else 1))

        df = df.dropna()
        df = df.drop(columns=['pct_change'])

        return df

    except Exception as e:
        print(f"Error adding future_close and labels: {e}")
        return None

# Step 4: Train and Save Model
def train_and_save_model(df, features, model_path):
    """
    Train a model and save it to a specified path.

    Args:
        df (pd.DataFrame): DataFrame with features and labels.
        features (list): List of feature columns to use for training.
        model_path (str): Path to save the trained model.
    """
    try:
        train_size = int(len(df) * 0.8)
        train_df = df.iloc[:train_size]
        test_df = df.iloc[train_size:]

        X_train = train_df[features]
        y_train = train_df['label']
        X_test = test_df[features]
        y_test = test_df['label']

        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("Classification Report:")
        print(classification_report(y_test, y_pred))

        dump(model, model_path)
        print(f"Model saved to {model_path}")

    except Exception as e:
        print(f"Error training and saving model: {e}")

# Step 5: Real-Time Prediction
def predict_realtime_data(realtime_data, historical_data, model_path):
    """
    Predict the trade action for real-time data based on a saved model.

    Args:
        realtime_data (dict): Real-time data with the current price.
        historical_data (pd.DataFrame): Historical data for feature engineering.
        model_path (str): Path to the saved model.

    Returns:
        int: Predicted label (0 = Sell, 1 = Hold, 2 = Buy).
    """
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

# Example usage
if __name__ == "__main__":
    with app.app_context():
        db_data = get_all_ohlcv_data()
        if db_data is not None:
            processed_df = process_dataframe(db_data)
            if processed_df is not None:
                df_with_indicators = add_technical_indicators(processed_df)
                if df_with_indicators is not None:
                    df_with_labels = add_future_close_and_multiclass_label(df_with_indicators)
                    if df_with_labels is not None:
                        feature_columns = ["open", "high", "low", "close", "volume", "RSI_14", "MACD", "Signal_Line", "close_lag_1", "close_lag_2", "volume_lag_1", "volume_lag_2"]
                        train_and_save_model(df_with_labels, feature_columns, MODEL_PATH)

                        # Simulate real-time prediction
                        realtime_data = {"close": 105.5}
                        prediction = predict_realtime_data(realtime_data, df_with_labels, MODEL_PATH)
                        print(f"Real-time prediction: {prediction}")
