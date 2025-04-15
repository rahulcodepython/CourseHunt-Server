#!/bin/sh

# Exit script on any error
set -e

echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Uncomment this line if you want to create a superuser automatically
# echo "Creating superuser..."
# python manage.py createsuperuser --noinput

echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 server.wsgi:application
