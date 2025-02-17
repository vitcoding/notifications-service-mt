from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import Base

ModelType = TypeVar("ModelType", bound=Base)  # type: ignore
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
DeleteSchemaType = TypeVar("DeleteSchemaType", bound=BaseModel)


class Repository(ABC):
    """An abstract class for work with a database."""

    @abstractmethod
    def get_one(self, *args, **kwargs): ...

    @abstractmethod
    def get_many(self, *args, **kwargs): ...

    @abstractmethod
    def get_many_with_condition(self, *args, **kwargs): ...

    @abstractmethod
    def create(self, *args, **kwargs): ...

    @abstractmethod
    def update(self, *args, **kwargs): ...

    @abstractmethod
    def delete(self, *args, **kwargs): ...


class RepositoryDB(
    Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):
    """A class for work with a database."""

    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get_one(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Gets the item by id."""

        statement = select(self._model).where(self._model.id == id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_many(
        self,
        db: AsyncSession,
        *,
        sort="-created_at",
        skip=0,
        limit=100,
    ) -> list[ModelType]:
        """Gets a list of items."""

        if sort is not None and len(sort) > 1:
            order = (asc, desc)[sort.startswith("-")]
            if sort.startswith(("-", "+")):
                sort_field = sort[1:]
            else:
                sort_field = sort

        statement = (
            select(self._model)
            .order_by(order(getattr(self._model, sort_field)))
            .offset(skip)
            .limit(limit)
        )
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def get_many_with_condition(
        self,
        db: AsyncSession,
        *,
        attribute: str | UUID,
        value: Any,
        sort="-created_at",
        skip=0,
        limit=100,
    ) -> list[ModelType]:
        """Gets a list of items with the condition."""

        if sort is not None and len(sort) > 1:
            order = (asc, desc)[sort.startswith("-")]
            if sort.startswith(("-", "+")):
                sort_field = sort[1:]
            else:
                sort_field = sort

        statement = (
            select(self._model)
            .where(
                self._model.__getattribute__(self._model, attribute) == value
            )
            .order_by(order(getattr(self._model, sort_field)))
            .offset(skip)
            .limit(limit)
        )
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: CreateSchemaType
    ) -> ModelType:
        """Creates an item."""

        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
    ) -> ModelType:
        """Updates the item."""
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
    ) -> None:
        """Deletes the item."""

        await db.delete(db_obj)
        await db.commit()
        db_obj = None
        return db_obj
