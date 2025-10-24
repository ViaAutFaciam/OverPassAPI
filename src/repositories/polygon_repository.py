"""Repository pour les polygones."""

from typing import Any

from ..clients.overpass_client import OverpassClient
from ..models.bounding_box import BoundingBox
from ..models.polygon import Polygon, PolygonType
from .base import BaseRepository


class PolygonRepository(BaseRepository[Polygon]):
    """
    Repository pour gérer les polygones.

    Fournit des méthodes pour récupérer des polygones
    via l'API Overpass.

    Attributes:
        client: Client Overpass pour les requêtes API
    """

    def __init__(self, client: OverpassClient):
        """
        Initialise le repository.

        Args:
            client: Client Overpass
        """
        self.client = client
        self._cache: dict[int, Polygon] = {}

    def find_all(self) -> list[Polygon]:
        """
        Non implémenté pour ce repository.

        Raises:
            NotImplementedError: Toujours levée
        """
        raise NotImplementedError(
            "Utilisez find_by_bbox() pour récupérer les polygones"
        )

    def find_by_id(self, item_id: int) -> Polygon | None:
        """
        Récupère un polygone par son ID OSM.

        Args:
            item_id: ID OSM du polygone

        Returns:
            Le polygone ou None s'il n'existe pas
        """
        return self._cache.get(item_id)

    def save(self, item: Polygon) -> Polygon:
        """
        Sauvegarde un polygone en cache.

        Args:
            item: Polygone à sauvegarder

        Returns:
            Le polygone sauvegardé
        """
        self._cache[item.osm_id] = item
        return item

    def delete(self, item_id: int) -> bool:
        """
        Supprime un polygone du cache.

        Args:
            item_id: ID OSM du polygone

        Returns:
            True si supprimé, False sinon
        """
        if item_id in self._cache:
            del self._cache[item_id]
            return True
        return False

    # ==================== MÉTHODES SPÉCIFIQUES ====================

    def find_ways(
        self, bbox: BoundingBox, tags: dict[str, str] | None = None
    ) -> list[Polygon]:
        """
        Récupère les polygones de type 'way' dans une bbox.

        Args:
            bbox: Bounding box de recherche
            tags: Filtres de tags OSM

        Returns:
            Liste des polygones trouvés

        Raises:
            ValueError: Si la bbox est invalide
        """
        if not bbox.is_valid():
            raise ValueError(f"BoundingBox invalide: {bbox}")

        if tags is None:
            tags = {"building": "yes"}

        tag_conditions = self._build_tag_conditions(tags)
        query = f"""
[bbox:{bbox.to_overpass()}];
(
  way{tag_conditions};
);
out geom;
"""
        return self._query_and_parse(query, PolygonType.WAY)

    def find_relations(
        self, bbox: BoundingBox, tags: dict[str, str] | None = None
    ) -> list[Polygon]:
        """
        Récupère les polygones de type 'relation' dans une bbox.

        Args:
            bbox: Bounding box de recherche
            tags: Filtres de tags OSM

        Returns:
            Liste des relations trouvées
        """
        if not bbox.is_valid():
            raise ValueError(f"BoundingBox invalide: {bbox}")

        if tags is None:
            tags = {"boundary": "administrative"}

        tag_conditions = self._build_tag_conditions(tags)
        query = f"""
[bbox:{bbox.to_overpass()}];
(
  relation{tag_conditions};
);
out count;
"""
        data = self.client.query(query)
        return []  # Les relations nécessitent un traitement spécial

    def find_by_tags(
        self, bbox: BoundingBox, tags: dict[str, str]
    ) -> list[Polygon]:
        """
        Récupère les polygones filtrés par tags dans une bbox.

        Args:
            bbox: Bounding box de recherche
            tags: Filtres de tags OSM

        Returns:
            Liste des polygones trouvés
        """
        return self.find_ways(bbox, tags)

    # ==================== MÉTHODES PRIVÉES ====================

    def _query_and_parse(
        self, query: str, polygon_type: PolygonType
    ) -> list[Polygon]:
        """
        Exécute une requête et parse les résultats.

        Args:
            query: Requête Overpass QL
            polygon_type: Type de polygone attendu

        Returns:
            Liste des polygones parsés
        """
        try:
            data = self.client.query(query)

            if not data or "elements" not in data:
                return []

            polygons = []
            for element in data["elements"]:
                if element.get("type") == polygon_type.value:
                    polygon = self._parse_element(element, polygon_type)
                    if polygon:
                        self.save(polygon)
                        polygons.append(polygon)

            return polygons

        except Exception as e:
            print(f"Erreur lors du parsing : {e}")
            return []

    def _parse_element(
        self, element: dict[str, Any], polygon_type: PolygonType
    ) -> Polygon | None:
        """
        Parse un élément Overpass en objet Polygon.

        Args:
            element: Élément Overpass
            polygon_type: Type de polygone

        Returns:
            Objet Polygon ou None si parsing échoue
        """
        try:
            osm_id = element.get("id")
            tags = element.get("tags", {})

            # Extraire les coordonnées
            coordinates = []
            if "geometry" in element:
                for node in element["geometry"]:
                    coordinates.append([node["lon"], node["lat"]])

            if not coordinates:
                return None

            polygon = Polygon(
                osm_id=osm_id,
                polygon_type=polygon_type,
                coordinates=coordinates,
                tags=tags,
            )

            # Fermer le polygone si nécessaire
            if polygon_type == PolygonType.WAY:
                polygon.close()

            return polygon

        except Exception as e:
            print(f"Erreur lors du parsing de l'élément {element.get('id')}: {e}")
            return None

    @staticmethod
    def _build_tag_conditions(tags: dict[str, str]) -> str:
        """
        Construit les conditions de tag pour Overpass QL.

        Args:
            tags: Dictionnaire {key: value}

        Returns:
            String formaté pour Overpass QL
        """
        conditions = ""
        for key, value in tags.items():
            conditions += f'["{key}"="{value}"]'
        return conditions

    def clear_cache(self) -> None:
        """Vide le cache."""
        self._cache.clear()

    def get_cache_size(self) -> int:
        """
        Retourne la taille du cache.

        Returns:
            Nombre de polygones en cache
        """
        return len(self._cache)