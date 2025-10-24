"""Tests for PolygonRepository."""

import pytest
from unittest.mock import Mock, patch
from src.repositories.polygon_repository import PolygonRepository
from src.clients.overpass_client import OverpassClient
from src.models.polygon import Polygon, PolygonType
from src.models.bounding_box import BoundingBox


class TestPolygonRepositoryInit:
    """Test PolygonRepository initialization."""

    def test_init_with_client(self):
        """Test initialization with OverpassClient."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)
        assert repo.client == client
        assert repo._cache == {}

    def test_init_creates_empty_cache(self):
        """Test that initialization creates empty cache."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)
        assert isinstance(repo._cache, dict)
        assert len(repo._cache) == 0


class TestPolygonRepositoryFindAll:
    """Test PolygonRepository.find_all() method."""

    def test_find_all_raises_not_implemented(self):
        """Test that find_all raises NotImplementedError."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        with pytest.raises(NotImplementedError):
            repo.find_all()


class TestPolygonRepositoryFindById:
    """Test PolygonRepository.find_by_id() method."""

    def test_find_by_id_returns_cached_polygon(self, simple_polygon):
        """Test that find_by_id returns polygon from cache."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)
        repo.save(simple_polygon)

        result = repo.find_by_id(123)
        assert result == simple_polygon

    def test_find_by_id_returns_none_for_missing(self):
        """Test that find_by_id returns None for missing polygon."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        result = repo.find_by_id(999)
        assert result is None


class TestPolygonRepositorySave:
    """Test PolygonRepository.save() method."""

    def test_save_caches_polygon(self, simple_polygon):
        """Test that save caches polygon by OSM ID."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        result = repo.save(simple_polygon)
        assert result == simple_polygon
        assert repo.find_by_id(123) == simple_polygon

    def test_save_returns_polygon(self, simple_polygon):
        """Test that save returns the saved polygon."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        result = repo.save(simple_polygon)
        assert result is simple_polygon

    def test_save_overwrites_existing(self, simple_polygon, triangle_polygon):
        """Test that save overwrites existing polygon with same ID."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        # Change triangle_polygon's ID to match simple_polygon
        triangle_polygon.osm_id = 123

        repo.save(simple_polygon)
        repo.save(triangle_polygon)

        # Should return the second one
        assert repo.find_by_id(123) == triangle_polygon


class TestPolygonRepositoryDelete:
    """Test PolygonRepository.delete() method."""

    def test_delete_removes_from_cache(self, simple_polygon):
        """Test that delete removes polygon from cache."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)
        repo.save(simple_polygon)

        result = repo.delete(123)
        assert result is True
        assert repo.find_by_id(123) is None

    def test_delete_returns_false_for_missing(self):
        """Test that delete returns False for missing polygon."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        result = repo.delete(999)
        assert result is False


class TestPolygonRepositoryFindWays:
    """Test PolygonRepository.find_ways() method."""

    def test_find_ways_with_valid_bbox(self, valid_bbox):
        """Test find_ways with valid bounding box."""
        client = Mock(spec=OverpassClient)
        client.query.return_value = {
            "elements": [
                {
                    "type": "way",
                    "id": 1,
                    "geometry": [
                        {"lat": 40.7128, "lon": -74.0060},
                        {"lat": 40.7580, "lon": -73.9855},
                    ],
                    "tags": {"building": "yes"},
                }
            ]
        }

        repo = PolygonRepository(client)
        results = repo.find_ways(valid_bbox)

        assert len(results) > 0
        assert all(isinstance(p, Polygon) for p in results)
        client.query.assert_called_once()

    def test_find_ways_with_invalid_bbox(self, invalid_bbox_reversed):
        """Test find_ways with invalid bounding box."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        with pytest.raises(ValueError):
            repo.find_ways(invalid_bbox_reversed)

    def test_find_ways_with_custom_tags(self, valid_bbox):
        """Test find_ways with custom tags."""
        client = Mock(spec=OverpassClient)
        client.query.return_value = {"elements": []}

        repo = PolygonRepository(client)
        repo.find_ways(valid_bbox, tags={"landuse": "industrial"})

        # Check that query contains custom tags
        call_args = client.query.call_args
        assert 'landuse' in call_args[0][0]
        assert 'industrial' in call_args[0][0]

    def test_find_ways_caches_results(self, valid_bbox):
        """Test that find_ways caches results."""
        client = Mock(spec=OverpassClient)
        client.query.return_value = {
            "elements": [
                {
                    "type": "way",
                    "id": 1,
                    "geometry": [
                        {"lat": 40.7128, "lon": -74.0060},
                        {"lat": 40.7580, "lon": -73.9855},
                    ],
                    "tags": {"building": "yes"},
                }
            ]
        }

        repo = PolygonRepository(client)
        results = repo.find_ways(valid_bbox)

        # Check that polygon is in cache
        assert repo.find_by_id(1) is not None
        assert len(results) == repo.get_cache_size()

    def test_find_ways_with_empty_response(self, valid_bbox):
        """Test find_ways with empty API response."""
        client = Mock(spec=OverpassClient)
        client.query.return_value = {"elements": []}

        repo = PolygonRepository(client)
        results = repo.find_ways(valid_bbox)

        assert results == []


class TestPolygonRepositoryFindRelations:
    """Test PolygonRepository.find_relations() method."""

    def test_find_relations_with_invalid_bbox(self, invalid_bbox_reversed):
        """Test find_relations with invalid bounding box."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        with pytest.raises(ValueError):
            repo.find_relations(invalid_bbox_reversed)

    def test_find_relations_returns_empty_list(self, valid_bbox):
        """Test that find_relations returns empty list (not yet implemented)."""
        client = Mock(spec=OverpassClient)
        client.query.return_value = {"elements": []}

        repo = PolygonRepository(client)
        results = repo.find_relations(valid_bbox)

        assert results == []


class TestPolygonRepositoryFindByTags:
    """Test PolygonRepository.find_by_tags() method."""

    def test_find_by_tags_delegates_to_find_ways(self, valid_bbox):
        """Test that find_by_tags delegates to find_ways."""
        client = Mock(spec=OverpassClient)
        client.query.return_value = {"elements": []}

        repo = PolygonRepository(client)
        tags = {"leisure": "park"}
        results = repo.find_by_tags(valid_bbox, tags)

        assert results == []
        client.query.assert_called_once()


class TestPolygonRepositoryCacheOperations:
    """Test cache-related operations."""

    def test_clear_cache(self, simple_polygon, triangle_polygon):
        """Test that clear_cache empties the cache."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)
        repo.save(simple_polygon)
        repo.save(triangle_polygon)

        assert repo.get_cache_size() == 2
        repo.clear_cache()
        assert repo.get_cache_size() == 0

    def test_get_cache_size(self, simple_polygon, triangle_polygon):
        """Test that get_cache_size returns correct count."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        assert repo.get_cache_size() == 0
        repo.save(simple_polygon)
        assert repo.get_cache_size() == 1
        repo.save(triangle_polygon)
        assert repo.get_cache_size() == 2


class TestPolygonRepositoryPrivateMethods:
    """Test private methods of PolygonRepository."""

    def test_build_tag_conditions_single_tag(self):
        """Test _build_tag_conditions with single tag."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        result = repo._build_tag_conditions({"building": "yes"})
        assert result == '["building"="yes"]'

    def test_build_tag_conditions_multiple_tags(self):
        """Test _build_tag_conditions with multiple tags."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        result = repo._build_tag_conditions({"building": "yes", "levels": "5"})
        assert '["building"="yes"]' in result
        assert '["levels"="5"]' in result

    def test_parse_element_creates_valid_polygon(self):
        """Test that _parse_element creates a valid polygon."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        element = {
            "type": "way",
            "id": 123,
            "geometry": [
                {"lat": 40.0, "lon": -74.0},
                {"lat": 40.1, "lon": -74.0},
                {"lat": 40.1, "lon": -73.9},
            ],
            "tags": {"building": "yes"},
        }

        polygon = repo._parse_element(element, PolygonType.WAY)
        assert polygon is not None
        assert polygon.osm_id == 123
        assert polygon.polygon_type == PolygonType.WAY
        assert polygon.tags == {"building": "yes"}

    def test_parse_element_handles_missing_geometry(self):
        """Test that _parse_element returns None for missing geometry."""
        client = Mock(spec=OverpassClient)
        repo = PolygonRepository(client)

        element = {"type": "way", "id": 123, "tags": {"building": "yes"}}

        polygon = repo._parse_element(element, PolygonType.WAY)
        assert polygon is None

    def test_query_and_parse_handles_empty_response(self):
        """Test that _query_and_parse handles empty response."""
        client = Mock(spec=OverpassClient)
        client.query.return_value = {}
        repo = PolygonRepository(client)

        results = repo._query_and_parse("[bbox:0,0,1,1];way;out;", PolygonType.WAY)
        assert results == []