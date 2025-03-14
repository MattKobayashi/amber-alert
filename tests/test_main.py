import json
import os
import sys 
import unittest
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

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
        self.file_open_patcher = patch("builtins.open", new_callable=mock_open)
        self.json_dump_patcher = patch("json.dump")
        self.json_load_patcher = patch("json.load")
        self.get_patcher = patch("requests.get")
        self.post_patcher = patch("requests.post")
        
        # Start patches
        self.mock_env = self.env_patcher.start()
        self.mock_isfile = self.isfile_patcher.start()
        self.mock_file_open = self.file_open_patcher.start()
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
        self.file_open_patcher.stop()
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
        
        # Create a separate API key file mock
        api_key_mock = mock_open(read_data="test-api-key")
        with patch("builtins.open", api_key_mock):
            import main

        # Assertions
        self.mock_isfile.assert_called_once_with("data/priceData.json")
        self.mock_file_open.assert_called_with("data/priceData.json", "w", encoding="utf-8")
        self.mock_json_dump.assert_called_with({"lastPrice": 0}, self.mock_file_open())

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
        
        # Create a separate API key file mock
        api_key_mock = mock_open(read_data="test-api-key")
        with patch("builtins.open", api_key_mock):
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
        
        # Create a separate API key file mock
        api_key_mock = mock_open(read_data="test-api-key")
        with patch("builtins.open", api_key_mock):
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
        
        # Create a separate API key file mock
        api_key_mock = mock_open(read_data="test-api-key")
        with patch("builtins.open", api_key_mock):
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
        
        # Create a separate API key file mock
        api_key_mock = mock_open(read_data="test-api-key")
        with patch("builtins.open", api_key_mock):
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
        
        # Create a separate API key file mock
        api_key_mock = mock_open(read_data="test-api-key")
        with patch("builtins.open", api_key_mock):
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
        
        # Create a separate API key file mock
        api_key_mock = mock_open(read_data="test-api-key")
        with patch("builtins.open", api_key_mock):
            import main

        # Use assert_any_call instead of assert_called_with
        expected_data = {"lastPrice": 25.0}
        self.mock_json_dump.assert_any_call(expected_data, self.mock_file_open())


if __name__ == "__main__":
    unittest.main()
