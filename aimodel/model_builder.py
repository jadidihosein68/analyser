import logging
from common.db_adapter import get_model_config_by_id, get_ohlcv_records_by_interval
from .technical_indicator_generator import TechnicalIndicatorGenerator
from .labeling_engine import LabelingEngine
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModelBuilder:
    def __init__(self, model_config_id):
        """
        Initialize the ModelBuilder with a model configuration ID.

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

    def build_model(self):
        """
        The main function to build the model by fetching the config, data, and generating indicators.

        Returns:
            pd.DataFrame: The DataFrame with indicators ready for training.
        """
        try:
            self.fetch_model_config()
            df = self.fetch_timeseries_data()
            df_with_indicators = self.generate_indicators(df)
            labeled_df = self.apply_labeling(df_with_indicators)
            return labeled_df
        except Exception as e:
            logging.error("Error building the model", exc_info=True)
            raise e
