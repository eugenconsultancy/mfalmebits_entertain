"""
core/wsgi.py
─────────────────────────────────────────────────────────────────────
WSGI entry point for MfalmeBits.

Runtime selection:
  • RENDER=true  →  core.settings.render  (Render.com hosting)
  • Otherwise    →  core.settings.development

Gunicorn launch command (2 GB RAM, 2 CPU cores):
─────────────────────────────────────────────────────────────────────
  gunicorn core.wsgi:application \\
      --workers 3 \\
      --worker-class sync \\
      --threads 2 \\
      --worker-connections 1000 \\
      --max-requests 1000 \\
      --max-requests-jitter 50 \\
      --timeout 120 \\
      --keep-alive 5 \\
      --log-level info \\
      --access-logfile - \\
      --error-logfile - \\
      --bind 0.0.0.0:$PORT

Worker sizing rationale (2 GB RAM / 2 vCPU):
  Formula: (2 × CPU_cores) + 1 = 5  — but Django + Jazzmin + Postgres
  is memory-hungry.  3 sync workers × 2 threads = 6 concurrent requests,
  using ~900 MB RSS.  Leaves 1.1 GB for Postgres connections and Redis.

  If you add --worker-class gevent or uvicorn.workers.UvicornWorker,
  reduce --workers to 2 to avoid OOM.
"""

import os

from django.core.wsgi import get_wsgi_application


# ── Settings module selection ────────────────────────────────────────

def _resolve_settings_module() -> str:
    # Explicit override always wins (e.g. set in Render dashboard)
    explicit = os.environ.get("DJANGO_SETTINGS_MODULE")
    if explicit:
        return explicit

    # Render sets RENDER=true automatically
    if os.environ.get("RENDER", "").lower() in ("true", "1"):
        return "core.settings.render"

    # CI / GitHub Actions
    if os.environ.get("CI", "").lower() in ("true", "1"):
        return "core.settings.base"

    return "core.settings.development"


settings_module = _resolve_settings_module()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

# Expose the WSGI callable as a module-level variable named "application"
application = get_wsgi_application()