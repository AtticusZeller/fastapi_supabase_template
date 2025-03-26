import logging
import os
from logging.config import fileConfig

from alembic import context
from alembic.operations import ops
# Import models and buckets
from app.models import (STORAGE_BUCKETS, Base, Item, Profile,
                        ProfilePicturesBucket)
from app.models.base import RLSModel
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool, text
from sqlmodel import SQLModel

logger = logging.getLogger("alembic")

from app.core.config import settings

# Charger les variables d'environnement
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support


target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Retourne l'URL de connection pour le session pooler Supabase"""
    project_id = os.getenv("SUPABASE_PROJECT_ID")
    password = os.getenv("POSTGRES_PASSWORD")
    server = os.getenv("POSTGRES_SERVER", "aws-0-eu-west-3.pooler.supabase.com")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "postgres")
    user = os.getenv("POSTGRES_USER", "postgres")

    # Construction du username spécial pour le pooler
    pooler_user = f"{user}.{project_id}" if project_id else user

    return f"postgresql://{pooler_user}:{password}@{server}:{port}/{db}"


def include_object(object, name, type_, reflected, compare_to):
    """Ne pas générer de migrations pour les tables du schéma auth"""
    if type_ == "table" and object.schema == "auth":
        return False
    return True


def process_revision_directives(context, revision, directives):
    """Ajoute les directives RLS directement dans les opérations"""
    logger.debug("Processing revision directives...")

    if not directives or not directives[0].upgrade_ops:
        logger.debug("No upgrade ops found!")
        return

    script = directives[0]

    if not script.upgrade_ops:
        script.upgrade_ops = ops.UpgradeOps([])
    if not script.downgrade_ops:
        script.downgrade_ops = ops.DowngradeOps([])

    # 1. Traitement des tables à créer
    created_tables = []
    for op in script.upgrade_ops.ops:
        if hasattr(op, 'table_name'):
            table_name = op.table_name
            if table_name != 'alembic_version':
                created_tables.append(table_name)
                logger.debug(f"Found table to process: {table_name}")

    # Pour chaque table, ajouter les opérations RLS
    for table_name in created_tables:
        # Trouver le modèle correspondent
        model = None
        for m in [Item, Profile]:  # Ajoutez tous vos modèles ici
            if (hasattr(m, '__tablename__') and
                getattr(m, '__tablename__', None) == table_name and
                issubclass(m, RLSModel) and
                getattr(m, '__rls_enabled__', False)):
                model = m
                break

        if model:
            logger.debug(f"Adding RLS for {table_name} from model {model.__name__}")

            # Enable RLS
            script.upgrade_ops.ops.append(
                ops.ExecuteSQLOp(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")
            )

            # Add policies
            for operation, policy in model.get_policies().items():
                sql = f"""
                    CREATE POLICY "{table_name}_{operation}" ON {table_name}
                    FOR {operation.upper()}
                """
                if policy.using:
                    sql += f"\n    USING ({policy.using})"
                if policy.check:
                    sql += f"\n    WITH CHECK ({policy.check})"
                sql += ";"

                script.upgrade_ops.ops.append(ops.ExecuteSQLOp(sql))
                logger.debug(f"Added {operation} policy for {table_name}")

            # Add downgrade operations at the beginning
            # Drop policies first
            for operation in model.get_policies().keys():
                script.downgrade_ops.ops.insert(0,
                    ops.ExecuteSQLOp(
                        f'DROP POLICY IF EXISTS "{table_name}_{operation}" ON {table_name};'
                    )
                )

            # Then disable RLS
            script.downgrade_ops.ops.insert(0,
                ops.ExecuteSQLOp(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;")
            )

    # 2. Traitement des buckets Storage
    for bucket_class in STORAGE_BUCKETS:  # Utilisez votre liste de buckets
        logger.debug(f"Processing storage bucket: {bucket_class.name}")

        # Create bucket
        script.upgrade_ops.ops.append(
            ops.ExecuteSQLOp(f"""
                INSERT INTO storage.buckets (id, name, public)
                VALUES (
                    '{bucket_class.name}',
                    '{bucket_class.name}',
                    {str(bucket_class.public).lower()}
                )
                ON CONFLICT (id) DO UPDATE
                SET public = EXCLUDED.public;
            """)
        )

        # Enable RLS on storage.objects
        script.upgrade_ops.ops.append(
            ops.ExecuteSQLOp(
                "ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;"
            )
        )

        # Add bucket policies
        for policy in bucket_class.get_policies():
            sql = f"""
                CREATE POLICY "{policy.name}"
                ON storage.objects
                FOR {policy.operation.value}
                {f"USING ({policy.using})" if policy.using else ""}
                {f"WITH CHECK ({policy.check})" if policy.check else ""};
            """
            script.upgrade_ops.ops.append(ops.ExecuteSQLOp(sql))
            logger.debug(f"Added {policy.operation.value} policy for bucket {bucket_class.name}")

        # Add downgrade operations
        for policy in bucket_class.get_policies():
            script.downgrade_ops.ops.insert(0,
                ops.ExecuteSQLOp(
                    f'DROP POLICY IF EXISTS "{policy.name}" ON storage.objects;'
                )
            )

        script.downgrade_ops.ops.append(
            ops.ExecuteSQLOp(
                f"DELETE FROM storage.buckets WHERE id = '{bucket_class.name}';"
            )
        )


def run_migrations_offline() -> None:
    """Pour générer le SQL sans connection DB."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        as_sql=True,
        include_object=include_object,
        process_revision_directives=process_revision_directives
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
            process_revision_directives=process_revision_directives
        )

        with context.begin_transaction():
            context.run_migrations()


# Choisir le mode selon l'environnement
if os.getenv("ALEMBIC_OFFLINE_MODE") == "1":
    run_migrations_offline()
else:
    run_migrations_online()
