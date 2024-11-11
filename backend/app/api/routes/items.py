from fastapi import APIRouter

router = APIRouter()


# @router.post("/create-item")
# async def create_item(item_in: ItemCreate, session: SessionDep) -> Item:
#     return await item.create(session, obj_in=item_in)


# @router.get("/read-all-item")
# async def read_items(session: SessionDep) -> list[Item]:
#     return await item.get_all(session)


# @router.get("/get-by-id/{id}")
# async def read_item_by_id(id: str, session: SessionDep) -> Item | None:
#     return await item.get(session, id=id)


# @router.get("/get-by-owner")
# async def read_item_by_owner(session: SessionDep, user: CurrentUser) -> list[Item]:
#     return await item.get_multi_by_owner(session, user=user)


# @router.put("/update-item")
# async def update_item(item_in: ItemUpdate, session: SessionDep) -> Item:
#     return await item.update(session, obj_in=item_in)


# @router.delete("/delete/{id}")
# async def delete_item(id: str, session: SessionDep) -> Item:
#     return await item.delete(session, id=id)
