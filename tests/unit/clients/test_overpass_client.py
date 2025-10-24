"""Tests for OverpassClient."""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from src.clients.overpass_client import OverpassClient
from src.config import OverpassConfig


class TestOverpassClientInit:
    """Test OverpassClient initialization."""

    def test_init_with_default_config(self):
        """Test initialization with default config."""
        client = OverpassClient()
        assert client.config is not None
        assert client.config.url == "https://overpass-api.de/api/interpreter"

    def test_init_with_custom_config(self, custom_config):
        """Test initialization with custom config."""
        client = OverpassClient(config=custom_config)
        assert client.config == custom_config
        assert client.config.url == "https://custom-overpass.api/interpreter"

    def test_init_with_none_uses_default(self):
        """Test that None config uses default."""
        client = OverpassClient(config=None)
        assert client.config is not None
        assert client.config.url == "https://overpass-api.de/api/interpreter"


class TestOverpassClientQuery:
    """Test OverpassClient.query() method."""

    @patch("src.clients.overpass_client.requests.get")
    def test_successful_query(self, mock_get):
        """Test successful query execution."""
        mock_response = Mock()
        mock_response.json.return_value = {"elements": []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = OverpassClient()
        result = client.query("[bbox:0,0,1,1];way;out;")

        assert result == {"elements": []}
        mock_get.assert_called_once()

    @patch("src.clients.overpass_client.requests.get")
    def test_query_passes_correct_parameters(self, mock_get):
        """Test that query passes correct parameters to requests.get."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = OverpassClient()
        query_str = "[bbox:0,0,1,1];way;out;"
        client.query(query_str)

        # Check that requests.get was called with correct parameters
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://overpass-api.de/api/interpreter"
        assert call_args[1]["params"]["data"] == query_str
        assert "timeout" in call_args[1]

    @patch("src.clients.overpass_client.requests.get")
    def test_query_uses_config_timeout(self, mock_get):
        """Test that query uses timeout from config."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        config = OverpassConfig(timeout=60)
        client = OverpassClient(config=config)
        client.query("[bbox:0,0,1,1];way;out;")

        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 60

    @patch("src.clients.overpass_client.time.sleep")
    @patch("src.clients.overpass_client.requests.get")
    def test_query_retry_on_failure(self, mock_get, mock_sleep):
        """Test that query retries on failure."""
        # First two attempts fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.ConnectionError()

        mock_response_success = Mock()
        mock_response_success.json.return_value = {"elements": []}
        mock_response_success.status_code = 200

        mock_get.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_success,
        ]

        config = OverpassConfig(max_retries=3, retry_delay=1.0)
        client = OverpassClient(config=config)

        # This should succeed on third attempt
        result = client.query("[bbox:0,0,1,1];way;out;")
        assert result == {"elements": []}
        assert mock_get.call_count == 3

    @patch("src.clients.overpass_client.time.sleep")
    @patch("src.clients.overpass_client.requests.get")
    def test_query_exponential_backoff(self, mock_get, mock_sleep):
        """Test that retry delays increase exponentially."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.ConnectionError()
        mock_get.return_value = mock_response

        config = OverpassConfig(max_retries=3, retry_delay=1.0)
        client = OverpassClient(config=config)

        with pytest.raises(requests.exceptions.ConnectionError):
            client.query("[bbox:0,0,1,1];way;out;")

        # Should have slept with exponential backoff: 1.0, 2.0
        assert mock_sleep.call_count == 2
        calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert calls[0] == pytest.approx(1.0)  # 1.0 * (2 ** 0)
        assert calls[1] == pytest.approx(2.0)  # 1.0 * (2 ** 1)

    @patch("src.clients.overpass_client.requests.get")
    def test_query_raises_after_max_retries(self, mock_get):
        """Test that query raises exception after max retries."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.Timeout()
        mock_get.return_value = mock_response

        config = OverpassConfig(max_retries=2, retry_delay=0.1)
        client = OverpassClient(config=config)

        with pytest.raises(requests.exceptions.Timeout):
            client.query("[bbox:0,0,1,1];way;out;")

        assert mock_get.call_count == 2

    @patch("src.clients.overpass_client.requests.get")
    def test_query_handles_http_error(self, mock_get):
        """Test that query handles HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        client = OverpassClient()

        with pytest.raises(requests.exceptions.HTTPError):
            client.query("[bbox:0,0,1,1];way;out;")

    @patch("src.clients.overpass_client.requests.get")
    def test_query_returns_json(self, mock_get):
        """Test that query returns JSON response."""
        expected_data = {
            "version": 0.6,
            "elements": [
                {"type": "way", "id": 123, "tags": {"building": "yes"}},
            ],
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = OverpassClient()
        result = client.query("[bbox:0,0,1,1];way;out;")

        assert result == expected_data
        mock_response.json.assert_called_once()


class TestOverpassClientIsAvailable:
    """Test OverpassClient.is_available() method."""

    @patch("src.clients.overpass_client.requests.get")
    def test_is_available_returns_true_for_200(self, mock_get):
        """Test that is_available returns True for 200 status."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = OverpassClient()
        assert client.is_available() is True

    @patch("src.clients.overpass_client.requests.get")
    def test_is_available_returns_false_for_non_200(self, mock_get):
        """Test that is_available returns False for non-200 status."""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response

        client = OverpassClient()
        assert client.is_available() is False

    @patch("src.clients.overpass_client.requests.get")
    def test_is_available_returns_false_on_connection_error(self, mock_get):
        """Test that is_available returns False on connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        client = OverpassClient()
        assert client.is_available() is False

    @patch("src.clients.overpass_client.requests.get")
    def test_is_available_returns_false_on_timeout(self, mock_get):
        """Test that is_available returns False on timeout."""
        mock_get.side_effect = requests.exceptions.Timeout()

        client = OverpassClient()
        assert client.is_available() is False

    @patch("src.clients.overpass_client.requests.get")
    def test_is_available_uses_short_timeout(self, mock_get):
        """Test that is_available uses a short timeout (5s)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = OverpassClient()
        client.is_available()

        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 5