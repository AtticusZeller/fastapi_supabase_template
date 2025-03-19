"""Add pgvector extension

Revision ID: 20250319
Revises: 
Create Date: 2025-03-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '20250319'
down_revision: Union[str, None] = None  # Ajuster selon la dernière migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Activer l'extension pgvector
    op.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
    
    # Créer les fonctions d'aide pour la recherche vectorielle
    op.execute(text('''
    CREATE OR REPLACE FUNCTION match_documents(
        query_embedding vector(1536),
        match_threshold float,
        match_count int
    )
    RETURNS TABLE (
        id uuid,
        content text,
        metadata jsonb,
        similarity float
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT
            n.id,
            n.content,
            n.metadata,
            1 - (n.embedding <=> query_embedding) AS similarity
        FROM documentnode n
        WHERE 1 - (n.embedding <=> query_embedding) > match_threshold
        ORDER BY similarity DESC
        LIMIT match_count;
    END;
    $$;
    '''))


def downgrade() -> None:
    # Supprimer les fonctions
    op.execute(text('DROP FUNCTION IF EXISTS match_documents;'))
    
    # On ne supprime pas l'extension car d'autres applications pourraient l'utiliser
    # op.execute(text('DROP EXTENSION IF EXISTS vector;'))
