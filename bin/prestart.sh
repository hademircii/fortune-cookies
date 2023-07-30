#! /usr/bin/env bash

ls -l
# Let the DB start
sleep 10;
# Run migrations
alembic upgrade head

