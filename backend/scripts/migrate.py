import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


def run_migration(
    environment: str, command: str, message: str = "", auto_apply: bool = False
):
    """
    Run alembic commands with specific environment
    :param environment: 'development', 'staging', or 'production'
    :param command: 'upgrade', 'downgrade', 'current', etc.
    :param message: Migration message
    :param auto_apply: Whether to automatically apply and test migrations
    """
    # Charger le bon fichier d'environnement
    env_file = Path(f".env.{environment}")
    if not env_file.exists():
        print(f"Environment file {env_file} not found!")
        sys.exit(1)

    load_dotenv(env_file)

    # Sauvegarder l'état actuel
    current_rev = subprocess.check_output(["alembic", "current"], text=True).strip()

    try:
        os.chdir("backend")

        if command == "revision":
            # Générer la migration
            subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", message], check=True
            )

            if auto_apply:
                # Vérifier le downgrade
                latest_migration = sorted(Path("migrations/versions").glob("*.py"))[-1]
                if "def downgrade" not in latest_migration.read_text():
                    print("⚠️ Migration n'a pas de fonction downgrade !")
                    latest_migration.unlink()
                    return False

                # Test upgrade
                subprocess.run(["alembic", "upgrade", "head"], check=True)

                # Test downgrade
                subprocess.run(["alembic", "downgrade", "-1"], check=True)

                # Réappliquer si tout est ok
                subprocess.run(["alembic", "upgrade", "head"], check=True)

        elif command == "downgrade":
            # Confirmation pour environnements sensibles
            if environment in ["production", "staging"]:
                confirm = input(
                    f"⚠️ Voulez-vous vraiment faire un rollback en {environment}? [y/N] "
                )
                if confirm.lower() != "y":
                    print("Rollback annulé")
                    return False

            subprocess.run(["alembic", "downgrade", "-1"], check=True)

        else:
            subprocess.run(["alembic"] + command.split(), check=True)

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        if command == "revision" and auto_apply:
            print("Rollback des changements...")
            subprocess.run(["alembic", "downgrade", current_rev], check=True)
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
