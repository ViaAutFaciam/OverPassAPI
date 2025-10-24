"""Tests for PolygonService."""

import pytest
from unittest.mock import Mock
from src.services.polygon_service import PolygonService
from src.repositories.polygon_repository import PolygonRepository
from src.models.polygon import Polygon, PolygonType


class TestPolygonServiceInit:
    """Test PolygonService initialization."""

    def test_init_with_repository(self):
        """Test initialization with PolygonRepository."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)
        assert service.repository == repo


class TestPolygonServiceGetBuildings:
    """Test PolygonService.get_buildings() method."""

    def test_get_buildings(self, valid_bbox):
        """Test get_buildings calls repository with correct tags."""
        repo = Mock(spec=PolygonRepository)
        repo.find_ways.return_value = []
        service = PolygonService(repo)

        service.get_buildings(valid_bbox)

        repo.find_ways.assert_called_once_with(valid_bbox, {"building": "yes"})

    def test_get_buildings_returns_buildings(self, valid_bbox, simple_polygon):
        """Test get_buildings returns buildings from repository."""
        repo = Mock(spec=PolygonRepository)
        repo.find_ways.return_value = [simple_polygon]
        service = PolygonService(repo)

        result = service.get_buildings(valid_bbox)

        assert result == [simple_polygon]


class TestPolygonServiceGetIndustrialZones:
    """Test PolygonService.get_industrial_zones() method."""

    def test_get_industrial_zones(self, valid_bbox):
        """Test get_industrial_zones calls repository with correct tags."""
        repo = Mock(spec=PolygonRepository)
        repo.find_ways.return_value = []
        service = PolygonService(repo)

        service.get_industrial_zones(valid_bbox)

        repo.find_ways.assert_called_once_with(valid_bbox, {"landuse": "industrial"})


class TestPolygonServiceGetWaterAreas:
    """Test PolygonService.get_water_areas() method."""

    def test_get_water_areas(self, valid_bbox):
        """Test get_water_areas calls repository with correct tags."""
        repo = Mock(spec=PolygonRepository)
        repo.find_ways.return_value = []
        service = PolygonService(repo)

        service.get_water_areas(valid_bbox)

        repo.find_ways.assert_called_once_with(valid_bbox, {"natural": "water"})


class TestPolygonServiceGetParks:
    """Test PolygonService.get_parks() method."""

    def test_get_parks(self, valid_bbox):
        """Test get_parks calls repository with correct tags."""
        repo = Mock(spec=PolygonRepository)
        repo.find_ways.return_value = []
        service = PolygonService(repo)

        service.get_parks(valid_bbox)

        repo.find_ways.assert_called_once_with(valid_bbox, {"leisure": "park"})


class TestPolygonServiceGetPolygonsByTags:
    """Test PolygonService.get_polygons_by_tags() method."""

    def test_get_polygons_by_tags(self, valid_bbox):
        """Test get_polygons_by_tags calls repository with custom tags."""
        repo = Mock(spec=PolygonRepository)
        repo.find_by_tags.return_value = []
        service = PolygonService(repo)

        custom_tags = {"name": "Custom"}
        service.get_polygons_by_tags(valid_bbox, custom_tags)

        repo.find_by_tags.assert_called_once_with(valid_bbox, custom_tags)


class TestPolygonServiceFilterByArea:
    """Test PolygonService.filter_by_area() method."""

    def test_filter_by_area_min_only(self, polygon_list):
        """Test filtering by minimum area only."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        # polygon_list has areas: 1.0, 1.0, 4.0
        result = service.filter_by_area(polygon_list, min_area=2.0)

        assert len(result) == 1
        assert result[0].osm_id == 3

    def test_filter_by_area_min_and_max(self, polygon_list):
        """Test filtering by min and max area."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        # polygon_list has areas: 1.0, 1.0, 4.0
        result = service.filter_by_area(polygon_list, min_area=0.5, max_area=2.0)

        assert len(result) == 2
        assert all(p.osm_id in [1, 2] for p in result)

    def test_filter_by_area_empty_list(self):
        """Test filtering empty list."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.filter_by_area([], min_area=1.0)

        assert result == []

    def test_filter_by_area_no_matches(self, polygon_list):
        """Test filtering with no matches."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.filter_by_area(polygon_list, min_area=100.0)

        assert result == []


class TestPolygonServiceFilterByTagValue:
    """Test PolygonService.filter_by_tag_value() method."""

    def test_filter_by_tag_value(self, polygon_list):
        """Test filtering by tag value."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        # All polygons in polygon_list have building=yes
        result = service.filter_by_tag_value(polygon_list, "building", "yes")

        assert len(result) == 3
        assert all(p.tags.get("building") == "yes" for p in result)

    def test_filter_by_tag_value_no_matches(self, polygon_list):
        """Test filtering by tag value with no matches."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.filter_by_tag_value(polygon_list, "building", "apartment")

        assert result == []

    def test_filter_by_tag_value_empty_list(self):
        """Test filtering empty list."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.filter_by_tag_value([], "building", "yes")

        assert result == []

    def test_filter_by_tag_value_missing_tag(self, simple_polygon):
        """Test filtering when tag is missing."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        polygons = [simple_polygon]
        result = service.filter_by_tag_value(polygons, "nonexistent", "value")

        assert result == []


class TestPolygonServiceConvertToGeojson:
    """Test PolygonService.convert_to_geojson() method."""

    def test_convert_to_geojson_structure(self, polygon_list):
        """Test GeoJSON structure is correct."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.convert_to_geojson(polygon_list)

        assert result["type"] == "FeatureCollection"
        assert "features" in result
        assert isinstance(result["features"], list)

    def test_convert_to_geojson_features_count(self, polygon_list):
        """Test that all polygons are converted to features."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.convert_to_geojson(polygon_list)

        assert len(result["features"]) == len(polygon_list)

    def test_convert_to_geojson_empty_list(self):
        """Test converting empty list."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.convert_to_geojson([])

        assert result["type"] == "FeatureCollection"
        assert result["features"] == []

    def test_convert_to_geojson_preserves_properties(self, simple_polygon):
        """Test that properties are preserved in GeoJSON."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.convert_to_geojson([simple_polygon])

        feature = result["features"][0]
        assert feature["properties"]["building"] == "yes"
        assert feature["properties"]["osm_id"] == 123


class TestPolygonServiceGetStatistics:
    """Test PolygonService.get_statistics() method."""

    def test_get_statistics_empty_list(self):
        """Test statistics for empty list."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.get_statistics([])

        assert result["count"] == 0
        assert result["avg_area"] == 0.0
        assert result["min_area"] == 0.0
        assert result["max_area"] == 0.0
        assert result["total_area"] == 0.0

    def test_get_statistics_single_polygon(self, simple_polygon):
        """Test statistics for single polygon."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.get_statistics([simple_polygon])

        assert result["count"] == 1
        assert result["avg_area"] == 1.0
        assert result["min_area"] == 1.0
        assert result["max_area"] == 1.0
        assert result["total_area"] == 1.0

    def test_get_statistics_multiple_polygons(self, polygon_list):
        """Test statistics for multiple polygons."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.get_statistics(polygon_list)

        assert result["count"] == 3
        assert result["total_area"] == pytest.approx(6.0, abs=0.01)
        assert result["avg_area"] == pytest.approx(2.0, abs=0.01)
        assert result["min_area"] == pytest.approx(1.0, abs=0.01)
        assert result["max_area"] == pytest.approx(4.0, abs=0.01)

    def test_get_statistics_has_required_keys(self, polygon_list):
        """Test that statistics has all required keys."""
        repo = Mock(spec=PolygonRepository)
        service = PolygonService(repo)

        result = service.get_statistics(polygon_list)

        required_keys = ["count", "avg_area", "min_area", "max_area", "total_area"]
        for key in required_keys:
            assert key in result