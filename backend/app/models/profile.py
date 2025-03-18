import os

from fastapi import UploadFile
from sqlmodel import Field
from supabase import Client, create_client

from .base import RLSModel, StorageBucket

supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", "")
)


class Profile(RLSModel):
    class Config:
        table = True
        table_name = "profiles"
        schema = "public"

    __rls_enabled__ = True
    email: str = Field(max_length=255)
    name: str | None = Field(default=None)
    picture_path: str | None = None  # Chemin dans le bucket

    @property
    def picture_url(self) -> str | None:
        """Génère l'URL de l'image de profil"""
        if self.picture_path:
            return f"/storage/v1/object/public/{ProfilePicturesBucket.name}/{self.picture_path}"
        return None

    async def upload_picture(self, file: UploadFile):
        """Upload une nouvelle image de profil"""
        path = ProfilePicturesBucket.get_path_pattern().format(
            record_id=self.id, filename=file.filename
        )

        # Upload via Supabase Storage
        await supabase.storage.from_(ProfilePicturesBucket.name).upload(
            path, file.file.read(), {"content-type": file.content_type}
        )

        # Mettre à jour le chemin
        self.picture_path = path
        return path


# Example avec un bucket lié à un modèle Profile
class ProfilePicturesBucket(StorageBucket):
    name = "profile-pictures"
    public = True
    allowed_mime_types = ["image/jpeg", "image/png", "image/webp"]
    max_file_size = 5 * 1024 * 1024  # 5MB
    linked_model = Profile  # Line
