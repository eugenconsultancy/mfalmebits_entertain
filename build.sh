#!/bin/bash
# Render build script for MfalmeBits

echo "========================================="
echo "🚀 Building MfalmeBits for Render"
echo "========================================="

# Exit on error
set -e

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export DJANGO_SETTINGS_MODULE=core.settings.render

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --verbosity 0

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Create superuser (using the script)
echo "👤 Creating superuser..."
python scripts/create_superuser.py

echo "========================================="
echo "✅ Build completed successfully!"
echo "========================================="
