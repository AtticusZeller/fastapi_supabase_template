#!/usr/bin/env python3
"""
Script de rollback pour les migrations avec PGMQ.
Permet de remettre la base de données dans un état cohérent après un rollback.
"""

import logging
import sys

from sqlalchemy import text

from app.core.db import engine

logger = logging.getLogger(__name__)


def rollback_pgmq(target_revision):
    """
    Rollback PGMQ après un rollback Alembic.

    Args:
        target_revision: Révision Alembic cible du rollback
    """
    try:
        # 1. Sauvegarder les messages non traités (optionnel)
        # 2. Effectuer le rollback Alembic
        # 3. Réinitialiser PGMQ si nécessaire

        with engine.connect() as conn:
            # Vérifier l'état de pgmq après le rollback
            conn.execute(text("SELECT pgmq.create_queue('default')"))
            conn.commit()
            logger.info("Queue 'default' réinitialisée avec succès")

            # Réinitialiser d'autres queues si nécessaire

        logger.info(f"Rollback PGMQ vers {target_revision} terminé avec succès")

    except Exception as e:
        logger.error(f"Erreur lors du rollback PGMQ: {e}")
        raise


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: rollback_pgmq.py <target_revision>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    rollback_pgmq(sys.argv[1])
