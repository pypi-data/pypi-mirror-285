import logging
from django.shortcuts import render

logger = logging.getLogger(name="django_axe")


def home(request):
    return render(request=request, template_name="base.html")
