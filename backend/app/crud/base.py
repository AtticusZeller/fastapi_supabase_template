import uuid
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.base import InDBBase

ModelType = TypeVar("ModelType", bound=InDBBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLModel model class
        """
        self.model = model

    async def get(self, session: AsyncSession, *, id: uuid.UUID) -> ModelType | None:
        """Get a single record by id"""
        statement = select(self.model).where(self.model.id == id)
        result = await session.exec(statement)
        return result.one_or_none()

    async def get_multi(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """Get multiple records with pagination"""
        statement = select(self.model).offset(skip).limit(limit)
        result = await session.exec(statement)
        return result.all()

    async def create(
        self, session: AsyncSession, *, owner_id: uuid.UUID, obj_in: CreateSchemaType
    ) -> ModelType:
        """Create new record"""
        db_obj = self.model(**dict(owner_id=owner_id, **obj_in.model_dump()))
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self, session: AsyncSession, *, id: uuid.UUID, obj_in: UpdateSchemaType
    ) -> ModelType | None:
        """Update existing record"""
        db_obj = await self.get(session, id=id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            db_obj.sqlmodel_update(update_data)

            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def remove(self, session: AsyncSession, *, id: uuid.UUID) -> ModelType | None:
        """Remove a record"""
        obj = await self.get(session, id=id)
        if obj:
            await session.delete(obj)
            await session.commit()
        return obj

    async def get_multi_by_owner(
        self, session: AsyncSession, *, owner_id: uuid.UUID
    ) -> Sequence[ModelType]:
        """Get multiple records by owner"""
        statement = select(self.model).where(self.model.owner_id == owner_id)
        result = await session.exec(statement)
        return result.all()
