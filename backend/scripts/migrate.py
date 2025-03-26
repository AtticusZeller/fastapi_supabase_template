import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


def load_environment(environment: str) -> bool:
    """
    Load environment variables from file or use existing CI/CD variables
    :param environment: 'development', 'staging', or 'production'
    :return: True if environment is loaded successfully
    """
    # Si on est dans GitHub Actions, les variables sont déjà définies
    if os.getenv("GITHUB_ACTIONS"):
        return True

    # Sinon, on cherche le fichier .env correspondant
    env_file = Path(f".env.{environment}")
    if env_file.exists():
        load_dotenv(env_file)
        return True

    print(f"⚠️ No environment file found for {environment}")
    return False


def run_migration(
    environment: str, command: str, message: str = "", auto_apply: bool = False
) -> bool:
    """
    Run alembic commands with specific environment
    :param environment: 'development', 'staging', or 'production'
    :param command: 'upgrade', 'downgrade', 'current', etc.
    :param message: Migration message for revision command
    :param auto_apply: Whether to automatically apply migrations
    :return: True if successful, False otherwise
    """
    # Vérifier que l'environnement est correctement configuré
    if not load_environment(environment):
        if not os.getenv("DATABASE_URL"):
            print("❌ No database configuration found!")
            sys.exit(1)

    # Vérifier la présence des variables requises
    required_vars = ["DATABASE_URL", "POSTGRES_SERVER"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    print(f"🎯 Target environment: {environment}")
    print(f"🔌 Database: {os.getenv('POSTGRES_SERVER')}")

    try:
        os.chdir("backend")

        if command == "revision":
            # Générer la migration
            subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", message], check=True
            )

            if auto_apply:
                # D'abord appliquer les migrations
                subprocess.run(["alembic", "upgrade", "head"], check=True)

                # Ensuite initialiser le storage
                from scripts.init_storage import init_storage

                if not init_storage():
                    print("⚠️ Erreur lors de l'initialisation du storage")
                    return False

        elif command == "downgrade":
            if environment in ["production", "staging"] and not os.getenv(
                "GITHUB_ACTIONS"
            ):
                confirm = input(
                    f"⚠️ Are you sure you want to downgrade in {environment}? [y/N] "
                )
                if confirm.lower() != "y":
                    print("Downgrade cancelled")
                    return False

            subprocess.run(["alembic", "downgrade", "-1"], check=True)

        else:
            subprocess.run(["alembic"] + command.split(), check=True)

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        os.chdir("..")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument("environment", choices=["development", "staging", "production"])
    parser.add_argument(
        "command",
        help="Migration command (upgrade, downgrade, current, revision, etc.)",
    )
    parser.add_argument("--message", "-m", help="Migration message")
    parser.add_argument(
        "--auto-apply",
        action="store_true",
        help="Automatically test and apply migrations",
    )

    args = parser.parse_args()
    success = run_migration(
        args.environment, args.command, args.message, args.auto_apply
    )
    sys.exit(0 if success else 1)
