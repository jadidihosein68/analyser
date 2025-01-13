from flask import Blueprint, jsonify, request
from api.binance_service import fetch_ohlcv_data
from common.db_adapter import get_latest_data_per_symbol, get_total_records_per_symbol, save_ohlcv_data


# Create a Blueprint for OHLCV-related routes
ohlcv_bp = Blueprint("ohlcv", __name__)


@ohlcv_bp.route("/fetch_and_store_ohlcv", methods=["GET"])
def fetch_and_store_ohlcv():
    """
    API endpoint to fetch OHLCV data from Binance and store it in the database.
    Query Parameters:
        - symbol (str): Trading pair (e.g., BTCUSDT).
        - interval (str): Time interval (e.g., 1m, 5m, 1h). Default is "1m".
        - limit (int): Number of candlesticks to fetch. Default is 5.
    """
    try:
        # Extract query parameters
        symbol = request.args.get("symbol", type=str)
        interval = request.args.get("interval", default="1m", type=str)
        limit = request.args.get("limit", default=5, type=int)

        # Validate required parameter
        if not symbol:
            return jsonify({"error": "Missing required parameter: symbol"}), 400

        # Fetch OHLCV data from Binance
        data = fetch_ohlcv_data(symbol, interval, limit)

        # Check if data was fetched successfully
        if data is None:
            return jsonify({"error": "Failed to fetch OHLCV data"}), 500

        # Variables to track inserted records
        fetched_count = len(data)
        updated_count = 0

        # Save the fetched data to the database
        for entry in data:
            save_ohlcv_data(symbol, entry)
            updated_count += 1

        return jsonify({
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
            "fetched_records": fetched_count,
            "updated_records": updated_count,
            "message": "OHLCV data fetched and stored successfully."
        }), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@ohlcv_bp.route("/get_latest_ohlcv", methods=["GET"])
def get_latest_ohlcv():
    """
    API endpoint to fetch the latest OHLCV record for each symbol along with total record count.

    Returns:
        JSON response with latest OHLCV data and record count for each symbol.
    """
    try:
        latest_data = get_latest_data_per_symbol()
        total_records = get_total_records_per_symbol()

        # Merge results by symbol
        combined_data = {}
        for data in latest_data:
            combined_data[data["symbol"]] = {"latest_record": data, "total_records": 0}

        for record in total_records:
            if record["symbol"] in combined_data:
                combined_data[record["symbol"]]["total_records"] = record["total_records"]

        # Format response
        response = [{"symbol": symbol, **details} for symbol, details in combined_data.items()]

        return jsonify({"data": response}), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500






