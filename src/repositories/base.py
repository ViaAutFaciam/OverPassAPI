"""Repository de base avec interface commune."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Classe de base abstraite pour tous les repositories.

    Définit l'interface commune pour l'accès aux données.

    Type:
        T: Type de l'entité gérée par le repository
    """

    @abstractmethod
    def find_all(self) -> list[T]:
        """
        Récupère tous les éléments.

        Returns:
            Liste de tous les éléments
        """
        pass

    @abstractmethod
    def find_by_id(self, item_id: int) -> T | None:
        """
        Récupère un élément par son ID.

        Args:
            item_id: ID de l'élément

        Returns:
            L'élément ou None s'il n'existe pas
        """
        pass

    @abstractmethod
    def save(self, item: T) -> T:
        """
        Sauvegarde un élément.

        Args:
            item: Élément à sauvegarder

        Returns:
            L'élément sauvegardé
        """
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        """
        Supprime un élément.

        Args:
            item_id: ID de l'élément

        Returns:
            True si supprimé, False sinon
        """
        pass