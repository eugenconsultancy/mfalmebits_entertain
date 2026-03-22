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

# Compress static files (if using django-compressor)
echo "🎨 Compressing static assets..."
python manage.py compress --force --verbosity 0 || echo "⚠️  Compression skipped"

# Run migrations (only if needed)
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Create cache tables
echo "💾 Creating cache tables..."
python manage.py createcachetable || echo "⚠️  Cache table creation skipped"

echo "========================================="
echo "✅ Build completed successfully!"
echo "========================================="