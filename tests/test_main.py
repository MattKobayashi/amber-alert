import json
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class Testmain(unittest.TestCase):
    """Test cases for the Amber Electric price monitoring mainlication."""

    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.isfile")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_create_price_data_file(self, mock_env, mock_isfile, mock_file_open, mock_json_dump):
        """Test creation of price data file if it doesn't exist."""
        mock_isfile.return_value = False

        # Import the script
        with patch("requests.get"):  # Prevent actual API calls during import
            with patch("requests.post"):
                with patch("json.load") as mock_json_load:
                    mock_json_load.return_value = {"lastPrice": 0}
                    # Mock the API key file
                    with patch("builtins.open", mock_open(read_data="test-api-key")):
                        import main

        mock_isfile.assert_called_once_with("data/priceData.json")
        mock_file_open.assert_called_with("data/priceData.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_with({"lastPrice": 0}, mock_file_open())

    @patch("requests.post")
    @patch("requests.get")
    @patch("json.dump")
    @patch("json.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.isfile")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "0.0",
        "DATA_RES": "30min"
    })
    def test_high_price_alert(self, mock_env, mock_isfile, mock_file_open, 
                              mock_json_load, mock_json_dump, mock_get, mock_post):
        """Test high price alert is triggered when price exceeds threshold."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 20.0}  # Below high threshold

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 35.0}]  # Above high threshold
        mock_get.return_value = mock_response

        # Mock the API key file
        api_key_mock = mock_open(read_data="test-api-key")
        file_handler = patch("builtins.open", api_key_mock)

        with file_handler:
            # Import and run the app
            if 'main' in sys.modules:
                import importlib
                import main
                importlib.reload(main)
            else:
                import main

        # Verify webhook called with high price alert
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test-webhook.com")
        self.assertIn("Power price is above 30.0c/kWh", kwargs["data"]["content"])

    @patch("requests.post")
    @patch("requests.get")
    @patch("json.dump")
    @patch("json.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.isfile")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_low_price_alert(self, mock_env, mock_isfile, mock_file_open, 
                              mock_json_load, mock_json_dump, mock_get, mock_post):
        """Test low price alert is triggered when price falls below threshold."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 10.0}  # Above low threshold

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 3.0}]  # Below low threshold
        mock_get.return_value = mock_response

        # Mock the API key file
        api_key_mock = mock_open(read_data="test-api-key")
        file_handler = patch("builtins.open", api_key_mock)

        with file_handler:
            # Import and run the app
            if 'main' in sys.modules:
                import importlib
                import main
                importlib.reload(main)
            else:
                import main

        # Verify webhook called with low price alert
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test-webhook.com")
        self.assertIn("Power price is below 5.0c/kWh", kwargs["data"]["content"])

    @patch("requests.post")
    @patch("requests.get")
    @patch("json.dump")
    @patch("json.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.isfile")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_negative_price_alert(self, mock_env, mock_isfile, mock_file_open, 
                                  mock_json_load, mock_json_dump, mock_get, mock_post):
        """Test negative price alert is triggered."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 2.0}  # Positive price

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": -5.0}]  # Negative price
        mock_get.return_value = mock_response

        # Mock the API key file
        api_key_mock = mock_open(read_data="test-api-key")
        file_handler = patch("builtins.open", api_key_mock)

        with file_handler:
            # Import and run the app
            if 'main' in sys.modules:
                import importlib
                import main
                importlib.reload(main)
            else:
                import main

        # Verify webhook called with negative price alert
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test-webhook.com")
        self.assertIn("Power prices are negative", kwargs["data"]["content"])

    @patch("requests.post")
    @patch("requests.get")
    @patch("json.dump")
    @patch("json.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.isfile")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_return_to_normal_alert(self, mock_env, mock_isfile, mock_file_open, 
                                    mock_json_load, mock_json_dump, mock_get, mock_post):
        """Test normal price alert when price returns to normal range."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 35.0}  # Above high threshold

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 20.0}]  # Normal price range
        mock_get.return_value = mock_response

        # Mock the API key file
        api_key_mock = mock_open(read_data="test-api-key")
        file_handler = patch("builtins.open", api_key_mock)

        with file_handler:
            # Import and run the app
            if 'main' in sys.modules:
                import importlib
                import main
                importlib.reload(main)
            else:
                import main

        # Verify webhook called with return to normal alert
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test-webhook.com")
        self.assertIn("Power prices have returned to normal", kwargs["data"]["content"])

    @patch("requests.post")
    @patch("requests.get")
    @patch("json.dump")
    @patch("json.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.isfile")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_no_alert_when_price_unchanged(self, mock_env, mock_isfile, mock_file_open, 
                                           mock_json_load, mock_json_dump, mock_get, mock_post):
        """Test no alerts are sent when price remains in same category."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 20.0}  # Normal price

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 25.0}]  # Still normal price
        mock_get.return_value = mock_response

        # Mock the API key file
        api_key_mock = mock_open(read_data="test-api-key")
        file_handler = patch("builtins.open", api_key_mock)

        with file_handler:
            # Import and run the app
            if 'main' in sys.modules:
                import importlib
                import main
                importlib.reload(main)
            else:
                import main

        # Verify no webhook calls
        mock_post.assert_not_called()

    @patch("requests.get")
    @patch("json.dump")
    @patch("json.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.isfile")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com", 
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_price_data_update(self, mock_env, mock_isfile, mock_file_open, 
                               mock_json_load, mock_json_dump, mock_get):
        """Test price data is updated in the JSON file."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 20.0}

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 25.0}]
        mock_get.return_value = mock_response

        # Store the mock file handler for later use in assertions
        mock_file = MagicMock()
        mock_file_open.return_value = mock_file

        # Create a specific API key file mock that's different
        api_key_mock = mock_open(read_data="test-api-key")
        file_handler = patch("builtins.open", api_key_mock)

        with file_handler:
            with patch("requests.post"):
                # Import and run the app
                if 'main' in sys.modules:
                    import importlib
                    import main
                    importlib.reload(main)
                else:
                    import main

        # Use assert_any_call instead of assert_called_with
        expected_data = {"lastPrice": 25.0}
        mock_json_dump.assert_any_call(expected_data, mock_file_open.return_value)


if __name__ == "__main__":
    unittest.main()
