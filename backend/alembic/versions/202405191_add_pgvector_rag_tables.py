"""Ajout de l'extension pgvector et tables RAG

Revision ID: 202405191
Revises: # Mettre ici la dernière révision
Create Date: 2024-05-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable
import uuid
from enum import Enum

# revision identifiers, used by Alembic.
revision = '202405191'
down_revision = None  # TODO: Mettre ici la dernière révision de la base
branch_labels = None
depends_on = None

Base = declarative_base()

# Définir les énums comme dans les modèles SQLModel
class DocumentTypeEnum(str, Enum):
    UNKNOWN = "unknown"
    FINANCIAL_REPORT = "financial_report"
    GEOTECHNICAL_REPORT = "geotechnical_report"
    CONTRACT = "contract"
    INVOICE = "invoice"
    TECHNICAL_SPEC = "technical_spec"
    GENERIC = "generic"

class ChunkingStrategyEnum(str, Enum):
    FIXED_SIZE = "fixed_size"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"

class NodeTypeEnum(str, Enum):
    DOCUMENT = "document"
    SECTION = "section"
    CHUNK = "chunk"
    TABLE = "table"
    IMAGE = "image"

# Définir les tables pour SQLAlchemy
class Document(Base):
    __tablename__ = "document"

    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)
    title = sa.Column(sa.String, nullable=False, index=True)
    source = sa.Column(sa.String, nullable=False)
    client_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = sa.Column(sa.Enum(DocumentTypeEnum), nullable=False, index=True, default=DocumentTypeEnum.UNKNOWN)
    file_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("file_metadata.id", ondelete="CASCADE"), nullable=False)

    # Paramètres de traitement
    chunking_strategy = sa.Column(sa.Enum(ChunkingStrategyEnum), nullable=False, default=ChunkingStrategyEnum.HYBRID)
    embedding_model = sa.Column(sa.String, nullable=False, default="text-embedding-3-small")
    chunk_size = sa.Column(sa.Integer, nullable=False, default=512)
    chunk_overlap = sa.Column(sa.Integer, nullable=False, default=50)

    # Statut et métadonnées
    metadata = sa.Column(postgresql.JSONB, nullable=False, default={})
    status = sa.Column(sa.String, nullable=False, default="pending")
    error_message = sa.Column(sa.String, nullable=True)
    text_length = sa.Column(sa.Integer, nullable=True)
    processing_stats = sa.Column(postgresql.JSONB, nullable=False, default={})

    # Dates
    created_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())

class DocumentNode(Base):
    __tablename__ = "documentnode"

    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)
    document_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("document.id", ondelete="CASCADE"), nullable=False, index=True)
    node_type = sa.Column(sa.Enum(NodeTypeEnum), nullable=False, default=NodeTypeEnum.CHUNK, index=True)
    parent_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("documentnode.id", ondelete="CASCADE"), nullable=True, index=True)

    # Données de contenu
    content = sa.Column(sa.Text, nullable=False)
    metadata = sa.Column(postgresql.JSONB, nullable=False, default={})
    # Le champ embedding sera créé après la création de la table

    # Métadonnées de position et structure
    index = sa.Column(sa.Integer, nullable=False, default=0, index=True)
    level = sa.Column(sa.Integer, nullable=False, default=0)
    heading = sa.Column(sa.String, nullable=True)

class QueryLog(Base):
    __tablename__ = "querylog"

    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)
    client_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True)
    query_text = sa.Column(sa.String, nullable=False)
    # Le champ embedding sera créé après la création de la table
    filters = sa.Column(postgresql.JSONB, nullable=False, default={})

    # Résultats et métadonnées
    retrieved_node_ids = sa.Column(postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False, default=[])
    relevance_scores = sa.Column(postgresql.ARRAY(sa.Float), nullable=False, default=[])
    response_text = sa.Column(sa.Text, nullable=True)

    # Feedback et métriques
    feedback_score = sa.Column(sa.Integer, nullable=True)
    feedback_text = sa.Column(sa.String, nullable=True)
    execution_time_ms = sa.Column(sa.Integer, nullable=False, default=0)

    created_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())


def upgrade():
    # Créer l'extension pgvector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Créer les types enum
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'document_type') THEN
            CREATE TYPE document_type AS ENUM (
                'unknown', 'financial_report', 'geotechnical_report',
                'contract', 'invoice', 'technical_spec', 'generic'
            );
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'chunking_strategy') THEN
            CREATE TYPE chunking_strategy AS ENUM (
                'fixed_size', 'paragraph', 'sentence', 'semantic', 'hybrid'
            );
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'node_type') THEN
            CREATE TYPE node_type AS ENUM (
                'document', 'section', 'chunk', 'table', 'image'
            );
        END IF;
    END $$;
    """)

    # Créer les tables avec SQLAlchemy
    op.create_table(
        'document',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', sa.Enum('unknown', 'financial_report', 'geotechnical_report', 'contract', 'invoice', 'technical_spec', 'generic', name='document_type'), nullable=False, server_default='unknown'),
        sa.Column('file_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('file_metadata.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunking_strategy', sa.Enum('fixed_size', 'paragraph', 'sentence', 'semantic', 'hybrid', name='chunking_strategy'), nullable=False, server_default='hybrid'),
        sa.Column('embedding_model', sa.String(), nullable=False, server_default='text-embedding-3-small'),
        sa.Column('chunk_size', sa.Integer(), nullable=False, server_default='512'),
        sa.Column('chunk_overlap', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('text_length', sa.Integer(), nullable=True),
        sa.Column('processing_stats', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_index('ix_document_title', 'document', ['title'])
    op.create_index('ix_document_client_id', 'document', ['client_id'])
    op.create_index('ix_document_document_type', 'document', ['document_type'])
    op.create_index('ix_document_metadata_gin', 'document', ['metadata'], postgresql_using='gin')

    op.create_table(
        'documentnode',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('document.id', ondelete='CASCADE'), nullable=False),
        sa.Column('node_type', sa.Enum('document', 'section', 'chunk', 'table', 'image', name='node_type'), nullable=False, server_default='chunk'),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documentnode.id', ondelete='CASCADE'), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('heading', sa.String(), nullable=True),
    )

    op.create_index('ix_documentnode_document_id', 'documentnode', ['document_id'])
    op.create_index('ix_documentnode_node_type', 'documentnode', ['node_type'])
    op.create_index('ix_documentnode_parent_id', 'documentnode', ['parent_id'])
    op.create_index('ix_documentnode_index', 'documentnode', ['index'])
    op.create_index('ix_documentnode_metadata_gin', 'documentnode', ['metadata'], postgresql_using='gin')

    # Ajouter la colonne embedding comme vector(1536)
    op.execute("ALTER TABLE documentnode ADD COLUMN embedding vector(1536);")

    op.create_table(
        'querylog',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('query_text', sa.String(), nullable=False),
        sa.Column('filters', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('retrieved_node_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False, server_default='{}'),
        sa.Column('relevance_scores', postgresql.ARRAY(sa.Float()), nullable=False, server_default='{}'),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('feedback_score', sa.Integer(), nullable=True),
        sa.Column('feedback_text', sa.String(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_index('ix_querylog_client_id', 'querylog', ['client_id'])

    # Ajouter la colonne embedding comme vector(1536)
    op.execute("ALTER TABLE querylog ADD COLUMN embedding vector(1536);")

    # Créer l'index ivfflat pour la recherche vectorielle rapide
    op.execute("CREATE INDEX IF NOT EXISTS ix_documentnode_embedding_vector_idx ON documentnode USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);")


def downgrade():
    # Supprimer les tables dans l'ordre inverse
    op.drop_table('querylog')
    op.drop_table('documentnode')
    op.drop_table('document')

    # Supprimer les types enum
    op.execute("DROP TYPE IF EXISTS node_type;")
    op.execute("DROP TYPE IF EXISTS chunking_strategy;")
    op.execute("DROP TYPE IF EXISTS document_type;")

    # Nous ne supprimons pas l'extension pgvector car elle pourrait être utilisée par d'autres applications
