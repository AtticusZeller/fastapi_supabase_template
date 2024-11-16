import uuid
from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import CRUDBase
from app.models.item import Item, ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    async def create(
        self, session: AsyncSession, *, owner_id: uuid.UUID, obj_in: ItemCreate
    ) -> Item:
        return await super().create(session, owner_id=owner_id, obj_in=obj_in)

    async def get(self, session: AsyncSession, *, id: uuid.UUID) -> Item | None:
        return await super().get(session, id=id)

    async def get_all(self, session: AsyncSession) -> Sequence[Item]:
        return await super().get_multi(session)

    async def get_multi_by_owner(
        self, session: AsyncSession, *, owner_id: uuid.UUID
    ) -> Sequence[Item]:
        return await super().get_multi_by_owner(session, owner_id=owner_id)

    async def update(
        self, session: AsyncSession, *, id: uuid.UUID, obj_in: ItemUpdate
    ) -> Item | None:
        return await super().update(session, id=id, obj_in=obj_in)

    async def remove(self, session: AsyncSession, *, id: uuid.UUID) -> Item | None:
        return await super().remove(session, id=id)


item = CRUDItem(Item)
