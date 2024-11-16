import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init(db_ngine: AsyncEngine) -> None:
    async with AsyncSession(db_ngine) as session:
        await init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    asyncio.run(init(engine))
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
