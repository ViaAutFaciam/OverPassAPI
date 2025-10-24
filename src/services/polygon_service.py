"""Service pour la gestion des polygones."""

from typing import Any

from ..models.bounding_box import BoundingBox
from ..models.polygon import Polygon
from ..repositories.polygon_repository import PolygonRepository


class PolygonService:
    """
    Service pour les opérations métier sur les polygones.

    Encapsule la logique métier et facilite l'interaction
    avec le repository des polygones.

    Attributes:
        repository: Repository pour accéder aux polygones
    """

    def __init__(self, repository: PolygonRepository):
        """
        Initialise le service.

        Args:
            repository: Repository des polygones
        """
        self.repository = repository

    def get_buildings(self, bbox: BoundingBox) -> list[Polygon]:
        """
        Récupère tous les bâtiments dans une zone.

        Args:
            bbox: Zone de recherche

        Returns:
            Liste des bâtiments trouvés
        """
        tags = {"building": "yes"}
        return self.repository.find_ways(bbox, tags)

    def get_industrial_zones(self, bbox: BoundingBox) -> list[Polygon]:
        """
        Récupère les zones industrielles dans une zone.

        Args:
            bbox: Zone de recherche

        Returns:
            Liste des zones industrielles trouvées
        """
        tags = {"landuse": "industrial"}
        return self.repository.find_ways(bbox, tags)

    def get_water_areas(self, bbox: BoundingBox) -> list[Polygon]:
        """
        Récupère les zones d'eau dans une zone.

        Args:
            bbox: Zone de recherche

        Returns:
            Liste des zones d'eau trouvées
        """
        tags = {"natural": "water"}
        return self.repository.find_ways(bbox, tags)

    def get_parks(self, bbox: BoundingBox) -> list[Polygon]:
        """
        Récupère les parcs dans une zone.

        Args:
            bbox: Zone de recherche

        Returns:
            Liste des parcs trouvés
        """
        tags = {"leisure": "park"}
        return self.repository.find_ways(bbox, tags)

    def get_polygons_by_tags(
        self, bbox: BoundingBox, tags: dict[str, str]
    ) -> list[Polygon]:
        """
        Récupère les polygones avec des tags personnalisés.

        Args:
            bbox: Zone de recherche
            tags: Filtres de tags OSM

        Returns:
            Liste des polygones trouvés
        """
        return self.repository.find_by_tags(bbox, tags)

    # ==================== OPERATIONS ====================

    def filter_by_area(
        self, polygons: list[Polygon], min_area: float, max_area: float | None = None
    ) -> list[Polygon]:
        """
        Filtre les polygones par aire.

        Args:
            polygons: Liste de polygones
            min_area: Aire minimale en degrés carrés
            max_area: Aire maximale en degrés carrés (optionnel)

        Returns:
            Polygones filtrés
        """
        filtered = [p for p in polygons if p.get_area() >= min_area]

        if max_area is not None:
            filtered = [p for p in filtered if p.get_area() <= max_area]

        return filtered

    def filter_by_tag_value(
        self, polygons: list[Polygon], tag_key: str, tag_value: str
    ) -> list[Polygon]:
        """
        Filtre les polygones par valeur de tag.

        Args:
            polygons: Liste de polygones
            tag_key: Clé du tag
            tag_value: Valeur du tag

        Returns:
            Polygones filtrés
        """
        return [
            p for p in polygons if p.tags.get(tag_key) == tag_value
        ]

    def convert_to_geojson(self, polygons: list[Polygon]) -> dict[str, Any]:
        """
        Convertit les polygones en FeatureCollection GeoJSON.

        Args:
            polygons: Liste de polygones

        Returns:
            FeatureCollection GeoJSON
        """
        features = [polygon.to_geojson_feature() for polygon in polygons]

        return {
            "type": "FeatureCollection",
            "features": features,
        }

    def get_statistics(self, polygons: list[Polygon]) -> dict[str, Any]:
        """
        Calcule des statistiques sur les polygones.

        Args:
            polygons: Liste de polygones

        Returns:
            Dictionnaire de statistiques
        """
        if not polygons:
            return {
                "count": 0,
                "avg_area": 0.0,
                "min_area": 0.0,
                "max_area": 0.0,
                "total_area": 0.0,
            }

        areas = [p.get_area() for p in polygons]
        total_area = sum(areas)

        return {
            "count": len(polygons),
            "avg_area": total_area / len(polygons),
            "min_area": min(areas),
            "max_area": max(areas),
            "total_area": total_area,
        }