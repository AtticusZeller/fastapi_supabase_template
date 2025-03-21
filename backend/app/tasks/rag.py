import logging
import time
import uuid
from typing import Any

import numpy as np
from sqlmodel import select

from app.core.auth import get_super_client
from app.core.celery import celery_app
from app.core.config import settings
from app.core.db import get_db
from app.models.rag import Document, DocumentNode, DocumentType, NodeType

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="process_document")
async def process_document(self, document_id: str) -> dict[str, Any]:
    """
    Pipeline de traitement complet pour un document RAG.

    Étapes:
    1. Extraction du texte selon le format
    2. Classification sémantique avancée
    3. Extraction hiérarchique de la structure
    4. Chunking intelligent adapté au contenu
    5. Génération d'embeddings
    6. Extraction de métadonnées spécifiques au type
    """
    logger.info(f"Starting document processing: {document_id}")
    task_id = self.request.id
    start_time = time.time()

    # Initialiser les stats de traitement
    processing_stats: dict[str, Any] = {
        "extraction_time": 0,
        "chunking_time": 0,
        "embedding_time": 0,
        "metadata_time": 0,
        "total_time": 0,
        "chunks_created": 0,
    }

    session = next(get_db())

    try:
        # 1. Récupérer le document et le fichier
        document = session.exec(
            select(Document).where(Document.id == uuid.UUID(document_id))
        ).first()

        if not document:
            logger.error(f"Document not found: {document_id}")
            return {"status": "error", "message": "Document not found"}

        # 2. Mettre à jour le statut
        document.status = "processing"
        session.commit()

        # 3. Récupérer le fichier depuis Supabase
        from app.services.storage import StorageService

        supabase_client = await get_super_client()
        storage_service = StorageService(supabase_client=supabase_client)

        # Récupérer les métadonnées du fichier
        from app.crud.file import file_metadata

        file_meta = file_metadata.get(session, id=document.file_id)

        if not file_meta:
            raise Exception(f"File metadata not found for document {document_id}")

        # Télécharger le fichier - simulation pour MVP
        # file_content = await storage_service.download_file(
        #     bucket_name=file_meta.bucket_name,
        #     file_path=file_meta.path
        # )

        # 4. Extraire le texte selon le format - simulation pour MVP
        extraction_start = time.time()
        extracted_text = f"Contenu du document {document.title} - Simulation pour MVP"
        document_structure = {"sections": [{"title": "Introduction", "level": 1}]}
        processing_stats["extraction_time"] = int(time.time() - extraction_start)

        # Mise à jour de la taille du texte
        document.text_length = len(extracted_text)

        # 5. Analyser et classifier le document (si type générique)
        if (
            document.document_type == DocumentType.UNKNOWN
            or document.document_type == DocumentType.GENERIC
        ):
            document.document_type = DocumentType.GENERIC  # Simulation pour MVP

        # 6. Extraction de structure hiérarchique
        document_node = DocumentNode(
            document_id=document.id,
            node_type=NodeType.DOCUMENT,
            content=extracted_text[:1000],  # Juste un aperçu
            metadata={
                "title": document.title,
                "source": document.source,
                "content_type": file_meta.content_type,
                "length": len(extracted_text),
            },
            level=0,
            index=0,
        )
        session.add(document_node)
        session.commit()

        # 7. Chunking intelligent selon la stratégie - simulation pour MVP
        chunking_start = time.time()
        chunks = []
        for i in range(5):  # Simulation de 5 chunks
            chunks.append(
                {
                    "text": f"Chunk {i + 1} du document {document.title} - Simulation pour MVP",
                    "metadata": {"start": i * 500, "end": (i + 1) * 500},
                }
            )
        processing_stats["chunking_time"] = int(time.time() - chunking_start)

        # 8. Stockage des chunks avec métadonnées de position
        for i, chunk in enumerate(chunks):
            chunk_node = DocumentNode(
                document_id=document.id,
                node_type=NodeType.CHUNK,
                parent_id=document_node.id,
                content=chunk["text"],
                metadata=chunk["metadata"],
                level=1,
                index=i,
            )
            session.add(chunk_node)

        session.commit()
        processing_stats["chunks_created"] = len(chunks)

        # 9. Mise à jour du statut
        document.status = "indexing"
        document.processing_stats = processing_stats
        session.commit()

        # 10. Lancer la tâche d'embedding (séparément pour permettre la parallélisation)
        generate_embeddings.delay(str(document.id))

        # 11. Extraire les métadonnées spécifiques au type - simulation pour MVP
        metadata_start = time.time()
        extracted_metadata = {
            "document_type": document.document_type,
            "processing_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        processing_stats["metadata_time"] = int(time.time() - metadata_start)

        # 12. Mise à jour des métadonnées
        if document.metadata is None:
            processing_stats["metadata"] = {}
        else:
            # Convertir les métadonnées SQLAlchemy en dict de manière sûre
            metadata_dict = (
                document.doc_metadata.copy() if document.doc_metadata else {}
            )
            processing_stats["metadata"] = {**metadata_dict, **extracted_metadata}

        processing_stats["total_time"] = int(time.time() - start_time)
        document.processing_stats = processing_stats
        session.commit()

        return {
            "status": "success",
            "document_id": document_id,
            "task_id": task_id,
            "document_type": document.document_type,
            "chunks_created": len(chunks),
            "processing_time": processing_stats["total_time"],
        }

    except Exception as e:
        logger.exception(f"Error processing document {document_id}: {str(e)}")

        # Mettre à jour le statut en cas d'erreur
        if document:
            document.status = "error"
            document.error_message = str(e)
            session.commit()

        return {"status": "error", "document_id": document_id, "message": str(e)}


@celery_app.task(bind=True, name="generate_embeddings")
def generate_embeddings(self, document_id: str) -> dict[str, Any]:
    """Génère les embeddings pour tous les chunks d'un document."""
    logger.info(f"Generating embeddings for document: {document_id}")

    session = next(get_db())

    try:
        # 1. Récupérer les chunks sans embeddings
        document = session.exec(
            select(Document).where(Document.id == uuid.UUID(document_id))
        ).first()

        if not document:
            raise Exception(f"Document not found: {document_id}")

        chunks = session.exec(
            select(DocumentNode).where(
                DocumentNode.document_id == uuid.UUID(document_id),
                DocumentNode.node_type == NodeType.CHUNK,
            )
        ).all()

        if not chunks:
            logger.info(f"No chunks found for document {document_id}")
            document.status = "ready"
            session.commit()
            return {"status": "success", "message": "No chunks to embed"}

        # 2. Générer les embeddings - simulation pour MVP
        for chunk in chunks:
            # Générer un embedding aléatoire pour simulation
            random_embedding = list(
                np.random.randn(settings.EMBEDDING_DIMENSION).astype(float)
            )
            chunk.embedding = random_embedding

        session.commit()

        # 3. Mettre à jour le statut du document
        document.status = "ready"
        session.commit()

        return {
            "status": "success",
            "document_id": document_id,
            "chunks_embedded": len(chunks),
        }

    except Exception as e:
        logger.exception(
            f"Error generating embeddings for document {document_id}: {str(e)}"
        )

        # Mettre à jour le statut en cas d'erreur
        document = session.exec(
            select(Document).where(Document.id == uuid.UUID(document_id))
        ).first()

        if document:
            document.status = "error"
            document.error_message = f"Embedding error: {str(e)}"
            session.commit()

        return {"status": "error", "document_id": document_id, "message": str(e)}
