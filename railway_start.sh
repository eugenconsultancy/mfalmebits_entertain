#!/bin/bash
# Railway deployment startup script for MfalmeBits

set -e  # Exit on any error

echo "========================================="
echo "🚀 Starting MfalmeBits deployment on Railway"
echo "========================================="
echo "Time: $(date)"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "========================================="

# Check for required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set"
    exit 1
fi

if [ -z "$DJANGO_SECRET_KEY" ]; then
    echo "❌ ERROR: DJANGO_SECRET_KEY is not set"
    exit 1
fi

echo "✅ Environment variables verified"

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python -c "
import time
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.railway')
django.setup()
from django.db import connections
from django.db.utils import OperationalError
for _ in range(30):
    try:
        connections['default'].ensure_connection()
        print('✅ Database is ready!')
        break
    except OperationalError:
        print('⏳ Database not ready yet, waiting...')
        time.sleep(2)
else:
    print('❌ Database connection timeout')
    exit(1)
"

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --verbosity 0
if [ $? -eq 0 ]; then
    echo "✅ Static files collected successfully"
else
    echo "❌ Failed to collect static files"
    exit 1
fi

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migrations failed"
    exit 1
fi

# Create superuser if not exists (optional - for development)
echo "👤 Checking for superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@mfalmebits.com',
        password='admin123'
    )
    print("✅ Superuser created (admin/admin123)")
else:
    print("✅ Superuser already exists")
EOF

# Optional: Run compress for CSS/JS
echo "🎨 Compressing static assets..."
python manage.py compress --force --verbosity 0 2>/dev/null || echo "⚠️  Compression skipped (django-compressor not configured)"

echo "========================================="
echo "✅ Deployment preparation complete!"
echo "🌐 Starting Gunicorn server..."
echo "========================================="

# Start Gunicorn with production settings
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info