"""
WSGI config for usermangment project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import usermangment


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'usermangment.settings')

application = get_wsgi_application()
