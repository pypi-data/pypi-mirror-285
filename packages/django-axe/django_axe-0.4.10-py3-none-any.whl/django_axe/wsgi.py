"""
WSGI config for django_axe project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import logging
import os
from django.core.wsgi import get_wsgi_application
from . import version

os.environ.setdefault(key="DJANGO_SETTINGS_MODULE", value="django_axe.settings")
logger = logging.getLogger(name="django_axe")
logger.info(msg=f"Web service is ready {version}")
application = get_wsgi_application()
