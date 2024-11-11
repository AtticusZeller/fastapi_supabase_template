from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.auth import get_current_user
from app.core.db import get_db
from app.schemas.auth import UserIn

CurrentUser = Annotated[UserIn, Depends(get_current_user)]


SessionDep = Annotated[Session, Depends(get_db)]
