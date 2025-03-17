#!/usr/bin/env python3
"""
Script pour installer et configurer Sentry dans l'application FastAPI.

Ce script doit être exécuté après l'installation des dépendances du projet.
Il vérifie que sentry-sdk est installé et aide à la configuration initiale.
"""

import os
import sys


def check_sentry_installed():
    """Vérifie si sentry-sdk est installé."""
    try:
        import sentry_sdk
        print(f"✅ sentry-sdk est installé (version {sentry_sdk.__version__})")
        return True
    except ImportError:
        print("❌ sentry-sdk n'est pas installé")
        return False


def install_sentry():
    """Installe sentry-sdk si nécessaire."""
    print("Installation de sentry-sdk...")
    os.system(f"{sys.executable} -m pip install sentry-sdk")
    try:
        import sentry_sdk
        print(f"✅ sentry-sdk installé avec succès (version {sentry_sdk.__version__})")
        return True
    except ImportError:
        print("❌ Échec de l'installation de sentry-sdk")
        return False


def generate_config_snippet():
    """Génère un extrait de code pour configurer Sentry dans FastAPI."""
    return """
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "development"),
    traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
    profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
    enable_tracing=os.getenv("SENTRY_ENABLE_TRACING", "False").lower() == "true",
    release=os.getenv("SENTRY_RELEASE", "unknown"),
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
)
"""


def update_env_templates():
    """Met à jour les modèles de fichiers .env pour inclure les variables Sentry."""
    sentry_env_vars = """
# Sentry Config
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
SENTRY_ENABLE_TRACING=False
SENTRY_RELEASE=local-dev
"""

    env_templates = [".env.example", ".env.test"]
    for template in env_templates:
        if os.path.exists(template):
            with open(template, "r") as f:
                content = f.read()

            if "SENTRY_DSN" not in content:
                with open(template, "a") as f:
                    f.write(sentry_env_vars)
                print(f"✅ Variables Sentry ajoutées au fichier {template}")
            else:
                print(f"ℹ️ Les variables Sentry sont déjà dans le fichier {template}")
        else:
            print(f"⚠️ Fichier {template} non trouvé")


def main():
    """Fonction principale."""
    print("🔍 Vérification de l'installation de Sentry..."
          "\n--------------------------------------------")

    if not check_sentry_installed():
        if not install_sentry():
            print("⚠️ Impossible d'installer sentry-sdk. Veuillez l'installer manuellement.")
            return

    print("\n📋 Configuration de Sentry dans votre application FastAPI"
          "\n--------------------------------------------")
    print("Ajoutez ce code à votre application FastAPI:")
    print("")
    print(generate_config_snippet())

    print("\n📝 Mise à jour des modèles .env"
          "\n--------------------------------------------")
    update_env_templates()

    print("\n🚀 Prochaines étapes:"
          "\n--------------------------------------------")
    print("1. Obtenez un DSN Sentry depuis votre compte Sentry")
    print("2. Ajoutez-le à votre fichier .env")
    print("3. Configurez les secrets GitHub pour l'intégration CI/CD:")
    print("   - SENTRY_AUTH_TOKEN")
    print("   - SENTRY_ORG")
    print("   - SENTRY_PROJECT")
    print("\n✨ Sentry est prêt à être configuré dans votre application !")


if __name__ == "__main__":
    main()
