"""Script utilitaire pour vérifier la connection à Supabase et les prérequis pour les tests.
Exécutez-le avant les tests pour diagnostiquer les problèmes de connection.
"""

import os
import sys

import httpx
from dotenv import load_dotenv


def main():
    # Charger les variables d'environnement
    env_file = ".env.test"
    print(f"📋 Recherche du fichier {env_file}...")
    if not os.path.exists(env_file):
        print(f"❌ Fichier {env_file} manquant")
        env_file = "../.env.test"
        if not os.path.exists(env_file):
            print(f"❌ Fichier {env_file} également manquant")
            print("🔍 Utilisation des variables d'environnement sans fichier .env")
        else:
            print(f"✅ Fichier {env_file} trouvé")
            load_dotenv(env_file)
    else:
        print(f"✅ Fichier {env_file} trouvé")
        load_dotenv(env_file)

    # Vérifier les variables requises
    required_vars = [
        "PROJECT_NAME",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SERVICE_KEY",
        "POSTGRES_SERVER",
        "POSTGRES_USER",
        "FIRST_SUPERUSER",
        "FIRST_SUPERUSER_PASSWORD",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        sys.exit(1)

    print("✅ Toutes les variables d'environnement requises sont présentes")

    # Tester la connection à Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    print(f"🔍 Test de connection à Supabase: {url}")

    # Test avec la clé anon
    try:
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}
        response = httpx.get(
            f"{url}/rest/v1/?apikey={key}", headers=headers, timeout=10
        )
        if response.status_code in (200, 204):
            print(
                f"✅ Connection réussie avec la clé anon (status: {response.status_code})"
            )
        else:
            print(
                f"❌ Échec de connection avec la clé anon (status: {response.status_code})"
            )
            print(f"Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur lors de la connection avec la clé anon: {e}")

    # Test avec la clé service
    try:
        headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}
        response = httpx.get(
            f"{url}/rest/v1/?apikey={service_key}", headers=headers, timeout=10
        )
        if response.status_code in (200, 204):
            print(
                f"✅ Connection réussie avec la clé service (status: {response.status_code})"
            )
        else:
            print(
                f"❌ Échec de connection avec la clé service (status: {response.status_code})"
            )
            print(f"Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur lors de la connection avec la clé service: {e}")

    # Vérifier l'existence du bucket de stockage
    try:
        headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}
        response = httpx.get(
            f"{url}/storage/v1/bucket/profile-pictures", headers=headers, timeout=10
        )
        if response.status_code == 200:
            print("✅ Bucket 'profile-pictures' trouvé")
        elif response.status_code == 404:
            print("❌ Bucket 'profile-pictures' manquant")

            # Essayer de créer le bucket
            try:
                create_response = httpx.post(
                    f"{url}/storage/v1/bucket",
                    headers=headers,
                    json={
                        "name": "profile-pictures",
                        "public": True,
                        "file_size_limit": 5242880,
                    },
                    timeout=10,
                )
                if create_response.status_code in (200, 201):
                    print("✅ Bucket 'profile-pictures' créé avec succès")
                else:
                    print(
                        f"❌ Échec de création du bucket (status: {create_response.status_code})"
                    )
                    print(f"Réponse: {create_response.text}")
            except Exception as e:
                print(f"❌ Erreur lors de la création du bucket: {e}")
        else:
            print(
                f"❌ Erreur inattendue lors de la vérification du bucket (status: {response.status_code})"
            )
            print(f"Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du bucket: {e}")


if __name__ == "__main__":
    main()
