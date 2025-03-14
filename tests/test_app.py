import json
import os
import unittest
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

class TestApp(unittest.TestCase):
    """Test cases for the Amber Electric price monitoring application."""

    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_create_price_data_file(self, mock_json_dump, mock_file_open, mock_isfile):
        """Test creation of price data file if it doesn't exist."""
        mock_isfile.return_value = False
        
        # Import the script
        with patch("requests.get"):  # Prevent actual API calls during import
            with patch("requests.post"):
                with patch("json.load") as mock_json_load:
                    mock_json_load.return_value = {"lastPrice": 0}
                    import app
        
        mock_isfile.assert_called_once_with("data/priceData.json")
        mock_file_open.assert_called_with("data/priceData.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_with({"lastPrice": 0}, mock_file_open())

    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("json.dump")
    @patch("requests.get")
    @patch("requests.post")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "0.0",
        "DATA_RES": "30min"
    })
    def test_high_price_alert(self, mock_post, mock_get, mock_json_dump, 
                             mock_json_load, mock_file_open, mock_isfile):
        """Test high price alert is triggered when price exceeds threshold."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 20.0}  # Below high threshold
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 35.0}]  # Above high threshold
        mock_get.return_value = mock_response
        
        # Mock the API key file
        with patch("builtins.open", mock_open(read_data="test-api-key")) as m:
            # Import and run the app
            import importlib
            import app
            importlib.reload(app)
        
        # Verify webhook called with high price alert
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test-webhook.com")
        self.assertIn("Power price is above 30.0c/kWh", kwargs["data"]["content"])

    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("json.dump")
    @patch("requests.get")
    @patch("requests.post")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_low_price_alert(self, mock_post, mock_get, mock_json_dump, 
                            mock_json_load, mock_file_open, mock_isfile):
        """Test low price alert is triggered when price falls below threshold."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 10.0}  # Above low threshold
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 3.0}]  # Below low threshold
        mock_get.return_value = mock_response
        
        # Mock the API key file
        with patch("builtins.open", mock_open(read_data="test-api-key")) as m:
            # Import and run the app
            import importlib
            import app
            importlib.reload(app)
        
        # Verify webhook called with low price alert
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test-webhook.com")
        self.assertIn("Power price is below 5.0c/kWh", kwargs["data"]["content"])

    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("json.dump")
    @patch("requests.get")
    @patch("requests.post")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_negative_price_alert(self, mock_post, mock_get, mock_json_dump, 
                                 mock_json_load, mock_file_open, mock_isfile):
        """Test negative price alert is triggered."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 2.0}  # Positive price
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": -5.0}]  # Negative price
        mock_get.return_value = mock_response
        
        # Mock the API key file
        with patch("builtins.open", mock_open(read_data="test-api-key")) as m:
            # Import and run the app
            import importlib
            import app
            importlib.reload(app)
        
        # Verify webhook called with negative price alert
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test-webhook.com")
        self.assertIn("Power prices are negative", kwargs["data"]["content"])

    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("json.dump")
    @patch("requests.get")
    @patch("requests.post")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_return_to_normal_alert(self, mock_post, mock_get, mock_json_dump, 
                                   mock_json_load, mock_file_open, mock_isfile):
        """Test normal price alert when price returns to normal range."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 35.0}  # Above high threshold
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 20.0}]  # Normal price range
        mock_get.return_value = mock_response
        
        # Mock the API key file
        with patch("builtins.open", mock_open(read_data="test-api-key")) as m:
            # Import and run the app
            import importlib
            import app
            importlib.reload(app)
        
        # Verify webhook called with return to normal alert
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test-webhook.com")
        self.assertIn("Power prices have returned to normal", kwargs["data"]["content"])

    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("json.dump")
    @patch("requests.get")
    @patch("requests.post")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_no_alert_when_price_unchanged(self, mock_post, mock_get, mock_json_dump, 
                                          mock_json_load, mock_file_open, mock_isfile):
        """Test no alerts are sent when price remains in same category."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 20.0}  # Normal price
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 25.0}]  # Still normal price
        mock_get.return_value = mock_response
        
        # Mock the API key file
        with patch("builtins.open", mock_open(read_data="test-api-key")) as m:
            # Import and run the app
            import importlib
            import app
            importlib.reload(app)
        
        # Verify no webhook calls
        mock_post.assert_not_called()

    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("json.dump")
    @patch("requests.get")
    @patch("os.environ", {
        "AMBER_SITE_ID": "test-site-id",
        "WEBHOOK_URL": "https://test-webhook.com",
        "ALERT_HIGH": "30.0",
        "ALERT_LOW": "5.0",
        "DATA_RES": "30min"
    })
    def test_price_data_update(self, mock_get, mock_json_dump, 
                              mock_json_load, mock_file_open, mock_isfile):
        """Test price data is updated in the JSON file."""
        # Setup
        mock_isfile.return_value = True
        mock_json_load.return_value = {"lastPrice": 20.0}
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"perKwh": 25.0}]
        mock_get.return_value = mock_response
        
        # Mock the API key file
        with patch("builtins.open", mock_open(read_data="test-api-key")) as m:
            with patch("requests.post"):
                # Import and run the app
                import importlib
                import app
                importlib.reload(app)
        
        # Verify price data was updated
        updated_data = {"lastPrice": 25.0}
        mock_json_dump.assert_called_with(updated_data, mock_file_open())


if __name__ == "__main__":
    unittest.main()
