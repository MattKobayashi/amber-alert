import json
import os
import sys 
import unittest
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock, call, ANY

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class Testmain(unittest.TestCase):
    """Test cases for the Amber Electric price monitoring application."""

    def setUp(self):
        """Set up test fixtures before each test."""
        # Create patches
        self.env_patcher = patch("os.environ", {
            "AMBER_SITE_ID": "test-site-id",
            "WEBHOOK_URL": "https://test-webhook.com",
            "ALERT_HIGH": "30.0",
            "ALERT_LOW": "5.0",
            "DATA_RES": "30min"
        })

        self.isfile_patcher = patch("os.path.isfile")
        self.json_dump_patcher = patch("json.dump")
        self.json_load_patcher = patch("json.load")
        self.get_patcher = patch("requests.get")
        self.post_patcher = patch("requests.post")

        # Start patches
        self.mock_env = self.env_patcher.start()
        self.mock_isfile = self.isfile_patcher.start()
        self.mock_json_dump = self.json_dump_patcher.start()
        self.mock_json_load = self.json_load_patcher.start()
        self.mock_get = self.get_patcher.start()
        self.mock_post = self.post_patcher.start()

        # Clean up any imported modules
        if 'main' in sys.modules:
            del sys.modules['main']

    def tearDown(self):
        """Tear down test fixtures after each test."""
        # Stop all patches
        self.env_patcher.stop()
        self.isfile_patcher.stop()
        self.json_dump_patcher.stop()
        self.json_load_patcher.stop()
        self.get_patcher.stop()
        self.post_patcher.stop()

        # Clean up any imported modules
        if 'main' in sys.modules:
            del sys.modules['main']

    def test_create_price_data_file(self):
        """Test creation of price data file if it doesn't exist."""
        # Setup
        self.mock_isfile.return_value = False
        self.mock_json_load.return_value = {"lastPrice": 0}

        mock_file = mock_open(read_data="test-api-key")
        with patch("builtins.open", mock_file) as mock_open_handle:
            import main

            # Assertions
            self.mock_isfile.assert_called_once_with("data/priceData.json")
            # Check that json.dump was called with the right data, don't worry about exact file handle
            self.mock_json_dump.assert_any_call({"lastPrice": 0}, ANY)

    def test_high_price_alert(self):
        """Test high price alert is triggered when price exceeds threshold."""
        # Setup
        self.mock_env["ALERT_HIGH"] = "30.0"
        self.mock_env["ALERT_LOW"] = "0.0"

        self.mock_isfile.return_value = True
        self.mock_json_load.return_value = {"lastPrice": 20.0}  # Below high threshold

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 35.0}]  # Above high threshold
        self.mock_get.return_value = mock_response

        # Mock file open
        mock_file = mock_open(read_data="test-api-key")
        with patch("builtins.open", mock_file):
            import main

            # Verify webhook called with high price alert
            self.mock_post.assert_called_once()
            args, kwargs = self.mock_post.call_args
            self.assertEqual(args[0], "https://test-webhook.com")
            self.assertIn("Power price is above 30.0c/kWh", kwargs["data"]["content"])

    def test_low_price_alert(self):
        """Test low price alert is triggered when price falls below threshold."""
        # Setup
        self.mock_isfile.return_value = True
        self.mock_json_load.return_value = {"lastPrice": 10.0}  # Above low threshold

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 3.0}]  # Below low threshold
        self.mock_get.return_value = mock_response

        # Mock file open
        mock_file = mock_open(read_data="test-api-key")
        with patch("builtins.open", mock_file):
            import main

            # Verify webhook called with low price alert
            self.mock_post.assert_called_once()
            args, kwargs = self.mock_post.call_args
            self.assertEqual(args[0], "https://test-webhook.com")
            self.assertIn("Power price is below 5.0c/kWh", kwargs["data"]["content"])

    def test_negative_price_alert(self):
        """Test negative price alert is triggered."""
        # Setup
        self.mock_isfile.return_value = True
        self.mock_json_load.return_value = {"lastPrice": 2.0}  # Positive price

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": -5.0}]  # Negative price
        self.mock_get.return_value = mock_response

        # Mock file open
        mock_file = mock_open(read_data="test-api-key")
        with patch("builtins.open", mock_file):
            import main

            # Verify webhook called with negative price alert
            self.mock_post.assert_called_once()
            args, kwargs = self.mock_post.call_args
            self.assertEqual(args[0], "https://test-webhook.com")
            self.assertIn("Power prices are negative", kwargs["data"]["content"])

    def test_return_to_normal_alert(self):
        """Test normal price alert when price returns to normal range."""
        # Setup
        self.mock_isfile.return_value = True
        self.mock_json_load.return_value = {"lastPrice": 35.0}  # Above high threshold

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 20.0}]  # Normal price range
        self.mock_get.return_value = mock_response

        # Mock file open
        mock_file = mock_open(read_data="test-api-key")
        with patch("builtins.open", mock_file):
            import main

            # Verify webhook called with return to normal alert
            self.mock_post.assert_called_once()
            args, kwargs = self.mock_post.call_args
            self.assertEqual(args[0], "https://test-webhook.com")
            self.assertIn("Power prices have returned to normal", kwargs["data"]["content"])

    def test_no_alert_when_price_unchanged(self):
        """Test no alerts are sent when price remains in same category."""
        # Setup
        self.mock_isfile.return_value = True
        self.mock_json_load.return_value = {"lastPrice": 20.0}  # Normal price

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 25.0}]  # Still normal price
        self.mock_get.return_value = mock_response

        # Mock file open
        mock_file = mock_open(read_data="test-api-key")
        with patch("builtins.open", mock_file):
            import main

            # Verify no webhook calls
            self.mock_post.assert_not_called()

    def test_price_data_update(self):
        """Test price data is updated in the JSON file."""
        # Setup mocks
        self.mock_isfile.return_value = True
        self.mock_json_load.return_value = {"lastPrice": 20.0}

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 25.0}]
        self.mock_get.return_value = mock_response

        # Mock file open
        mock_file = mock_open(read_data="test-api-key")
        with patch("builtins.open", mock_file):
            import main

            # Use assert_any_call with ANY for the file handle
            expected_data = {"lastPrice": 25.0}
            self.mock_json_dump.assert_any_call(expected_data, ANY)


if __name__ == "__main__":
    unittest.main()
