import uuid
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlmodel import desc, func, select

from app.api.deps import CurrentUser, SessionDep, StorageServiceDep
from app.crud.file import file_metadata
from app.models.rag import (
    ChunkingStrategy,
    Document,
    DocumentNode,
    DocumentType,
    NodeType,
)
from app.services.rag import RAGService

router = APIRouter(prefix="/rag", tags=["rag"])


# Dépendance pour le RAGService
def get_rag_service(storage_service: StorageServiceDep = Depends()) -> RAGService:
    return RAGService(storage_service=storage_service)


@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: DocumentType | None = Form(None),
    chunking_strategy: ChunkingStrategy | None = Form(None),
    embedding_model: str | None = Form(None),
    metadata: dict[str, Any] | None = Form(None),
    user: CurrentUser = Depends(),
    session: SessionDep = Depends(),
    rag_service: RAGService = Depends(get_rag_service),
) -> dict[str, Any]:
    """
    Endpoint d'ingestion unifié pour tous types de documents.

    - Supporte multiples formats (PDF, DOCX, XLSX, TXT...)
    - Auto-détection du type sémantique
    - Configuration du chunking et de l'embedding
    - Traitement asynchrone
    """
    return await rag_service.ingest_document(
        file=file,
        client_id=uuid.UUID(user.id),
        title=title,
        document_type=document_type,
        chunking_strategy=chunking_strategy,
        embedding_model=embedding_model,
        metadata=metadata,
        session=session,
    )


@router.get("/document/{document_id}")
async def get_document_status(
    document_id: uuid.UUID,
    include_metadata: bool = Query(False),
    include_stats: bool = Query(False),
    session: SessionDep = Depends(),
    user: CurrentUser = Depends(),
) -> dict[str, Any]:
    """Récupère le statut et les métadonnées d'un document."""

    document = session.exec(
        select(Document).where(
            Document.id == document_id, Document.client_id == uuid.UUID(user.id)
        )
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )

    result = {
        "document_id": str(document_id),
        "title": document.title,
        "status": document.status,
        "document_type": document.document_type,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
    }

    if include_metadata:
        result["metadata"] = document.metadata

    if include_stats:
        result["processing_stats"] = document.processing_stats
        result["text_length"] = document.text_length

        # Ajouter les stats de chunks
        chunks_count = session.exec(
            select(func.count()).where(
                DocumentNode.document_id == document_id,
                DocumentNode.node_type == NodeType.CHUNK,
            )
        ).first()

        result["chunks_count"] = chunks_count or 0

    return result


@router.get("/documents")
async def list_documents(
    status: str | None = Query(None),
    document_type: DocumentType | None = Query(None),
    skip: int = Query(0),
    limit: int = Query(20, le=100),
    session: SessionDep = Depends(),
    user: CurrentUser = Depends(),
) -> dict[str, Any]:
    """Liste les documents de l'utilisateur avec filtrage."""

    # Construire la requête de base
    query = select(Document).where(Document.client_id == uuid.UUID(user.id))

    # Ajouter les filtres optionnels
    if status:
        query = query.where(Document.status == status)

    if document_type:
        query = query.where(Document.document_type == document_type)

    # Compter le total avant pagination
    count_query = select(func.count()).select_from(query.alias())
    total_count = session.exec(count_query).first()

    # Ajouter la pagination
    query = query.offset(skip).limit(limit).order_by(desc(Document.created_at))

    # Exécuter la requête
    documents = session.exec(query).all()

    # Formater les résultats
    results = []
    for doc in documents:
        results.append(
            {
                "document_id": str(doc.id),
                "title": doc.title,
                "document_type": doc.document_type,
                "status": doc.status,
                "created_at": doc.created_at.isoformat(),
            }
        )

    return {
        "count": len(results),
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "results": results,
    }


@router.post("/search")
async def search_documents(
    query: str,
    filters: dict[str, Any] | None = None,
    document_types: list[DocumentType] | None = None,
    limit: int = Query(10, le=50),
    session: SessionDep = Depends(),
    user: CurrentUser = Depends(),
    rag_service: RAGService = Depends(get_rag_service),
) -> dict[str, Any]:
    """
    Recherche hybride avancée dans les documents.

    - Recherche sémantique par similarité vectorielle
    - Filtrage par métadonnées spécifiques au type
    - Reranking contextuel
    """
    return await rag_service.search(
        query=query,
        client_id=uuid.UUID(user.id),
        filters=filters,
        document_types=document_types,
        limit=limit,
        session=session,
    )


@router.delete("/document/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    session: SessionDep = Depends(),
    user: CurrentUser = Depends(),
    storage_service: StorageServiceDep = Depends(),
) -> dict[str, Any]:
    """Supprime un document et toutes ses données associées."""

    # Vérifier que le document existe et appartient à l'utilisateur
    document = session.exec(
        select(Document).where(
            Document.id == document_id, Document.client_id == uuid.UUID(user.id)
        )
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )

    # Supprimer le fichier du stockage
    file_meta = file_metadata.get(session, id=document.file_id)

    if file_meta:
        await storage_service.delete_file(
            bucket_name=file_meta.bucket_name,
            file_path=file_meta.path,
            session=session,
            metadata_id=file_meta.id,
        )

    # Supprimer les noeuds du document
    nodes = session.exec(
        select(DocumentNode).where(DocumentNode.document_id == document_id)
    ).all()

    for node in nodes:
        session.delete(node)

    # Supprimer le document
    session.delete(document)
    session.commit()

    return {
        "status": "success",
        "message": f"Document {document_id} and all associated data deleted",
    }
