from gotrue import User, UserAttributes  # type: ignore
from pydantic import BaseModel


# Shared properties
class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None


# request
class UserIn(Token, User):  # type: ignore
    pass


# Properties to receive via API on creation
# in
class UserCreate(BaseModel):
    pass


# Properties to receive via API on update
# in
class UserUpdate(UserAttributes):  # type: ignore
    pass


# response


class UserInDBBase(BaseModel):
    pass


# Properties to return to client via api
# out
class UserOut(Token):
    pass


# Properties properties stored in DB
class UserInDB(User):  # type: ignore
    pass
