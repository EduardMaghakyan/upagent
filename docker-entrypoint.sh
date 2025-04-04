#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Function to wait for PostgreSQL to be ready
postgres_ready() {
    poetry run python << END
import sys
import psycopg2
import os
import dj_database_url

try:
    url = os.environ.get('DATABASE_URL')
    if url:
        conn_params = dj_database_url.parse(url)
        conn = psycopg2.connect(
            dbname=conn_params['NAME'],
            user=conn_params['USER'],
            password=conn_params['PASSWORD'],
            host=conn_params['HOST'],
            port=conn_params['PORT'],
        )
        conn.close()
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")
    sys.exit(1)
END
}

# Function to wait for Redis to be ready
redis_ready() {
    poetry run python << END
import sys
import redis
import os
import time

try:
    url = os.environ.get('RQ_REDIS_URL', 'redis://redis:6379/0')
    conn = redis.from_url(url)
    conn.ping()
    sys.exit(0)
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    sys.exit(1)
END
}

# Wait for PostgreSQL
until postgres_ready; do
  echo >&2 "PostgreSQL is unavailable - waiting..."
  sleep 1
done
echo >&2 "PostgreSQL is up - continuing..."

# Wait for Redis
until redis_ready; do
  echo >&2 "Redis is unavailable - waiting..."
  sleep 1
done
echo >&2 "Redis is up - continuing..."

# Apply database migrations
if [ "$1" = "python" ] && [ "$2" = "manage.py" ] && [ "$3" = "runserver" ]; then
    echo >&2 "Applying database migrations..."
    poetry run python manage.py migrate --noinput
    
    echo >&2 "Creating superuser if it doesn't exist..."
    poetry run python << END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upagent_monitor.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created.')
else:
    print('Superuser already exists.')
END

    echo >&2 "Collecting static files..."
    poetry run python manage.py collectstatic --noinput
    poetry run python manage.py compress --force
    
    # Run the actual command (runserver)
    exec poetry run "$@"
else
    # For other commands like rqworker, rqscheduler, etc.
    exec poetry run "$@"
fi