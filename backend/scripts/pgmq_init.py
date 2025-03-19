#!/usr/bin/env python3
"""
Script d'initialisation pour PGMQ.
Vérifie que PGMQ est correctement installé et que les queues nécessaires existent.
À exécuter après les migrations de base de données.
"""

import logging

from sqlalchemy import text

from app.database.session import engine

logger = logging.getLogger(__name__)


def init_pgmq():
    """Initialise PGMQ et crée les queues nécessaires."""
    try:
        # Vérifier si l'extension pgmq est activée
        with engine.connect() as conn:
            # Vérifier si l'extension pgmq existe
            check_ext = conn.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'pg_message_queue'")
            ).fetchone()

            if not check_ext:
                logger.info(
                    "Extension pg_message_queue n'est pas active, activation..."
                )
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_message_queue"))
                conn.commit()
                logger.info("Extension pg_message_queue activée avec succès")

            # Liste des queues à créer
            queues = [
                "default",
                "rag_queue",
                "embeddings",
            ]  # Ajoutez vos files selon vos besoins

            # Créer chaque queue si elle n'existe pas
            for queue in queues:
                # Vérifier si la queue existe déjà
                queue_exists = conn.execute(
                    text(
                        "SELECT EXISTS(SELECT 1 FROM pgmq.list_queues() WHERE queue_name = :queue)"
                    ).bindparams(queue=queue)
                ).scalar()

                if not queue_exists:
                    logger.info(f"Création de la queue PGMQ: {queue}")
                    conn.execute(
                        text("SELECT pgmq.create_queue(:queue)").bindparams(queue=queue)
                    )
                    conn.commit()
                    logger.info(f"Queue {queue} créée avec succès")
                else:
                    logger.info(f"Queue {queue} existe déjà")

            logger.info("Initialisation PGMQ terminée avec succès")

    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de PGMQ: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_pgmq()
