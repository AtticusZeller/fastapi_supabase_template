import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """NOTE: do not migrate with alembic with it"""

    __tablename__ = "users"
    __table_args__ = {"schema": "auth", "keep_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(max_length=255)
