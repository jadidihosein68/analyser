import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

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
    from sklearn.metrics import classification_report, accuracy_score

    # Extended example data with more variation to include 'Sell'
    data = {
        "open_time": [1591258320000 + i * 60000 for i in range(300)],
        "open": [100 + (i % 20) - (i % 10) for i in range(300)],
        "high": [101 + (i % 20) - (i % 10) for i in range(300)],
        "low": [99 + (i % 20) - (i % 10) for i in range(300)],
        "close": [100 + (i % 20) - (i % 15) for i in range(300)],
        "volume": [200 + (i * 5) for i in range(300)],
        "close_time": [1591258379999 + i * 60000 for i in range(300)],
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Process DataFrame
    processed_df = process_dataframe(df)

    if processed_df is not None:
        # Add future_close and labels
        df_with_labels = add_future_close_and_multiclass_label(processed_df)

        if df_with_labels is not None:
            # Split data chronologically
            train_size = int(len(df_with_labels) * 0.8)
            train_df = df_with_labels.iloc[:train_size]
            test_df = df_with_labels.iloc[train_size:]

            # Define features and target
            features = ["open", "high", "low", "close", "volume"]
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
