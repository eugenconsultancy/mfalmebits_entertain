#!/bin/bash
# Render startup script for MfalmeBits

echo "========================================="
echo "🌐 Starting MfalmeBits on Render"
echo "========================================="

# Set environment
export DJANGO_SETTINGS_MODULE=core.settings.render

# Wait for database to be ready
echo "⏳ Waiting for database..."
python -c "
import os, time, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.render')
import django
django.setup()
from django.db import connections
from django.db.utils import OperationalError

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        connections['default'].ensure_connection()
        print('✅ Database is ready!')
        sys.exit(0)
    except OperationalError:
        retry_count += 1
        print(f'⏳ Database not ready (attempt {retry_count}/{max_retries}), waiting...')
        time.sleep(2)

print('❌ Could not connect to database after 30 attempts')
sys.exit(1)
"

# Check if migrations need to be run
echo "🔄 Checking for pending migrations..."
python manage.py migrate --check --noinput
if [ $? -ne 0 ]; then
    echo "📝 Running pending migrations..."
    python manage.py migrate --noinput
fi

# Start Gunicorn
echo "🚀 Starting Gunicorn server..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info