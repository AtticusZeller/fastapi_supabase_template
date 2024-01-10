from pydantic import BaseModel


## request


# Shared properties
class ItemBase(BaseModel):
    # where the data
    table_name: str


# Properties to receive on item creation
# in
class ItemCreate(ItemBase):
    # inherent to add more properties for creating
    test_data: str


# Properties to receive on item update
# in
class ItemUpdate(ItemBase):
    # inherent to add more properties for updating
    id: str
    test_data: str

## response


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: str
    user_id: str
    created_at: str


# Properties to return to client
# out
class Item(ItemInDBBase):
    test_data: str


# Properties properties stored in DB
class ItemInDB(ItemInDBBase):
    test_data: str
