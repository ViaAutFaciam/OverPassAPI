"""Client pour l'API Overpass."""

import time
from typing import Any

import requests

from ..config import DEFAULT_CONFIG, OverpassConfig


class OverpassClient:
    """
    Client pour interroger l'API Overpass.

    Ce client gère la communication avec l'API Overpass,
    les tentatives de nouvelle connexion et les erreurs.

    Attributes:
        config: Configuration d'Overpass
    """

    def __init__(self, config: OverpassConfig | None = None):
        """
        Initialise le client Overpass.

        Args:
            config: Configuration personnalisée (défaut: DEFAULT_CONFIG)
        """
        self.config = config or DEFAULT_CONFIG

    def query(self, overpass_ql: str) -> dict[str, Any]:
        """
        Exécute une requête Overpass QL.

        Effectue des tentatives automatiques en cas d'erreur.

        Args:
            overpass_ql: Requête en langage Overpass QL

        Returns:
            Dictionnaire contenant les données en JSON

        Raises:
            requests.exceptions.RequestException: Si toutes les tentatives échouent
        """
        for attempt in range(self.config.max_retries):
            try:
                response = requests.get(
                    self.config.url,
                    params={"data": overpass_ql},
                    timeout=self.config.timeout,
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                if attempt < self.config.max_retries - 1:
                    wait_time = self.config.retry_delay * (2 ** attempt)
                    print(
                        f"Tentative {attempt + 1} échouée. "
                        f"Nouvelle tentative dans {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    print(
                        f"Erreur après {self.config.max_retries} tentatives : {e}"
                    )
                    raise

        return {}

    def is_available(self) -> bool:
        """
        Vérifie si l'API Overpass est disponible.

        Returns:
            True si disponible, False sinon.
        """
        try:
            simple_query = "[bbox:0,0,0.1,0.1];node;out count;"
            response = requests.get(
                self.config.url,
                params={"data": simple_query},
                timeout=5,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False