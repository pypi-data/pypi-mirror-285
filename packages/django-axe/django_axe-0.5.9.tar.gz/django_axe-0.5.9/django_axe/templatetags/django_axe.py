import logging
from django import template
from django.template.loader import render_to_string

from django.conf import settings

register = template.Library()
logger = logging.getLogger("django_axe")

@register.simple_tag(takes_context=True)
def django_axe_script(context):
    try:
        if settings.DJANGO_AXE_ENABLED:
            return render_to_string(
                request=context.get("request"),
                template_name="django_axe/script.html",
                context={},
            )
    except Exception as e:
        logger.error(e)  # noqa
    return ""
