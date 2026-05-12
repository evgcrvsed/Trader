from typing import TypeVar, Generic, Type
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql import Select

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def add(self, obj: T) -> T:
        self.session.add(obj)
        return obj

    def get_by_id(self, id_: int) -> T | None:
        return self.session.get(self.model, id_)

    def get_all(self) -> list[T]:
        return list(self.session.scalars(select(self.model)).all())

    def delete(self, obj: T) -> None:
        self.session.delete(obj)