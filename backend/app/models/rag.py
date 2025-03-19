import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import Column, Float, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import RLSModel


class DocumentType(str, Enum):
    """Types sémantiques de documents supportés."""

    UNKNOWN = "unknown"
    FINANCIAL_REPORT = "financial_report"
    GEOTECHNICAL_REPORT = "geotechnical_report"
    CONTRACT = "contract"
    INVOICE = "invoice"
    TECHNICAL_SPEC = "technical_spec"
    GENERIC = "generic"


class ChunkingStrategy(str, Enum):
    """Stratégies de chunking disponibles."""

    FIXED_SIZE = "fixed_size"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class NodeType(str, Enum):
    """Types de nœuds dans le graphe de document."""

    DOCUMENT = "document"
    SECTION = "section"
    CHUNK = "chunk"
    TABLE = "table"
    IMAGE = "image"


class Document(RLSModel):
    """Modèle de document RAG complet."""

    # Métadonnées de base
    title: str = Field(index=True)
    source: str
    client_id: uuid.UUID = Field(foreign_key="auth.users.id", index=True)
    document_type: DocumentType = Field(default=DocumentType.UNKNOWN, index=True)
    file_id: uuid.UUID = Field(foreign_key="file_metadata.id")

    # Paramètres de traitement
    chunking_strategy: ChunkingStrategy = Field(default=ChunkingStrategy.HYBRID)
    embedding_model: str = Field(default="openai/text-embedding-3-small")
    chunk_size: int = Field(default=512)
    chunk_overlap: int = Field(default=50)

    # Statut et métadonnées
    metadata: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    status: str = Field(
        default="pending"
    )  # pending, processing, indexing, ready, error
    error_message: str | None = Field(default=None)
    text_length: int | None = Field(default=None)
    processing_stats: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )

    # Dates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relations
    nodes: list["DocumentNode"] = Relationship(back_populates="document")

    # Index pour recherche full-text (sera configuré dans les migrations)
    # __table_args__ = (
    #     Index("ix_document_metadata_gin", metadata, postgresql_using="gin"),
    # )


class DocumentNode(RLSModel):
    """Nœud dans la hiérarchie du document (document, section, chunk)."""

    document_id: uuid.UUID = Field(foreign_key="document.id", index=True)
    node_type: NodeType = Field(default=NodeType.CHUNK, index=True)
    parent_id: uuid.UUID | None = Field(
        foreign_key="documentnode.id", default=None, index=True
    )

    # Données de contenu
    content: str = Field(sa_column=Column(Text))
    metadata: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    embedding: list[float] | None = Field(
        default=None
    )  # Sera configuré comme VECTOR dans les migrations

    # Métadonnées de position et structure
    index: int = Field(default=0)
    level: int = Field(default=0)
    heading: str | None = Field(default=None)

    # Relations de navigation
    document: Document = Relationship(back_populates="nodes")

    # Les relations parent-enfant seront gérées au niveau applicatif
    # pour simplifier le modèle et éviter les problèmes de circularité


class QueryLog(RLSModel):
    """Journal des requêtes RAG pour amélioration continue."""

    client_id: uuid.UUID = Field(foreign_key="auth.users.id", index=True)
    query_text: str
    embedding: list[float] | None = Field(
        default=None
    )  # Sera configuré comme VECTOR dans les migrations
    filters: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))

    # Résultats et métadonnées
    retrieved_node_ids: list[uuid.UUID] = Field(
        default_factory=list, sa_column=Column(ARRAY(SQLModel.UUID))
    )
    relevance_scores: list[float] = Field(
        default_factory=list, sa_column=Column(ARRAY(Float))
    )
    response_text: str | None = Field(default=None)

    # Feedback et métriques
    feedback_score: int | None = Field(default=None)
    feedback_text: str | None = Field(default=None)
    execution_time_ms: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
