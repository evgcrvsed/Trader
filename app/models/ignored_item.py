from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped
from .base import Base


class IgnoredItem(Base):
    __tablename__ = "ignored_items"

    id: Mapped[int] = Column(Integer, primary_key=True)
    market_hash_name: Mapped[str] = Column(String(100), nullable=False, unique=True)
