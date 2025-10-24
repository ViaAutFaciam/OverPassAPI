"""Tests for Polygon model."""

import pytest
from src.models.polygon import Polygon, PolygonType


class TestPolygonCreation:
    """Test Polygon instantiation."""

    def test_create_closed_polygon(self, simple_polygon):
        """Test creating a closed polygon."""
        assert simple_polygon.osm_id == 123
        assert simple_polygon.polygon_type == PolygonType.WAY
        assert len(simple_polygon.coordinates) == 5
        assert simple_polygon.tags["building"] == "yes"

    def test_create_unclosed_polygon(self, unclosed_polygon):
        """Test creating an unclosed polygon."""
        assert unclosed_polygon.osm_id == 456
        assert unclosed_polygon.polygon_type == PolygonType.RELATION
        assert len(unclosed_polygon.coordinates) == 4

    def test_polygon_with_empty_tags(self):
        """Test polygon with empty tags."""
        poly = Polygon(
            osm_id=1,
            polygon_type=PolygonType.NODE,
            coordinates=[(0, 0), (1, 0), (1, 1), (0, 0)],
            tags={},
            properties={},
        )
        assert poly.tags == {}
        assert poly.properties == {}


class TestPolygonIsClosed:
    """Test Polygon.is_closed() method."""

    def test_closed_polygon_is_closed(self, simple_polygon):
        """Test that a closed polygon returns True."""
        assert simple_polygon.is_closed() is True

    def test_unclosed_polygon_not_closed(self, unclosed_polygon):
        """Test that an unclosed polygon returns False."""
        assert unclosed_polygon.is_closed() is False

    def test_triangle_is_closed(self, triangle_polygon):
        """Test that a closed triangle returns True."""
        assert triangle_polygon.is_closed() is True

    def test_single_point_polygon(self):
        """Test polygon with single point."""
        poly = Polygon(
            osm_id=1,
            polygon_type=PolygonType.NODE,
            coordinates=[(0, 0)],
            tags={},
            properties={},
        )
        assert poly.is_closed() is False

    def test_two_point_polygon(self):
        """Test polygon with only two points."""
        poly = Polygon(
            osm_id=1,
            polygon_type=PolygonType.WAY,
            coordinates=[(0, 0), (1, 1)],
            tags={},
            properties={},
        )
        assert poly.is_closed() is False


class TestPolygonClose:
    """Test Polygon.close() method."""

    def test_close_unclosed_polygon(self, unclosed_polygon):
        """Test that closing an unclosed polygon appends first coordinate."""
        original_length = len(unclosed_polygon.coordinates)
        unclosed_polygon.close()
        assert len(unclosed_polygon.coordinates) == original_length + 1
        assert unclosed_polygon.coordinates[0] == unclosed_polygon.coordinates[-1]
        assert unclosed_polygon.is_closed() is True

    def test_close_already_closed_polygon(self, simple_polygon):
        """Test that closing an already closed polygon doesn't double-close."""
        original_length = len(simple_polygon.coordinates)
        simple_polygon.close()
        # Should not add another point since it's already closed
        assert len(simple_polygon.coordinates) == original_length

    def test_close_modifies_coordinates(self, unclosed_polygon):
        """Test that close() modifies the coordinates list."""
        original_coords = unclosed_polygon.coordinates.copy()
        unclosed_polygon.close()
        assert unclosed_polygon.coordinates != original_coords
        assert unclosed_polygon.coordinates[-1] == original_coords[0]


class TestPolygonIsValid:
    """Test Polygon.is_valid() method."""

    def test_valid_closed_polygon(self, simple_polygon):
        """Test that a valid closed polygon returns True."""
        assert simple_polygon.is_valid() is True

    def test_valid_closed_triangle(self, triangle_polygon):
        """Test that a valid closed triangle returns True."""
        assert triangle_polygon.is_valid() is True

    def test_invalid_unclosed_polygon(self, unclosed_polygon):
        """Test that an unclosed polygon returns False."""
        assert unclosed_polygon.is_valid() is False

    def test_invalid_less_than_three_points(self):
        """Test polygon with less than 3 points."""
        poly = Polygon(
            osm_id=1,
            polygon_type=PolygonType.WAY,
            coordinates=[(0, 0), (1, 1)],  # Only 2 points
            tags={},
            properties={},
        )
        # Less than 3 points should be invalid
        assert poly.is_valid() is False

    def test_invalid_empty_coordinates(self):
        """Test polygon with empty coordinates."""
        poly = Polygon(
            osm_id=1,
            polygon_type=PolygonType.WAY,
            coordinates=[],
            tags={},
            properties={},
        )
        assert poly.is_valid() is False


class TestPolygonGetArea:
    """Test Polygon.get_area() method using Shoelace formula."""

    def test_unit_square_area(self, simple_polygon):
        """Test area of unit square (1x1)."""
        area = simple_polygon.get_area()
        assert area == 1.0

    def test_triangle_area(self, triangle_polygon):
        """Test area of triangle."""
        area = triangle_polygon.get_area()
        # Triangle with base 1 and height 1 should have area 0.5
        assert area == pytest.approx(0.5, abs=0.01)

    def test_rectangle_area(self):
        """Test area of rectangle (2x3)."""
        poly = Polygon(
            osm_id=1,
            polygon_type=PolygonType.WAY,
            coordinates=[(0, 0), (2, 0), (2, 3), (0, 3), (0, 0)],
            tags={},
            properties={},
        )
        area = poly.get_area()
        assert area == pytest.approx(6.0, abs=0.01)

    def test_area_unclosed_polygon(self, unclosed_polygon):
        """Test area calculation for unclosed polygon."""
        # Should handle unclosed polygons
        area = unclosed_polygon.get_area()
        assert isinstance(area, (int, float))

    def test_area_empty_polygon(self):
        """Test area of polygon with empty coordinates."""
        poly = Polygon(
            osm_id=1,
            polygon_type=PolygonType.WAY,
            coordinates=[],
            tags={},
            properties={},
        )
        area = poly.get_area()
        assert area == 0.0


class TestPolygonToGeojson:
    """Test Polygon.to_geojson_feature() method."""

    def test_geojson_structure(self, simple_polygon):
        """Test that GeoJSON feature has correct structure."""
        geojson = simple_polygon.to_geojson_feature()
        assert "type" in geojson
        assert "geometry" in geojson
        assert "properties" in geojson
        assert geojson["type"] == "Feature"

    def test_geojson_geometry_type(self, simple_polygon):
        """Test that geometry has type Polygon."""
        geojson = simple_polygon.to_geojson_feature()
        assert geojson["geometry"]["type"] == "Polygon"

    def test_geojson_coordinates(self, simple_polygon):
        """Test that GeoJSON contains coordinates."""
        geojson = simple_polygon.to_geojson_feature()
        assert "coordinates" in geojson["geometry"]
        assert len(geojson["geometry"]["coordinates"][0]) > 0

    def test_geojson_properties_include_tags(self, simple_polygon):
        """Test that properties include tags."""
        geojson = simple_polygon.to_geojson_feature()
        properties = geojson["properties"]
        assert "building" in properties
        assert properties["building"] == "yes"

    def test_geojson_properties_include_osm_id(self, simple_polygon):
        """Test that properties include osm_id."""
        geojson = simple_polygon.to_geojson_feature()
        properties = geojson["properties"]
        assert "osm_id" in properties
        assert properties["osm_id"] == 123

    def test_geojson_properties_include_type(self, simple_polygon):
        """Test that properties include type (polygon_type value)."""
        geojson = simple_polygon.to_geojson_feature()
        properties = geojson["properties"]
        assert "type" in properties
        assert properties["type"] == "way"

    def test_geojson_empty_polygon(self):
        """Test GeoJSON for polygon with no tags."""
        poly = Polygon(
            osm_id=1,
            polygon_type=PolygonType.NODE,
            coordinates=[(0, 0), (1, 0), (1, 1), (0, 0)],
            tags={},
            properties={},
        )
        geojson = poly.to_geojson_feature()
        assert geojson["type"] == "Feature"
        assert isinstance(geojson["properties"], dict)


class TestPolygonRepr:
    """Test Polygon string representation."""

    def test_repr_contains_osm_id(self, simple_polygon):
        """Test that repr contains osm_id."""
        repr_str = repr(simple_polygon)
        assert "123" in repr_str

    def test_repr_contains_type(self, simple_polygon):
        """Test that repr contains polygon type."""
        repr_str = repr(simple_polygon)
        assert "Polygon" in repr_str or "WAY" in repr_str