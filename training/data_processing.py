import pandas as pd

def process_dataframe(df):
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

# Function to calculate RSI
def calculate_rsi(df, column='close', period=14):
    delta = df[column].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    '''
    print("Delta:", delta.tail())
    print("Gain:", gain.tail())
    print("Loss:", loss.tail())
    print("Average Gain:", avg_gain.tail())
    print("Average Loss:", avg_loss.tail())
    print("RSI:", rsi.tail())
    '''
    return rsi

# Function to calculate MACD and Signal Line
def calculate_macd(df, column='close', short_span=12, long_span=26, signal_span=9):
    ema_12 = df[column].ewm(span=short_span, adjust=False).mean()
    ema_26 = df[column].ewm(span=long_span, adjust=False).mean()
    macd = ema_12 - ema_26
    signal_line = macd.ewm(span=signal_span, adjust=False).mean()

    return macd, signal_line

# Function to add lagged features
def add_lagged_features(df, columns, lags):
    for column in columns:
        for lag in range(1, lags + 1):
            df[f"{column}_lag_{lag}"] = df[column].shift(lag)
    return df

# Main function to add technical indicators
def add_technical_indicators(df):
    try:
        df = df.copy()

        # Add RSI
        df['RSI_14'] = calculate_rsi(df)

        # Add MACD and Signal Line
        df['MACD'], df['Signal_Line'] = calculate_macd(df)

        # Debugging MACD calculations
        print("Debug MACD Calculations:")
        print(f"EMA_12: {df['MACD'].iloc[-1] if not df.empty else 'N/A'}")
        print(f"Signal Line: {df['Signal_Line'].iloc[-1] if not df.empty else 'N/A'}")

        # Add lagged features
        df = add_lagged_features(df, ['close', 'volume'], lags=2)

        # Drop rows with NaN values introduced by rolling or lagging
        df = df.dropna()

        return df

    except Exception as e:
        print(f"Error adding technical indicators: {e}")
        return None

