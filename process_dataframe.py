import pandas as pd

# Set pandas options to display all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


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
    Adds 5-day and 20-day moving averages, daily returns, and RSI(14) to the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame with columns ['open', 'high', 'low', 'close'].

    Returns:
        pd.DataFrame: DataFrame with added technical indicators.
    """
    try:
        # Create a copy of the DataFrame to avoid modifying the original slice
        df = df.copy()

        # Ensure the necessary columns are present
        required_columns = ['open', 'high', 'low', 'close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Input DataFrame must contain the columns: {', '.join(required_columns)}")

        # Add 5-day and 20-day moving averages
        df['MA_5'] = df['close'].rolling(window=5).mean()
        df['MA_20'] = df['close'].rolling(window=20).mean()

        # Add daily returns
        df['daily_return'] = df['close'].pct_change()

        # Add RSI(14)
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=14, min_periods=14).mean()
        avg_loss = loss.rolling(window=14, min_periods=14).mean()

        rs = avg_gain / avg_loss
        df['RSI_14'] = 100 - (100 / (1 + rs))

        # Drop rows with NaN values generated during calculations
        df = df.dropna()

        return df

    except Exception as e:
        print(f"Error adding technical indicators: {e}")
        return None

def add_lag_features(df):
    """
    Adds lag features for the previous 1 and 2 periods for 'close' and 'volume'.

    Args:
        df (pd.DataFrame): Input DataFrame with columns ['close', 'volume'].

    Returns:
        pd.DataFrame: DataFrame with lag features added.
    """
    try:
        # Create a copy of the DataFrame to avoid modifying the original slice
        df = df.copy()

        # Ensure the necessary columns are present
        required_columns = ['close', 'volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Input DataFrame must contain the columns: {', '.join(required_columns)}")

        # Add lag features
        df['close_lag_1'] = df['close'].shift(1)
        df['close_lag_2'] = df['close'].shift(2)
        df['volume_lag_1'] = df['volume'].shift(1)
        df['volume_lag_2'] = df['volume'].shift(2)

        # Drop rows with NaN values generated during calculations
        df = df.dropna()

        return df

    except Exception as e:
        print(f"Error adding lag features: {e}")
        return None

def add_future_close_and_label(df):
    """
    Adds a 'future_close' column which is the next bar's close (shifted by -1),
    and a 'label' column which is 1 if future_close > close else 0.
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

        # Add label column
        df['label'] = (df['future_close'] > df['close']).astype(int)

        # Drop the last row with NaN in future_close
        df = df.dropna()

        return df

    except Exception as e:
        print(f"Error adding future_close and label: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Extended example data
    data = {
        "open_time": [1591258320000 + i * 60000 for i in range(30)],
        "open": [100 + i for i in range(30)],
        "high": [101 + i for i in range(30)],
        "low": [99 + i for i in range(30)],
        "close": [100 + i + (i % 2) for i in range(30)],
        "volume": [200 + (i * 10) for i in range(30)],
        "close_time": [1591258379999 + i * 60000 for i in range(30)],
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Process DataFrame
    processed_df = process_dataframe(df)

    if processed_df is not None:
        # Add technical indicators
        df_with_indicators = add_technical_indicators(processed_df)

        if df_with_indicators is not None:
            # Add lag features
            df_with_lag_features = add_lag_features(df_with_indicators)

            if df_with_lag_features is not None:
                # Add future_close and label
                df_with_labels = add_future_close_and_label(df_with_lag_features)

                # Output the DataFrame with future_close and label
                if df_with_labels is not None:
                    print(df_with_labels)
