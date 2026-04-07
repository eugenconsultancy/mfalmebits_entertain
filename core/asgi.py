"""
core/asgi.py
─────────────────────────────────────────────────────────────────────
ASGI entry point for MfalmeBits.

Use this when you want to handle WebSockets (e.g. Django Channels) or
simply prefer the async Uvicorn / Daphne server.

Uvicorn launch command (2 GB RAM, 2 CPU cores):
─────────────────────────────────────────────────────────────────────
  uvicorn core.asgi:application \\
      --workers 3 \\
      --host 0.0.0.0 \\
      --port $PORT \\
      --log-level info \\
      --access-log \\
      --timeout-keep-alive 5 \\
      --loop uvloop \\
      --http h11

  — OR via Gunicorn with UvicornWorker (preferred on Render):

  gunicorn core.asgi:application \\
      --workers 2 \\
      --worker-class uvicorn.workers.UvicornWorker \\
      --bind 0.0.0.0:$PORT \\
      --timeout 120 \\
      --max-requests 500 \\
      --max-requests-jitter 50 \\
      --log-level info \\
      --access-logfile - \\
      --error-logfile -

  Note: Use 2 workers (not 3) with UvicornWorker on 2 GB boxes because
  each uvicorn worker carries a larger memory footprint than sync workers.

Dependencies:
    pip install uvicorn[standard] uvloop httptools
    # For Channels support:
    pip install channels channels-redis
"""

import os

from django.core.asgi import get_asgi_application


# ── Settings resolution (mirrors wsgi.py) ────────────────────────────

def _resolve_settings_module() -> str:
    explicit = os.environ.get("DJANGO_SETTINGS_MODULE")
    if explicit:
        return explicit
    if os.environ.get("RENDER", "").lower() in ("true", "1"):
        return "core.settings.render"
    if os.environ.get("CI", "").lower() in ("true", "1"):
        return "core.settings.base"
    return "core.settings.development"


settings_module = _resolve_settings_module()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)


# ── ASGI application ─────────────────────────────────────────────────
#
# Plain Django ASGI (no WebSocket / Channels).
# If you add django-channels later, replace the block below with:
#
#   from channels.routing import ProtocolTypeRouter, URLRouter
#   from channels.auth import AuthMiddlewareStack
#   import apps.myapp.routing
#
#   django_asgi_app = get_asgi_application()
#
#   application = ProtocolTypeRouter({
#       "http":      django_asgi_app,
#       "websocket": AuthMiddlewareStack(
#           URLRouter(apps.myapp.routing.websocket_urlpatterns)
#       ),
#   })

application = get_asgi_application()