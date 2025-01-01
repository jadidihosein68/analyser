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


def add_technical_indicators(df):
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
