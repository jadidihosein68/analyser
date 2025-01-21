from flask import Blueprint, request, jsonify
from aimodel.data_preparation_pipeline import DataPreparationPipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the Blueprint
model_bp = Blueprint('model', __name__)


@model_bp.route('/model/test_indicator/<int:model_id>', methods=['POST'])
def test_indicator(model_id):
    """
    Generate indicators and return the dataset with total record count.
    """
    try:
        # Initialize DataPreparationPipeline
        builder = DataPreparationPipeline(model_config_id=model_id)
        builder.fetch_model_config()
        
        # Fetch and process timeseries data
        df = builder.fetch_timeseries_data()
        df_with_indicators = builder.generate_indicators(df)
        
        # Log total records
        total_records = len(df_with_indicators)
        logging.info(f"Total records after generating indicators: {total_records}")
        
        # Convert dataset to JSON and return
        result = df_with_indicators.to_dict(orient="records")
        return jsonify({
            "status": "success", 
            "total_records": total_records, 
            "data": result,
            "features_config":builder.model_config.features_config
        }), 200
    except Exception as e:
        logging.error("Error in test_indicator API.", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500



@model_bp.route('/model/test_labeling/<int:model_id>', methods=['POST'])
def test_labeling(model_id):
    """
    Apply labeling and return the labeled dataset with total record count and label distribution.
    """
    try:
        # Initialize DataPreparationPipeline
        builder = DataPreparationPipeline(model_config_id=model_id)
        builder.fetch_model_config()
        
        # Fetch, process data, and generate indicators
        df = builder.fetch_timeseries_data()
        df_with_indicators = builder.generate_indicators(df)
        
        # Apply labeling
        labeled_df = builder.apply_labeling(df_with_indicators)
        
        # Log total records and label distribution
        total_records = len(labeled_df)
        label_distribution = labeled_df["label"].value_counts().to_dict()
        logging.info(f"Total records after labeling: {total_records}")
        logging.info(f"Label distribution: {label_distribution}")
        
        # Convert dataset to JSON and return
        result = labeled_df.to_dict(orient="records")
        return jsonify({
            "status": "success",
            "total_records": total_records,
            "label_distribution": label_distribution,
            "label_config":builder.model_config.label_config
        }), 200
    except Exception as e:
        logging.error("Error in test_labeling API.", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500




@model_bp.route('/model/build/<int:model_id>', methods=['POST'])
def build_model(model_id):
    """
    API endpoint to build a model.

    Args:
        model_id (int): The ID of the model configuration.

    Returns:
        JSON response with status and message.
    """
    try:
        # Initialize the pipeline and build the model
        pipeline = DataPreparationPipeline(model_config_id=model_id)
        pipeline.build_model()

        # Return success response
        return jsonify({"status": "success", "message": "Model built and saved successfully."}), 200
    except Exception as e:
        # Log the error and return failure response
        logging.error("Error building model via API.", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

