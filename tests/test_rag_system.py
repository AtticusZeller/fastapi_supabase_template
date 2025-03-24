import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.models.rag import RAGCollection
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService


# Mock pour le service d'embedding
@pytest.fixture
def mock_embedding_service():
    embedding_service = MagicMock(spec=EmbeddingService)
    # Simuler la création d'un embedding
    embedding_service.create_embedding.return_value = "[0.1,0.2,0.3,0.4,0.5]"
    return embedding_service


# Test du service RAG
@pytest.mark.asyncio
async def test_create_collection(db_session: Session):
    """Test la création d'une collection RAG"""
    # Arrange
    rag_service = RAGService(db_session)
    name = "Test Collection"
    description = "This is a test collection"

    # Act
    collection = await rag_service.create_collection(name, description)

    # Assert
    assert collection is not None
    assert collection.name == name
    assert collection.description == description
    assert collection.is_active is True


@pytest.mark.asyncio
async def test_add_document(db_session: Session, mock_embedding_service):
    """Test l'ajout d'un document à une collection"""
    # Arrange
    with patch(
        "app.services.rag_service.EmbeddingService", return_value=mock_embedding_service
    ):
        rag_service = RAGService(db_session)
        collection = await rag_service.create_collection("Test Collection")
        title = "Test Document"
        content = "This is the content of a test document."

        # Act
        document = await rag_service.add_document(
            collection_id=collection.id,
            title=title,
            content=content,
            process_async=False,  # Pour exécuter directement sans Celery
        )

        # Assert
        assert document is not None
        assert document.title == title
        assert document.content == content
        assert document.collection_id == collection.id


@pytest.mark.asyncio
async def test_search_documents(db_session: Session, mock_embedding_service):
    """Test la recherche de documents similaires"""
    # Arrange
    with patch(
        "app.services.rag_service.EmbeddingService", return_value=mock_embedding_service
    ):
        # Configurer le mock pour la recherche de similarité
        mock_embedding_service.calculate_similarity.return_value = 0.85

        rag_service = RAGService(db_session)
        collection = await rag_service.create_collection("Test Collection")

        # Ajouter des documents de test
        doc1 = await rag_service.add_document(
            collection_id=collection.id,
            title="Document 1",
            content="This is the first document about artificial intelligence.",
            process_async=False,
        )

        doc2 = await rag_service.add_document(
            collection_id=collection.id,
            title="Document 2",
            content="This is about machine learning and neural networks.",
            process_async=False,
        )

        # Act
        query = "What is artificial intelligence?"
        results = await rag_service.search_documents(collection.id, query, limit=5)

        # Assert
        assert len(results) > 0
        # Vérifier que le service d'embedding a été appelé
        mock_embedding_service.create_embedding.assert_called_with(query)


@pytest.mark.asyncio
async def test_delete_collection(db_session: Session):
    """Test la suppression d'une collection et ses documents"""
    # Arrange
    rag_service = RAGService(db_session)
    collection = await rag_service.create_collection("Test Collection for Deletion")

    # Act
    result = await rag_service.delete_collection(collection.id)

    # Assert
    assert result is True
    # Vérifier que la collection a bien été supprimée
    remaining = (
        db_session.query(RAGCollection)
        .filter(RAGCollection.id == collection.id)
        .first()
    )
    assert remaining is None
