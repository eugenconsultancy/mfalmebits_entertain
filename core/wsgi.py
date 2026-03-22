"""
WSGI config for core project.
"""

import os

from django.core.wsgi import get_wsgi_application

# Use railway settings if on Railway
if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.railway')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

application = get_wsgi_application()