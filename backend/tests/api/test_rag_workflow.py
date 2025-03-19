# backend/tests/api/test_rag_workflow.py
import io
import uuid
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.celery import celery_app
from app.models.rag import Document, DocumentNode, NodeType
from app.tasks.rag import process_document


@pytest.fixture
def mock_celery_task():
    """Remplace l'appel Celery par un mock qui capture les arguments."""
    with patch.object(celery_app.tasks["process_document"], "delay") as mock_delay:
        mock_async_result = MagicMock()
        mock_async_result.id = "test-task-id"
        mock_delay.return_value = mock_async_result
        yield mock_delay


@pytest.mark.asyncio
async def test_complete_rag_workflow(
    async_client: AsyncClient, db_session, auth_headers, mock_celery_task
):
    """Test le workflow RAG complet de l'ingestion à la fin du traitement."""
    # 1. Préparer un fichier de test
    test_file = io.BytesIO(b"Test document content")

    # 2. Appeler l'API d'ingestion
    response = await async_client.post(
        "/api/v1/rag/ingest",
        files={"file": ("test.pdf", test_file, "application/pdf")},
        data={"title": "Test Document", "document_type": "generic"},
        headers=auth_headers,
    )

    # 3. Vérifier la réponse initiale
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    document_id = data["document_id"]
    task_id = data["task_id"]

    # 4. Vérifier que Celery a été appelé avec les bons arguments
    mock_celery_task.assert_called_once_with(document_id)

    # 5. Simuler l'exécution de la tâche Celery
    # Récupérer le document depuis la BD
    document = (
        db_session.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
    )
    assert document is not None
    assert document.status == "pending"

    # Simuler l'exécution de la tâche process_document
    with patch("app.tasks.rag.generate_embeddings.delay") as mock_embeddings:
        mock_embeddings.return_value.id = "embeddings-task-id"

        # Exécuter la tâche (pas via Celery, mais directement)
        result = process_document(document_id)

        # Vérifier que la tâche a réussi
        assert result["status"] == "success"

        # Vérifier que l'embedding a été appelé
        mock_embeddings.assert_called_once_with(document_id)

    # 6. Rafraîchir le document depuis la BD
    db_session.refresh(document)
    assert document.status == "indexing"  # Le statut après process_document

    # 7. Vérifier que des noeuds ont été créés
    nodes = (
        db_session.query(DocumentNode)
        .filter(DocumentNode.document_id == uuid.UUID(document_id))
        .all()
    )
    assert len(nodes) > 0

    # 8. Vérifier l'état via l'API
    response = await async_client.get(
        f"/api/v1/rag/document/{document_id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexing"

    # 9. Simuler la fin du processus - mettre le document à ready
    document.status = "ready"
    db_session.commit()

    # 10. Vérifier l'état final
    response = await async_client.get(
        f"/api/v1/rag/document/{document_id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_search_workflow(async_client: AsyncClient, db_session, auth_headers):
    """Test le workflow de recherche RAG."""
    # 1. Créer un document de test avec des nodes
    test_doc = Document(
        title="Test Search Document",
        source="test",
        client_id=uuid.UUID(
            "00000000-0000-0000-0000-000000000001"
        ),  # Utilisateur de test
        document_type="generic",
        file_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),  # Fichier fictif
        status="ready",
    )
    db_session.add(test_doc)
    db_session.flush()

    # 2. Ajouter des nodes de test
    for i in range(3):
        node = DocumentNode(
            document_id=test_doc.id,
            node_type=NodeType.CHUNK,
            content=f"Test content chunk {i}",
            owner_id=uuid.UUID(
                "00000000-0000-0000-0000-000000000001"
            ),  # Utilisateur de test
            metadata={"chunk_index": i},
            index=i,
        )
        db_session.add(node)

    db_session.commit()

    # 3. Effectuer une recherche
    response = await async_client.post(
        "/api/v1/rag/search", json={"query": "test query"}, headers=auth_headers
    )

    # 4. Vérifier les résultats
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
