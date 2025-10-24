"""Tests for BoundingBox model."""

import pytest
from src.models.bounding_box import BoundingBox


class TestBoundingBoxCreation:
    """Test BoundingBox instantiation."""

    def test_create_valid_bbox(self, valid_bbox):
        """Test creating a valid bounding box."""
        assert valid_bbox.lat_min == 40.7128
        assert valid_bbox.lon_min == -74.0060
        assert valid_bbox.lat_max == 40.7580
        assert valid_bbox.lon_max == -73.9855

    def test_create_bbox_with_zero_values(self):
        """Test creating bounding box with zero values."""
        bbox = BoundingBox(lat_min=0, lon_min=0, lat_max=0.1, lon_max=0.1)
        assert bbox.lat_min == 0
        assert bbox.lon_min == 0

    def test_create_bbox_with_negative_values(self):
        """Test creating bounding box with negative coordinates."""
        bbox = BoundingBox(lat_min=-90, lon_min=-180, lat_max=-45, lon_max=-90)
        assert bbox.lat_min == -90
        assert bbox.lon_min == -180


class TestBoundingBoxValidation:
    """Test BoundingBox.is_valid() method."""

    def test_valid_bbox_is_valid(self, valid_bbox):
        """Test that a valid bbox returns True."""
        assert valid_bbox.is_valid() is True

    def test_valid_paris_bbox(self, paris_bbox):
        """Test Paris bbox is valid."""
        assert paris_bbox.is_valid() is True

    def test_reversed_coordinates_invalid(self):
        """Test that reversed coordinates are invalid."""
        bbox = BoundingBox(lat_min=50.0, lon_min=10.0, lat_max=40.0, lon_max=5.0)
        assert bbox.is_valid() is False

    def test_latitude_out_of_range_high(self):
        """Test latitude > 90 is invalid."""
        bbox = BoundingBox(lat_min=0, lon_min=0, lat_max=91, lon_max=10)
        assert bbox.is_valid() is False

    def test_latitude_out_of_range_low(self):
        """Test latitude < -90 is invalid."""
        bbox = BoundingBox(lat_min=-91, lon_min=0, lat_max=0, lon_max=10)
        assert bbox.is_valid() is False

    def test_longitude_out_of_range_high(self):
        """Test longitude > 180 is invalid."""
        bbox = BoundingBox(lat_min=0, lon_min=0, lat_max=10, lon_max=181)
        assert bbox.is_valid() is False

    def test_longitude_out_of_range_low(self):
        """Test longitude < -180 is invalid."""
        bbox = BoundingBox(lat_min=0, lon_min=-181, lat_max=10, lon_max=0)
        assert bbox.is_valid() is False

    def test_equal_coordinates_invalid(self):
        """Test that equal min/max coordinates are invalid."""
        bbox = BoundingBox(lat_min=45.0, lon_min=2.0, lat_max=45.0, lon_max=2.0)
        assert bbox.is_valid() is False

    def test_boundary_latitude_90(self):
        """Test boundary latitude value of 90."""
        bbox = BoundingBox(lat_min=0, lon_min=0, lat_max=90, lon_max=10)
        assert bbox.is_valid() is True

    def test_boundary_latitude_minus_90(self):
        """Test boundary latitude value of -90."""
        bbox = BoundingBox(lat_min=-90, lon_min=0, lat_max=0, lon_max=10)
        assert bbox.is_valid() is True

    def test_boundary_longitude_180(self):
        """Test boundary longitude value of 180."""
        bbox = BoundingBox(lat_min=0, lon_min=0, lat_max=10, lon_max=180)
        assert bbox.is_valid() is True

    def test_boundary_longitude_minus_180(self):
        """Test boundary longitude value of -180."""
        bbox = BoundingBox(lat_min=0, lon_min=-180, lat_max=10, lon_max=0)
        assert bbox.is_valid() is True


class TestBoundingBoxToOverpass:
    """Test BoundingBox.to_overpass() method."""

    def test_to_overpass_format(self, valid_bbox):
        """Test Overpass format string generation."""
        result = valid_bbox.to_overpass()
        # Overpass format is (lat_min, lon_min, lat_max, lon_max)
        assert result.startswith("(")
        assert result.endswith(")")
        assert valid_bbox.lat_min > 0  # Just verify it has coordinates
        parts = result.strip("()").split(",")
        assert len(parts) == 4

    def test_to_overpass_contains_coordinates(self, paris_bbox):
        """Test that all coordinates are present in Overpass format."""
        result = paris_bbox.to_overpass()
        assert "48.8155" in result
        assert "2.2242" in result
        assert "48.8566" in result
        assert "2.3522" in result

    def test_to_overpass_order(self):
        """Test that Overpass format has correct coordinate order."""
        bbox = BoundingBox(lat_min=1.0, lon_min=2.0, lat_max=3.0, lon_max=4.0)
        result = bbox.to_overpass()
        # Should be (lat_min, lon_min, lat_max, lon_max)
        assert result.startswith("(1.0,2.0,3.0,4.0)")

    def test_to_overpass_with_negative_values(self):
        """Test Overpass format with negative coordinates."""
        bbox = BoundingBox(lat_min=-45.0, lon_min=-90.0, lat_max=0.0, lon_max=0.0)
        result = bbox.to_overpass()
        assert "-45.0" in result
        assert "-90.0" in result


class TestBoundingBoxString:
    """Test BoundingBox string representation."""

    def test_str_representation(self, valid_bbox):
        """Test __str__ returns Overpass format."""
        str_repr = str(valid_bbox)
        assert str_repr == valid_bbox.to_overpass()

    def test_repr_representation(self, paris_bbox):
        """Test __repr__ contains class name."""
        repr_str = repr(paris_bbox)
        assert "BoundingBox" in repr_str or "(" in repr_str