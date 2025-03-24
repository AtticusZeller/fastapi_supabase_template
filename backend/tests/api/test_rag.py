import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session, select

from app.models.rag import (
    ChunkingStrategy,
    Document,
    DocumentNode,
    DocumentType,
    NodeType,
)


@pytest.fixture
def mock_storage_service_upload():
    """Mock du service de stockage pour l'upload."""
    with patch("app.services.storage.StorageService.upload_file") as mock:
        # Simuler un résultat d'upload réussi
        mock.return_value = (
            "path/to/file.pdf",
            MagicMock(
                id=uuid.uuid4(),
                bucket_name="rag-documents",
                path="path/to/file.pdf",
                content_type="application/pdf",
            ),
        )
        yield mock


@pytest.fixture
def mock_celery_task():
    """Mock des tâches Celery."""
    with patch("app.tasks.rag.process_document.delay") as mock:
        # Simuler une tâche asynchrone avec un ID
        task_mock = MagicMock()
        task_mock.id = str(uuid.uuid4())
        mock.return_value = task_mock
        yield mock


async def test_ingest_document(
    client: AsyncClient,
    token_headers,
    mock_storage_service_upload,
    mock_celery_task,
    session: Session,
):
    """Test de l'ingestion de document."""
    # Préparation de la requête multipart
    files = {"file": ("test.pdf", b"test content", "application/pdf")}
    data = {
        "title": "Test Document",
        "document_type": DocumentType.GENERIC.value,
        "chunking_strategy": ChunkingStrategy.HYBRID.value,
    }

    # Envoi de la requête
    response = await client.post(
        "/api/v1/rag/ingest", files=files, data=data, headers=token_headers
    )

    # Vérification de la réponse
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "document_id" in response_data
    assert "task_id" in response_data
    assert response_data["status"] == "pending"

    # Vérification en base de données
    document_id = uuid.UUID(response_data["document_id"])
    document = session.exec(select(Document).where(Document.id == document_id)).first()
    assert document is not None
    assert document.title == "Test Document"
    assert document.document_type == DocumentType.GENERIC
    assert document.chunking_strategy == ChunkingStrategy.HYBRID

    # Vérification des appels aux mocks
    mock_storage_service_upload.assert_called_once()
    mock_celery_task.assert_called_once()


async def test_get_document_status(
    client: AsyncClient, token_headers, session: Session
):
    """Test de la récupération du statut d'un document."""
    # Créer un document de test
    document = Document(
        title="Test Document Status",
        source="test.pdf",
        client_id=uuid.UUID(
            "10000000-0000-0000-0000-000000000000"
        ),  # Utilisateur de test
        document_type=DocumentType.GENERIC,
        file_id=uuid.uuid4(),
        status="processing",
        processing_stats={"chunks_created": 5},
        text_length=1000,
    )
    session.add(document)
    session.commit()

    # Créer quelques nodes pour ce document
    for i in range(3):
        node = DocumentNode(
            document_id=document.id,
            node_type=NodeType.CHUNK,
            content=f"Chunk {i + 1}",
            metadata={},
            index=i,
        )
        session.add(node)
    session.commit()

    # Requête pour récupérer le statut avec statistiques
    response = await client.get(
        f"/api/v1/rag/document/{document.id}",
        params={"include_metadata": True, "include_stats": True},
        headers=token_headers,
    )

    # Vérification de la réponse
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Test Document Status"
    assert data["status"] == "processing"
    assert "metadata" in data
    assert "processing_stats" in data
    assert data["processing_stats"]["chunks_created"] == 5
    assert data["text_length"] == 1000
    assert data["chunks_count"] == 3


async def test_list_documents(client: AsyncClient, token_headers, session: Session):
    """Test de la liste des documents."""
    # Créer plusieurs documents de test
    documents = [
        Document(
            title=f"Test Document {i}",
            source=f"test{i}.pdf",
            client_id=uuid.UUID(
                "10000000-0000-0000-0000-000000000000"
            ),  # Utilisateur de test
            document_type=DocumentType.GENERIC if i % 2 == 0 else DocumentType.CONTRACT,
            file_id=uuid.uuid4(),
            status="ready" if i < 3 else "processing",
        )
        for i in range(5)
    ]

    for doc in documents:
        session.add(doc)
    session.commit()

    # Test de la liste sans filtres
    response = await client.get("/api/v1/rag/documents", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "results" in data
    assert data["count"] >= 5  # Au moins nos 5 documents créés

    # Test avec filtre sur le statut
    response = await client.get(
        "/api/v1/rag/documents", params={"status": "ready"}, headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(doc["status"] == "ready" for doc in data["results"])
    assert data["count"] >= 3  # Au moins nos 3 documents "ready"

    # Test avec filtre sur le type de document
    response = await client.get(
        "/api/v1/rag/documents",
        params={"document_type": DocumentType.CONTRACT.value},
        headers=token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(
        doc["document_type"] == DocumentType.CONTRACT.value for doc in data["results"]
    )
    assert data["count"] >= 2  # Au moins nos 2 documents de type CONTRACT


@patch("app.services.rag.RAGService.search")
async def test_search_documents(mock_search, client: AsyncClient, token_headers):
    """Test de la recherche de documents."""
    # Simuler une réponse de recherche
    mock_search.return_value = {
        "query": "test query",
        "total": 2,
        "results": [
            {
                "node_id": str(uuid.uuid4()),
                "document_id": str(uuid.uuid4()),
                "document_title": "Document 1",
                "document_type": DocumentType.GENERIC.value,
                "content": "Contenu du chunk 1",
                "metadata": {},
                "score": 0.95,
            },
            {
                "node_id": str(uuid.uuid4()),
                "document_id": str(uuid.uuid4()),
                "document_title": "Document 2",
                "document_type": DocumentType.CONTRACT.value,
                "content": "Contenu du chunk 2",
                "metadata": {},
                "score": 0.85,
            },
        ],
    }

    # Requête de recherche
    response = await client.post(
        "/api/v1/rag/search",
        json={
            "query": "test query",
            "filters": {"date": "2024-05-19"},
            "document_types": [DocumentType.GENERIC.value, DocumentType.CONTRACT.value],
            "limit": 10,
        },
        headers=token_headers,
    )

    # Vérification de la réponse
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["query"] == "test query"
    assert data["total"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["score"] > data["results"][1]["score"]

    # Vérification de l'appel au mock
    mock_search.assert_called_once()
    call_args = mock_search.call_args[1]
    assert call_args["query"] == "test query"
    assert call_args["filters"] == {"date": "2024-05-19"}
    assert call_args["document_types"] == [
        DocumentType.GENERIC.value,
        DocumentType.CONTRACT.value,
    ]
    assert call_args["limit"] == 10


@patch("app.services.storage.StorageService.delete_file")
async def test_delete_document(
    mock_delete_file, client: AsyncClient, token_headers, session: Session
):
    """Test de la suppression d'un document."""
    # Créer un document de test avec ses nodes
    document = Document(
        title="Document to Delete",
        source="delete_test.pdf",
        client_id=uuid.UUID(
            "10000000-0000-0000-0000-000000000000"
        ),  # Utilisateur de test
        document_type=DocumentType.GENERIC,
        file_id=uuid.uuid4(),
        status="ready",
    )
    session.add(document)
    session.commit()

    # Ajouter des nodes
    for i in range(3):
        node = DocumentNode(
            document_id=document.id,
            node_type=NodeType.CHUNK,
            content=f"Chunk {i + 1}",
            metadata={},
            index=i,
        )
        session.add(node)
    session.commit()

    # Requête de suppression
    response = await client.delete(
        f"/api/v1/rag/document/{document.id}", headers=token_headers
    )

    # Vérification de la réponse
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"

    # Vérifier que le document et ses nodes sont supprimés
    document_check = session.exec(
        select(Document).where(Document.id == document.id)
    ).first()
    assert document_check is None

    nodes_check = session.exec(
        select(DocumentNode).where(DocumentNode.document_id == document.id)
    ).all()
    assert len(nodes_check) == 0

    # Vérification de l'appel au mock
    mock_delete_file.assert_called_once()
