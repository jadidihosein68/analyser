from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

def train_and_save_model(df, features, model_path):
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
