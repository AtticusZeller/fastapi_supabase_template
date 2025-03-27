from sqlmodel import SQLModel

# Import base models first
from .base import User

# Then models that depend on base
from .file import FileMetadata
from .item import Item
from .profile import Profile, ProfilePicturesBucket
from .storage import ItemDocuments, ProfilePictures

# Pour Alembic
Base = SQLModel

__all__ = [
    "User",
    "Item",
    "Base",
    "Profile",
    "ProfilePicturesBucket",
    "FileMetadata",
    "ProfilePictures",
    "ItemDocuments",
]

STORAGE_BUCKETS = [
    ProfilePicturesBucket,
    ProfilePictures,
    ItemDocuments,
    # Ajoutez d'autres buckets ici...
]
