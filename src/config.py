"""
Configuration de l'application.

Ce module définit les constantes et paramètres de configuration
pour l'application OverPassAPI.
"""

from dataclasses import dataclass


@dataclass
class OverpassConfig:
    """Configuration pour l'API Overpass."""

    url: str = "https://overpass-api.de/api/interpreter"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


# Configuration par défaut
DEFAULT_CONFIG = OverpassConfig()