# services/ignored_item.py
from sqlalchemy.orm import Session
from db.session import get_db                     # ← используем contextmanager
from repositories.ignored_item import IgnoredItemRepository
from schemas.ignored_item import IgnoredItemCreate, IgnoredItemRead
from models.ignored_item import IgnoredItem

class IgnoredItemService:
    def create(self, data: IgnoredItemCreate) -> IgnoredItemRead:
        """
        Добавляет предмет в игнор-лист только если его ещё нет.
        Если предмет уже существует — просто возвращает существующий объект.
        """
        with get_db() as session:
            repo = IgnoredItemRepository(session)

            # Проверяем существование по market_hash_name
            existing_item = repo.get_by_market_hash_name(data.market_hash_name)

            if existing_item:
                # Ничего не добавляем, возвращаем существующий
                return IgnoredItemRead.model_validate(existing_item)

            # Предмета нет — создаём новый
            new_item = IgnoredItem(**data.model_dump())
            repo.add(new_item)

            # commit происходит автоматически при выходе из with
            return IgnoredItemRead.model_validate(new_item)

    def get_by_market_hash_name(self, market_hash_name: str) -> IgnoredItemRead | None:
        with get_db() as session:
            repo = IgnoredItemRepository(session)
            # предполагаем, что в репозитории уже есть этот метод
            item = repo.get_by_market_hash_name(market_hash_name)
            return IgnoredItemRead.model_validate(item) if item else None