from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from alembic.env import get_url
from app.models import STORAGE_BUCKETS


def init_storage():
    """Initialise les buckets et policies storage"""
    engine = create_engine(get_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
                text("SELECT EXISTS(SELECT 1 FROM storage.buckets WHERE id = :bucket)"),
                {"bucket": bucket_class.name},
            ).scalar()

            if not bucket_exists:
                print(f"Création du bucket {bucket_class.name}")
                session.execute(
                    text(
                        """
                    INSERT INTO storage.buckets (id, name)
                    VALUES (:bucket, :bucket)
                    ON CONFLICT (id) DO NOTHING
                    """
                    ),
                    {"bucket": bucket_class.name},
                )

            # 2. Gérer les policies
            for policy_name, policy in bucket_class.policies.items():
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
                    {"policy_name": policy_name},
                ).scalar()

                if policy_exists:
                    print(f"🔄 Mise à jour de la policy {policy_name}")
                    # Supprimer l'ancienne policy
                    session.execute(
                        text(
                            f'DROP POLICY IF EXISTS "{policy_name}" ON storage.objects'
                        )
                    )
                else:
                    print(f"➕ Création de la policy {policy_name}")

                # Créer/Recréer la policy
                session.execute(
                    text(
                        f"""
                    CREATE POLICY "{policy_name}"
                    ON storage.objects
                    FOR ALL
                    USING ({policy.using})
                    WITH CHECK ({policy.check})
                    """
                    )
                )

        session.commit()
        print("✅ Configuration storage terminée")
        return True


if __name__ == "__main__":
    init_storage()
