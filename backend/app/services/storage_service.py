from io import BytesIO
from typing import Any

from fastapi import HTTPException, UploadFile

from app.core.auth import get_super_client


class StorageService:
    async def __init__(self):
        self.supabase = await get_super_client()

    async def upload_file(
        self, bucket: str, path: str, file: UploadFile
    ) -> dict[str, Any]:
        """Upload un fichier vers Supabase Storage"""
        try:
            # Lire le contenu du fichier
            file_bytes = await file.read()

            # Récupérer le type MIME depuis les headers
            content_type = file.content_type or "application/octet-stream"

            # Utiliser BytesIO pour créer un object file-like à partir des bytes
            file_obj = BytesIO(file_bytes)

            # Upload avec l'objet file-like qui a une méthode seek()
            response = await self.supabase.storage.from_(bucket).upload(
                path=path,
                file=file_obj,  # Utiliser l'objet file-like
                file_options={"content-type": content_type},
            )

            # Remettre le curseur du fichier au début
            await file.seek(0)

            return {"path": path, "size": len(file_bytes), "mimetype": content_type}
        except Exception as e:
            raise HTTPException(500, f"Error uploading file: {e}")

    async def get_file_url(self, bucket: str, path: str, expires_in: int = 60) -> str:
        """Génère une URL signée pour accéder à un fichier"""
        try:
            result = await self.supabase.storage.from_(bucket).create_signed_url(
                path=path, expires_in=expires_in
            )
            return result["signedUrl"]
        except Exception as e:
            raise HTTPException(500, f"Error generating file URL: {e}")

    async def download_file(self, bucket: str, path: str) -> bytes:
        """Télécharge un fichier depuis Supabase Storage"""
        try:
            result = await self.supabase.storage.from_(bucket).download(path)
            return result
        except Exception as e:
            raise HTTPException(404, f"Error downloading file: {e}")

    async def list_files(
        self, bucket: str, path: str | None = None
    ) -> list[dict[str, Any]]:
        """Liste les fichiers dans un bucket"""
        try:
            result = await self.supabase.storage.from_(bucket).list(path or "")
            return result
        except Exception as e:
            raise HTTPException(500, f"Error listing files: {e}")

    async def delete_file(self, bucket: str, path: str) -> bool:
        """Supprime un fichier de Supabase Storage"""
        try:
            await self.supabase.storage.from_(bucket).remove([path])
            return True
        except Exception as e:
            raise HTTPException(500, f"Error deleting file: {e}")
