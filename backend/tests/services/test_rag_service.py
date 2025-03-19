import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.rag import ChunkingStrategy, DocumentType
from app.services.rag import RAGService
from app.services.storage import StorageService


@pytest.fixture
def mock_storage_service():
    # Créer un mock du StorageService
    storage_service = MagicMock(spec=StorageService)
    storage_service.upload_file = AsyncMock()
    return storage_service


@pytest.fixture
def rag_service(mock_storage_service):
    # Créer le service RAG avec le mock du StorageService
    return RAGService(storage_service=mock_storage_service)


async def test_validate_file_size_limit(rag_service):
    """Test de la validation de la taille du fichier."""
    # Créer un fichier simulé trop grand (21MB)
    mock_file = MagicMock()
    mock_file.read = AsyncMock(return_value=b"x" * (21 * 1024 * 1024))
    mock_file.seek = AsyncMock()

    # Tester que l'exception est bien levée
    with pytest.raises(HTTPException) as exc_info:
        await rag_service._validate_file(mock_file)

    assert exc_info.value.status_code == 413
    assert "File too large" in exc_info.value.detail

    # Vérifier que seek a été appelé
    mock_file.seek.assert_called_once_with(0)


async def test_validate_file_type(rag_service):
    """Test de la validation du type de fichier."""
    # Créer un fichier simulé avec un type non supporté
    mock_file = MagicMock()
    mock_file.read = AsyncMock(return_value=b"test content")
    mock_file.seek = AsyncMock()
    mock_file.content_type = "image/jpeg"  # Type non supporté pour RAG

    # Tester que l'exception est bien levée
    with pytest.raises(HTTPException) as exc_info:
        await rag_service._validate_file(mock_file)

    assert exc_info.value.status_code == 415
    assert "Unsupported file type" in exc_info.value.detail


async def test_detect_document_type(rag_service):
    """Test de la détection du type de document."""
    # Créer un fichier simulé pour un contrat
    mock_file = MagicMock()
    mock_file.read = AsyncMock(return_value=b"contract agreement between parties")
    mock_file.seek = AsyncMock()
    mock_file.filename = "contract.pdf"

    # Détecter le type
    doc_type = await rag_service._detect_document_type(mock_file, "Contract Title")

    # Vérifier le résultat
    assert doc_type == DocumentType.CONTRACT

    # Réinitialiser le mock
    mock_file.read = AsyncMock(return_value=b"financial report 2024 revenue")
    mock_file.filename = "financial.pdf"

    # Détecter le type
    doc_type = await rag_service._detect_document_type(mock_file, "Financial Report")

    # Vérifier le résultat
    assert doc_type == DocumentType.FINANCIAL_REPORT


@patch("app.core.celery.celery_app.send_task")
async def test_ingest_document(
    mock_send_task, rag_service, mock_storage_service, session: Session
):
    """Test de l'ingestion d'un document."""
    # Configurer les mocks
    mock_file = MagicMock()
    mock_file.read = AsyncMock(return_value=b"test content")
    mock_file.seek = AsyncMock()
    mock_file.content_type = "application/pdf"
    mock_file.filename = "test.pdf"

    # Simuler le résultat de l'upload
    file_meta = MagicMock()
    file_meta.id = uuid.uuid4()
    mock_storage_service.upload_file.return_value = ("path/to/file.pdf", file_meta)

    # Simuler la tâche Celery
    task_mock = MagicMock()
    task_mock.id = "task-123"
    mock_send_task.return_value = task_mock

    # Appeler la méthode d'ingestion
    client_id = uuid.uuid4()
    result = await rag_service.ingest_document(
        file=mock_file,
        client_id=client_id,
        title="Test Document",
        document_type=DocumentType.GENERIC,
        chunking_strategy=ChunkingStrategy.HYBRID,
        session=session,
    )

    # Vérifier les résultats
    assert "document_id" in result
    assert result["task_id"] == "task-123"
    assert result["status"] == "pending"

    # Vérifier que les mocks ont été appelés correctement
    mock_storage_service.upload_file.assert_called_once()
    mock_send_task.assert_called_once_with(
        "process_document", args=[result["document_id"]]
    )


@patch("numpy.random.rand")
async def test_get_embedding(mock_rand, rag_service):
    """Test de la génération d'embeddings."""
    # Simuler un vecteur aléatoire pour le test
    mock_rand.return_value = [0.1, 0.2, 0.3]

    # Appeler la méthode
    embedding = await rag_service._get_embedding("test query")

    # Vérifier le résultat
    assert isinstance(embedding, list)
    assert len(embedding) > 0

    # Dans la version réelle, cela appellerait une API d'embedding
    # mais pour le test, on vérifie juste que ça retourne une liste non vide
