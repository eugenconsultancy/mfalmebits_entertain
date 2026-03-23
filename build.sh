#!/bin/bash
# Render build script for MfalmeBits Entertainment

echo "========================================="
echo "🚀 Building MfalmeBits Entertainment for Render"
echo "========================================="

set -e

echo "🐍 Python version:"
python --version

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=core.settings.render
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --verbosity 0

echo "🔄 Running database migrations..."
python manage.py migrate --noinput

echo "👤 Setting up superuser..."
# Run the create_admin.py script from project root
python create_admin.py

if [ $? -ne 0 ]; then
    echo "⚠️ Warning: Superuser setup had issues, but continuing..."
fi

echo "========================================="
echo "✅ Build completed successfully!"
echo "========================================="