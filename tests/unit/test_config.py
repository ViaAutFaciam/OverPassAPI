"""Tests for configuration module."""

import pytest
from src.config import OverpassConfig, DEFAULT_CONFIG


class TestOverpassConfig:
    """Test OverpassConfig dataclass."""

    def test_default_config_url(self):
        """Test default API URL."""
        config = OverpassConfig()
        assert config.url == "https://overpass-api.de/api/interpreter"

    def test_default_config_timeout(self):
        """Test default timeout."""
        config = OverpassConfig()
        assert config.timeout == 30

    def test_default_config_max_retries(self):
        """Test default max retries."""
        config = OverpassConfig()
        assert config.max_retries == 3

    def test_default_config_retry_delay(self):
        """Test default retry delay."""
        config = OverpassConfig()
        assert config.retry_delay == 1.0

    def test_custom_url(self):
        """Test custom API URL."""
        custom_url = "https://custom.api/overpass"
        config = OverpassConfig(url=custom_url)
        assert config.url == custom_url

    def test_custom_timeout(self):
        """Test custom timeout."""
        config = OverpassConfig(timeout=60)
        assert config.timeout == 60

    def test_custom_max_retries(self):
        """Test custom max retries."""
        config = OverpassConfig(max_retries=5)
        assert config.max_retries == 5

    def test_custom_retry_delay(self):
        """Test custom retry delay."""
        config = OverpassConfig(retry_delay=2.5)
        assert config.retry_delay == 2.5

    def test_all_custom_values(self):
        """Test setting all custom values."""
        config = OverpassConfig(
            url="https://custom.api/interpreter",
            timeout=120,
            max_retries=10,
            retry_delay=3.0,
        )
        assert config.url == "https://custom.api/interpreter"
        assert config.timeout == 120
        assert config.max_retries == 10
        assert config.retry_delay == 3.0

    def test_config_is_dataclass(self):
        """Test that OverpassConfig is a dataclass."""
        config = OverpassConfig()
        assert hasattr(config, "__dataclass_fields__")

    def test_config_equality(self):
        """Test that configs with same values are equal."""
        config1 = OverpassConfig(timeout=60)
        config2 = OverpassConfig(timeout=60)
        assert config1 == config2

    def test_config_inequality(self):
        """Test that configs with different values are not equal."""
        config1 = OverpassConfig(timeout=30)
        config2 = OverpassConfig(timeout=60)
        assert config1 != config2


class TestDefaultConfig:
    """Test DEFAULT_CONFIG constant."""

    def test_default_config_exists(self):
        """Test that DEFAULT_CONFIG is defined."""
        assert DEFAULT_CONFIG is not None

    def test_default_config_is_overpass_config(self):
        """Test that DEFAULT_CONFIG is an OverpassConfig instance."""
        assert isinstance(DEFAULT_CONFIG, OverpassConfig)

    def test_default_config_has_default_values(self):
        """Test that DEFAULT_CONFIG has default values."""
        assert DEFAULT_CONFIG.url == "https://overpass-api.de/api/interpreter"
        assert DEFAULT_CONFIG.timeout == 30
        assert DEFAULT_CONFIG.max_retries == 3
        assert DEFAULT_CONFIG.retry_delay == 1.0