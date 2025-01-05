import unittest
import pandas as pd
from training.data_processing import calculate_rsi, calculate_macd, add_lagged_features, add_technical_indicators

class TestDataProcessing(unittest.TestCase):
    def setUp(self):
        # Hardcoded dataset for testing
        self.test_data = pd.DataFrame({
            "close": [
                1.2, 1.3, 1.25, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65,
                1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05, 2.1, 2.15,
                2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6, 2.65
            ],
            "volume": [
                100, 110, 120, 130, 140, 150, 160, 170, 180, 190,
                200, 210, 220, 230, 240, 250, 260, 270, 280, 290,
                300, 310, 320, 330, 340, 350, 360, 370, 380, 390
            ]
        })

    def test_calculate_rsi(self):
        # Test RSI calculation
        expected_rsi = [None] * 13 + [
            93.333333, 93.750000, 93.333333, 100.000000, 100.000000,
            100.000000, 100.000000, 100.000000, 100.000000, 100.000000,
            100.000000, 100.000000, 100.000000, 100.000000, 100.000000,
        ]
        rsi = calculate_rsi(self.test_data)
        
        '''
        print("Calculated RSI:")
        print(rsi)
        '''
        self.assertEqual(len(rsi), len(self.test_data), "RSI length mismatch")
        self.assertIsNotNone(rsi.iloc[-1], "RSI calculation failed")
        # Assert RSI values
        '''print(rsi.head(20))'''
        for i in range(len(expected_rsi)):
            if expected_rsi[i] is None:
                self.assertTrue(pd.isnull(rsi.iloc[i]), f"RSI at index {i} should be NaN")
            else:
                self.assertAlmostEqual(
                    rsi.iloc[i], expected_rsi[i], 2, f"RSI at index {i} is incorrect"
                )


    def test_calculate_macd(self):
        # Test MACD and Signal Line calculation
        macd, signal_line = calculate_macd(self.test_data)
        self.assertEqual(len(macd), len(self.test_data), "MACD length mismatch")
        self.assertEqual(len(signal_line), len(self.test_data), "Signal Line length mismatch")
        self.assertIsNotNone(macd.iloc[-1], "MACD calculation failed")
        self.assertIsNotNone(signal_line.iloc[-1], "Signal Line calculation failed")

    def test_add_lagged_features(self):
        # Test adding lagged features
        lagged_data = add_lagged_features(self.test_data.copy(), ['close', 'volume'], lags=2)
        
        '''
        print("Lagged DataFrame:")
        print(lagged_data.head())  # Debugging output
        '''

        self.assertIn("close_lag_1", lagged_data.columns, "Lagged feature 'close_lag_1' missing")
        self.assertIn("volume_lag_2", lagged_data.columns, "Lagged feature 'volume_lag_2' missing")
        
        # Validate the NaN values for the initial rows
        self.assertTrue(pd.isnull(lagged_data.iloc[0]["close_lag_1"]), "First row's 'close_lag_1' should be NaN")
        self.assertTrue(pd.isnull(lagged_data.iloc[0]["close_lag_2"]), "First row's 'close_lag_2' should be NaN")
        self.assertTrue(pd.isnull(lagged_data.iloc[1]["close_lag_2"]), "Second row's 'close_lag_2' should be NaN")

        # Validate that lagged values exist for rows beyond the lag count
        self.assertEqual(lagged_data.iloc[1]["close_lag_1"], 1.20, "Second row's 'close_lag_1' value is incorrect")
        self.assertEqual(lagged_data.iloc[2]["close_lag_2"], 1.20, "Third row's 'close_lag_2' value is incorrect")
        self.assertIsNotNone(lagged_data.iloc[-1]["close_lag_1"], "Last row's 'close_lag_1' value should not be None")

    def test_add_technical_indicators(self):
        # Test full pipeline
        enriched_data = add_technical_indicators(self.test_data.copy())
        self.assertIn("RSI_14", enriched_data.columns, "RSI_14 column missing")
        self.assertIn("MACD", enriched_data.columns, "MACD column missing")
        self.assertIn("Signal_Line", enriched_data.columns, "Signal Line column missing")
        self.assertIn("close_lag_1", enriched_data.columns, "Lagged feature 'close_lag_1' missing")
        self.assertFalse(enriched_data.empty, "Enriched DataFrame is empty after processing")
        self.assertIsNotNone(enriched_data.iloc[-1]["MACD"], "MACD value calculation failed")
        self.assertIsNotNone(enriched_data.iloc[-1]["Signal_Line"], "Signal Line calculation failed")

if __name__ == "__main__":
    unittest.main()
