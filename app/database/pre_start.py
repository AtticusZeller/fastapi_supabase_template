import logging
import os
from sqlalchemy import text

from app.database.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    # Créer les tables si elles n'existent pas déjà
    try:
        logger.info("Initialising database connections")
        # Activer l'extension pgvector si elle n'est pas déjà active
        create_extension_query = text("CREATE EXTENSION IF NOT EXISTS vector;")
        with engine.connect() as conn:
            conn.execute(create_extension_query)
            conn.commit()
        logger.info("Extension pgvector activated successfully")
        
    except Exception as e:
        logger.error(f"Error initialising database: {e}")
        raise e


def main() -> None:
    logger.info("Initialising database")
    init()
    logger.info("Database initialised")


if __name__ == "__main__":
    main()