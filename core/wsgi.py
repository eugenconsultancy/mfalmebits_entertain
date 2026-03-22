"""
WSGI config for core project.
"""

import os

from django.core.wsgi import get_wsgi_application

# Use render settings if on Render
if os.environ.get('RENDER') == 'true':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.render')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

application = get_wsgi_application()
