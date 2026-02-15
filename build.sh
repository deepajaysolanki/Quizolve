#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install libraries
pip install -r requirements.txt

# 2. Collect static files (CSS/Images)
python manage.py collectstatic --no-input

# 3. Migrate Database (Create tables in the new Postgres DB)
python manage.py migrate