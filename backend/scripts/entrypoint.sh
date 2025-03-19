#!/bin/bash
# entrypoint.sh

set -e

echo "Starting application in $APP_MODE mode (Environment: $ENVIRONMENT)"

# Fonction pour appliquer les migrations
apply_migrations() {
  echo "Checking database connection..."
  cd backend
  python -m app.database.pre_start

  echo "Checking for pending migrations..."
  PENDING_MIGRATIONS=$(alembic show head 2>/dev/null | grep -i "Pending migrations" || echo "")

  if [ -n "$PENDING_MIGRATIONS" ]; then
    echo "Pending migrations detected"

    # En production, générer d'abord un fichier SQL pour revue
    if [ "$ENVIRONMENT" = "production" ]; then
      echo "Production environment detected. Generating SQL migration script."
      alembic upgrade head --sql > /tmp/migration_sql.txt
      echo "SQL migration script generated at /tmp/migration_sql.txt"

      # Appliquer uniquement si explicitement demandé en production
      if [ "${AUTORUN_MIGRATIONS}" = "true" ]; then
        echo "AUTORUN_MIGRATIONS is enabled. Applying migrations automatically..."

        # Créer une sauvegarde de la base avant la migration
        if [ -n "$DB_BACKUP_CMD" ]; then
          echo "Creating database backup before migration..."
          eval "$DB_BACKUP_CMD"
        fi

        # Signaler aux services de se mettre en pause (si configuré)
        if [ -n "$PAUSE_SERVICES_CMD" ]; then
          echo "Pausing services before migration..."
          eval "$PAUSE_SERVICES_CMD"
        fi

        # Appliquer les migrations
        alembic upgrade head

        # Vérifier que pgmq est correctement initialisé après migration
        python -m app.utils.pgmq_init

        echo "Migrations applied successfully."

        # Signaler aux services qu'ils peuvent reprendre (si configuré)
        if [ -n "$RESUME_SERVICES_CMD" ]; then
          echo "Resuming services after migration..."
          eval "$RESUME_SERVICES_CMD"
        fi
      else
        echo "AUTORUN_MIGRATIONS is not enabled. Review the SQL and apply manually or set AUTORUN_MIGRATIONS=true."
      fi
    else
      # En développement ou staging, appliquer automatiquement
      echo "Applying migrations automatically in non-production environment..."
      alembic upgrade head

      # Initialiser pgmq après migrations
      python -m app.utils.pgmq_init

      echo "Migrations applied successfully."
    fi
  else
    echo "No pending migrations."

    # Vérifier pgmq même sans migrations
    python -m app.utils.pgmq_init
  fi

  cd ..
}

# Appliquer les migrations en mode API et en mode worker pour pgmq
# Les workers doivent également attendre que les migrations soient appliquées
if [ "$APP_MODE" = "api" ] || [ "$APP_MODE" = "worker" ] || [ "$APP_MODE" = "migrate" ]; then
  apply_migrations
fi

# Si le mode est uniquement migration, on s'arrête ici
if [ "$APP_MODE" = "migrate" ]; then
  echo "Migration completed. Exiting as requested."
  exit 0
fi

# Démarrage selon le mode configuré
case "$APP_MODE" in
  "api")
    echo "Starting FastAPI server on port $PORT"
    cd backend
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
    ;;

  "worker")
    # Vérifier si la queue est spécifiée
    if [ -z "$CELERY_QUEUE" ]; then
      CELERY_QUEUE="default"
      echo "CELERY_QUEUE not specified, using 'default'"
    fi

    # Configurer la concurrence
    if [ -z "$CELERY_CONCURRENCY" ]; then
      CELERY_CONCURRENCY=$(nproc)
      echo "Auto-detecting concurrency: $CELERY_CONCURRENCY"
    fi

    echo "Starting Celery worker for queue: $CELERY_QUEUE with concurrency: $CELERY_CONCURRENCY"
    cd backend
    exec python worker.py --queue=$CELERY_QUEUE --concurrency=$CELERY_CONCURRENCY
    ;;

  "flower")
    echo "Starting Flower monitoring on port $PORT"
    cd backend
    exec celery -A app.core.celery flower --port=$PORT
    ;;

  *)
    echo "ERROR: Unknown APP_MODE: $APP_MODE"
    echo "Supported modes: api, worker, flower, migrate"
    exit 1
    ;;
esac
