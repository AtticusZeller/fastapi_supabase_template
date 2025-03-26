import uuid
from dataclasses import dataclass
from enum import Enum  # Pour lier avec nos modèles
from typing import ClassVar

from sqlmodel import UUID, Field, Relationship, SQLModel, text

from app.models.user import User


@dataclass
class PolicyDefinition:
    using: str | None = None  # Pour filtrer les lignes existantes
    check: str | None = None  # Pour valider les nouvelles valeurs


class RLSModel(SQLModel, table=True):  # type: ignore
    """Classe de base avec politiques RLS par défaut"""

    # Configuration SQLAlchemy via variables de classe
    __table_args__ = {
        "schema": "public",
        "keep_existing": True,
        "arbitrary_types_allowed": True,
    }

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        UUID(as_uuid=True),
        sa_column_kwargs={"server_default": text("auth.uid()")},
        nullable=False,
        foreign_key="auth.users.id",
        ondelete="CASCADE",
    )

    # Modifié : définir la relation comme un attribut supplémentaire (sans annotation de type)
    # L'annotation de type causes le problème quand SQLModel essaie de la mapper
    owner: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "RLSModel.owner_id == User.id",
            "lazy": "joined",
            "uselist": False,
        }
    )

    # Flag pour activer/désactiver RLS
    __rls_enabled__: ClassVar[bool] = True

    @classmethod
    def get_select_policy(cls) -> PolicyDefinition:
        """SELECT - besoin uniquement de USING"""
        return PolicyDefinition(
            using="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """
        )

    @classmethod
    def get_insert_policy(cls) -> PolicyDefinition:
        """INSERT - besoin uniquement de CHECK"""
        return PolicyDefinition(
            check="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """
        )

    @classmethod
    def get_update_policy(cls) -> PolicyDefinition:
        """UPDATE - besoin des deux"""
        return PolicyDefinition(
            using="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """,
            check="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """,
        )

    @classmethod
    def get_delete_policy(cls) -> PolicyDefinition:
        """DELETE - besoin uniquement de USING"""
        return PolicyDefinition(
            using="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """
        )

    @classmethod
    def get_policies(cls) -> dict[str, PolicyDefinition]:
        """Retourne toutes les politiques actives"""
        policies = {}

        if select_policy := cls.get_select_policy():
            policies["select"] = select_policy

        if insert_policy := cls.get_insert_policy():
            policies["insert"] = insert_policy

        if update_policy := cls.get_update_policy():
            policies["update"] = update_policy

        if delete_policy := cls.get_delete_policy():
            policies["delete"] = delete_policy

        return policies


class StorageOperation(str, Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ALL = "ALL"


@dataclass
class BucketPolicy:
    operation: StorageOperation
    using: str | None = None
    check: str | None = None
    name: str | None = None


class StorageBucket:
    name: ClassVar[str]
    public: ClassVar[bool] = False
    allowed_mime_types: ClassVar[list[str]] = ["*/*"]
    max_file_size: ClassVar[int] = 50 * 1024 * 1024
    linked_model: ClassVar[type[RLSModel] | None] = None  # Modèle lié

    @classmethod
    def get_path_pattern(cls) -> str:
        """Pattern de chemin par défaut"""
        if cls.linked_model:
            return f"{cls.linked_model.__tablename__}/{{record_id}}/{{filename}}"
        return "{user_id}/{filename}"

    @classmethod
    def get_policies(cls) -> list[BucketPolicy]:
        """Retourne une politique RLS simple pour le storage"""
        size_check = f"(metadata->>'size')::bigint <= {cls.max_file_size}"
        mime_check = (
            "metadata->>'mimetype' IN ('" + "', '".join(cls.allowed_mime_types) + "')"
        )

        table_prefix = cls.name

        # TODO: Ajouter la vérification du size et du mime_type
        base_policy = """(
            auth.role() = 'authenticated' AND
            (storage.foldername(name))[1] = (select auth.uid()::text)
        )"""

        #  AND
        # starts_with(name, '{table_prefix}/') AND
        # (storage.foldername(name))[1] = (select auth.uid()::text)
        # AND
        #    {size_check} AND
        #    {mime_check}

        return [
            BucketPolicy(
                name=f"Users can manage their own files in {table_prefix}",
                operation=StorageOperation.ALL,
                using=base_policy,
                check=base_policy,
            )
        ]
