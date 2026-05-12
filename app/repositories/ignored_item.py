from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from .base import BaseRepository
from models.ignored_item import IgnoredItem


class IgnoredItemRepository(BaseRepository[IgnoredItem]):
    def __init__(self, session: Session):
        super().__init__(session, IgnoredItem)

    def get_by_market_hash_name(self, market_hash_name: str) -> IgnoredItem | None:
        stmt = select(IgnoredItem).where(
            IgnoredItem.market_hash_name == market_hash_name
        )
        return self.session.scalars(stmt).first()