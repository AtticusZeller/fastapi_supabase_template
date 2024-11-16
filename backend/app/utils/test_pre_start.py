import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init(db_engine: AsyncEngine) -> None:
    try:
        async with AsyncSession(db_engine) as session:
            await session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    asyncio.run(init(engine))
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
