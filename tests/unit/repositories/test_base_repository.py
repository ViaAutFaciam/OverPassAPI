"""Tests for BaseRepository abstract class."""

import pytest
from src.repositories.base import BaseRepository
from src.models.polygon import Polygon


class TestBaseRepositoryAbstract:
    """Test BaseRepository abstract base class."""

    def test_cannot_instantiate_base_repository(self):
        """Test that BaseRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseRepository()

    def test_subclass_must_implement_find_all(self):
        """Test that subclass must implement find_all."""
        class IncompleteRepository(BaseRepository):
            def find_by_id(self, item_id: int): pass
            def save(self, item): pass
            def delete(self, item_id: int): pass

        with pytest.raises(TypeError):
            IncompleteRepository()

    def test_subclass_must_implement_find_by_id(self):
        """Test that subclass must implement find_by_id."""
        class IncompleteRepository(BaseRepository):
            def find_all(self): pass
            def save(self, item): pass
            def delete(self, item_id: int): pass

        with pytest.raises(TypeError):
            IncompleteRepository()

    def test_subclass_must_implement_save(self):
        """Test that subclass must implement save."""
        class IncompleteRepository(BaseRepository):
            def find_all(self): pass
            def find_by_id(self, item_id: int): pass
            def delete(self, item_id: int): pass

        with pytest.raises(TypeError):
            IncompleteRepository()

    def test_subclass_must_implement_delete(self):
        """Test that subclass must implement delete."""
        class IncompleteRepository(BaseRepository):
            def find_all(self): pass
            def find_by_id(self, item_id: int): pass
            def save(self, item): pass

        with pytest.raises(TypeError):
            IncompleteRepository()

    def test_concrete_subclass_can_be_instantiated(self):
        """Test that a concrete implementation can be instantiated."""
        class ConcreteRepository(BaseRepository[Polygon]):
            def find_all(self) -> list[Polygon]:
                return []
            def find_by_id(self, item_id: int) -> Polygon | None:
                return None
            def save(self, item: Polygon) -> Polygon:
                return item
            def delete(self, item_id: int) -> bool:
                return False

        repo = ConcreteRepository()
        assert repo is not None