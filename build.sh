#!/bin/bash
# Render build script for MfalmeBits
# This runs during deployment on Render

echo "========================================="
echo "🚀 Building MfalmeBits for Render"
echo "========================================="

# Exit on error - fail fast if something breaks
set -e

# Display Python version for debugging
echo "🐍 Python version:"
python --version

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables for this build
export DJANGO_SETTINGS_MODULE=core.settings.render
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Collect static files (required for WhiteNoise)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --verbosity 0

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Create/update superuser using the safe script
echo "👤 Setting up superuser..."
python create_admin.py

# Check if superuser creation was successful
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Superuser setup had issues, but continuing..."
fi

echo "========================================="
echo "✅ Build completed successfully!"
echo "========================================="

# List static files for debugging (optional, remove in production)
# echo "Static files collected:"
# ls -la staticfiles/ | head -20