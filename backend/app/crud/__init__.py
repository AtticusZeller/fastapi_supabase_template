from .crud_item import item
from .file import file_metadata

# For a new basic set of CRUD operations you could just do
__all__ = ["item", "file_metadata"]
# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
