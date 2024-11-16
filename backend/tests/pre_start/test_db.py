import logging

import pytest

from app.core.db import engine
from app.utils.init_data import init as init_db
from app.utils.test_pre_start import init as connect_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.anyio
async def test_init_db() -> None:
    await connect_db(engine)
    await init_db(engine)
