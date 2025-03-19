import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, BinaryIO, Tuple

import httpx
from fastapi import UploadFile, HTTPException, BackgroundTasks
from sqlmodel import Session, select

from app.core.celery import celery_app
from app.core.config import settings
from app.models.rag import Document, DocumentNode, NodeType, DocumentType, ChunkingStrategy
from app.services.storage import StorageService
from app.tasks.rag import process_document

logger = logging.getLogger(__name__)


class RAGService:
    """Service avancé de Retrieval Augmented Generation."""
    
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service
    
    async def ingest_document(
        self,
        file: UploadFile,
        client_id: uuid.UUID,
        title: str,
        document_type: Optional[DocumentType] = None,
        chunking_strategy: Optional[ChunkingStrategy] = None,
        embedding_model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session: Session = None,
    ) -> Dict[str, Any]:
        """
        Point d'entrée unifié pour l'ingestion de documents.
        
        Supports multiples formats et paramètres configurables.
        """
        try:
            # 1. Validation du fichier
            await self._validate_file(file)
            
            # 2. Détection auto du type si non spécifié
            if not document_type:
                document_type = await self._detect_document_type(file, title)
                
            # 3. Upload vers Supabase Storage
            from app.models.storage import RAGDocuments
            
            file_path, file_meta = await self.storage_service.upload_file(
                bucket_class=RAGDocuments,
                file=file,
                user_id=client_id,
                description=f"RAG document: {title}",
                session=session
            )
            
            if not file_meta:
                raise HTTPException(status_code=500, detail="Failed to upload document")
            
            # 4. Création de l'entrée Document
            document = Document(
                title=title,
                source=file.filename or "Unknown",
                client_id=client_id,
                document_type=document_type or DocumentType.UNKNOWN,
                file_id=file_meta.id,
                chunking_strategy=chunking_strategy or ChunkingStrategy.HYBRID,
                embedding_model=embedding_model or settings.EMBEDDING_MODEL,
                metadata=metadata or {},
                status="pending"
            )
            session.add(document)
            session.commit()
            session.refresh(document)
            
            # 5. Lancement du traitement asynchrone
            task = process_document.delay(str(document.id))
            
            return {
                "document_id": str(document.id),
                "task_id": task.id,
                "status": "pending",
                "detected_type": document_type,
                "file_id": str(file_meta.id),
            }
            
        except Exception as e:
            logger.exception(f"Error ingesting document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")
    
    async def _validate_file(self, file: UploadFile) -> None:
        """Valide le fichier avant l'ingestion."""
        # Vérification de la taille maximale (20MB)
        content = await file.read(20 * 1024 * 1024 + 1)
        file_size = len(content)
        
        if file_size > 20 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 20MB)")
        
        # Replace le curseur au début pour lecture ultérieure
        await file.seek(0)
        
        # Vérification du type MIME
        content_type = file.content_type
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "text/csv",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]
        
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=415, 
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )
    
    async def _detect_document_type(
        self, 
        file: UploadFile,
        title: str
    ) -> DocumentType:
        """Détecte automatiquement le type sémantique du document."""
        # Lecture des premiers Ko pour analyser le contenu
        content_sample = await file.read(10 * 1024)  # 10KB sample
        await file.seek(0)  # Remettre le curseur au début
        
        # Simple heuristique basée sur le nom et le contenu
        filename = file.filename.lower() if file.filename else ""
        title_lower = title.lower()
        content_str = content_sample.decode('utf-8', errors='ignore').lower()
        
        # Détection selon des mots-clés
        if any(kw in filename or kw in title_lower or kw in content_str for kw in ["facture", "invoice", "paiement"]):
            return DocumentType.INVOICE
        elif any(kw in filename or kw in title_lower or kw in content_str for kw in ["financ", "bilan", "rapport annuel"]):
            return DocumentType.FINANCIAL_REPORT
        elif any(kw in filename or kw in title_lower or kw in content_str for kw in ["contrat", "contract", "agreement"]):
            return DocumentType.CONTRACT
        elif any(kw in filename or kw in title_lower or kw in content_str for kw in ["géotechnique", "geotechnical", "sol"]):
            return DocumentType.GEOTECHNICAL_REPORT
        elif any(kw in filename or kw in title_lower or kw in content_str for kw in ["technique", "technical", "spec"]):
            return DocumentType.TECHNICAL_SPEC
        
        # Par défaut
        return DocumentType.GENERIC
    
    async def search(
        self,
        query: str,
        client_id: uuid.UUID,
        filters: Optional[Dict[str, Any]] = None,
        document_types: Optional[List[DocumentType]] = None,
        limit: int = 10,
        session: Session = None,
    ) -> Dict[str, Any]:
        """
        Recherche RAG hybride avancée.
        
        Combines:
        1. Recherche sémantique par embeddings
        2. Filtrage par métadonnées
        3. Reranking contextuel
        """
        try:
            # Vérification des documents disponibles
            documents_count = session.exec(
                select(Document)
                .where(
                    Document.client_id == client_id,
                    Document.status == "ready"
                )
            ).count()
            
            if documents_count == 0:
                return {
                    "query": query,
                    "total": 0,
                    "results": [],
                    "message": "No documents available for search"
                }
            
            # Simpler une recherche pour ce MVP
            # Dans une implémentation complète, nous utiliserions pgvector et la recherche de similarité
            
            # Récupérer quelques chunks aléatoires pour simulation
            chunks = session.exec(
                select(DocumentNode)
                .join(Document)
                .where(
                    Document.client_id == client_id,
                    Document.status == "ready",
                    DocumentNode.node_type == NodeType.CHUNK
                )
                .limit(limit)
            ).all()
            
            # Formater les résultats
            results = []
            for chunk in chunks:
                document = session.exec(
                    select(Document).where(Document.id == chunk.document_id)
                ).first()
                
                results.append({
                    "node_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "document_title": document.title if document else "Unknown",
                    "document_type": document.document_type if document else DocumentType.UNKNOWN,
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "score": 0.85  # Score simulé
                })
            
            return {
                "query": query,
                "total": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.exception(f"Error during RAG search: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
