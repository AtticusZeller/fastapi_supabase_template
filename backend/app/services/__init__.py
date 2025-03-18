from supabase._async.client import AsyncClient

from app.models import STORAGE_BUCKETS
from app.services.storage import StorageService

# Singleton pour le service de stockage
_storage_service: StorageService | None = None


async def get_storage_service(supabase_client: AsyncClient) -> StorageService:
    """Retourne le service de stockage, l'initialise si nécessaire"""
    global _storage_service

    if _storage_service is None:
        _storage_service = StorageService(supabase_client)
        # Initialiser les buckets
        await _storage_service.initialize_buckets(STORAGE_BUCKETS)

    return _storage_service
