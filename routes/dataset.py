from flask import Blueprint, jsonify, request
from common.db_adapter import get_ohlcv_data_collections, save_ohlcv_data_collection

# Define the blueprint
dataset_bp = Blueprint("dataset", __name__)

@dataset_bp.route("/data_collections", methods=["GET"])
def fetch_all_data_collections():
    """
    Fetch all records from the dataset table.

    Returns:
        JSON response containing all records.
    """
    try:
        records = get_ohlcv_data_collections()
        result = [
            {
                "id": record.id,
                "name_of_dataset": record.name_of_dataset,
                "symbol": record.symbol,
                "interval": record.interval,
                "startdate": record.startdate,
                "enddate": record.enddate,
                "dataset_type": record.dataset_type,
                "total_records": record.total_records,
            }
            for record in records
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch records: {e}"}), 500


@dataset_bp.route("/data_collection", methods=["POST"])
def add_data_collection():
    """
    Add a new dataset record.

    Returns:
        JSON response confirming the operation's success or failure.
    """
    try:
        data = request.get_json()
        required_fields = [
            "name_of_dataset", "symbol", "interval", 
            "startdate", "enddate", "dataset_type", "total_records"
        ]

        # Validate input
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing fields in request. Required: {required_fields}"}), 400

        # Save to the database using adapter
        save_ohlcv_data_collection(
            name_of_dataset=data["name_of_dataset"],
            symbol=data["symbol"],
            interval=data["interval"],
            startdate=data["startdate"],
            enddate=data["enddate"],
            dataset_type=data["dataset_type"],
            total_records=data["total_records"]
        )

        return jsonify({"message": "Record added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add record: {e}"}), 500
