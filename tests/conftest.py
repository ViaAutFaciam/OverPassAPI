"""Shared fixtures for all tests."""

import pytest
from src.models.bounding_box import BoundingBox
from src.models.polygon import Polygon, PolygonType
from src.config import OverpassConfig
from src.clients.overpass_client import OverpassClient


# ============================================================================
# BOUNDING BOX FIXTURES
# ============================================================================

@pytest.fixture
def valid_bbox():
    """Create a valid bounding box."""
    return BoundingBox(lat_min=40.7128, lon_min=-74.0060, lat_max=40.7580, lon_max=-73.9855)


@pytest.fixture
def paris_bbox():
    """Create a bounding box around Paris."""
    return BoundingBox(lat_min=48.8155, lon_min=2.2242, lat_max=48.8566, lon_max=2.3522)


@pytest.fixture
def invalid_bbox_reversed():
    """Create an invalid bounding box with reversed coordinates."""
    return BoundingBox(lat_min=50.0, lon_min=10.0, lat_max=40.0, lon_max=5.0)


# ============================================================================
# POLYGON FIXTURES
# ============================================================================

@pytest.fixture
def simple_polygon():
    """Create a simple valid closed polygon (square)."""
    coordinates = [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
        (0.0, 0.0),  # Closed
    ]
    return Polygon(
        osm_id=123,
        polygon_type=PolygonType.WAY,
        coordinates=coordinates,
        tags={"building": "yes", "name": "Test Building"},
        properties={"area": 1.0},
    )


@pytest.fixture
def unclosed_polygon():
    """Create an unclosed polygon."""
    coordinates = [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
        # Not closed
    ]
    return Polygon(
        osm_id=456,
        polygon_type=PolygonType.RELATION,
        coordinates=coordinates,
        tags={"landuse": "industrial"},
        properties={},
    )


@pytest.fixture
def triangle_polygon():
    """Create a valid triangle polygon."""
    coordinates = [
        (0.0, 0.0),
        (1.0, 0.0),
        (0.5, 1.0),
        (0.0, 0.0),  # Closed
    ]
    return Polygon(
        osm_id=789,
        polygon_type=PolygonType.RELATION,
        coordinates=coordinates,
        tags={"natural": "water"},
        properties={"area": 0.5},
    )


@pytest.fixture
def park_polygon():
    """Create a polygon representing a park."""
    coordinates = [
        (48.8566, 2.3522),
        (48.8600, 2.3522),
        (48.8600, 2.3560),
        (48.8566, 2.3560),
        (48.8566, 2.3522),
    ]
    return Polygon(
        osm_id=999,
        polygon_type=PolygonType.RELATION,
        coordinates=coordinates,
        tags={"leisure": "park", "name": "Sample Park"},
        properties={"area": 0.0001},
    )


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def default_config():
    """Create default OverpassConfig."""
    return OverpassConfig()


@pytest.fixture
def custom_config():
    """Create custom OverpassConfig."""
    return OverpassConfig(
        url="https://custom-overpass.api/interpreter",
        timeout=60,
        max_retries=5,
        retry_delay=2.0,
    )


# ============================================================================
# CLIENT FIXTURES
# ============================================================================

@pytest.fixture
def default_client():
    """Create OverpassClient with default config."""
    return OverpassClient()


@pytest.fixture
def custom_client(custom_config):
    """Create OverpassClient with custom config."""
    return OverpassClient(config=custom_config)


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================

@pytest.fixture
def mock_overpass_response():
    """Create a mock Overpass API response for buildings."""
    return {
        "version": 0.6,
        "generator": "Overpass API",
        "elements": [
            {
                "type": "way",
                "id": 1001,
                "nodes": [1, 2, 3, 1],
                "tags": {"building": "yes", "name": "Test Building"},
            },
            {
                "type": "way",
                "id": 1002,
                "nodes": [4, 5, 6, 4],
                "tags": {"building": "apartment", "levels": "5"},
            },
        ],
    }


@pytest.fixture
def mock_empty_response():
    """Create an empty Overpass API response."""
    return {
        "version": 0.6,
        "generator": "Overpass API",
        "elements": [],
    }


@pytest.fixture
def polygon_list():
    """Create a list of test polygons."""
    return [
        Polygon(
            osm_id=1,
            polygon_type=PolygonType.WAY,
            coordinates=[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
            tags={"building": "yes"},
            properties={"area": 1.0},
        ),
        Polygon(
            osm_id=2,
            polygon_type=PolygonType.WAY,
            coordinates=[(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)],
            tags={"building": "yes"},
            properties={"area": 1.0},
        ),
        Polygon(
            osm_id=3,
            polygon_type=PolygonType.WAY,
            coordinates=[(4, 4), (6, 4), (6, 6), (4, 6), (4, 4)],
            tags={"building": "yes"},
            properties={"area": 4.0},
        ),
    ]