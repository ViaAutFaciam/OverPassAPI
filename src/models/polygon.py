"""Modèle pour les polygones."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PolygonType(Enum):
    """Types de polygones OSM."""

    WAY = "way"
    RELATION = "relation"
    NODE = "node"


@dataclass
class Polygon:
    """
    Représente un polygone OpenStreetMap.

    Attributes:
        osm_id: Identifiant unique OpenStreetMap
        polygon_type: Type de géométrie (way, relation, node)
        coordinates: Liste de coordonnées [lon, lat]
        tags: Dictionnaire des tags OSM
        properties: Propriétés additionnelles

    Exemple:
        >>> coords = [[2.25, 48.81], [2.26, 48.82], [2.25, 48.81]]
        >>> polygon = Polygon(
        ...     osm_id=123,
        ...     polygon_type=PolygonType.WAY,
        ...     coordinates=coords,
        ...     tags={"building": "yes"}
        ... )
    """

    osm_id: int
    polygon_type: PolygonType
    coordinates: list = field(default_factory=list)
    tags: dict = field(default_factory=dict)
    properties: dict = field(default_factory=dict)

    def is_closed(self) -> bool:
        """
        Vérifie si le polygone est fermé.

        Returns:
            True si le premier et dernier point sont identiques.
        """
        if len(self.coordinates) < 3:
            return False
        return self.coordinates[0] == self.coordinates[-1]

    def close(self) -> None:
        """Ferme le polygone si nécessaire."""
        if not self.is_closed():
            self.coordinates.append(self.coordinates[0])

    def is_valid(self) -> bool:
        """
        Valide la structure du polygone.

        Returns:
            True si le polygone est valide.
        """
        if len(self.coordinates) < 3:
            return False
        return self.is_closed()

    def get_area(self) -> float:
        """
        Calcule approximativement l'aire du polygone (formule de Shoelace).

        Returns:
            Aire approximative en degrés carrés.
        """
        if not self.is_closed() or len(self.coordinates) < 3:
            return 0.0

        area = 0.0
        for i in range(len(self.coordinates) - 1):
            x1, y1 = self.coordinates[i]
            x2, y2 = self.coordinates[i + 1]
            area += (x1 * y2) - (x2 * y1)

        return abs(area) / 2.0

    def to_geojson_feature(self) -> dict[str, Any]:
        """
        Convertit le polygone en feature GeoJSON.

        Returns:
            Feature GeoJSON.
        """
        properties = {
            "osm_id": self.osm_id,
            "type": self.polygon_type.value,
            **self.tags,
            **self.properties,
        }

        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [self.coordinates],
            },
            "properties": properties,
        }

    def __repr__(self) -> str:
        """Représentation string du polygone."""
        return (
            f"Polygon(id={self.osm_id}, type={self.polygon_type.value}, "
            f"coords={len(self.coordinates)}, tags={len(self.tags)})"
        )