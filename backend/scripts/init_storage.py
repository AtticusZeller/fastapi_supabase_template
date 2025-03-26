import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models import STORAGE_BUCKETS


def get_db_url() -> str:
    """Construit l'URL de connexion à partir des variables d'environnement"""
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")
    server = os.getenv("POSTGRES_SERVER")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "postgres")
    project_id = os.getenv("SUPABASE_PROJECT_ID")

    # Format spécial pour Supabase
    pooler_user = f"{user}.{project_id}" if project_id else user

    return f"postgresql://{pooler_user}:{password}@{server}:{port}/{db}"


def init_storage():
    """Initialise les buckets et policies storage"""
    engine = create_engine(get_db_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        with SessionLocal() as session:
            # Vérifier si le schéma storage existe
            schema_exists = session.execute(
                text(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'storage')"
                )
            ).scalar()

            if not schema_exists:
                print("⚠️ Schéma storage non trouvé. Est-ce une base Supabase ?")
                return False

            for bucket_class in STORAGE_BUCKETS:
                print(f"📦 Configuration du bucket {bucket_class.name}...")

                # 1. Vérifier/Créer le bucket
                bucket_exists = session.execute(
                    text(
                        "SELECT EXISTS(SELECT 1 FROM storage.buckets WHERE id = :bucket)"
                    ),
                    {"bucket": bucket_class.name},
                ).scalar()

                if not bucket_exists:
                    print(f"Création du bucket {bucket_class.name}")
                    session.execute(
                        text(
                            """
                            INSERT INTO storage.buckets (id, name, public)
                            VALUES (:bucket, :bucket, :public)
                            ON CONFLICT (id) DO NOTHING
                            """
                        ),
                        {"bucket": bucket_class.name, "public": bucket_class.public},
                    )

                # 2. Gérer les policies
                try:
                    policies = bucket_class.get_policies()
                    for policy in policies:
                        # Vérifier si la policy existe
                        policy_exists = session.execute(
                            text(
                                """
                                SELECT EXISTS (
                                    SELECT 1 FROM pg_policies
                                    WHERE schemaname = 'storage'
                                    AND tablename = 'objects'
                                    AND policyname = :policy_name
                                )
                                """
                            ),
                            {"policy_name": policy.name},
                        ).scalar()

                        if policy_exists:
                            print(f"🔄 Mise à jour de la policy {policy.name}")
                            session.execute(
                                text(
                                    f'DROP POLICY IF EXISTS "{policy.name}" ON storage.objects'
                                )
                            )
                        else:
                            print(f"➕ Création de la policy {policy.name}")

                        # Créer/Recréer la policy
                        session.execute(
                            text(
                                f"""
                                CREATE POLICY "{policy.name}"
                                ON storage.objects
                                FOR {policy.operation.value}
                                USING ({policy.using})
                                WITH CHECK ({policy.check})
                                """
                            )
                        )

                except Exception as e:
                    print(
                        f"⚠️ Erreur lors de la configuration des policies pour {bucket_class.name}: {e}"
                    )
                    continue

            session.commit()
            print("✅ Configuration storage terminée")
            return True

    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du storage: {e}")
        return False


if __name__ == "__main__":
    init_storage()
