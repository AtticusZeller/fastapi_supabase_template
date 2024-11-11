#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python -m app.utils.test_pre_start

# before migrations
# alembic init
# mkdir -p app/alembic/versions
# alembic revision --autogenerate -m "initial commit"

# Run migrations
alembic upgrade head

# Create initial data in DB
python -m app.utils.init_data
