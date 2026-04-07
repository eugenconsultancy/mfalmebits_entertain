#!/usr/bin/env bash
# build.sh — Render.com build script for MfalmeBits
# ─────────────────────────────────────────────────────────────────────
# Render runs this script once before starting the web service.
# It runs as a non-root user in a fresh container on every deploy.
#
# Environment variables expected on Render dashboard:
#   DJANGO_SETTINGS_MODULE=core.settings.render
#   DJANGO_SECRET_KEY=<50-char random string>
#   DATABASE_URL=<postgresql://...>
#   ALLOWED_HOSTS=mfalmebits-entertain.onrender.com
#   CSRF_TRUSTED_ORIGINS=https://mfalmebits-entertain.onrender.com
# ─────────────────────────────────────────────────────────────────────

set -euo pipefail   # Exit on any error; treat unset vars as errors

echo "════════════════════════════════════════════"
echo "  MfalmeBits — Render Build Script"
echo "════════════════════════════════════════════"

# ── Python & pip ─────────────────────────────────────────────────────
echo "🐍  Python version: $(python --version)"
echo "📦  Upgrading pip..."
pip install --upgrade pip --quiet

echo "📦  Installing dependencies..."
pip install -r requirements.txt --quiet

# ── Settings module ───────────────────────────────────────────────────
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-core.settings.render}"
echo "⚙️   Settings module: $DJANGO_SETTINGS_MODULE"

# ── Static files ─────────────────────────────────────────────────────
# CompressedManifestStaticFilesStorage creates a staticfiles.json
# manifest so each filename gets a content hash → perfect cache busting.
echo "📁  Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity 1
echo "✅  Static files collected."

# ── Database migrations ───────────────────────────────────────────────
echo "🔄  Running database migrations..."
python manage.py migrate --noinput --verbosity 1
echo "✅  Migrations complete."

# ── Create superuser (idempotent via create_admin.py) ─────────────────
echo "👤  Ensuring superuser exists..."
if python create_admin.py; then
    echo "✅  Superuser ready."
else
    echo "⚠️   create_admin.py reported an issue — check logs above."
    echo "     The build will continue; you can create the superuser manually."
fi

# ── Sanity check ──────────────────────────────────────────────────────
echo "🔍  Running Django system check..."
python manage.py check --deploy 2>&1 | grep -v "^System check" || true

echo ""
echo "════════════════════════════════════════════"
echo "  ✅  Build completed successfully!"
echo "════════════════════════════════════════════"