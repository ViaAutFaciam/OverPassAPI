"""Tests for PolygonType enum."""

import pytest
from src.models.polygon import PolygonType


class TestPolygonTypeEnum:
    """Test PolygonType enum values."""

    def test_polygon_type_way_exists(self):
        """Test that WAY enum value exists."""
        assert hasattr(PolygonType, "WAY")
        assert PolygonType.WAY.value == "way"

    def test_polygon_type_relation_exists(self):
        """Test that RELATION enum value exists."""
        assert hasattr(PolygonType, "RELATION")
        assert PolygonType.RELATION.value == "relation"

    def test_polygon_type_node_exists(self):
        """Test that NODE enum value exists."""
        assert hasattr(PolygonType, "NODE")
        assert PolygonType.NODE.value == "node"

    def test_polygon_type_values_are_strings(self):
        """Test that all enum values are strings."""
        for poly_type in PolygonType:
            assert isinstance(poly_type.value, str)

    def test_polygon_type_comparison(self):
        """Test enum value comparison."""
        assert PolygonType.WAY == PolygonType.WAY
        assert PolygonType.WAY != PolygonType.RELATION

    def test_polygon_type_from_value(self):
        """Test creating enum from value."""
        assert PolygonType("way") == PolygonType.WAY
        assert PolygonType("relation") == PolygonType.RELATION
        assert PolygonType("node") == PolygonType.NODE

    def test_polygon_type_from_invalid_value(self):
        """Test that invalid value raises ValueError."""
        with pytest.raises(ValueError):
            PolygonType("invalid")

    def test_polygon_type_all_members(self):
        """Test that enum has exactly 3 members."""
        assert len(PolygonType) == 3
        members = [member.name for member in PolygonType]
        assert "WAY" in members
        assert "RELATION" in members
        assert "NODE" in members