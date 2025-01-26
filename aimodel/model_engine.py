import logging
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.utils.multiclass import unique_labels


class ModelEngine:
    def __init__(self, model_config):
        self.method = model_config["method"]
        self.params = self._parse_params(model_config["params"])
        self.model = None

    def _parse_params(self, params_list):
        parsed_params = {}
        for param in params_list:
            for key, value in param.items():
                parsed_params[key] = self._convert_value(value)
        return parsed_params

    def _convert_value(self, value):
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            if value.lower() == "none":
                return None
            if value.lower() in ["true", "false"]:
                return value.lower() == "true"
            return value

    def create_model(self):
        try:
            model_creation_methods = {
                "randomForest": self._create_random_forest,
                "logisticRegression": self._create_logistic_regression,
                "svc": self._create_svc,
                "xgboost": self._create_xgboost,
            }

            if self.method not in model_creation_methods:
                raise ValueError(f"Unsupported model method: {self.method}")

            # Call the appropriate model creation method
            self.model = model_creation_methods[self.method]()
            logging.info(f"Model {self.method} created with parameters: {self.params}")
            assert self.model is not None, "Model creation failed."
            return self.model
        except Exception as e:
            logging.error("Error creating model", exc_info=True)
            raise e

    def _create_random_forest(self):
        return RandomForestClassifier(**self.params)

    def _create_logistic_regression(self):
        return LogisticRegression(**self.params)

    def _create_svc(self):
        return SVC(**self.params)

    def _create_xgboost(self):
        return XGBClassifier(**self.params)

    def train_model(self, X_train, y_train):
        try:
            if self.model is None:
                raise ValueError("Model has not been created. Call `create_model` first.")
            
            self.model.fit(X_train, y_train)
            logging.info(f"Model {self.method} trained successfully.")
        except Exception as e:
            logging.error("Error training the model", exc_info=True)
            raise e

    def test_model(self, X_test, y_test):
        """
        Test the model on the testing dataset, log performance metrics, and return the results in an object.
        """
        try:
            if self.model is None:
                raise ValueError("Model has not been trained. Call `train_model` first.")

            y_pred = self.model.predict(X_test)

            # Handle label mapping for XGBoost if necessary
            if self.method == "xgboost":
                reverse_label_mapping = {0: -1, 1: 0, 2: 1}
                y_pred = pd.Series(y_pred).map(reverse_label_mapping).to_numpy()
                y_test = y_test.map(reverse_label_mapping)

            # Calculate accuracy and classification report
            accuracy = accuracy_score(y_test, y_pred)
            classification_rep = classification_report(y_test, y_pred, output_dict=True)
            logging.info(f"Model Accuracy: {accuracy:.4f}")
            logging.info("Classification Report:")
            logging.info(classification_rep)

            # Generate confusion matrix
            all_labels = sorted(unique_labels(y_test, y_pred))
            conf_matrix = confusion_matrix(y_test, y_pred, labels=all_labels)
            logging.info("Confusion Matrix:")
            logging.info(conf_matrix)

            # Optional: Calculate ROC-AUC for binary classification
            roc_auc = None
            if len(all_labels) == 2:
                roc_auc = roc_auc_score(y_test, y_pred)
                logging.info(f"ROC-AUC Score: {roc_auc:.4f}")

            # Return the results in an object
            return {
                "classification_rep": classification_rep,
                "conf_matrix": conf_matrix,
                "roc_auc": roc_auc
            }

        except Exception as e:
            logging.error("Error testing the model", exc_info=True)
            raise e

    def save_model(self, file_path):
        try:
            if self.model is None:
                raise ValueError("Model has not been trained. Call `train_model` first.")

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            joblib.dump(self.model, file_path)
            logging.info(f"Trained model saved to: {file_path}")
        except Exception as e:
            logging.error("Error saving the model", exc_info=True)
            raise e

    def load_model(self, file_path):
        try:
            self.model = joblib.load(file_path)
            logging.info(f"Model loaded from: {file_path}")
            return self.model
        except Exception as e:
            logging.error("Error loading the model", exc_info=True)
            raise e
