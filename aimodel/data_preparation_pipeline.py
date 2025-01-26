import logging
from common.db_adapter import get_model_config_by_id, get_ohlcv_records_by_interval
from .technical_indicator_generator import TechnicalIndicatorGenerator
from .labeling_engine import LabelingEngine
from .model_engine import ModelEngine
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def map_labels(y):
        label_mapping = {-1: 0, 0: 1, 1: 2}
        return y.map(label_mapping)

class DataPreparationPipeline:
    def __init__(self, model_config_id):
        """
        Initialize the DataPreparationPipeline with a model configuration ID.

        Args:
            model_config_id (int): The ID of the model configuration.
        """
        self.model_config_id = model_config_id
        self.model_config = None

    def fetch_model_config(self):
        """
        Fetch the model configuration using the provided ID.

        Raises:
            ValueError: If the model configuration is not found.
        """
        try:
            self.model_config = get_model_config_by_id(self.model_config_id)
            if not self.model_config:
                raise ValueError(f"Model config with ID {self.model_config_id} not found.")
            logging.info(f"Model config fetched: {self.model_config}")
        except Exception as e:
            logging.error("Error fetching model configuration", exc_info=True)
            raise e

    def fetch_timeseries_data(self):
        """
        Fetch time series data based on the training dataset config in the model configuration.

        Returns:
            pd.DataFrame: A DataFrame containing OHLCV data.
        """
        try:
            training_config = self.model_config.training_dataset_config

            # Validate the training dataset configuration
            if not training_config or not isinstance(training_config, dict):
                raise ValueError("Invalid or missing training_dataset_config in model configuration.")

            # Map the correct keys
            symbol = training_config["symbol"]
            start_time = training_config["startdate"]  # Updated to match the JSON contract
            end_time = training_config["enddate"]      # Updated to match the JSON contract
            interval = int(training_config["interval"].rstrip('m')) 

            records = get_ohlcv_records_by_interval(symbol, start_time, end_time, interval)
            if not records:
                raise ValueError("No time series data found for the given configuration.")

            # Convert records to DataFrame
            data = [
                {
                    "open_time": record.open_time,
                    "open": record.open,
                    "high": record.high,
                    "low": record.low,
                    "close": record.close,
                    "volume": record.volume,
                    "time": record.close_time,
                    "close_time": record.close_time,
                }
                for record in records
            ]
            df = pd.DataFrame(data)
            logging.info(f"Time series data fetched with {len(df)} rows.")
            return df
        except KeyError as e:
            logging.error(f"Missing key in training_dataset_config: {e}, Config: {self.model_config.training_dataset_config}")
            raise e
        except Exception as e:
            logging.error("Error fetching time series data", exc_info=True)
            raise e

    def generate_indicators(self, df):
        """
        Generate technical indicators for the provided DataFrame.

        Args:
            df (pd.DataFrame): The OHLCV DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with technical indicators added.
        """
        try:
            # Extract the list of indicators from features_config
            if not hasattr(self.model_config, 'features_config') or not isinstance(self.model_config.features_config, dict):
                raise ValueError("Invalid features_config in the model configuration.")

            indicators = self.model_config.features_config.get("indicators", [])
            if not isinstance(indicators, list):
                raise ValueError("The 'indicators' field in features_config must be a list.")

            # Pass the indicators list to the TechnicalIndicatorGenerator
            generator = TechnicalIndicatorGenerator(indicators)
            df_with_indicators = generator.generate_indicators(df)
            logging.info("Technical indicators generated successfully.")
            return df_with_indicators
        except Exception as e:
            logging.error("Error generating indicators", exc_info=True)
            raise e

    def apply_labeling(self, df):
        """
        Apply labeling to the DataFrame using the labeling configuration.

        Args:
            df (pd.DataFrame): The DataFrame with technical indicators.

        Returns:
            pd.DataFrame: The labeled DataFrame.
        """
        try:
            label_config = self.model_config.label_config
            labeling_engine = LabelingEngine(label_config)
            labeled_df = labeling_engine.apply_labeling_strategy(df)

            # Log label distribution
            label_counts = labeled_df['label'].value_counts().to_dict()
            logging.info(f"Label distribution: {label_counts}")

            logging.info("Labeling applied successfully.")
            return labeled_df
        except Exception as e:
            logging.error("Error applying labeling", exc_info=True)
            raise e

    def build_model(self, test_data=None):
        """
        Build and train a machine learning model, and return the logs.

        Args:
            test_data (tuple or None): External test dataset as (X_test, y_test) or None for auto-splitting.

        Returns:
            dict: Logs summarizing the build process, including data summary, metrics, and execution steps.
        """
        try:
            # Initialize logging structure
            build_logs = {
                "data_summary": {},
                "model_metrics": {},
                "confusion_matrix": None,
                "execution_summary": {"steps": []}
            }

            # Fetch and prepare model configuration
            self.fetch_model_config()
            build_logs["execution_summary"]["steps"].append("Model configuration fetched successfully.")

            # Fetch and process time series data
            df = self.fetch_timeseries_data()
            build_logs["execution_summary"]["steps"].append(f"Time series data fetched with {len(df)} rows.")
            df_with_indicators = self.generate_indicators(df)
            build_logs["execution_summary"]["steps"].append("Technical indicators generated successfully.")

            # Apply labeling
            labeled_df = self.apply_labeling(df_with_indicators)
            build_logs["execution_summary"]["steps"].append("Labeling applied successfully.")
            build_logs["data_summary"]["label_distribution"] = labeled_df["label"].value_counts().to_dict()

            # Prepare features and labels
            feature_columns = [col for col in labeled_df.columns if col not in ["label", "open_time", "close_time"]]
            X, y = labeled_df[feature_columns], labeled_df["label"]

            # Stratified splitting or use external test data
            if test_data is None:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )
                logging.info(f"Training label distribution: {y_train.value_counts().to_dict()}")
                logging.info(f"Testing label distribution: {y_test.value_counts().to_dict()}")
                build_logs["data_summary"]["training_label_distribution"] = y_train.value_counts().to_dict()
                build_logs["data_summary"]["testing_label_distribution"] = y_test.value_counts().to_dict()
            else:
                X_train, X_test, y_train, y_test = X, test_data[0], y, test_data[1]
                logging.info(f"Using external test dataset: Training samples={X_train.shape[0]}, Testing samples={X_test.shape[0]}")
                build_logs["execution_summary"]["steps"].append(f"Using external test dataset with {X_train.shape[0]} training samples and {X_test.shape[0]} testing samples.")

            # Map labels for XGBoost compatibility if required
            if self.model_config.model_config["method"] == "xgboost":
                logging.info("Mapping labels for XGBoost compatibility.")
                build_logs["execution_summary"]["steps"].append("Mapping labels for XGBoost compatibility.")
                y_train = map_labels(y_train)
                y_test = map_labels(y_test)

            # Train and test the model
            model_engine = ModelEngine(self.model_config.model_config)
            model_engine.create_model()
            build_logs["execution_summary"]["steps"].append("Model created successfully.")

            model_engine.train_model(X_train, y_train)
            build_logs["execution_summary"]["steps"].append("Model trained successfully.")

            # Test the model and collect metrics
            test_results = model_engine.test_model(X_test, y_test)
            build_logs["model_metrics"]["classification_report"] = test_results["classification_rep"]
            build_logs["confusion_matrix"] = test_results["conf_matrix"].tolist() if isinstance(test_results["conf_matrix"], np.ndarray) else test_results["conf_matrix"]

            if test_results["roc_auc"] is not None:
                build_logs["model_metrics"]["roc_auc"] = test_results["roc_auc"]

            # Save the model
            model_file_path = f"models/model_{self.model_config_id}.joblib"
            model_engine.save_model(model_file_path)
            build_logs["execution_summary"]["steps"].append(f"Model saved successfully at {model_file_path}.")

            # Ensure all logs are JSON-serializable
            build_logs = self._make_json_serializable(build_logs)

            return build_logs

        except Exception as e:
            logging.error("Error building the model", exc_info=True)
            raise e

    def _make_json_serializable(self, logs):
        """
        Convert any non-serializable objects in logs to JSON-serializable formats.

        Args:
            logs (dict): Dictionary containing logs to sanitize.

        Returns:
            dict: Sanitized logs with all objects JSON-serializable.
        """
        for key, value in logs.items():
            if isinstance(value, dict):
                logs[key] = self._make_json_serializable(value)
            elif isinstance(value, np.ndarray):
                logs[key] = value.tolist()
            elif isinstance(value, (np.float32, np.float64)):
                logs[key] = float(value)
            elif isinstance(value, (np.int32, np.int64)):
                logs[key] = int(value)
        return logs