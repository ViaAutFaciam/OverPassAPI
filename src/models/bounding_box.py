"""Modèle pour les bounding boxes."""

from dataclasses import dataclass


@dataclass
class BoundingBox:
    """
    Représente une bounding box géographique.

    Format : (sud, ouest, nord, est)
    ou (lat_min, lon_min, lat_max, lon_max)

    Attributes:
        lat_min: Latitude minimale (sud)
        lon_min: Longitude minimale (ouest)
        lat_max: Latitude maximale (nord)
        lon_max: Longitude maximale (est)

    Exemple:
        >>> bbox = BoundingBox(48.81, 2.22, 48.90, 2.47)
        >>> print(bbox.to_overpass())
        '(48.81,2.22,48.90,2.47)'
    """

    lat_min: float
    lon_min: float
    lat_max: float
    lon_max: float

    def to_overpass(self) -> str:
        """
        Convertit la bbox au format Overpass QL.

        Returns:
            String formaté pour Overpass QL: (lat_min,lon_min,lat_max,lon_max)
        """
        return f"({self.lat_min},{self.lon_min},{self.lat_max},{self.lon_max})"

    def __str__(self) -> str:
        """Représentation string de la bbox."""
        return self.to_overpass()

    def is_valid(self) -> bool:
        """
        Valide les coordonnées de la bbox.

        Returns:
            True si les coordonnées sont valides, False sinon.
        """
        if self.lat_min >= self.lat_max:
            return False
        if self.lon_min >= self.lon_max:
            return False
        if not (-90 <= self.lat_min <= 90):
            return False
        if not (-90 <= self.lat_max <= 90):
            return False
        if not (-180 <= self.lon_min <= 180):
            return False
        if not (-180 <= self.lon_max <= 180):
            return False
        return True