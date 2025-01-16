from flask import Blueprint, request, jsonify
from common.db_adapter import (
    create_model_config,
    get_model_config_by_id,
    list_model_configs,
    update_model_config,
    delete_model_config
)

# Define the Blueprint
model_config_bp = Blueprint('model_config', __name__)

# Create a new model config
@model_config_bp.route('/model_config', methods=['POST'])
def create_model_config_api():
    """
    Create a new model config.
    """
    data = request.json
    try:
        model_config = create_model_config(data)
        return jsonify({"message": "Model config created successfully", "id": model_config.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Get a specific model config by ID
@model_config_bp.route('/model_config/<int:id>', methods=['GET'])
def get_model_config_api(id):
    """
    Retrieve a specific model config by its ID.
    """
    try:
        model_config = get_model_config_by_id(id)
        if model_config:
            return jsonify({
                "id": model_config.id,
                "model_name": model_config.model_name,
                "model_type": model_config.model_type,
                "model_config": model_config.model_config,
                "coin_symbol": model_config.coin_symbol,
                "training_dataset_name": model_config.training_dataset_name,
                "training_dataset_config": model_config.training_dataset_config,
                "features_config": model_config.features_config,
                "physical_location": model_config.physical_location,
                "file_name": model_config.file_name,
                "remark": model_config.remark,
                "accuracy_percent": model_config.accuracy_percent,
                "date_of_creation": model_config.date_of_creation,
                "label_config": model_config.label_config
            }), 200
        return jsonify({"error": "Model config not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# List all model configs
@model_config_bp.route('/model_config', methods=['GET'])
def list_model_configs_api():
    """
    List all model configs.
    """
    try:
        configs = list_model_configs()
        result = [{
            "id": config.id,
            "model_name": config.model_name,
            "model_type": config.model_type,
            "model_config": config.model_config,
            "coin_symbol": config.coin_symbol,
            "training_dataset_name": config.training_dataset_name,
            "training_dataset_config": config.training_dataset_config,
            "features_config": config.features_config,
            "physical_location": config.physical_location,
            "file_name": config.file_name,
            "remark": config.remark,
            "accuracy_percent": config.accuracy_percent,
            "date_of_creation": config.date_of_creation,
            "label_config": config.label_config
        } for config in configs]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update a specific model config by ID
@model_config_bp.route('/model_config/<int:id>', methods=['PUT'])
def update_model_config_api(id):
    """
    Update an existing model config by ID.
    """
    data = request.json
    try:
        model_config = update_model_config(id, data)
        if model_config:
            return jsonify({"message": "Model config updated successfully"}), 200
        return jsonify({"error": "Model config not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Delete a specific model config by ID
@model_config_bp.route('/model_config/<int:id>', methods=['DELETE'])
def delete_model_config_api(id):
    """
    Delete a model config by its ID.
    """
    try:
        success = delete_model_config(id)
        if success:
            return jsonify({"message": "Model config deleted successfully"}), 200
        return jsonify({"error": "Model config not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
