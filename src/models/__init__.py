"""Modèles de données pour l'application."""

from .bounding_box import BoundingBox
from .polygon import Polygon, PolygonType

__all__ = [
    "BoundingBox",
    "Polygon",
    "PolygonType",
]