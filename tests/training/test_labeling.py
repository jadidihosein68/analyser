import unittest
import pandas as pd
from training.labeling import add_future_close_and_multiclass_label

class TestAddFutureCloseAndMulticlassLabel(unittest.TestCase):
    def test_labeling(self):
        # Input data
        data = {
            'close': [1.2, 1.3, 1.25, 1.35, 1.4, 1.45]
        }
        df = pd.DataFrame(data)

        # Expected output data
        expected_data = {
            'close': [1.2, 1.3, 1.25, 1.35, 1.4],  # Last row dropped due to no future_close
            'future_close': [1.3, 1.25, 1.35, 1.4, 1.45],
            'label': [2, 0, 2, 2, 2]  # Derived from pct_change
        }
        expected_df = pd.DataFrame(expected_data)

        # Call the function
        result_df = add_future_close_and_multiclass_label(df , positive_threshold=0.1, negative_threshold=-0.1)

        # Debug output
        print("Result DataFrame:")
        print(result_df)
        print("\nExpected DataFrame:")
        print(expected_df)

        # Check equality of resulting DataFrame and expected DataFrame
        pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected_df)

if __name__ == '__main__':
    unittest.main()
