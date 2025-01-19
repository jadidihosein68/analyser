from flask import Blueprint, request, jsonify
from aimodel.model_builder import ModelBuilder
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the Blueprint
model_bp = Blueprint('model', __name__)

@model_bp.route('/model/build/<int:model_id>', methods=['POST'])
def build_model(model_id):
    """
    Build a model using the given model ID.

    Args:
        model_id (int): ID of the model configuration.

    Returns:
        JSON response with the resulting DataFrame or an error message.
    """
    try:
        builder = ModelBuilder(model_config_id=model_id)
        df_ready = builder.build_model()
        result = df_ready.to_dict(orient="records")
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        logging.error("Error building model via API.", exc_info=True)
        return jsonify({"error": str(e)}), 500
