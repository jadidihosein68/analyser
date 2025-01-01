def add_future_close_and_multiclass_label(df):
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
