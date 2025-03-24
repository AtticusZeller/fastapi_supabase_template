import uuid

from sqlmodel import Session, select

from app.models.rag import (
    ChunkingStrategy,
    Document,
    DocumentNode,
    DocumentType,
    NodeType,
    QueryLog,
)


def test_document_model(session: Session):
    """Test du modèle Document."""
    # Création d'un document
    document = Document(
        title="Test Document",
        source="test.pdf",
        client_id=uuid.uuid4(),
        document_type=DocumentType.GENERIC,
        file_id=uuid.uuid4(),
        chunking_strategy=ChunkingStrategy.HYBRID,
        embedding_model="openai/text-embedding-3-small",
        chunk_size=512,
        chunk_overlap=50,
        metadata={"author": "Test Author", "keywords": ["test", "document"]},
        status="pending",
    )

    # Ajout à la session et commit
    session.add(document)
    session.commit()
    session.refresh(document)

    # Vérification des valeurs
    assert document.id is not None
    assert document.title == "Test Document"
    assert document.source == "test.pdf"
    assert document.document_type == DocumentType.GENERIC
    assert document.chunking_strategy == ChunkingStrategy.HYBRID
    assert document.embedding_model == "openai/text-embedding-3-small"
    assert document.chunk_size == 512
    assert document.chunk_overlap == 50
    assert document.metadata == {
        "author": "Test Author",
        "keywords": ["test", "document"],
    }
    assert document.status == "pending"
    assert document.created_at is not None
    assert document.updated_at is not None

    # Récupération depuis la base
    retrieved = session.exec(select(Document).where(Document.id == document.id)).first()
    assert retrieved is not None
    assert retrieved.title == "Test Document"


def test_document_node_model(session: Session):
    """Test du modèle DocumentNode."""
    # Création d'un document parent
    document = Document(
        title="Parent Document",
        source="parent.pdf",
        client_id=uuid.uuid4(),
        document_type=DocumentType.GENERIC,
        file_id=uuid.uuid4(),
        status="ready",
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    # Création d'un node racine
    root_node = DocumentNode(
        document_id=document.id,
        node_type=NodeType.DOCUMENT,
        content="Document content",
        metadata={"page_count": 10},
        index=0,
        level=0,
    )
    session.add(root_node)
    session.commit()
    session.refresh(root_node)

    # Création d'un node enfant
    child_node = DocumentNode(
        document_id=document.id,
        node_type=NodeType.CHUNK,
        parent_id=root_node.id,
        content="Chunk content",
        metadata={"start": 0, "end": 500},
        index=1,
        level=1,
        heading="Introduction",
    )
    session.add(child_node)
    session.commit()
    session.refresh(child_node)

    # Vérification des valeurs
    assert root_node.id is not None
    assert root_node.document_id == document.id
    assert root_node.node_type == NodeType.DOCUMENT
    assert root_node.parent_id is None

    assert child_node.id is not None
    assert child_node.document_id == document.id
    assert child_node.node_type == NodeType.CHUNK
    assert child_node.parent_id == root_node.id
    assert child_node.content == "Chunk content"
    assert child_node.metadata == {"start": 0, "end": 500}
    assert child_node.index == 1
    assert child_node.level == 1
    assert child_node.heading == "Introduction"

    # Récupération depuis la base avec la relation
    retrieved_document = session.exec(
        select(Document).where(Document.id == document.id)
    ).first()

    retrieved_nodes = session.exec(
        select(DocumentNode).where(DocumentNode.document_id == document.id)
    ).all()

    assert len(retrieved_nodes) == 2
    assert any(node.node_type == NodeType.DOCUMENT for node in retrieved_nodes)
    assert any(node.node_type == NodeType.CHUNK for node in retrieved_nodes)


def test_query_log_model(session: Session):
    """Test du modèle QueryLog."""
    # Création d'un log de requête
    query_log = QueryLog(
        client_id=uuid.uuid4(),
        query_text="test query",
        embedding=[0.1, 0.2, 0.3],  # Simplifié pour le test
        filters={"date": "2024-05-19"},
        retrieved_node_ids=[uuid.uuid4(), uuid.uuid4()],
        relevance_scores=[0.95, 0.85],
        response_text="Generated response",
        feedback_score=4,
        execution_time_ms=150,
    )

    # Ajout à la session et commit
    session.add(query_log)
    session.commit()
    session.refresh(query_log)

    # Vérification des valeurs
    assert query_log.id is not None
    assert query_log.query_text == "test query"
    assert len(query_log.embedding or []) == 3
    assert query_log.filters == {"date": "2024-05-19"}
    assert len(query_log.retrieved_node_ids or []) == 2
    assert len(query_log.relevance_scores or []) == 2
    assert query_log.relevance_scores[0] == 0.95
    assert query_log.response_text == "Generated response"
    assert query_log.feedback_score == 4
    assert query_log.execution_time_ms == 150
    assert query_log.created_at is not None
