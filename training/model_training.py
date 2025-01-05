from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

def train_and_save_models(df, features, models_dir, model_type="random_forest"):
    """
    Train and save models based on the selected model type.
    
    Args:
        df (DataFrame): The dataset containing features and labels.
        features (list): List of feature column names.
        models_dir (str): Directory path to save the models.
        model_type (str): The type of model to train. Options: 'random_forest', 'logistic_regression', 'svm', 'xgboost'.
    """
    try:
        # Split dataset into training and testing
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
        X_train, y_train = train_df[features], train_df['label']
        X_test, y_test = test_df[features], test_df['label']

        # Initialize the selected model
        if model_type == "random_forest":
            model = RandomForestClassifier(random_state=42)
        elif model_type == "logistic_regression":
            model = LogisticRegression(random_state=42, max_iter=1000)
        elif model_type == "svm":
            model = SVC(random_state=42, probability=True)
        elif model_type == "xgboost":
            model = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        # Train the model
        model.fit(X_train, y_train)

        # Evaluate the model
        y_pred = model.predict(X_test)
        print(f"Model Type: {model_type}")
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("Classification Report:")
        print(classification_report(y_test, y_pred))

        # Save the model
        model_path = f"{models_dir}/{model_type}_model.joblib"
        dump(model, model_path)
        print(f"Model saved to {model_path}")

    except Exception as e:
        print(f"Error training and saving model: {e}")

# Example usage
# Assuming `df` is a pandas DataFrame and `features` is a list of feature columns
# train_and_save_models(df, features, "./models", model_type="xgboost")
