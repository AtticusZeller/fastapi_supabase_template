import uuid
from collections.abc import AsyncGenerator

import pytest
from faker import Faker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app import crud
from app.core.auth import get_super_client
from app.models import User as UserInDB
from app.models.item import Item, ItemCreate, ItemUpdate

fake = Faker()


@pytest.fixture(scope="module")
async def test_user_id(db: AsyncSession) -> AsyncGenerator[uuid.UUID, None]:
    """Fixture to create a test user"""
    super_client = await get_super_client()
    try:
        response = await super_client.auth.sign_up(
            {"email": fake.email(), "password": "testpassword123"}
        )
        yield uuid.UUID(response.user.id)
    finally:
        result = await db.exec(
            select(UserInDB).where(str(UserInDB.id) == response.user.id)
        )
        user = result.first()
        if user:
            await db.delete(user)
            await db.commit()


@pytest.fixture
async def test_item(
    db: AsyncSession, test_user_id: uuid.UUID
) -> AsyncGenerator[Item, None]:
    """Fixture to create a test item and clean it up after the test"""
    item_in = ItemCreate(
        title=fake.sentence(nb_words=3), description=fake.text(max_nb_chars=200)
    )
    item = await crud.item.create(db, owner_id=test_user_id, obj_in=item_in)
    yield item
    # Cleanup
    await crud.item.remove(db, id=item.id)


@pytest.mark.anyio
async def test_create_item(db: AsyncSession, test_user_id: uuid.UUID) -> None:
    """Test creating a new item"""
    title = fake.sentence(nb_words=3)
    description = fake.text(max_nb_chars=200)
    item_in = ItemCreate(title=title, description=description)

    item = await crud.item.create(db, owner_id=test_user_id, obj_in=item_in)

    assert item.id is not None
    assert item.title == title
    assert item.description == description
    assert item.owner_id == test_user_id

    # Cleanup
    await crud.item.remove(db, id=item.id)


@pytest.mark.anyio
async def test_get_item(db: AsyncSession, test_item: Item) -> None:
    """Test retrieving a single item"""
    stored_item = await crud.item.get(db, id=test_item.id)

    assert stored_item is not None
    assert stored_item.id == test_item.id
    assert stored_item.title == test_item.title
    assert stored_item.description == test_item.description
    assert stored_item.owner_id == test_item.owner_id


@pytest.mark.anyio
async def test_get_nonexistent_item(db: AsyncSession, test_user_id: uuid.UUID) -> None:
    """Test retrieving a non-existent item"""
    nonexistent_item = await crud.item.get(db, id=test_user_id)
    assert nonexistent_item is None


@pytest.mark.anyio
async def test_update_item(db: AsyncSession, test_item: Item) -> None:
    """Test updating an item"""
    new_title = fake.sentence(nb_words=3)
    new_description = fake.text(max_nb_chars=200)
    update_data = ItemUpdate(title=new_title, description=new_description)

    updated_item = await crud.item.update(db, id=test_item.id, obj_in=update_data)

    assert updated_item is not None
    assert updated_item.id == test_item.id
    assert updated_item.title == new_title
    assert updated_item.description == new_description
    assert updated_item.owner_id == test_item.owner_id


@pytest.mark.anyio
async def test_update_nonexistent_item(
    db: AsyncSession, test_user_id: uuid.UUID
) -> None:
    """Test updating a non-existent item"""
    update_data = ItemUpdate(title=fake.sentence(nb_words=3))
    updated_item = await crud.item.update(db, id=test_user_id, obj_in=update_data)
    assert updated_item is None


@pytest.mark.anyio
async def test_delete_item(db: AsyncSession, test_item: Item) -> None:
    """Test deleting an item"""
    deleted_item = await crud.item.remove(db, id=test_item.id)
    assert deleted_item is not None
    assert deleted_item.id == test_item.id

    # Verify item is deleted
    item = await crud.item.get(db, id=test_item.id)
    assert item is None


# @pytest.mark.anyio
# async def test_get_multi_by_owner(db: AsyncSession, test_user_id: uuid.UUID) -> None:
#     """Test retrieving multiple items by owner"""
#     # Create multiple items for the same owner
#     items_data = [
#         ItemCreate(title=fake.sentence(nb_words=3), description=fake.text())
#         for _ in range(3)
#     ]
#     created_items = []
#     for item_data in items_data:
#         item = await crud.item.create(db, owner_id=test_user_id, obj_in=item_data)
#         created_items.append(item)

#     # Retrieve items by owner
#     items = await crud.item.get_multi_by_owner(db, owner_id=test_user_id)

#     assert len(items) == len(created_items)
#     assert all(item.owner_id == test_user_id for item in items)

#     # Cleanup
#     for item in created_items:
#         await crud.item.remove(db, id=item.id)


# @pytest.mark.anyio
# async def test_get_all_items(db: AsyncSession, test_user_id: uuid.UUID) -> None:
#     """Test retrieving all items with pagination"""
#     # Create multiple items
#     items_data = [
#         ItemCreate(title=fake.sentence(nb_words=3), description=fake.text())
#         for _ in range(5)
#     ]
#     created_items = []
#     for item_data in items_data:
#         item = await crud.item.create(db, owner_id=test_user_id, obj_in=item_data)
#         created_items.append(item)

#     # Test pagination
#     items_page_1 = await crud.item.get_multi(db, skip=0, limit=3)
#     items_page_2 = await crud.item.get_multi(db, skip=3, limit=3)

#     assert len(items_page_1) == 3
#     assert len(items_page_2) == 2

#     # Cleanup
#     for item in created_items:
#         await crud.item.remove(db, id=item.id)
#         await db.commit()
