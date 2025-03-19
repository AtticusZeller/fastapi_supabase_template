#!/bin/bash
# rollback.sh

set -e

if [ -z "$1" ]; then
  echo "Error: Please specify the number of migrations to roll back or a specific revision."
  echo "Usage: rollback.sh [-n N | -r REVISION]"
  exit 1
fi

cd backend

# Parse arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -n|--number)
      STEPS="$2"
      echo "Rolling back $STEPS migrations..."
      alembic downgrade -${STEPS}
      shift 2
      ;;
    -r|--revision)
      REVISION="$2"
      echo "Rolling back to revision $REVISION..."
      alembic downgrade ${REVISION}
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Rollback completed successfully."
