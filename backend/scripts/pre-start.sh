#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python -m app.utils.pre_start

# # Run migrations
# alembic upgrade head

# # Create initial data in DB
# python app/initial_data.py
