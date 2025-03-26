from sqlmodel import SQLModel

from .file import FileMetadata
from .item import Item
from .profile import Profile, ProfilePicturesBucket
from .storage import ItemDocuments, ProfilePictures
from .user import User  # Modèle pour la table auth.users, ne pas migrer

# Pour Alembic
Base = SQLModel

__all__ = [
    "User",  # Inclus pour les relations, mais pas pour les migrations
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
