import asyncio
import logging

from sqlalchemy import Engine
from sqlmodel import Session

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init(db_engine: Engine) -> None:
    with Session(db_engine) as session:
        await init_db(session)


async def main() -> None:
    logger.info("Creating initial data")
    await init(engine)
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
