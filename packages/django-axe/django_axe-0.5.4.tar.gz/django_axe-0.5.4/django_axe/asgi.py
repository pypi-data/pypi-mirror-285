"""
ASGI config for django_axe project.
It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import logging
import os
from django.core.asgi import get_asgi_application
from . import version

os.environ.setdefault(key="DJANGO_SETTINGS_MODULE", value="django_axe.settings")
logger = logging.getLogger(name="django_axe")
logger.info(msg=f"Web service is ready {version}")
application = get_asgi_application()
