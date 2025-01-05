def add_future_close_and_multiclass_label(df, positive_threshold=0.09, negative_threshold=-0.09):
    try:
        df = df.copy()
        df['future_close'] = df['close'].shift(-1)
        df['pct_change'] = (df['future_close'] - df['close']) / df['close'] * 100

        # Debugging: Print intermediate DataFrame with pct_change
        print("\nIntermediate DataFrame with pct_change:")
        print(df[['close', 'future_close', 'pct_change']])

        # Adjusted labeling logic
        df['label'] = df['pct_change'].apply(
            lambda x: 2 if x > positive_threshold else (0 if x < negative_threshold else 1)
        )

        df = df.dropna()
        df = df.drop(columns=['pct_change'])

        return df

    except Exception as e:
        print(f"Error adding future_close and labels: {e}")
        return None
