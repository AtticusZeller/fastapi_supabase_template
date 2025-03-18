import uuid

from fastapi import APIRouter, HTTPException, UploadFile, status
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep, StorageServiceDep
from app.crud import file_metadata
from app.models.file import FileMetadata, FileMetadataPublic, FileMetadataUpdate
from app.models.storage import ItemDocuments, ProfilePictures

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload/profile-picture", response_model=FileMetadataPublic)
async def upload_profile_picture(
    file: UploadFile,
    description: str,
    user: CurrentUser,
    session: SessionDep,
    storage_service: StorageServiceDep,
) -> FileMetadata:
    """Upload une image de profil

    Args:
        file: Le fichier à uploader
        description: Description optionnelle du fichier
        user: L'utilisateur connecté
        session: La session de base de données
        storage_service: Le service de stockage

    Returns:
        Les métadonnées du fichier uploadé
    """
    # Vérifier que c'est une image
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être une image",
        )

    # Upload du fichier
    _, file_meta = await storage_service.upload_file(
        bucket_class=ProfilePictures,
        file=file,
        user_id=uuid.UUID(user.id),
        description=description,
        session=session,
    )

    if not file_meta:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'enregistrement des métadonnées du fichier",
        )

    return file_meta


@router.post("/upload/document/{item_id}", response_model=FileMetadataPublic)
async def upload_item_document(
    item_id: uuid.UUID,
    file: UploadFile,
    description: str,
    user: CurrentUser,
    session: SessionDep,
    storage_service: StorageServiceDep,
) -> FileMetadata:
    """Upload un document lié à un item

    Args:
        item_id: L'ID de l'item auquel associer le document
        file: Le fichier à uploader
        description: Description optionnelle du fichier
        user: L'utilisateur connecté
        session: La session de base de données
        storage_service: Le service de stockage

    Returns:
        Les métadonnées du fichier uploadé
    """
    # Vérifier si l'item existe et appartient à l'utilisateur
    from app.models.item import Item

    statement = select(Item).where(
        Item.id == item_id, Item.owner_id == uuid.UUID(user.id)
    )
    result = session.exec(statement)
    item = result.first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item avec l'id {item_id} non trouvé ou n'appartient pas à l'utilisateur",
        )

    # Upload du fichier
    _, file_meta = await storage_service.upload_file(
        bucket_class=ItemDocuments,
        file=file,
        user_id=uuid.UUID(user.id),
        record_id=item_id,
        description=description,
        session=session,
    )

    if not file_meta:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'enregistrement des métadonnées du fichier",
        )

    return file_meta


@router.get("/files", response_model=list[FileMetadataPublic])
async def list_user_files(
    bucket_name: str,
    item_id: uuid.UUID,
    skip: int,
    limit: int,
    user: CurrentUser,
    session: SessionDep,
) -> list[FileMetadata]:
    """Liste les fichiers de l'utilisateur

    Args:
        bucket_name: Filtre par nom de bucket (optionnel)
        item_id: Filtre par item_id (optionnel)
        skip: Nombre d'items à sauter (pagination)
        limit: Nombre maximum d'items à retourner
        user: L'utilisateur connecté
        session: La session de base de données

    Returns:
        Liste des métadonnées des fichiers
    """
    user_id = uuid.UUID(user.id)

    # Filtrage selon les paramètres
    if item_id:
        return file_metadata.get_by_item_id(
            session, item_id=item_id, skip=skip, limit=limit
        )
    elif bucket_name:
        files = file_metadata.get_by_bucket(
            session, bucket_name=bucket_name, skip=skip, limit=limit
        )
        # Filtrer par propriétaire (sécurité supplémentaire)
        return [f for f in files if f.owner_id == user_id]
    else:
        # Par défaut, retourner tous les fichiers de l'utilisateur
        return file_metadata.get_by_user_id(
            session, user_id=user_id, skip=skip, limit=limit
        )


@router.get("/file/{file_id}", response_model=FileMetadataPublic)
async def get_file_metadata(
    file_id: uuid.UUID, user: CurrentUser, session: SessionDep
) -> FileMetadata:
    """Récupère les métadonnées d'un fichier

    Args:
        file_id: L'ID du fichier
        user: L'utilisateur connecté
        session: La session de base de données

    Returns:
        Les métadonnées du fichier
    """
    file_meta = file_metadata.get(session, id=file_id)

    if not file_meta or file_meta.owner_id != uuid.UUID(user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fichier avec l'id {file_id} non trouvé ou n'appartient pas à l'utilisateur",
        )

    return file_meta


@router.get("/file/{file_id}/url")
async def get_file_download_url(
    file_id: uuid.UUID,
    expiration: int,
    user: CurrentUser,
    session: SessionDep,
    storage_service: StorageServiceDep,
) -> dict:
    """Génère une URL signée pour télécharger un fichier

    Args:
        file_id: L'ID du fichier
        expiration: Durée de validité de l'URL en secondes
        user: L'utilisateur connecté
        session: La session de base de données
        storage_service: Le service de stockage

    Returns:
        Un dictionnaire contenant l'URL signée
    """
    file_meta = file_metadata.get(session, id=file_id)

    if not file_meta or file_meta.owner_id != uuid.UUID(user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fichier avec l'id {file_id} non trouvé ou n'appartient pas à l'utilisateur",
        )

    # Générer l'URL signée
    signed_url = await storage_service.get_file_url(
        bucket_name=file_meta.bucket_name,
        file_path=file_meta.path,
        expiration=expiration,
    )

    return {"url": signed_url, "expires_in": expiration}


@router.put("/file/{file_id}", response_model=FileMetadataPublic)
async def update_file_metadata(
    file_id: uuid.UUID,
    update_data: FileMetadataUpdate,
    user: CurrentUser,
    session: SessionDep,
) -> FileMetadata:
    """Mise à jour des métadonnées d'un fichier

    Args:
        file_id: L'ID du fichier
        update_data: Les données à mettre à jour
        user: L'utilisateur connecté
        session: La session de base de données

    Returns:
        Les métadonnées mises à jour
    """
    # Vérifier que le fichier existe et appartient à l'utilisateur
    file_meta = file_metadata.get(session, id=file_id)

    if not file_meta or file_meta.owner_id != uuid.UUID(user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fichier avec l'id {file_id} non trouvé ou n'appartient pas à l'utilisateur",
        )

    # Mise à jour des métadonnées
    updated_meta = file_metadata.update(session, id=file_id, obj_in=update_data)

    if not updated_meta:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour des métadonnées",
        )

    return updated_meta


@router.delete("/file/{file_id}")
async def delete_file(
    file_id: uuid.UUID,
    user: CurrentUser,
    session: SessionDep,
    storage_service: StorageServiceDep,
) -> dict:
    """Supprime un fichier

    Args:
        file_id: L'ID du fichier
        user: L'utilisateur connecté
        session: La session de base de données
        storage_service: Le service de stockage

    Returns:
        Un message de confirmation
    """
    # Vérifier que le fichier existe et appartient à l'utilisateur
    file_meta = file_metadata.get(session, id=file_id)

    if not file_meta or file_meta.owner_id != uuid.UUID(user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fichier avec l'id {file_id} non trouvé ou n'appartient pas à l'utilisateur",
        )

    # Supprimer le fichier et ses métadonnées
    await storage_service.delete_file(
        bucket_name=file_meta.bucket_name,
        file_path=file_meta.path,
        session=session,
        metadata_id=file_id,
    )

    return {"status": "success", "message": "Fichier supprimé avec succès"}
