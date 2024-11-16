from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import get_super_client
from app.core.config import settings
from app.models import User

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), echo=True, future=True
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


async def init_db(session: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel
    # # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    result = await session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    )
    user = result.first()
    if not user:
        super_client = await get_super_client()
        response = await super_client.auth.sign_up(
            {
                "email": settings.FIRST_SUPERUSER,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
            }
        )
        assert response.user.email == settings.FIRST_SUPERUSER
        assert response.user.id is not None
        assert response.session.access_token is not None
