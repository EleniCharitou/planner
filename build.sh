#!/usr/bin/env bash
# Stop script on first error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files into STATIC_ROOT (needed for WhiteNoise)
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
