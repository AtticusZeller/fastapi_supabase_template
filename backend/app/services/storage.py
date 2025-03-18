import logging
import os
import uuid
from io import BytesIO
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlmodel import Session
from supabase._async.client import AsyncClient

from app.crud.file import file_metadata
from app.models.base import StorageBucket
from app.models.file import FileMetadata, FileMetadataCreate

logger = logging.getLogger(__name__)


class StorageService:
    """Service pour gérer le stockage de fichiers dans Supabase"""

    def __init__(self, supabase_client: AsyncClient):
        self.client = supabase_client

    async def initialize_buckets(self, buckets: list[type[StorageBucket]]):
        """Initialise les buckets de stockage définis dans l'application"""
        try:
            # Récupérer la liste des buckets existants
            existing_buckets_response = await self.client.storage.list_buckets()
            existing_buckets = [bucket["name"] for bucket in existing_buckets_response]

            for bucket_class in buckets:
                bucket_name = bucket_class.name
                if bucket_name not in existing_buckets:
                    logger.info(f"Creating bucket: {bucket_name}")
                    await self.client.storage.create_bucket(
                        bucket_name, public=bucket_class.public
                    )
                    # Ici, on pourrait aussi configurer les politiques RLS spécifiques au bucket
                else:
                    logger.info(f"Bucket already exists: {bucket_name}")

        except Exception as e:
            logger.error(f"Error initializing buckets: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error initializing storage buckets: {str(e)}"
            )

    async def upload_file(
        self,
        bucket_class: type[StorageBucket],
        file: UploadFile,
        user_id: uuid.UUID,
        record_id: uuid.UUID | None = None,
        description: str | None = None,
        session: Session | None = None,
        custom_path: str | None = None,
    ) -> tuple[str, FileMetadata | None]:
        """Upload un fichier vers Supabase Storage et enregistre ses métadonnées"""
        try:
            # Valider le type MIME
            if (
                bucket_class.allowed_mime_types != ["*/*"]
                and file.content_type not in bucket_class.allowed_mime_types
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed types: {', '.join(bucket_class.allowed_mime_types)}",
                )

            # Lire le contenu du fichier
            file_content = await file.read()

            # Vérifier la taille du fichier
            if len(file_content) > bucket_class.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {bucket_class.max_file_size / 1024 / 1024}MB",
                )

            # Générer le chemin du fichier
            if custom_path:
                file_path = custom_path
            else:
                pattern = bucket_class.get_path_pattern()

                # Remplacer les placeholders dans le pattern
                filename = file.filename or f"upload_{uuid.uuid4()}"
                file_path = pattern.format(
                    user_id=str(user_id),
                    record_id=str(record_id) if record_id else "unknown",
                    filename=filename,
                )

            # Upload le fichier
            file_io = BytesIO(file_content)
            response = await self.client.storage.from_(bucket_class.name).upload(
                path=file_path,
                file=file_io,
                file_options={"content-type": file.content_type},
            )

            # Enregistrer les métadonnées si session est fournie
            file_meta = None
            if session:
                file_meta_data = FileMetadataCreate(
                    filename=file.filename or os.path.basename(file_path),
                    content_type=file.content_type or "application/octet-stream",
                    size=len(file_content),
                    bucket_name=bucket_class.name,
                    path=file_path,
                    description=description,
                    item_id=record_id,
                )
                file_meta = file_metadata.create(
                    session, owner_id=user_id, obj_in=file_meta_data
                )

            return file_path, file_meta

        except HTTPException:
            # Renvoyer l'exception HTTP déjà levée
            raise
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error uploading file: {str(e)}"
            )
        finally:
            # S'assurer que le fichier est remis à zéro pour une utilisation ultérieure
            await file.seek(0)

    async def get_file_url(
        self, bucket_name: str, file_path: str, expiration: int = 60
    ) -> str:
        """Génère une URL signée pour accéder au fichier"""
        try:
            signed_url = await self.client.storage.from_(bucket_name).create_signed_url(
                path=file_path, expires_in=expiration
            )
            return signed_url
        except Exception as e:
            logger.error(f"Error generating signed URL: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error generating file URL: {str(e)}"
            )

    async def download_file(self, bucket_name: str, file_path: str) -> BytesIO:
        """Télécharge un fichier depuis Supabase Storage"""
        try:
            response = await self.client.storage.from_(bucket_name).download(file_path)
            return BytesIO(response)
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise HTTPException(
                status_code=404, detail=f"Error downloading file: {str(e)}"
            )

    async def delete_file(
        self,
        bucket_name: str,
        file_path: str,
        session: Session | None = None,
        metadata_id: uuid.UUID | None = None,
    ) -> bool:
        """Supprime un fichier de Supabase Storage et ses métadonnées si présentes"""
        try:
            # Supprimer le fichier du stockage
            await self.client.storage.from_(bucket_name).remove(file_path)

            # Supprimer les métadonnées si nécessaire
            if session and metadata_id:
                file_metadata.remove(session, id=metadata_id)

            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error deleting file: {str(e)}"
            )

    async def list_files(
        self, bucket_name: str, path: str = ""
    ) -> list[dict[str, Any]]:
        """Liste les fichiers dans un bucket de stockage"""
        try:
            response = await self.client.storage.from_(bucket_name).list(path)
            return response
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error listing files: {str(e)}"
            )
