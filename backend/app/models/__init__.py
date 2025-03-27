from sqlmodel import SQLModel

# Then models that depend on base
from .file import FileMetadata
from .item import Item
from .profile import Profile, ProfilePicturesBucket
from .storage import ItemDocuments, ProfilePictures

# Import base models first
from .user import User

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
