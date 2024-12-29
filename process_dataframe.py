import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from db_adapter import get_all_ohlcv_data  # Assuming this retrieves data from the database
from flask import Flask
from models import db

# Initialize Flask app
app = Flask(__name__)
app.config.from_object("config.Config")  # Ensure you have a Config class in config.py

# Initialize the database
db.init_app(app)

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
        # Ensure proper column names are present
        required_columns = ["open_time", "open", "high", "low", "close", "volume", "close_time"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Input DataFrame must contain the columns: {', '.join(required_columns)}")

        # Create a copy of the DataFrame to avoid modifying the original slice
        df = df.copy()

        # Convert open_time and close_time to datetime
        df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')  # Assuming timestamps are in milliseconds
        df["close_time"] = pd.to_datetime(df["close_time"], unit='ms')

        # Convert numerical columns to float
        numerical_columns = ["open", "high", "low", "close", "volume"]
        for col in numerical_columns:
            df[col] = df[col].astype(float)

        # Drop rows with missing values
        df = df.dropna()

        # Sort by open_time in ascending order
        df = df.sort_values(by="open_time", ascending=True)

        return df

    except Exception as e:
        print(f"Error processing DataFrame: {e}")
        return None

def add_technical_indicators(df):
    """
    Adds technical indicators: RSI(14), MACD, and lag features.

    Args:
        df (pd.DataFrame): Input DataFrame with columns ['open', 'high', 'low', 'close', 'volume'].

    Returns:
        pd.DataFrame: DataFrame with added technical indicators.
    """
    try:
        # Create a copy of the DataFrame to avoid modifying the original slice
        df = df.copy()

        # Add RSI(14)
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=14, min_periods=14).mean()
        avg_loss = loss.rolling(window=14, min_periods=14).mean()

        rs = avg_gain / avg_loss
        df['RSI_14'] = 100 - (100 / (1 + rs))

        # Add MACD
        short_ema = df['close'].ewm(span=12, adjust=False).mean()
        long_ema = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = short_ema - long_ema
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # Add lag features
        df['close_lag_1'] = df['close'].shift(1)
        df['close_lag_2'] = df['close'].shift(2)
        df['volume_lag_1'] = df['volume'].shift(1)
        df['volume_lag_2'] = df['volume'].shift(2)

        # Drop rows with NaN values generated during calculations
        df = df.dropna()

        return df

    except Exception as e:
        print(f"Error adding technical indicators: {e}")
        return None

def add_future_close_and_multiclass_label(df):
    """
    Adds a 'future_close' column which is the next bar's close (shifted by -1),
    and a 'label' column with three classes:
      - 0 (Sell) if future_close <= close - 0.5% of close
      - 2 (Buy) if future_close >= close + 0.5% of close
      - 1 (Hold) otherwise
    Drops the last row with NaN in future_close.

    Args:
        df (pd.DataFrame): Input DataFrame with a 'close' column.

    Returns:
        pd.DataFrame: DataFrame with future_close and label columns added.
    """
    try:
        # Create a copy of the DataFrame to avoid modifying the original slice
        df = df.copy()

        # Add future_close column
        df['future_close'] = df['close'].shift(-1)

        # Calculate percentage change
        df['pct_change'] = (df['future_close'] - df['close']) / df['close'] * 100

        # Add label column based on thresholds
        df['label'] = df['pct_change'].apply(lambda x: 2 if x >= 0.5 else (0 if x <= -0.5 else 1))

        # Drop the last row with NaN in future_close
        df = df.dropna()

        # Drop temporary pct_change column
        df = df.drop(columns=['pct_change'])

        return df

    except Exception as e:
        print(f"Error adding future_close and labels: {e}")
        return None

# Example usage
if __name__ == "__main__":
    with app.app_context():
        from sklearn.metrics import classification_report, accuracy_score

        # Retrieve data from the database
        db_data = get_all_ohlcv_data()  # This function should return a Pandas DataFrame

        if db_data is not None:
            print("Data loaded successfully from the database.")

            # Process DataFrame
            processed_df = process_dataframe(db_data)

            if processed_df is not None:
                # Add technical indicators
                df_with_indicators = add_technical_indicators(processed_df)

                if df_with_indicators is not None:
                    # Add future_close and labels
                    df_with_labels = add_future_close_and_multiclass_label(df_with_indicators)

                    if df_with_labels is not None:
                        # Show the full dataset before prediction
                        
                        pd.set_option('display.max_columns', None)
                        pd.set_option('display.max_rows', None)
                        pd.set_option('display.width', 1000)
                        
                        print("Complete Dataset with Features and Labels:")
                        print(df_with_labels)

                        # Split data chronologically
                        train_size = int(len(df_with_labels) * 0.8)
                        train_df = df_with_labels.iloc[:train_size]
                        test_df = df_with_labels.iloc[train_size:]

                        # Define features and target
                        features = ["open", "high", "low", "close", "volume", "RSI_14", "MACD", "Signal_Line", "close_lag_1", "close_lag_2", "volume_lag_1", "volume_lag_2"]
                        X_train = train_df[features]
                        y_train = train_df['label']
                        X_test = test_df[features]
                        y_test = test_df['label']

                        # Train a RandomForestClassifier
                        model = RandomForestClassifier(random_state=42)
                        model.fit(X_train, y_train)

                        # Make predictions
                        y_pred = model.predict(X_test)

                        # Evaluate the model
                        print("Accuracy:", accuracy_score(y_test, y_pred))
                        print("Classification Report:")
                        print(classification_report(y_test, y_pred))
                        print("diagnosis")
                        print(test_df['label'].value_counts())
